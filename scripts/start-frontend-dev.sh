#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="${ROOT_DIR}/frontend"

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
exec npm run dev -- --host 127.0.0.1
