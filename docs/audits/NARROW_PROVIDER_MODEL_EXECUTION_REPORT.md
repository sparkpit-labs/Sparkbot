# Narrow Provider Model Execution Report

- Branch: `port-narrow-provider-model-execution`
- Base commit: `6689eaa0ea0c9a9054916c61ce08c983223d2a30`
- Scope: narrow Chat provider/model execution only

## Summary

This branch adds a backend-only model execution service and wires Chat to the selected Command Center provider/model route. It does not add connectors, external sends, schedulers, background workers, file/process/terminal execution, browser automation, device control, or private runtime imports.

Round Table remains deterministic and provider-safe. Its persisted session, turn, assignment, summary, and wrap-up note behavior is unchanged.

## Existing Provider Source Of Truth

Command Center remains the source of truth:

- `SPARKBOT_DATA_DIR/config.json`: default provider/model selection, stack, local runtime, routing policy, agents, and guardrail settings.
- `SPARKBOT_DATA_DIR/secrets.json`: server-side provider credentials saved through Command Center.
- Environment variables such as `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `GROQ_API_KEY`, `MINIMAX_API_KEY`, and `XAI_API_KEY` can also mark a provider configured.
- Workstation seats remain persisted in the shared SQLite store. Chat now resolves through the Command Center default route first, with Seat 1 metadata retained for display/fallback context.

## Service Added

Added `backend/app/services/model_execution.py`.

The service:

- resolves provider/model from existing Command Center config
- validates provider readiness without returning credentials
- dispatches a single chat-completion style request
- supports OpenRouter, OpenAI, Anthropic, Google, Groq, xAI, and Ollama route shapes already present in Command Center
- treats subscription-only routes as unsupported for server-side execution in this public slice
- normalizes response text
- returns user-safe error/timeout statuses
- logs redacted `model.call.completed` or `model.call.failed` events

## Chat Integration

Chat now calls the selected configured provider route after:

- saving the user turn
- recalling shared context counts
- checking memory-delete confirmation needs
- blocking protected user requests

If the provider succeeds, the assistant message stores the model text. If the provider is unconfigured, unsupported, errors, or times out, Chat stores a safe assistant error and no secret-bearing details.

Model output is treated as text only. If output appears to request protected work, Chat logs a Guardian block event and returns a safe refusal instead of executing or exposing the protected instruction as the assistant answer.

## Round Table Integration

Round Table provider execution is intentionally not included in this branch.

The deterministic provider-safe flow remains available and tested:

1. first pass
2. manager assessment
3. assignments
4. second pass
5. manager summary

No per-turn notes were added. The wrap-up note remains manager-wrap-up only.

## Event Logging And Redaction

Model-call events are written to the shared Spine/event log.

Logged payloads include:

- provider
- model
- status
- message count
- output character count
- duration
- safe error label or HTTP status when relevant

Logged payloads do not include:

- provider credentials
- authorization headers
- API keys
- raw provider request payloads
- prompts
- model output text
- saved secret values

The shared store also continues to sanitize sensitive payload keys such as `api_key`, `credential`, `password`, `secret`, and `token`.

## Guardian Boundary

Protected user requests continue to fail closed before provider dispatch.

Protected model output also fails closed:

- no protected action is executed
- a `guardian.action_blocked` event is recorded
- the assistant response explains that a Guardian-confirmed backend route is required

The branch adds no action-capable routes.

## Tests Added

Added `backend/tests/test_narrow_provider_model_execution.py` for:

- provider success path with mocked provider
- selected provider/model lookup from Command Center config
- provider error handling
- provider timeout handling
- no secret exposure in API responses
- no secret exposure in event payloads
- no prompt/output storage in model-call events
- model output cannot execute protected actions
- protected user requests fail closed before provider dispatch

Existing Chat tests now clear provider environment variables so baseline shared-state tests never make accidental live provider calls.

Round Table deterministic tests still pass unchanged.

## Validation Results

- `python3 -m py_compile backend/app/services/model_execution.py backend/app/api/workstation.py`: pass
- `env PYTHONPATH=backend .venv-local/bin/pytest backend/tests -q`: 32 passed, 1 Starlette/httpx deprecation warning
- `npm test -- --run`: 7 passed
- `npm run build`: pass
- `git diff --check`: pass
- `npm audit --audit-level=moderate`: 0 vulnerabilities
- `bash scripts/check-public-safety.sh`: pass
- `bash scripts/validate-public-shell.sh`: pass; backend 32 passed, frontend 7 passed, build passed, npm audit 0 vulnerabilities
- Changed-file privacy scan for blocked private references, identity names, private IP ranges, and provider-key assignments: pass
- Manual route check: `/`, `/spine`, `/controls`, `/command-center`, `/workstation`, `/chat`, and `/roundtable` returned HTTP 200 from the local frontend server
- Manual backend health check: `/health` returned `{"status":"ok","service":"sparkbot-server","mode":"local"}` from the local backend server

## Remaining Gaps

- Round Table live provider seats remain deferred.
- Streaming responses remain deferred.
- Connector sends remain deferred.
- Scheduler/background workers remain deferred.
- File/process/terminal execution remains deferred.
- Device control remains deferred.
- Subscription-only desktop/browser model surfaces are not executed server-side in this public branch.

## Recommendation

Proceed to a narrow audit branch for this provider execution slice before adding Round Table provider-enabled seats.
