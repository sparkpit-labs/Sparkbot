# Guardian Controls

Guardian controls in the current public app are a limited safety boundary, not a full private policy runtime.

## Current behavior

- Chat and Round Table detect protected-action requests and fail closed before dispatching or persisting unsafe model output.
- Memory delete uses server-side Guardian confirmation before deletion.
- Task run/write-mode requests fail closed in backend routes and log safe block events.
- Command Center stores local security settings such as operator PIN state, guardrail text, and routing monitor labels.
- Workstation, Command Center, and Spine show pending confirmations, safe Guardian block events, and disabled execution state.

## What remains disabled

- No full policy engine is included.
- No connector action approval/resume path is included.
- No file/process/terminal/browser/device action approval path is included.
- No scheduler or automatic runner approval path is included.
- No full private Vault or platform-internal control system is included.
- No sensitive action is executed from Guardian state in this public MVP.

## Follow-up direction

Any future action-capable route must be explicit, server-side, source-bound, one-time confirmed, fail-closed, tested for redaction, and clear in UI copy before execution is enabled.
