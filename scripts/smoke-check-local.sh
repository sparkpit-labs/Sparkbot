#!/usr/bin/env bash
set -euo pipefail

SPARKBOT_BACKEND_URL="${SPARKBOT_BACKEND_URL:-http://127.0.0.1:8000}"
SPARKBOT_FRONTEND_URL="${SPARKBOT_FRONTEND_URL:-http://127.0.0.1:5173}"

backend_health_url="${SPARKBOT_BACKEND_URL%/}/health"

echo "Checking backend health at ${backend_health_url}"
backend_response="$(curl -fsS "${backend_health_url}")"
printf '%s\n' "${backend_response}"

case "${backend_response}" in
  *'"status":"ok"'*|*'"status": "ok"'*)
    ;;
  *)
    echo "Backend health response did not report status ok." >&2
    exit 1
    ;;
esac

echo "Checking frontend HTTP response at ${SPARKBOT_FRONTEND_URL}"
curl -fsSI "${SPARKBOT_FRONTEND_URL}" >/dev/null

echo "PASS: local Sparkbot shell smoke check completed"
