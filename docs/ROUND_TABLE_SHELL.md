# Round Table Surface

The Round Table surface is now a provider-capable public room workflow inside Sparkbot. It is backend-backed by the shared Workstation store and is available from `/workstation` and `/roundtable`.

## Current behavior

- Operators can create a Round Table session with a title and problem statement.
- Session creation also creates or uses a persisted Workstation room with persisted seat participants.
- Seat 1 is identified as the Meeting Manager.
- Other persisted seats participate as configured contributors.
- Running the session uses configured provider/model routes for seat turns when available, then falls back to deterministic local turns when no configured route exists.
- The manager wrap-up creates one Round Table summary and one wrap-up note. Turn-by-turn notes are not generated.
- Round Table recalls shared memory and Workstation or room notes before saving turns.
- Round Table events write to the shared Spine/event log, including redacted model-call metadata when provider execution runs.
- Provider outputs are persisted as text-only meeting turns; model-call events remain metadata-only and do not store prompts or outputs.

## Provider and action limits

- Provider credentials stay server-side and are not returned to the browser.
- Model-call events record provider, model, status, counts, phase metadata, and duration, not prompts, outputs, headers, or credentials.
- No connector sends or external delivery are made.
- No files, processes, shell commands, or terminal commands are executed.
- No scheduled jobs or background work are started.
- No device actions are executed.

## Guardian boundary

Round Table does not execute external delivery, connector work, file/process work, terminal work, scheduled work, or device actions. Requests for that kind of work are handled as text planning/drafting through the selected model route or deterministic fallback.

Future action-capable Round Table behavior must use explicit backend routes and the shared Guardian confirmation boundary before execution.

## Current provider boundary

Round Table now shares the provider/model execution service with Chat. It uses persisted seat routes when configured, falls back safely when routes are unavailable, keeps secrets server-side, redacts event payloads, and treats model output as text only.
