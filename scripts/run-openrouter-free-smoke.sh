#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SPARKBOT_OPENROUTER_SMOKE_BACKEND_HOST="${SPARKBOT_OPENROUTER_SMOKE_BACKEND_HOST:-127.0.0.1}"
SPARKBOT_OPENROUTER_SMOKE_BACKEND_PORT="${SPARKBOT_OPENROUTER_SMOKE_BACKEND_PORT:-18380}"
SPARKBOT_OPENROUTER_SMOKE_DATA_DIR="${SPARKBOT_OPENROUTER_SMOKE_DATA_DIR:-}"
SPARKBOT_OPENROUTER_SMOKE_MODEL="${SPARKBOT_OPENROUTER_SMOKE_MODEL:-${SPARKBOT_OPENROUTER_MODEL:-meta-llama/llama-3.2-3b-instruct:free}}"
SPARKBOT_OPENROUTER_SMOKE_PROMPT="${SPARKBOT_OPENROUTER_SMOKE_PROMPT:-Say OK.}"
SPARKBOT_OPENROUTER_SMOKE_REPORT_PATH="${SPARKBOT_OPENROUTER_SMOKE_REPORT_PATH:-}"
SPARKBOT_OPENROUTER_SMOKE_PROMPT_FOR_KEY="${SPARKBOT_OPENROUTER_SMOKE_PROMPT_FOR_KEY:-false}"
OPENROUTER_KEY_VAR="OPENROUTER""_API_KEY"
OPENROUTER_KEY_VALUE="${!OPENROUTER_KEY_VAR-}"

case "${SPARKBOT_OPENROUTER_SMOKE_BACKEND_HOST}" in
  127.0.0.1|localhost) ;;
  *)
    echo "OpenRouter smoke backend host must be 127.0.0.1 or localhost." >&2
    exit 1
    ;;
esac

case "${SPARKBOT_OPENROUTER_SMOKE_PROMPT_FOR_KEY}" in
  true|false) ;;
  *)
    echo "SPARKBOT_OPENROUTER_SMOKE_PROMPT_FOR_KEY must be true or false." >&2
    exit 1
    ;;
esac

if [[ -z "${OPENROUTER_KEY_VALUE}" && "${SPARKBOT_OPENROUTER_SMOKE_PROMPT_FOR_KEY}" == "true" ]]; then
  if [[ ! -t 0 ]]; then
    echo "OPENROUTER_API_KEY is not set and SPARKBOT_OPENROUTER_SMOKE_PROMPT_FOR_KEY=true requires an interactive terminal." >&2
    exit 1
  fi
  read -rsp "OpenRouter key: " OPENROUTER_KEY_VALUE
  printf "\n"
fi

if [[ -z "${OPENROUTER_KEY_VALUE}" ]]; then
  echo "Set OPENROUTER_API_KEY before running the real OpenRouter free-model smoke." >&2
  exit 1
fi

case "${SPARKBOT_OPENROUTER_SMOKE_MODEL}" in
  *:free) ;;
  *)
    echo "SPARKBOT_OPENROUTER_SMOKE_MODEL must end in :free unless a separate paid-model smoke is explicitly approved." >&2
    exit 1
    ;;
esac

WORK_DIR="$(mktemp -d /tmp/sparkbot-openrouter-free-smoke-XXXXXX)"
DATA_DIR="${SPARKBOT_OPENROUTER_SMOKE_DATA_DIR:-${WORK_DIR}/data}"
BACKEND_LOG="${WORK_DIR}/backend.log"
RESPONSE_JSON="${WORK_DIR}/openrouter-response.json"
BACKEND_PID=""
backend_url="http://${SPARKBOT_OPENROUTER_SMOKE_BACKEND_HOST}:${SPARKBOT_OPENROUTER_SMOKE_BACKEND_PORT}"

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

write_report() {
  if [[ -n "${SPARKBOT_OPENROUTER_SMOKE_REPORT_PATH}" ]]; then
    printf "%s\n" "$1" >>"${SPARKBOT_OPENROUTER_SMOKE_REPORT_PATH}"
  fi
}

json_payload() {
  MODEL="${SPARKBOT_OPENROUTER_SMOKE_MODEL}" PROMPT="${SPARKBOT_OPENROUTER_SMOKE_PROMPT}" python3 - <<'PYJSON'
import json
import os
print(json.dumps({"prompt": os.environ["PROMPT"], "model": os.environ["MODEL"]}, separators=(",", ":")))
PYJSON
}

start_backend() {
  mkdir -p "${DATA_DIR}"
  : >"${BACKEND_LOG}"
  echo "Starting Sparkbot backend for real OpenRouter free-model smoke at ${backend_url}"
  env \
    SPARKBOT_DATA_DIR="${DATA_DIR}" \
    SPARKBOT_PROVIDER_CALLS_ENABLED=true \
    "${OPENROUTER_KEY_VAR}=${OPENROUTER_KEY_VALUE}" \
    SPARKBOT_OPENROUTER_MODEL="${SPARKBOT_OPENROUTER_SMOKE_MODEL}" \
    SPARKBOT_BACKEND_HOST="${SPARKBOT_OPENROUTER_SMOKE_BACKEND_HOST}" \
    SPARKBOT_BACKEND_PORT="${SPARKBOT_OPENROUTER_SMOKE_BACKEND_PORT}" \
    bash "${ROOT_DIR}/scripts/start-backend-dev.sh" >"${BACKEND_LOG}" 2>&1 &
  BACKEND_PID="$!"
  wait_for_url "backend" "${backend_url}/health" "${BACKEND_LOG}"
}

check_openrouter_status() {
  local status_json
  status_json="$(curl -fsS "${backend_url}/provider-config/status")"
  SPARKBOT_PROVIDER_STATUS_JSON="${status_json}" SPARKBOT_OPENROUTER_SMOKE_MODEL="${SPARKBOT_OPENROUTER_SMOKE_MODEL}" python3 - <<'PYJSON'
import json
import os
import sys

payload = json.loads(os.environ["SPARKBOT_PROVIDER_STATUS_JSON"])
providers = {provider.get("id"): provider for provider in payload.get("providers", [])}
openrouter = providers.get("openrouter")
errors = []
if payload.get("provider_calls") != "guarded-manual":
    errors.append("provider_calls must be guarded-manual.")
if not openrouter:
    errors.append("OpenRouter provider card is missing.")
else:
    if openrouter.get("status") != "available":
        errors.append(f"OpenRouter status is {openrouter.get('status')!r}; expected available.")
    if openrouter.get("configured") is not True:
        errors.append("OpenRouter is not configured.")
    if openrouter.get("default_model") != os.environ["SPARKBOT_OPENROUTER_SMOKE_MODEL"]:
        errors.append("OpenRouter default model does not match the smoke model.")
if errors:
    print("OpenRouter free-model smoke preflight failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)
print("PASS: OpenRouter provider status is ready for explicit free-model smoke.")
PYJSON
}

run_openrouter_smoke() {
  local request_body
  local http_code
  request_body="$(json_payload)"
  echo "Checking guarded OpenRouter free-model prompt at ${backend_url}/provider-config/openrouter/prompt"
  http_code="$(curl -sS -o "${RESPONSE_JSON}" -w "%{http_code}" -X POST "${backend_url}/provider-config/openrouter/prompt" -H "Accept: application/json" -H "Content-Type: application/json" -d "${request_body}")"
  if [[ "${http_code}" != "200" ]]; then
    echo "OpenRouter free-model prompt smoke failed with HTTP ${http_code}." >&2
    RESPONSE_JSON_PATH="${RESPONSE_JSON}" python3 - <<'PYJSON'
import json
import os
import sys
from pathlib import Path
try:
    payload = json.loads(Path(os.environ["RESPONSE_JSON_PATH"]).read_text())
except Exception:
    print("Response body was not JSON.", file=sys.stderr)
    raise SystemExit(0)
detail = payload.get("detail") if isinstance(payload, dict) else None
if isinstance(detail, str):
    print(f"Detail: {detail}", file=sys.stderr)
else:
    print("Response did not include a safe detail string.", file=sys.stderr)
PYJSON
    exit 1
  fi

  MODEL="${SPARKBOT_OPENROUTER_SMOKE_MODEL}" RESPONSE_JSON_PATH="${RESPONSE_JSON}" python3 - <<'PYJSON'
import json
import os
import sys
from pathlib import Path

model = os.environ["MODEL"]
payload = json.loads(Path(os.environ["RESPONSE_JSON_PATH"]).read_text())
errors = []
if payload.get("provider") != "openrouter":
    errors.append("provider mismatch")
if payload.get("model") != model:
    errors.append("model mismatch")
expected_request_model = model.removeprefix("openrouter/")
if payload.get("request_model") != expected_request_model:
    errors.append("request_model mismatch")
response = payload.get("response")
if not isinstance(response, str) or not response.strip():
    errors.append("response is empty")
serialized = json.dumps(payload, sort_keys=True).lower()
for forbidden in ("api_key", "apikey", "authorization", "bearer ", "password", "secret"):
    if forbidden in serialized:
        errors.append(f"response includes forbidden secret marker {forbidden!r}")
if errors:
    print("OpenRouter free-model response contract failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)
PYJSON
}

cd "${ROOT_DIR}"
ensure_backend_deps
if [[ -n "${SPARKBOT_OPENROUTER_SMOKE_REPORT_PATH}" ]]; then
  mkdir -p "$(dirname "${SPARKBOT_OPENROUTER_SMOKE_REPORT_PATH}")"
  : >"${SPARKBOT_OPENROUTER_SMOKE_REPORT_PATH}"
  write_report "Sparkbot OpenRouter free-model smoke"
  write_report "backend_url=${backend_url}"
  write_report "model=${SPARKBOT_OPENROUTER_SMOKE_MODEL}"
fi
start_backend
check_openrouter_status
write_report "PASS preflight openrouter available"
run_openrouter_smoke
write_report "PASS provider=openrouter model=${SPARKBOT_OPENROUTER_SMOKE_MODEL}"

echo "PASS: real OpenRouter free-model smoke completed"
echo "This smoke used a configured backend OPENROUTER_API_KEY, enforced a :free model, and did not print the model response text."
if [[ -n "${SPARKBOT_OPENROUTER_SMOKE_REPORT_PATH}" ]]; then
  echo "Sanitized OpenRouter smoke report: ${SPARKBOT_OPENROUTER_SMOKE_REPORT_PATH}"
fi
