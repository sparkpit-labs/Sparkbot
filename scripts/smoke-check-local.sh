#!/usr/bin/env bash
set -euo pipefail

SPARKBOT_BACKEND_URL="${SPARKBOT_BACKEND_URL:-http://127.0.0.1:8000}"
SPARKBOT_FRONTEND_URL="${SPARKBOT_FRONTEND_URL:-http://127.0.0.1:5173}"

backend_health_url="${SPARKBOT_BACKEND_URL%/}/health"
capabilities_url="${SPARKBOT_BACKEND_URL%/}/capabilities"
provider_config_status_url="${SPARKBOT_BACKEND_URL%/}/provider-config/status"
connector_status_url="${SPARKBOT_BACKEND_URL%/}/connector-status"
guardian_status_url="${SPARKBOT_BACKEND_URL%/}/guardian/status"

echo "Checking backend health at ${backend_health_url}"
backend_response="$(curl -fsS "${backend_health_url}")"
printf "%s\n" "${backend_response}"

case "${backend_response}" in
  *\"status\":\"ok\"*|*\"status\":\ \"ok\"*)
    ;;
  *)
    echo "Backend health response did not report status ok." >&2
    exit 1
    ;;
esac

echo "Checking capabilities at ${capabilities_url}"
capabilities_response="$(curl -fsS "${capabilities_url}")"
printf "%s\n" "${capabilities_response}"

case "${capabilities_response}" in
  *\"service\":\"sparkbot-server\"*|*\"service\":\ \"sparkbot-server\"*)
    ;;
  *)
    echo "Capabilities response did not report sparkbot-server." >&2
    exit 1
    ;;
esac

case "${capabilities_response}" in
  *\"capabilities\"*)
    ;;
  *)
    echo "Capabilities response did not include capabilities." >&2
    exit 1
    ;;
esac

echo "Checking provider config status at ${provider_config_status_url}"
provider_config_status_response="$(curl -fsS "${provider_config_status_url}")"
printf "%s\n" "${provider_config_status_response}"

case "${provider_config_status_response}" in
  *\"credential_storage\":\"not-implemented\"*|*\"credential_storage\":\ \"not-implemented\"*)
    ;;
  *)
    echo "Provider config status response did not report credential storage as not implemented." >&2
    exit 1
    ;;
esac

case "${provider_config_status_response}" in
  *\"provider_calls\":\"not-implemented\"*|*\"provider_calls\":\ \"not-implemented\"*)
    ;;
  *)
    echo "Provider config status response did not report provider calls as not implemented." >&2
    exit 1
    ;;
esac

echo "Checking connector status at ${connector_status_url}"
connector_status_response="$(curl -fsS "${connector_status_url}")"
printf "%s\n" "${connector_status_response}"

case "${connector_status_response}" in
  *\"connectors_enabled\":false*)
    ;;
  *)
    echo "Connector status response did not report connectors as disabled." >&2
    exit 1
    ;;
esac

case "${connector_status_response}" in
  *\"outbound_actions\":\"not-implemented\"*|*\"outbound_actions\":\ \"not-implemented\"*)
    ;;
  *)
    echo "Connector status response did not report outbound actions as not implemented." >&2
    exit 1
    ;;
esac

echo "Checking Guardian status at ${guardian_status_url}"
guardian_status_response="$(curl -fsS "${guardian_status_url}")"
printf "%s\n" "${guardian_status_response}"

case "${guardian_status_response}" in
  *\"runtime_enforcement\":\"not-implemented\"*|*\"runtime_enforcement\":\ \"not-implemented\"*)
    ;;
  *)
    echo "Guardian status response did not report runtime enforcement as not implemented." >&2
    exit 1
    ;;
esac

case "${guardian_status_response}" in
  *\"policy_decisions\":\"not-implemented\"*|*\"policy_decisions\":\ \"not-implemented\"*)
    ;;
  *)
    echo "Guardian status response did not report policy decisions as not implemented." >&2
    exit 1
    ;;
esac

echo "Checking frontend HTTP response at ${SPARKBOT_FRONTEND_URL}"
curl -fsS "${SPARKBOT_FRONTEND_URL}" >/dev/null

echo "PASS: local Sparkbot shell smoke check completed"
