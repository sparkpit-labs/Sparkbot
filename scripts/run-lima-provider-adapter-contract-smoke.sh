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
        self._send_json(200, {
            "contract_version": 1,
            "request_id": request_id,
            "provider_id": provider_id,
            "status": "succeeded",
            "model": model,
            "response_text": "OK from contract adapter.",
            "usage": None,
            "audit_id": f"contract-audit-{provider_id}",
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

echo "PASS: Sparkbot LIMA provider adapter contract smoke completed"
echo "This contract smoke used a local mock adapter and fake sign-in markers; it did not run Codex or Claude CLIs."
