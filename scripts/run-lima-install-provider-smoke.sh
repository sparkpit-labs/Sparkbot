#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SPARKBOT_LIMA_INSTALL_SMOKE_BACKEND_HOST="${SPARKBOT_LIMA_INSTALL_SMOKE_BACKEND_HOST:-127.0.0.1}"
SPARKBOT_LIMA_INSTALL_SMOKE_BACKEND_PORT="${SPARKBOT_LIMA_INSTALL_SMOKE_BACKEND_PORT:-18280}"
SPARKBOT_LIMA_INSTALL_SMOKE_DATA_DIR="${SPARKBOT_LIMA_INSTALL_SMOKE_DATA_DIR:-}"
SPARKBOT_LIMA_INSTALL_SMOKE_REPORT_PATH="${SPARKBOT_LIMA_INSTALL_SMOKE_REPORT_PATH:-}"
SPARKBOT_LIMA_PROVIDER_ADAPTER_URL="${SPARKBOT_LIMA_PROVIDER_ADAPTER_URL:-}"

case "${SPARKBOT_LIMA_INSTALL_SMOKE_BACKEND_HOST}" in
  127.0.0.1|localhost) ;;
  *)
    echo "LIMA install smoke backend host must be 127.0.0.1 or localhost." >&2
    exit 1
    ;;
esac

if [[ -z "${SPARKBOT_LIMA_PROVIDER_ADAPTER_URL}" ]]; then
  echo "Set SPARKBOT_LIMA_PROVIDER_ADAPTER_URL to the localhost LIMA Guardian provider adapter endpoint." >&2
  exit 1
fi

validate_adapter_url() {
  SPARKBOT_LIMA_PROVIDER_ADAPTER_URL="${SPARKBOT_LIMA_PROVIDER_ADAPTER_URL}" python3 - <<'PYURL'
import os
import sys
from urllib.parse import urlparse

url = os.environ["SPARKBOT_LIMA_PROVIDER_ADAPTER_URL"].strip()
parsed = urlparse(url)
if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost"}:
    print("SPARKBOT_LIMA_PROVIDER_ADAPTER_URL must be an http localhost endpoint.", file=sys.stderr)
    raise SystemExit(1)
if parsed.username or parsed.password or parsed.query or parsed.fragment:
    print("SPARKBOT_LIMA_PROVIDER_ADAPTER_URL must not include credentials, query parameters, or fragments.", file=sys.stderr)
    raise SystemExit(1)
if not parsed.path or parsed.path == "/":
    print("SPARKBOT_LIMA_PROVIDER_ADAPTER_URL must include the adapter dispatch path.", file=sys.stderr)
    raise SystemExit(1)
PYURL
}

WORK_DIR="$(mktemp -d /tmp/sparkbot-lima-install-smoke-XXXXXX)"
DATA_DIR="${SPARKBOT_LIMA_INSTALL_SMOKE_DATA_DIR:-${WORK_DIR}/data}"
BACKEND_LOG="${WORK_DIR}/backend.log"
BACKEND_PID=""
backend_url="http://${SPARKBOT_LIMA_INSTALL_SMOKE_BACKEND_HOST}:${SPARKBOT_LIMA_INSTALL_SMOKE_BACKEND_PORT}"

stop_backend() {
  if [[ -n "${BACKEND_PID}" ]] && kill -0 "${BACKEND_PID}" >/dev/null 2>&1; then
    kill "${BACKEND_PID}" >/dev/null 2>&1 || true
    wait "${BACKEND_PID}" >/dev/null 2>&1 || true
  fi
  BACKEND_PID=""
}

cleanup() {
  stop_backend
  rm -rf "${WORK_DIR}"
}
trap cleanup EXIT

ensure_backend_deps() {
  if [[ -x "${ROOT_DIR}/.venv-local/bin/python" ]] && "${ROOT_DIR}/.venv-local/bin/python" -c "import uvicorn" >/dev/null 2>&1; then
    return 0
  fi

  echo "Backend development dependencies are missing. Run scripts/run-local-smoke-test.sh once to prepare .venv-local." >&2
  exit 1
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

start_backend() {
  mkdir -p "${DATA_DIR}"
  : >"${BACKEND_LOG}"
  echo "Starting Sparkbot backend for real LIMA provider smoke at ${backend_url}"
  env \
    SPARKBOT_DATA_DIR="${DATA_DIR}" \
    SPARKBOT_PROVIDER_CALLS_ENABLED=true \
    SPARKBOT_LIMA_PROVIDER_ADAPTER_URL="${SPARKBOT_LIMA_PROVIDER_ADAPTER_URL}" \
    SPARKBOT_BACKEND_HOST="${SPARKBOT_LIMA_INSTALL_SMOKE_BACKEND_HOST}" \
    SPARKBOT_BACKEND_PORT="${SPARKBOT_LIMA_INSTALL_SMOKE_BACKEND_PORT}" \
    bash "${ROOT_DIR}/scripts/start-backend-dev.sh" >"${BACKEND_LOG}" 2>&1 &
  BACKEND_PID="$!"
  wait_for_url "backend" "${backend_url}/health" "${BACKEND_LOG}"
}

run_adapter_smoke() {
  if [[ -n "${SPARKBOT_LIMA_INSTALL_SMOKE_REPORT_PATH}" ]]; then
    SPARKBOT_BACKEND_URL="${backend_url}" \
      SPARKBOT_LIMA_SMOKE_REPORT_PATH="${SPARKBOT_LIMA_INSTALL_SMOKE_REPORT_PATH}" \
      bash "${ROOT_DIR}/scripts/smoke-check-lima-provider-adapter.sh"
    return 0
  fi

  SPARKBOT_BACKEND_URL="${backend_url}" bash "${ROOT_DIR}/scripts/smoke-check-lima-provider-adapter.sh"
}

cd "${ROOT_DIR}"
validate_adapter_url
ensure_backend_deps
start_backend
run_adapter_smoke

echo "PASS: real LIMA provider install smoke completed"
echo "This smoke used the configured localhost LIMA adapter and host Codex/Claude sign-in state; Sparkbot did not execute Codex or Claude CLIs directly."
if [[ -n "${SPARKBOT_LIMA_INSTALL_SMOKE_REPORT_PATH}" ]]; then
  echo "Sanitized install smoke report: ${SPARKBOT_LIMA_INSTALL_SMOKE_REPORT_PATH}"
fi
