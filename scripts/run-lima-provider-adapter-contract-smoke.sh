#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SPARKBOT_CONTRACT_SMOKE_BACKEND_HOST="${SPARKBOT_CONTRACT_SMOKE_BACKEND_HOST:-127.0.0.1}"
SPARKBOT_CONTRACT_SMOKE_BACKEND_PORT="${SPARKBOT_CONTRACT_SMOKE_BACKEND_PORT:-18180}"
SPARKBOT_CONTRACT_SMOKE_ADAPTER_PORT="${SPARKBOT_CONTRACT_SMOKE_ADAPTER_PORT:-18199}"
SPARKBOT_CONTRACT_SMOKE_CODEX_MODEL="${SPARKBOT_CONTRACT_SMOKE_CODEX_MODEL:-openai-codex/gpt-5.3-codex}"
SPARKBOT_CONTRACT_SMOKE_CLAUDE_MODEL="${SPARKBOT_CONTRACT_SMOKE_CLAUDE_MODEL:-claude-sub/sonnet}"

case "${SPARKBOT_CONTRACT_SMOKE_BACKEND_HOST}" in
  127.0.0.1|localhost) ;;
  *)
    echo "Contract smoke backend host must be 127.0.0.1 or localhost." >&2
    exit 1
    ;;
esac

WORK_DIR="$(mktemp -d /tmp/sparkbot-lima-contract-smoke-XXXXXX)"
BACKEND_LOG="${WORK_DIR}/backend.log"
ADAPTER_LOG="${WORK_DIR}/adapter.log"
BACKEND_PID=""
ADAPTER_PID=""
backend_url="http://${SPARKBOT_CONTRACT_SMOKE_BACKEND_HOST}:${SPARKBOT_CONTRACT_SMOKE_BACKEND_PORT}"
adapter_url="http://127.0.0.1:${SPARKBOT_CONTRACT_SMOKE_ADAPTER_PORT}/provider-adapter/dispatch"

stop_process() {
  local pid="$1"
  if [[ -n "${pid}" ]] && kill -0 "${pid}" >/dev/null 2>&1; then
    kill "${pid}" >/dev/null 2>&1 || true
    wait "${pid}" >/dev/null 2>&1 || true
  fi
}

cleanup() {
  stop_process "${BACKEND_PID}"
  stop_process "${ADAPTER_PID}"
  rm -rf "${WORK_DIR}"
}
trap cleanup EXIT

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

ensure_backend_deps() {
  if [[ -x "${ROOT_DIR}/.venv-local/bin/python" ]] && "${ROOT_DIR}/.venv-local/bin/python" -c "import uvicorn" >/dev/null 2>&1; then
    return 0
  fi

  echo "Backend development dependencies are missing. Run scripts/run-local-smoke-test.sh once to prepare .venv-local." >&2
  exit 1
}

write_contract_adapter() {
  cat >"${WORK_DIR}/contract_adapter.py" <<'PYADAPTER'
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ALLOWED_PROVIDERS = {"openai-codex-subscription", "claude-subscription"}

class Handler(BaseHTTPRequestHandler):
    server_version = "SparkbotLimaContractAdapter/1"

    def log_message(self, format, *args):
        return

    def _send_json(self, status, payload):
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._send_json(200, {"status": "ok", "service": "sparkbot-lima-contract-adapter"})
            return
        self._send_json(404, {"detail": "not found"})

    def do_POST(self):
        length = int(self.headers.get("content-length", "0"))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._send_json(400, {"detail": "invalid json"})
            return
        provider_id = payload.get("provider_id")
        request_id = payload.get("request_id")
        model = payload.get("model")
        errors = []
        if payload.get("contract_version") != 1:
            errors.append("contract_version")
        if provider_id not in ALLOWED_PROVIDERS:
            errors.append("provider_id")
        if not isinstance(request_id, str) or not request_id:
            errors.append("request_id")
        if not isinstance(model, str) or not model:
            errors.append("model")
        if not isinstance(payload.get("prompt"), str) or not payload.get("prompt").strip():
            errors.append("prompt")
        if not isinstance(payload.get("operator_approval"), dict):
            errors.append("operator_approval")
        audit = payload.get("audit")
        if not isinstance(audit, dict) or audit.get("store_prompt") is not False or audit.get("store_response") is not False:
            errors.append("audit")
        if errors:
            self._send_json(422, {"detail": "contract validation failed", "fields": errors})
            return
        adapter_status = "succeeded"
        prompt = payload.get("prompt")
        status_prefix = "__sparkbot_contract_status:"
        if isinstance(prompt, str) and prompt.startswith(status_prefix) and prompt.endswith("__"):
            requested_status = prompt[len(status_prefix):-2]
            if requested_status in {"denied", "blocked", "timeout", "failed"}:
                adapter_status = requested_status
        self._send_json(200, {
            "contract_version": 1,
            "request_id": request_id,
            "provider_id": provider_id,
            "status": adapter_status,
            "model": model,
            "response_text": "OK from contract adapter." if adapter_status == "succeeded" else "",
            "usage": None,
            "audit_id": f"contract-audit-{provider_id}-{adapter_status}",
            "redactions_applied": True,
            "runtime": {
                "adapter": "sparkbot-contract-test-adapter",
                "dispatch": "contract-test-only",
                "timeout_seconds": 120,
            },
        })

if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", int(__import__("os").environ["SPARKBOT_CONTRACT_SMOKE_ADAPTER_PORT"])), Handler).serve_forever()
PYADAPTER
}

prepare_fake_subscription_state() {
  mkdir -p "${WORK_DIR}/bin" "${WORK_DIR}/codex-home" "${WORK_DIR}/claude-home"
  printf '#!/usr/bin/env sh\nexit 0\n' >"${WORK_DIR}/bin/codex"
  printf '#!/usr/bin/env sh\nexit 0\n' >"${WORK_DIR}/bin/claude"
  chmod +x "${WORK_DIR}/bin/codex" "${WORK_DIR}/bin/claude"
  printf '{}\n' >"${WORK_DIR}/codex-auth.json"
  printf '{}\n' >"${WORK_DIR}/claude-auth.json"
}

start_contract_adapter() {
  write_contract_adapter
  echo "Starting mock LIMA provider contract adapter at ${adapter_url}"
  env SPARKBOT_CONTRACT_SMOKE_ADAPTER_PORT="${SPARKBOT_CONTRACT_SMOKE_ADAPTER_PORT}" \
    "${ROOT_DIR}/.venv-local/bin/python" "${WORK_DIR}/contract_adapter.py" >"${ADAPTER_LOG}" 2>&1 &
  ADAPTER_PID="$!"
  wait_for_url "contract adapter" "http://127.0.0.1:${SPARKBOT_CONTRACT_SMOKE_ADAPTER_PORT}/health" "${ADAPTER_LOG}"
}

json_request_body() {
  local prompt="$1"
  local model="$2"
  PROMPT="${prompt}" MODEL="${model}" python3 - <<'PYJSON'
import json
import os
print(json.dumps({"prompt": os.environ["PROMPT"], "model": os.environ["MODEL"]}, separators=(",", ":")))
PYJSON
}

check_fail_closed_adapter_statuses() {
  local provider_id="openai-codex-subscription"
  local model="${SPARKBOT_CONTRACT_SMOKE_CODEX_MODEL}"
  local adapter_status
  local response_json
  local request_body
  local http_code

  for adapter_status in denied blocked timeout failed; do
    response_json="${WORK_DIR}/fail-closed-${adapter_status}.json"
    request_body="$(json_request_body "__sparkbot_contract_status:${adapter_status}__" "${model}")"
    echo "Checking fail-closed adapter status ${adapter_status} through ${provider_id}"
    http_code="$(curl -sS -o "${response_json}" -w "%{http_code}" -X POST "${backend_url}/provider-config/${provider_id}/prompt" -H "Accept: application/json" -H "Content-Type: application/json" -d "${request_body}")"
    if [[ "${http_code}" != "503" ]]; then
      echo "Expected ${provider_id} ${adapter_status} smoke to return HTTP 503; got ${http_code}." >&2
      RESPONSE_JSON_PATH="${response_json}" python3 - <<'PYJSON' >&2
import json
import os
from pathlib import Path
try:
    print(json.dumps(json.loads(Path(os.environ["RESPONSE_JSON_PATH"]).read_text()), sort_keys=True))
except Exception:
    print("Response body was not JSON.")
PYJSON
      exit 1
    fi
    ADAPTER_STATUS="${adapter_status}" RESPONSE_JSON_PATH="${response_json}" python3 - <<'PYJSON'
import json
import os
import sys
from pathlib import Path
status = os.environ["ADAPTER_STATUS"]
payload = json.loads(Path(os.environ["RESPONSE_JSON_PATH"]).read_text())
expected_detail = f"LIMA Guardian provider adapter returned status {status}."
errors = []
if payload.get("detail") != expected_detail:
    errors.append(f"expected safe detail {expected_detail!r}, got {payload.get('detail')!r}")
serialized = json.dumps(payload, sort_keys=True).lower()
for forbidden in ("api_key", "apikey", "authorization", "bearer ", "password", "secret", "contract-audit"):
    if forbidden in serialized:
        errors.append(f"response includes forbidden marker {forbidden!r}")
if errors:
    print(f"Fail-closed {status} response contract failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)
print(f"PASS: adapter status {status} failed closed with a safe Sparkbot response")
PYJSON
  done
}

start_backend() {
  : >"${BACKEND_LOG}"
  echo "Starting Sparkbot backend contract smoke server at ${backend_url}"
  env \
    SPARKBOT_DATA_DIR="${WORK_DIR}/data" \
    SPARKBOT_PROVIDER_CALLS_ENABLED=true \
    SPARKBOT_LIMA_PROVIDER_ADAPTER_URL="${adapter_url}" \
    SPARKBOT_CODEX_CLI="${WORK_DIR}/bin/codex" \
    SPARKBOT_CODEX_AUTH_FILE="${WORK_DIR}/codex-auth.json" \
    SPARKBOT_CODEX_MODEL="${SPARKBOT_CONTRACT_SMOKE_CODEX_MODEL}" \
    SPARKBOT_CLAUDE_CLI="${WORK_DIR}/bin/claude" \
    SPARKBOT_CLAUDE_AUTH_FILE="${WORK_DIR}/claude-auth.json" \
    SPARKBOT_CLAUDE_SUB_MODEL="${SPARKBOT_CONTRACT_SMOKE_CLAUDE_MODEL}" \
    CODEX_HOME="${WORK_DIR}/codex-home" \
    CLAUDE_HOME="${WORK_DIR}/claude-home" \
    SPARKBOT_BACKEND_HOST="${SPARKBOT_CONTRACT_SMOKE_BACKEND_HOST}" \
    SPARKBOT_BACKEND_PORT="${SPARKBOT_CONTRACT_SMOKE_BACKEND_PORT}" \
    bash "${ROOT_DIR}/scripts/start-backend-dev.sh" >"${BACKEND_LOG}" 2>&1 &
  BACKEND_PID="$!"
  wait_for_url "backend" "${backend_url}/health" "${BACKEND_LOG}"
}

cd "${ROOT_DIR}"
ensure_backend_deps
prepare_fake_subscription_state
start_contract_adapter
start_backend
SPARKBOT_BACKEND_URL="${backend_url}" \
SPARKBOT_LIMA_SMOKE_CODEX_MODEL="${SPARKBOT_CONTRACT_SMOKE_CODEX_MODEL}" \
SPARKBOT_LIMA_SMOKE_CLAUDE_MODEL="${SPARKBOT_CONTRACT_SMOKE_CLAUDE_MODEL}" \
bash "${ROOT_DIR}/scripts/smoke-check-lima-provider-adapter.sh"
check_fail_closed_adapter_statuses

echo "PASS: Sparkbot LIMA provider adapter contract smoke completed"
echo "This contract smoke used a local mock adapter and fake sign-in markers; it did not run Codex or Claude CLIs."
