#!/usr/bin/env bash
set -euo pipefail

SPARKBOT_BACKEND_URL="${SPARKBOT_BACKEND_URL:-http://127.0.0.1:8000}"
SPARKBOT_FRONTEND_URL="${SPARKBOT_FRONTEND_URL:-http://127.0.0.1:5173}"

backend_health_url="${SPARKBOT_BACKEND_URL%/}/health"
capabilities_url="${SPARKBOT_BACKEND_URL%/}/capabilities"
chat_status_url="${SPARKBOT_BACKEND_URL%/}/chat/status"
provider_config_status_url="${SPARKBOT_BACKEND_URL%/}/provider-config/status"
openrouter_prompt_url="${SPARKBOT_BACKEND_URL%/}/provider-config/openrouter/prompt"
connector_status_url="${SPARKBOT_BACKEND_URL%/}/connector-status"
guardian_status_url="${SPARKBOT_BACKEND_URL%/}/guardian/status"
round_table_status_url="${SPARKBOT_BACKEND_URL%/}/round-table/status"
model_seats_status_url="${SPARKBOT_BACKEND_URL%/}/model-seats/status"
task_lanes_status_url="${SPARKBOT_BACKEND_URL%/}/work-lanes/status"
local_chat_sessions_url="${SPARKBOT_BACKEND_URL%/}/local/chat/sessions"
local_memory_notes_url="${SPARKBOT_BACKEND_URL%/}/local/memory-notes"
local_work_lane_cards_url="${SPARKBOT_BACKEND_URL%/}/local/work-lane-cards"
local_data_export_url="${SPARKBOT_BACKEND_URL%/}/local/export"
local_runtime_settings_url="${SPARKBOT_BACKEND_URL%/}/local/runtime/settings"
local_models_status_url="${SPARKBOT_BACKEND_URL%/}/local-models/status"
local_models_prompt_url="${SPARKBOT_BACKEND_URL%/}/local-models/ollama/prompt"

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

echo "Checking Chat status at ${chat_status_url}"
chat_status_response="$(curl -fsS "${chat_status_url}")"
printf "%s\n" "${chat_status_response}"

case "${chat_status_response}" in
  *\"chat_runtime\":\"not-implemented\"*|*\"chat_runtime\":\ \"not-implemented\"*)
    ;;
  *)
    echo "Chat status response did not report chat runtime as not implemented." >&2
    exit 1
    ;;
esac

case "${chat_status_response}" in
  *\"message_persistence\":\"not-implemented\"*|*\"message_persistence\":\ \"not-implemented\"*)
    ;;
  *)
    echo "Chat status response did not report message persistence as not implemented." >&2
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
  *\"provider_calls\":\"disabled-by-default\"*|*\"provider_calls\":\ \"disabled-by-default\"*)
    provider_calls_mode="disabled-by-default"
    ;;
  *\"provider_calls\":\"guarded-manual\"*|*\"provider_calls\":\ \"guarded-manual\"*)
    provider_calls_mode="guarded-manual"
    ;;
  *)
    echo "Provider config status response did not report provider calls as disabled-by-default or guarded-manual." >&2
    exit 1
    ;;
esac

for provider_id in local-ollama openrouter openai anthropic google groq minimax xai openai-codex-subscription claude-subscription; do
  case "${provider_config_status_response}" in
    *\"id\":\"${provider_id}\"*|*\"id\":\ \"${provider_id}\"*) ;;
    *)
      echo "Provider config status response did not include provider ${provider_id}." >&2
      exit 1
      ;;
  esac
done

case "${provider_config_status_response}" in
  *:free*) ;;
  *)
    echo "Provider config status response did not include a free OpenRouter model." >&2
    exit 1
    ;;
esac

case "${provider_config_status_response}" in
  *\"runtime_gate\":\"lima-guardian-required\"*|*\"runtime_gate\":\ \"lima-guardian-required\"*) ;;
  *)
    echo "Provider config status response did not include the LIMA Guardian subscription runtime gate." >&2
    exit 1
    ;;
esac

if [[ "${provider_calls_mode}" == "disabled-by-default" ]]; then
  echo "Checking OpenRouter prompt remains disabled by default at ${openrouter_prompt_url}"
  openrouter_prompt_code="$(curl -sS -o /dev/null -w "%{http_code}" -X POST "${openrouter_prompt_url}" -H "Content-Type: application/json" -d '{"prompt":"smoke","model":"mistralai/mistral-7b-instruct:free"}')"
  case "${openrouter_prompt_code}" in
    403) ;;
    *)
      echo "OpenRouter prompt did not return 403 while provider calls are disabled; got ${openrouter_prompt_code}." >&2
      exit 1
      ;;
  esac
else
  echo "OpenRouter prompt endpoint is env-enabled; skipping disabled-gate assertion."
fi

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

echo "Checking Round Table status at ${round_table_status_url}"
round_table_status_response="$(curl -fsS "${round_table_status_url}")"
printf "%s\n" "${round_table_status_response}"

case "${round_table_status_response}" in
  *\"meeting_engine\":\"not-implemented\"*|*\"meeting_engine\":\ \"not-implemented\"*)
    ;;
  *)
    echo "Round Table status response did not report meeting engine as not implemented." >&2
    exit 1
    ;;
esac

case "${round_table_status_response}" in
  *\"agent_orchestration\":\"not-implemented\"*|*\"agent_orchestration\":\ \"not-implemented\"*)
    ;;
  *)
    echo "Round Table status response did not report agent orchestration as not implemented." >&2
    exit 1
    ;;
esac


echo "Checking Model Seat status at ${model_seats_status_url}"
model_seats_status_response="$(curl -fsS "${model_seats_status_url}")"
printf "%s\n" "${model_seats_status_response}"

case "${model_seats_status_response}" in
  *\"model_calls\":\"not-implemented\"*|*\"model_calls\":\ \"not-implemented\"*)
    ;;
  *)
    echo "Model Seat status response did not report model calls as not implemented." >&2
    exit 1
    ;;
esac

case "${model_seats_status_response}" in
  *\"model_routing\":\"not-implemented\"*|*\"model_routing\":\ \"not-implemented\"*)
    ;;
  *)
    echo "Model Seat status response did not report model routing as not implemented." >&2
    exit 1
    ;;
esac

echo "Checking Task Lane status at ${task_lanes_status_url}"
task_lanes_status_response="$(curl -fsS "${task_lanes_status_url}")"
printf "%s\n" "${task_lanes_status_response}"

case "${task_lanes_status_response}" in
  *\"task_runtime\":\"not-implemented\"*|*\"task_runtime\":\ \"not-implemented\"*)
    ;;
  *)
    echo "Task Lane status response did not report task runtime as not implemented." >&2
    exit 1
    ;;
esac

case "${task_lanes_status_response}" in
  *\"scheduler\":\"not-implemented\"*|*\"scheduler\":\ \"not-implemented\"*)
    ;;
  *)
    echo "Task Lane status response did not report scheduler as not implemented." >&2
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

case "${guardian_status_response}" in
  *\"provider_execution_boundary\"*) ;;
  *)
    echo "Guardian status response did not include the provider execution boundary." >&2
    exit 1
    ;;
esac

case "${guardian_status_response}" in
  *\"runtime_gate\":\"lima-guardian-required\"*|*\"runtime_gate\":\ \"lima-guardian-required\"*) ;;
  *)
    echo "Guardian status response did not report the LIMA Guardian runtime gate." >&2
    exit 1
    ;;
esac

case "${guardian_status_response}" in
  *\"dispatch\":\"fail-closed\"*|*\"dispatch\":\ \"fail-closed\"*) ;;
  *)
    echo "Guardian status response did not report fail-closed provider dispatch." >&2
    exit 1
    ;;
esac

case "${guardian_status_response}" in
  *\"provider_adapter_contract\"*) ;;
  *)
    echo "Guardian status response did not include the provider adapter contract." >&2
    exit 1
    ;;
esac

case "${guardian_status_response}" in
  *\"contract_version\":1*|*\"contract_version\":\ 1*) ;;
  *)
    echo "Guardian provider adapter contract did not report contract_version=1." >&2
    exit 1
    ;;
esac

case "${guardian_status_response}" in
  *\"provider_ids\"*\"openai-codex-subscription\"*\"claude-subscription\"*) ;;
  *)
    echo "Guardian provider adapter contract did not report subscription provider IDs." >&2
    exit 1
    ;;
esac

case "${guardian_status_response}" in
  *\"allowed_response_statuses\"*\"succeeded\"*\"denied\"*\"blocked\"*\"timeout\"*\"failed\"*) ;;
  *)
    echo "Guardian provider adapter contract did not report expected response statuses." >&2
    exit 1
    ;;
esac

echo "Checking local chat sessions at ${local_chat_sessions_url}"
local_chat_sessions_response="$(curl -fsS "${local_chat_sessions_url}")"
printf "%s\n" "${local_chat_sessions_response}"
case "${local_chat_sessions_response}" in
  *\"sessions\"*) ;;
  *)
    echo "Local chat sessions response did not include sessions." >&2
    exit 1
    ;;
esac

echo "Checking local memory notes at ${local_memory_notes_url}"
local_memory_notes_response="$(curl -fsS "${local_memory_notes_url}")"
printf "%s\n" "${local_memory_notes_response}"
case "${local_memory_notes_response}" in
  *\"notes\"*) ;;
  *)
    echo "Local memory notes response did not include notes." >&2
    exit 1
    ;;
esac

echo "Checking local work lane cards at ${local_work_lane_cards_url}"
local_work_lane_cards_response="$(curl -fsS "${local_work_lane_cards_url}")"
printf "%s\n" "${local_work_lane_cards_response}"
case "${local_work_lane_cards_response}" in
  *\"cards\"*) ;;
  *)
    echo "Local work lane cards response did not include cards." >&2
    exit 1
    ;;
esac

echo "Checking local data export at ${local_data_export_url}"
local_data_export_response="$(curl -fsS "${local_data_export_url}")"
printf "%s\n" "${local_data_export_response}"
case "${local_data_export_response}" in
  *\"export_type\":\"local-workstation-data\"*|*\"export_type\":\ \"local-workstation-data\"*) ;;
  *)
    echo "Local data export response did not report the local Workstation export type." >&2
    exit 1
    ;;
esac
case "${local_data_export_response}" in
  *\"import_supported\":false*) ;;
  *)
    echo "Local data export response did not report import as unsupported." >&2
    exit 1
    ;;
esac
case "${local_data_export_response}" in
  *\"data\"*) ;;
  *)
    echo "Local data export response did not include data." >&2
    exit 1
    ;;
esac

echo "Checking local runtime settings at ${local_runtime_settings_url}"
local_runtime_settings_response="$(curl -fsS "${local_runtime_settings_url}")"
printf "%s\n" "${local_runtime_settings_response}"
case "${local_runtime_settings_response}" in
  *\"configuration\":\"env-driven\"*|*\"configuration\":\ \"env-driven\"*) ;;
  *)
    echo "Local runtime settings response did not report env-driven configuration." >&2
    exit 1
    ;;
esac
case "${local_runtime_settings_response}" in
  *\"settings_writes\":\"not-supported\"*|*\"settings_writes\":\ \"not-supported\"*) ;;
  *)
    echo "Local runtime settings response did not report settings writes as unsupported." >&2
    exit 1
    ;;
esac
case "${local_runtime_settings_response}" in
  *\"data_directory\"*\"sqlite_database\"*\"local_models\"*) ;;
  *)
    echo "Local runtime settings response did not include data directory, SQLite, and local model settings." >&2
    exit 1
    ;;
esac

echo "Checking local model status at ${local_models_status_url}"
local_models_status_response="$(curl -fsS "${local_models_status_url}")"
printf "%s\n" "${local_models_status_response}"
case "${local_models_status_response}" in
  *\"adapter\":\"ollama\"*|*\"adapter\":\ \"ollama\"*) ;;
  *)
    echo "Local model status response did not report the Ollama adapter." >&2
    exit 1
    ;;
esac
case "${local_models_status_response}" in
  *\"base_url_policy\":\"localhost-only\"*|*\"base_url_policy\":\ \"localhost-only\"*) ;;
  *)
    echo "Local model status response did not report localhost-only policy." >&2
    exit 1
    ;;
esac

echo "Checking local model prompt remains disabled by default at ${local_models_prompt_url}"
local_models_prompt_code="$(curl -sS -o /dev/null -w "%{http_code}" -X POST "${local_models_prompt_url}" -H "Content-Type: application/json" -d '{"prompt":"smoke","model":"llama3.2"}')"
case "${local_models_prompt_code}" in
  403) ;;
  *)
    echo "Local model prompt did not return 403 while disabled; got ${local_models_prompt_code}." >&2
    exit 1
    ;;
esac

echo "Checking frontend HTTP response at ${SPARKBOT_FRONTEND_URL}"
curl -fsS "${SPARKBOT_FRONTEND_URL}" >/dev/null

echo "PASS: local Sparkbot shell smoke check completed"
