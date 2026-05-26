#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="${ROOT_DIR}/backend"

cd "${ROOT_DIR}"
python3 -m compileall backend

cd "${BACKEND_DIR}"
pytest tests -q

