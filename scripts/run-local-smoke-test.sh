#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SPARKBOT_SMOKE_BACKEND_PORT="${SPARKBOT_SMOKE_BACKEND_PORT:-18080}"
SPARKBOT_SMOKE_FRONTEND_PORT="${SPARKBOT_SMOKE_FRONTEND_PORT:-15180}"
SPARKBOT_SMOKE_BACKEND_HOST="${SPARKBOT_SMOKE_BACKEND_HOST:-127.0.0.1}"
SPARKBOT_SMOKE_FRONTEND_HOST="${SPARKBOT_SMOKE_FRONTEND_HOST:-127.0.0.1}"
SPARKBOT_SMOKE_OLLAMA_MODEL="${SPARKBOT_SMOKE_OLLAMA_MODEL:-llama3.2}"
SPARKBOT_SMOKE_DATA_DIR="${SPARKBOT_SMOKE_DATA_DIR:-}"
SPARKBOT_SMOKE_USE_HOST_SUBSCRIPTIONS="${SPARKBOT_SMOKE_USE_HOST_SUBSCRIPTIONS:-false}"

case "${SPARKBOT_SMOKE_USE_HOST_SUBSCRIPTIONS}" in
  true|false) ;;
  *)
    echo "SPARKBOT_SMOKE_USE_HOST_SUBSCRIPTIONS must be true or false." >&2
    exit 1
    ;;
esac

case "${SPARKBOT_SMOKE_BACKEND_HOST}" in
  127.0.0.1|localhost) ;;
  *)
    echo "Smoke backend host must be 127.0.0.1 or localhost." >&2
    exit 1
    ;;
esac

case "${SPARKBOT_SMOKE_FRONTEND_HOST}" in
  127.0.0.1|localhost) ;;
  *)
    echo "Smoke frontend host must be 127.0.0.1 or localhost." >&2
    exit 1
    ;;
esac

WORK_DIR="$(mktemp -d /tmp/sparkbot-local-smoke-XXXXXX)"
DATA_DIR="${SPARKBOT_SMOKE_DATA_DIR:-${WORK_DIR}/data}"
BACKEND_LOG="${WORK_DIR}/backend.log"
FRONTEND_LOG="${WORK_DIR}/frontend.log"
BACKEND_PID=""
FRONTEND_PID=""

BACKEND_SUBSCRIPTION_ENV=()
if [[ "${SPARKBOT_SMOKE_USE_HOST_SUBSCRIPTIONS}" == "true" ]]; then
  echo "Smoke test will use host Codex/Claude subscription sign-in state if present."
else
  BACKEND_SUBSCRIPTION_ENV=(
    "CODEX_HOME=${WORK_DIR}/codex-home"
    "SPARKBOT_CODEX_AUTH_FILE="
    "CLAUDE_HOME=${WORK_DIR}/claude-home"
    "SPARKBOT_CLAUDE_AUTH_FILE="
    "SPARKBOT_CLAUDE_SUBSCRIPTION_ENABLED=false"
  )
fi

backend_url="http://${SPARKBOT_SMOKE_BACKEND_HOST}:${SPARKBOT_SMOKE_BACKEND_PORT}"
frontend_url="http://${SPARKBOT_SMOKE_FRONTEND_HOST}:${SPARKBOT_SMOKE_FRONTEND_PORT}"

stop_backend() {
  if [[ -n "${BACKEND_PID}" ]] && kill -0 "${BACKEND_PID}" >/dev/null 2>&1; then
    kill "${BACKEND_PID}" >/dev/null 2>&1 || true
    wait "${BACKEND_PID}" >/dev/null 2>&1 || true
  fi
  BACKEND_PID=""
}

stop_frontend() {
  if [[ -n "${FRONTEND_PID}" ]] && kill -0 "${FRONTEND_PID}" >/dev/null 2>&1; then
    kill "${FRONTEND_PID}" >/dev/null 2>&1 || true
    wait "${FRONTEND_PID}" >/dev/null 2>&1 || true
  fi
  FRONTEND_PID=""
}

cleanup() {
  stop_frontend
  stop_backend
  rm -rf "${WORK_DIR}"
}
trap cleanup EXIT

ensure_backend_deps() {
  if [[ -x "${ROOT_DIR}/.venv-local/bin/python" ]] && "${ROOT_DIR}/.venv-local/bin/python" -c "import uvicorn" >/dev/null 2>&1; then
    return 0
  fi

  echo "Preparing local backend development environment in .venv-local"
  python3 -m venv "${ROOT_DIR}/.venv-local"
  "${ROOT_DIR}/.venv-local/bin/python" -m pip install --upgrade pip
  "${ROOT_DIR}/.venv-local/bin/python" -m pip install -e "${ROOT_DIR}/backend[dev]"
}

ensure_frontend_deps() {
  if [[ -x "${ROOT_DIR}/frontend/node_modules/.bin/vite" ]]; then
    return 0
  fi

  echo "Preparing frontend development dependencies with npm ci"
  (cd "${ROOT_DIR}/frontend" && npm ci)
}

wait_for_url() {
  local label="$1"
  local url="$2"
  local log_file="$3"
  local attempts=60
  local attempt

  for attempt in $(seq 1 "${attempts}"); do
    if curl -fsS "${url}" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done

  echo "Timed out waiting for ${label} at ${url}." >&2
  if [[ -f "${log_file}" ]]; then
    echo "--- ${label} log ---" >&2
    tail -80 "${log_file}" >&2 || true
  fi
  exit 1
}

start_backend_disabled() {
  mkdir -p "${DATA_DIR}"
  : >"${BACKEND_LOG}"
  echo "Starting backend disabled-mode smoke server at ${backend_url}"
  env \
    SPARKBOT_DATA_DIR="${DATA_DIR}" \
    "${BACKEND_SUBSCRIPTION_ENV[@]}" \
    SPARKBOT_BACKEND_HOST="${SPARKBOT_SMOKE_BACKEND_HOST}" \
    SPARKBOT_BACKEND_PORT="${SPARKBOT_SMOKE_BACKEND_PORT}" \
    bash "${ROOT_DIR}/scripts/start-backend-dev.sh" >"${BACKEND_LOG}" 2>&1 &
  BACKEND_PID="$!"
  wait_for_url "backend" "${backend_url}/health" "${BACKEND_LOG}"
}

start_backend_enabled() {
  : >"${BACKEND_LOG}"
  echo "Starting backend enabled-mode status smoke server at ${backend_url}"
  env \
    SPARKBOT_DATA_DIR="${DATA_DIR}" \
    "${BACKEND_SUBSCRIPTION_ENV[@]}" \
    SPARKBOT_LOCAL_MODELS_ENABLED=true \
    SPARKBOT_OLLAMA_MODEL="${SPARKBOT_SMOKE_OLLAMA_MODEL}" \
    SPARKBOT_BACKEND_HOST="${SPARKBOT_SMOKE_BACKEND_HOST}" \
    SPARKBOT_BACKEND_PORT="${SPARKBOT_SMOKE_BACKEND_PORT}" \
    bash "${ROOT_DIR}/scripts/start-backend-dev.sh" >"${BACKEND_LOG}" 2>&1 &
  BACKEND_PID="$!"
  wait_for_url "backend" "${backend_url}/health" "${BACKEND_LOG}"
}

start_frontend() {
  : >"${FRONTEND_LOG}"
  echo "Starting frontend smoke server at ${frontend_url}"
  env \
    SPARKBOT_BACKEND_PORT="${SPARKBOT_SMOKE_BACKEND_PORT}" \
    VITE_SPARKBOT_API_BASE_URL="${backend_url}" \
    SPARKBOT_FRONTEND_HOST="${SPARKBOT_SMOKE_FRONTEND_HOST}" \
    SPARKBOT_FRONTEND_PORT="${SPARKBOT_SMOKE_FRONTEND_PORT}" \
    bash "${ROOT_DIR}/scripts/start-frontend-dev.sh" >"${FRONTEND_LOG}" 2>&1 &
  FRONTEND_PID="$!"
  wait_for_url "frontend" "${frontend_url}" "${FRONTEND_LOG}"
}

check_runtime_data_dir() {
  local response
  response="$(curl -fsS "${backend_url}/local/runtime/settings")"
  case "${response}" in
    *"${DATA_DIR}"*) ;;
    *)
      echo "Runtime settings did not report the smoke data directory ${DATA_DIR}." >&2
      echo "${response}" >&2
      exit 1
      ;;
  esac
}

check_enabled_local_model_status() {
  local response
  response="$(curl -fsS "${backend_url}/local-models/status")"
  printf "%s\n" "${response}"
  case "${response}" in
    *\"local_models_enabled\":true*) ;;
    *)
      echo "Enabled-mode local model status did not report local_models_enabled=true." >&2
      exit 1
      ;;
  esac
  case "${response}" in
    *\"prompt_calls\":\"enabled-local-only\"*|*\"prompt_calls\":\ \"enabled-local-only\"*) ;;
    *)
      echo "Enabled-mode local model status did not report enabled-local-only prompt calls." >&2
      exit 1
      ;;
  esac
  case "${response}" in
    *\"base_url_policy\":\"localhost-only\"*|*\"base_url_policy\":\ \"localhost-only\"*) ;;
    *)
      echo "Enabled-mode local model status did not report localhost-only base URL policy." >&2
      exit 1
      ;;
  esac
}

cd "${ROOT_DIR}"
ensure_backend_deps
ensure_frontend_deps

start_backend_disabled
start_frontend
SPARKBOT_BACKEND_URL="${backend_url}" SPARKBOT_FRONTEND_URL="${frontend_url}" bash "${ROOT_DIR}/scripts/smoke-check-local.sh"
check_runtime_data_dir

stop_backend
start_backend_enabled
check_enabled_local_model_status

stop_frontend
stop_backend

echo "PASS: one-command local Sparkbot smoke test completed"
if [[ -n "${SPARKBOT_SMOKE_DATA_DIR}" ]]; then
  echo "Smoke data directory preserved: ${DATA_DIR}"
else
  echo "Smoke data directory was temporary and will be removed on exit."
fi
