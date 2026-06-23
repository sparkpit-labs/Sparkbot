#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$(mktemp -d /tmp/sparkbot-public-shell-validate-XXXXXX)"

cleanup() {
  rm -rf "${VENV_DIR}"
}
trap cleanup EXIT

cd "${ROOT_DIR}"

find scripts -name '*.sh' -print0 | sort -z | xargs -0 -n1 bash -n

if bash scripts/run-lima-install-provider-smoke.sh >"${VENV_DIR}/lima-install-smoke-missing-url.out" 2>&1; then
  echo "FAIL: LIMA install provider smoke should require SPARKBOT_LIMA_PROVIDER_ADAPTER_URL." >&2
  exit 1
fi
if ! grep -q "Set SPARKBOT_LIMA_PROVIDER_ADAPTER_URL" "${VENV_DIR}/lima-install-smoke-missing-url.out"; then
  echo "FAIL: LIMA install provider smoke missing-url error changed unexpectedly." >&2
  cat "${VENV_DIR}/lima-install-smoke-missing-url.out" >&2
  exit 1
fi
rm -f "${VENV_DIR}/lima-install-smoke-missing-url.out"

if SPARKBOT_LIMA_PROVIDER_ADAPTER_URL=https://example.com/provider-adapter/dispatch bash scripts/run-lima-install-provider-smoke.sh >"${VENV_DIR}/lima-install-smoke-nonlocal-url.out" 2>&1; then
  echo "FAIL: LIMA install provider smoke should reject non-local adapter URLs." >&2
  exit 1
fi
if ! grep -q "must be an http localhost endpoint" "${VENV_DIR}/lima-install-smoke-nonlocal-url.out"; then
  echo "FAIL: LIMA install provider smoke non-local URL error changed unexpectedly." >&2
  cat "${VENV_DIR}/lima-install-smoke-nonlocal-url.out" >&2
  exit 1
fi
rm -f "${VENV_DIR}/lima-install-smoke-nonlocal-url.out"

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
