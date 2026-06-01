#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="${ROOT_DIR}/frontend"
SPARKBOT_BACKEND_PORT="${SPARKBOT_BACKEND_PORT:-8000}"
SPARKBOT_FRONTEND_HOST="${SPARKBOT_FRONTEND_HOST:-127.0.0.1}"
SPARKBOT_FRONTEND_PORT="${SPARKBOT_FRONTEND_PORT:-5173}"
VITE_SPARKBOT_API_BASE_URL="${VITE_SPARKBOT_API_BASE_URL:-http://127.0.0.1:${SPARKBOT_BACKEND_PORT}}"
export VITE_SPARKBOT_API_BASE_URL

case "${SPARKBOT_FRONTEND_HOST}" in
  127.0.0.1|localhost)
    ;;
  *)
    echo "Frontend dev server must bind to 127.0.0.1 or localhost." >&2
    exit 1
    ;;
esac

if [[ ! -x "${FRONTEND_DIR}/node_modules/.bin/vite" ]]; then
  cat <<'MSG'
Frontend development dependencies are not installed.

Run:
  cd frontend
  npm ci
MSG
  exit 1
fi

cd "${FRONTEND_DIR}"
exec "${FRONTEND_DIR}/node_modules/.bin/vite" --host "${SPARKBOT_FRONTEND_HOST}" --port "${SPARKBOT_FRONTEND_PORT}" --strictPort
