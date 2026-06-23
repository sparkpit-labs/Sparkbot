#!/usr/bin/env bash
set -euo pipefail

SPARKBOT_BACKEND_URL="${SPARKBOT_BACKEND_URL:-http://127.0.0.1:8000}"
SPARKBOT_LIMA_SMOKE_PROVIDERS="${SPARKBOT_LIMA_SMOKE_PROVIDERS:-openai-codex-subscription claude-subscription}"
SPARKBOT_LIMA_SMOKE_CODEX_MODEL="${SPARKBOT_LIMA_SMOKE_CODEX_MODEL:-openai-codex/gpt-5.3-codex}"
SPARKBOT_LIMA_SMOKE_CLAUDE_MODEL="${SPARKBOT_LIMA_SMOKE_CLAUDE_MODEL:-claude-sub/sonnet}"
SPARKBOT_LIMA_SMOKE_PROMPT="${SPARKBOT_LIMA_SMOKE_PROMPT:-Say OK.}"

case "${SPARKBOT_BACKEND_URL}" in
  http://127.0.0.1:*|http://localhost:*) ;;
  *)
    echo "SPARKBOT_BACKEND_URL must be an http localhost endpoint." >&2
    exit 1
    ;;
esac

case " ${SPARKBOT_LIMA_SMOKE_PROVIDERS} " in
  *" openai-codex-subscription "*|*" claude-subscription "*) ;;
  *)
    echo "SPARKBOT_LIMA_SMOKE_PROVIDERS must include openai-codex-subscription and/or claude-subscription." >&2
    exit 1
    ;;
esac

backend_base="${SPARKBOT_BACKEND_URL%/}"
status_url="${backend_base}/provider-config/status"
work_dir="$(mktemp -d /tmp/sparkbot-lima-provider-smoke-XXXXXX)"
status_json="${work_dir}/provider-status.json"
response_json="${work_dir}/provider-response.json"
cleanup() {
  rm -rf "${work_dir}"
}
trap cleanup EXIT

provider_model() {
  case "$1" in
    openai-codex-subscription) printf "%s" "${SPARKBOT_LIMA_SMOKE_CODEX_MODEL}" ;;
    claude-subscription) printf "%s" "${SPARKBOT_LIMA_SMOKE_CLAUDE_MODEL}" ;;
    *)
      echo "Unsupported subscription provider $1." >&2
      exit 1
      ;;
  esac
}

json_payload() {
  local model="$1"
  MODEL="${model}" PROMPT="${SPARKBOT_LIMA_SMOKE_PROMPT}" python3 - <<'PYJSON'
import json
import os
print(json.dumps({"prompt": os.environ["PROMPT"], "model": os.environ["MODEL"]}, separators=(",", ":")))
PYJSON
}

echo "Checking Sparkbot provider status at ${status_url}"
curl -fsS "${status_url}" >"${status_json}"

SPARKBOT_PROVIDER_STATUS_JSON="$(cat "${status_json}")" SPARKBOT_LIMA_SMOKE_PROVIDERS="${SPARKBOT_LIMA_SMOKE_PROVIDERS}" python3 - <<'PYJSON'
import json
import os

payload = json.loads(os.environ["SPARKBOT_PROVIDER_STATUS_JSON"])
providers = {provider.get("id"): provider for provider in payload.get("providers", [])}
errors = []
if payload.get("provider_calls") != "guarded-manual":
    errors.append("provider_calls must be guarded-manual; start backend with SPARKBOT_PROVIDER_CALLS_ENABLED=true.")
for provider_id in os.environ["SPARKBOT_LIMA_SMOKE_PROVIDERS"].split():
    provider = providers.get(provider_id)
    if not provider:
        errors.append(f"{provider_id} provider card is missing.")
        continue
    if provider.get("status") != "available":
        errors.append(f"{provider_id} status is {provider.get('status')!r}; expected 'available'.")
    if provider.get("configured") is not True:
        errors.append(f"{provider_id} is not configured; sign-in readiness is missing.")
    if provider.get("adapter_configured") is not True:
        errors.append(f"{provider_id} adapter_configured is not true; set SPARKBOT_LIMA_PROVIDER_ADAPTER_URL before starting backend.")
    if provider.get("runtime_gate") != "lima-guardian-required":
        errors.append(f"{provider_id} does not report the LIMA Guardian runtime gate.")
    if provider.get("prompt_adapter") != "lima-guardian-provider-adapter":
        errors.append(f"{provider_id} does not report the LIMA provider adapter.")
    if provider.get("prompt_endpoint") != f"/provider-config/{provider_id}/prompt":
        errors.append(f"{provider_id} prompt endpoint is missing or unexpected.")

if errors:
    print("LIMA provider adapter smoke preflight failed:", file=__import__("sys").stderr)
    for error in errors:
        print(f"- {error}", file=__import__("sys").stderr)
    raise SystemExit(1)
print("PASS: subscription provider status is ready for guarded LIMA adapter dispatch.")
PYJSON

for provider_id in ${SPARKBOT_LIMA_SMOKE_PROVIDERS}; do
  model="$(provider_model "${provider_id}")"
  prompt_url="${backend_base}/provider-config/${provider_id}/prompt"
  request_body="$(json_payload "${model}")"
  echo "Checking guarded subscription prompt for ${provider_id} at ${prompt_url}"
  http_code="$(curl -sS -o "${response_json}" -w "%{http_code}" -X POST "${prompt_url}" -H "Accept: application/json" -H "Content-Type: application/json" -d "${request_body}")"
  if [[ "${http_code}" != "200" ]]; then
    echo "${provider_id} prompt smoke failed with HTTP ${http_code}." >&2
    RESPONSE_JSON_PATH="${response_json}" python3 - <<'PYJSON'
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
  PROVIDER_ID="${provider_id}" MODEL="${model}" RESPONSE_JSON_PATH="${response_json}" python3 - <<'PYJSON'
import json
import os
import sys
from pathlib import Path

provider_id = os.environ["PROVIDER_ID"]
model = os.environ["MODEL"]
payload = json.loads(Path(os.environ["RESPONSE_JSON_PATH"]).read_text())
errors = []
if payload.get("provider") != provider_id:
    errors.append("provider mismatch")
if payload.get("model") != model:
    errors.append("model mismatch")
if payload.get("request_model") != model:
    errors.append("request_model mismatch")
response = payload.get("response")
if not isinstance(response, str) or not response.strip():
    errors.append("response is empty")
audit_id = payload.get("audit_id")
if not isinstance(audit_id, str) or not audit_id.strip():
    errors.append("audit_id is missing")
serialized = json.dumps(payload, sort_keys=True).lower()
for forbidden in ("api_key", "apikey", "authorization", "bearer ", "password", "secret"):
    if forbidden in serialized:
        errors.append(f"response includes forbidden secret marker {forbidden!r}")
if errors:
    print(f"{provider_id} response contract failed:", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)
print(f"PASS: {provider_id} returned guarded response with audit_id={audit_id}")
PYJSON
  : >"${response_json}"
done

echo "PASS: LIMA Guardian provider adapter smoke completed"
