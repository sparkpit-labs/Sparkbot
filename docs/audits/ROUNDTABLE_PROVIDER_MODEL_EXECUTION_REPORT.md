# Round Table Provider Model Execution Report

- Branch: `port-rd-roundtable-provider-model-execution`
- Scope: narrow Round Table text-generation execution through configured provider routes

## Summary

This branch wires Round Table sessions to the existing server-side model execution service. When at least one persisted seat resolves to a configured provider route, Round Table calls the provider for first-pass turns, manager assessment, second-pass turns, and manager summary. When no configured route exists, the existing deterministic provider-safe flow remains the fallback.

## Safety Boundary

Provider credentials remain server-side. Model-call events record provider, model, status, message/output counts, duration, and Round Table phase metadata only. They do not store prompts, model outputs, headers, or credentials.

Round Table still does not execute connector sends, file/process/terminal work, schedulers, background jobs, device actions, or protected tools. Operator requests are checked before model dispatch. Model output is checked before any turns, assignments, summaries, or notes are persisted; protected output blocks the session and records a Guardian event.

## Persistence Behavior

Provider-backed sessions keep the established Round Table artifact shape:

- 7 first-pass participant turns
- 1 Seat 1 manager assessment
- 7 assignments
- 7 second-pass participant turns linked to assignments
- 1 Seat 1 manager summary
- 1 wrap-up note linked to the summary

Reruns of complete, blocked, or partially persisted sessions remain idempotent and do not duplicate artifacts.

## Tests Added

- Configured OpenRouter flow with mocked provider responses persists provider/model metadata on all turns and redacted model-call events.
- Protected model output blocks the Round Table session before any turns, assignments, summaries, or notes are written.
- Existing deterministic fallback tests now clear provider environment variables to avoid accidental live calls.

## Validation Results

- `env PYTHONPATH=backend .venv-local/bin/pytest backend/tests/test_roundtable_workstation_integration.py -q`: 5 passed, 1 existing Starlette/httpx deprecation warning
- `env PYTHONPATH=backend .venv-local/bin/pytest backend/tests -q`: 42 passed, 1 existing Starlette/httpx deprecation warning
- `npm test -- --run`: 7 passed
- `npm run build`: pass
- `npm audit --audit-level=moderate`: 0 vulnerabilities
- `bash scripts/check-public-safety.sh`: pass
- `bash scripts/validate-public-shell.sh`: pass; backend 42 passed, frontend 7 passed, npm audit 0 vulnerabilities, build passed
- `git diff --check`: pass
- Changed-file privacy scan for blocked private references, private paths, identity names, private IPs, and provider-key assignments: pass

## Remaining Deferred Work

- Connector sends and external delivery
- File/process/terminal execution
- Scheduler and background job execution
- Device actions
- Streaming model responses
- Broader Guardian policy expansion beyond current fail-closed checks
