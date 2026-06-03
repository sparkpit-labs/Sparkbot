# Chat Surface

The current public Sparkbot app includes a backend-backed Chat surface at `/chat`.

Chat is the operator conversation channel. It stores sessions and messages in the shared local Workstation store, reads shared memory and notes for context, writes Spine event-log entries, and shows Guardian confirmation state. Provider/model execution is still deferred: Chat returns a local Workstation acknowledgement instead of calling a model.

## Current behavior

- Chat sessions and messages persist through the backend SQLite Workstation store.
- Chat can create a new session, send a turn, reload previous sessions, and save a chat-scoped note.
- User messages can optionally be saved to shared Workstation memory.
- Chat reads shared memory and notes context and reports the selected Command Center/Seat 1 model route.
- Chat writes event-log entries for session creation, user turns, assistant acknowledgements, context recall, and Guardian blocks.
- Memory delete requests create a Guardian confirmation and do not delete memory directly.
- Unsupported privileged requests are blocked and logged without execution.

## Deferred from this branch

- Provider/model execution
- Streaming responses
- Full Round Table meeting turns
- Connector sends
- File, process, terminal, or shell execution
- Scheduler/background jobs
- Physical device control

## Boundary

Chat can become Sparkbot's operator-facing middle person only by continuing to use the shared Workstation state and Guardian boundary. Any future action-capable Chat path must create or consume an action-bound Guardian confirmation before executing destructive, external, privileged, or scheduled work.
