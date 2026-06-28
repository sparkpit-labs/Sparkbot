#!/usr/bin/env bash
set -euo pipefail

SPARKBOT_PROVIDER_INSTALL_READINESS_REPORT_PATH="${SPARKBOT_PROVIDER_INSTALL_READINESS_REPORT_PATH:-}"
SPARKBOT_OPENROUTER_SMOKE_MODEL="${SPARKBOT_OPENROUTER_SMOKE_MODEL:-${SPARKBOT_OPENROUTER_MODEL:-meta-llama/llama-3.2-3b-instruct:free}}"
SPARKBOT_PROVIDER_INSTALL_ENV_FILE="${SPARKBOT_PROVIDER_INSTALL_ENV_FILE:-}"
SPARKBOT_OPENROUTER_SMOKE_ENV_FILE="${SPARKBOT_OPENROUTER_SMOKE_ENV_FILE:-${SPARKBOT_PROVIDER_INSTALL_ENV_FILE}}"
SPARKBOT_LIMA_INSTALL_SMOKE_ENV_FILE="${SPARKBOT_LIMA_INSTALL_SMOKE_ENV_FILE:-${SPARKBOT_PROVIDER_INSTALL_ENV_FILE}}"
SPARKBOT_LIMA_PROVIDER_ADAPTER_URL="${SPARKBOT_LIMA_PROVIDER_ADAPTER_URL:-}"

OPENROUTER_KEY_VAR="OPENROUTER""_API_KEY"

write_report() {
  if [[ -n "${SPARKBOT_PROVIDER_INSTALL_READINESS_REPORT_PATH}" ]]; then
    printf "%s\n" "$1" >>"${SPARKBOT_PROVIDER_INSTALL_READINESS_REPORT_PATH}"
  fi
}

emit() {
  printf "%s\n" "$1"
  write_report "$1"
}

has_openrouter_key_in_env_file() {
  if [[ -z "${SPARKBOT_OPENROUTER_SMOKE_ENV_FILE}" ]]; then
    return 1
  fi
  SPARKBOT_OPENROUTER_SMOKE_ENV_FILE="${SPARKBOT_OPENROUTER_SMOKE_ENV_FILE}" python3 - <<'PYENV'
import os
from pathlib import Path

path = Path(os.environ["SPARKBOT_OPENROUTER_SMOKE_ENV_FILE"].strip()).expanduser()
if not path.is_file():
    raise SystemExit(1)

for raw_line in path.read_text(encoding="utf-8").splitlines():
    line = raw_line.strip()
    if not line or line.startswith("#"):
        continue
    if line.startswith("export "):
        line = line[len("export "):].lstrip()
    key, separator, value = line.partition("=")
    if separator and key.strip() == "OPENROUTER_API_KEY" and value.strip():
        raise SystemExit(0)
raise SystemExit(1)
PYENV
}

lima_adapter_url_from_env_file() {
  if [[ -z "${SPARKBOT_LIMA_INSTALL_SMOKE_ENV_FILE}" || -n "${SPARKBOT_LIMA_PROVIDER_ADAPTER_URL}" ]]; then
    return 1
  fi

  SPARKBOT_LIMA_PROVIDER_ADAPTER_URL="$(
    SPARKBOT_LIMA_INSTALL_SMOKE_ENV_FILE="${SPARKBOT_LIMA_INSTALL_SMOKE_ENV_FILE}" python3 - <<'PYENV'
import os
import sys
from pathlib import Path

path = Path(os.environ["SPARKBOT_LIMA_INSTALL_SMOKE_ENV_FILE"].strip()).expanduser()
if not path.is_file():
    raise SystemExit(1)

for raw_line in path.read_text(encoding="utf-8").splitlines():
    line = raw_line.strip()
    if not line or line.startswith("#"):
        continue
    if line.startswith("export "):
        line = line[len("export "):].lstrip()
    key, separator, value = line.partition("=")
    if separator and key.strip() == "SPARKBOT_LIMA_PROVIDER_ADAPTER_URL":
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", chr(34)}:
            value = value[1:-1]
        print(value)
        raise SystemExit(0)
raise SystemExit(1)
PYENV
  )"
  validate_lima_adapter_url
}


codex_auth_ready() {
  CODEX_HOME="${CODEX_HOME:-}" SPARKBOT_CODEX_AUTH_FILE="${SPARKBOT_CODEX_AUTH_FILE:-}" python3 - <<'PYCodex'
import json
import os
from pathlib import Path

def has_token_marker(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in {"access_token", "refresh_token", "id_token"} and isinstance(child, str) and child.strip():
                return True
            if has_token_marker(child):
                return True
    if isinstance(value, list):
        return any(has_token_marker(child) for child in value)
    return False

override = os.environ.get("SPARKBOT_CODEX_AUTH_FILE", "").strip()
if override:
    path = Path(override).expanduser()
else:
    home = os.environ.get("CODEX_HOME", "").strip()
    path = (Path(home).expanduser() if home else Path.home() / ("." + "codex")) / "auth.json"
try:
    payload = json.loads(path.read_text(encoding="utf-8"))
except Exception:
    raise SystemExit(1)
raise SystemExit(0 if has_token_marker(payload) else 1)
PYCodex
}

claude_auth_ready() {
  if [[ "${SPARKBOT_CLAUDE_SUBSCRIPTION_ENABLED:-}" =~ ^(1|true|yes|on)$ ]]; then
    return 0
  fi
  if [[ -n "${SPARKBOT_CLAUDE_AUTH_FILE:-}" && -f "${SPARKBOT_CLAUDE_AUTH_FILE/#\~/${HOME}}" ]]; then
    return 0
  fi
  local claude_home="${CLAUDE_HOME:-${HOME}/.claude}"
  [[ -d "${claude_home/#\~/${HOME}}" ]]
}

validate_lima_adapter_url() {
  SPARKBOT_LIMA_PROVIDER_ADAPTER_URL="${SPARKBOT_LIMA_PROVIDER_ADAPTER_URL}" python3 - <<'PYURL'
import os
from urllib.parse import urlparse

url = os.environ["SPARKBOT_LIMA_PROVIDER_ADAPTER_URL"].strip()
if not url:
    raise SystemExit(1)
parsed = urlparse(url)
if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost"}:
    raise SystemExit(2)
if parsed.username or parsed.password or parsed.query or parsed.fragment:
    raise SystemExit(3)
if not parsed.path or parsed.path == "/":
    raise SystemExit(4)
raise SystemExit(0)
PYURL
}

if [[ -n "${SPARKBOT_PROVIDER_INSTALL_READINESS_REPORT_PATH}" ]]; then
  mkdir -p "$(dirname "${SPARKBOT_PROVIDER_INSTALL_READINESS_REPORT_PATH}")"
  : >"${SPARKBOT_PROVIDER_INSTALL_READINESS_REPORT_PATH}"
fi

emit "Sparkbot provider install readiness"

if [[ "${SPARKBOT_OPENROUTER_SMOKE_MODEL}" == *:free ]]; then
  emit "PASS openrouter_model_free model=${SPARKBOT_OPENROUTER_SMOKE_MODEL}"
else
  emit "TODO openrouter_model_free set SPARKBOT_OPENROUTER_SMOKE_MODEL to an OpenRouter :free model"
fi

if [[ -n "${!OPENROUTER_KEY_VAR-}" ]]; then
  emit "PASS openrouter_key_source source=environment"
elif has_openrouter_key_in_env_file; then
  emit "PASS openrouter_key_source source=env-file"
else
  emit "TODO openrouter_key_source provide OPENROUTER_API_KEY, SPARKBOT_OPENROUTER_SMOKE_ENV_FILE, or SPARKBOT_PROVIDER_INSTALL_ENV_FILE"
fi

lima_adapter_url_status=0
validate_lima_adapter_url || lima_adapter_url_status=$?
if [[ "${lima_adapter_url_status}" -eq 0 ]]; then
  emit "PASS lima_adapter_url localhost-dispatch-path"
else
  if [[ "${lima_adapter_url_status}" -eq 1 && -z "${SPARKBOT_LIMA_PROVIDER_ADAPTER_URL}" && -n "${SPARKBOT_LIMA_INSTALL_SMOKE_ENV_FILE}" ]]; then
    if lima_adapter_url_from_env_file; then
      emit "PASS lima_adapter_url source=env-file"
      lima_adapter_url_status=0
    else
      lima_adapter_url_status=$?
    fi
  fi
  if [[ "${lima_adapter_url_status}" -ne 0 ]]; then
    case "${lima_adapter_url_status}" in
      1) emit "TODO lima_adapter_url set SPARKBOT_LIMA_PROVIDER_ADAPTER_URL" ;;
      2) emit "TODO lima_adapter_url must be http localhost or 127.0.0.1" ;;
      3) emit "TODO lima_adapter_url remove credentials query parameters and fragments" ;;
      4) emit "TODO lima_adapter_url include an explicit dispatch path" ;;
      *) emit "TODO lima_adapter_url invalid adapter URL" ;;
    esac
  fi
fi

if command -v codex >/dev/null 2>&1 || [[ -n "${SPARKBOT_CODEX_CLI:-}" ]]; then
  emit "PASS codex_cli available"
else
  emit "TODO codex_cli install Codex CLI or set SPARKBOT_CODEX_CLI"
fi

if codex_auth_ready; then
  emit "PASS codex_sign_in token-marker-detected"
else
  emit "TODO codex_sign_in run codex login with ChatGPT sign-in"
fi

if command -v claude >/dev/null 2>&1 || [[ -n "${SPARKBOT_CLAUDE_CLI:-}" ]]; then
  emit "PASS claude_cli available"
else
  emit "TODO claude_cli install Claude Code or set SPARKBOT_CLAUDE_CLI"
fi

if claude_auth_ready; then
  emit "PASS claude_sign_in detected"
else
  emit "TODO claude_sign_in run Claude Code sign-in or set approved readiness flag"
fi

emit "NEXT openrouter_smoke SPARKBOT_OPENROUTER_SMOKE_PROMPT_FOR_KEY=true SPARKBOT_OPENROUTER_SMOKE_MODEL=${SPARKBOT_OPENROUTER_SMOKE_MODEL} bash scripts/run-openrouter-free-smoke.sh"
emit "NEXT lima_smoke SPARKBOT_LIMA_PROVIDER_ADAPTER_URL=http://127.0.0.1:<port>/<path> bash scripts/run-lima-install-provider-smoke.sh"
