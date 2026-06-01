#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="${ROOT_DIR}/backend"
PYTHON_BIN="${PYTHON_BIN:-python3}"
SPARKBOT_BACKEND_HOST="${SPARKBOT_BACKEND_HOST:-127.0.0.1}"
SPARKBOT_BACKEND_PORT="${SPARKBOT_BACKEND_PORT:-8000}"

case "${SPARKBOT_BACKEND_HOST}" in
  127.0.0.1|localhost)
    ;;
  *)
    echo "Backend dev server must bind to 127.0.0.1 or localhost." >&2
    exit 1
    ;;
esac

if [[ -x "${ROOT_DIR}/.venv-local/bin/python" ]]; then
  PYTHON_BIN="${ROOT_DIR}/.venv-local/bin/python"
fi

if ! "${PYTHON_BIN}" -c "import uvicorn" >/dev/null 2>&1; then
  cat <<'MSG'
Backend development dependencies are not installed.

Run:
  python3 -m venv .venv-local
  . .venv-local/bin/activate
  python -m pip install --upgrade pip
  python -m pip install -e "backend[dev]"
MSG
  exit 1
fi

cd "${BACKEND_DIR}"
exec "${PYTHON_BIN}" -m uvicorn app.main:app --reload --host "${SPARKBOT_BACKEND_HOST}" --port "${SPARKBOT_BACKEND_PORT}"
