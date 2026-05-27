#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$(mktemp -d /tmp/sparkbot-public-shell-validate-XXXXXX)"

cleanup() {
  rm -rf "${VENV_DIR}"
}
trap cleanup EXIT

cd "${ROOT_DIR}"

python3 -m compileall backend

python3 -m venv "${VENV_DIR}"
# shellcheck disable=SC1091
. "${VENV_DIR}/bin/activate"
python -m pip install --upgrade pip
python -m pip install -e "backend[dev]"
pytest backend/tests -q

deactivate

cd "${ROOT_DIR}/frontend"
npm ci
npm audit --audit-level=moderate
npm test -- --run
npm run build
