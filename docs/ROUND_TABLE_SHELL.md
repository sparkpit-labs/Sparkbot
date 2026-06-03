# Round Table Surface

The Round Table surface is now a provider-safe public room workflow inside Sparkbot. It is backend-backed by the shared Workstation store and is available from `/workstation` and `/roundtable`.

## Current behavior

- Operators can create a Round Table session with a title and problem statement.
- Session creation also creates or uses a persisted Workstation room with persisted seat participants.
- Seat 1 is identified as the Meeting Manager.
- Other persisted seats participate as provider-safe contributors.
- Running the session saves a deterministic local flow: first-pass ideas, manager assessment, assignments, second-pass answers, and manager wrap-up.
- The manager wrap-up creates one Round Table summary and one wrap-up note. Turn-by-turn notes are not generated.
- Round Table recalls shared memory and Workstation or room notes before saving turns.
- Round Table events write to the shared Spine/event log.

## Provider-safe limits

- No real provider/model calls are made.
- No connector sends or external delivery are made.
- No files, processes, shell commands, or terminal commands are executed.
- No scheduled jobs or background work are started.
- No device actions are executed.

## Guardian boundary

Requests that look destructive, external, privileged, scheduled, connector-based, file/process-related, terminal-related, or device-related fail closed. Round Table logs Guardian block events for those requests and does not execute them.

Future action-capable Round Table behavior must use the shared Guardian confirmation boundary before execution.

## Next public slice

The next slice should audit this integration, then decide between a narrow provider/model execution path or model-seat/provider configuration polish. Real provider execution must keep secrets server-side, preserve event redaction, and keep Guardian as the mandatory boundary for protected actions.
