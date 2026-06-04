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
- Provider outputs are scanned for protected-action requests before any turns, assignments, summaries, or notes are persisted.

## Provider and action limits

- Provider credentials stay server-side and are not returned to the browser.
- Model-call events record provider, model, status, counts, phase metadata, and duration, not prompts, outputs, headers, or credentials.
- No connector sends or external delivery are made.
- No files, processes, shell commands, or terminal commands are executed.
- No scheduled jobs or background work are started.
- No device actions are executed.

## Guardian boundary

Requests that look destructive, external, privileged, scheduled, connector-based, file/process-related, terminal-related, or device-related fail closed. Round Table logs Guardian block events for those requests and does not execute them.

Future action-capable Round Table behavior must use the shared Guardian confirmation boundary before execution.

## Current provider boundary

Round Table now shares the narrow provider/model execution service with Chat. It uses persisted seat routes when configured, falls back safely when routes are unavailable, keeps secrets server-side, redacts event payloads, and blocks protected actions requested by model output before persisting meeting artifacts.
