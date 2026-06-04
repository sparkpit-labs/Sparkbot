# Workstation Surface

The current public Workstation surface is no longer a disconnected static preview. `/workstation` is a backend-backed operating-floor view for rooms, model seats, provider-safe Round Table sessions, shared memory, notes, Spine activity, and Guardian confirmation state.

## What exists

- `/workstation` shows shared rooms, seats, Round Table state, counters, recent memory, notes, events, and pending confirmations.
- `/roundtable` opens the same backend-backed Round Table room surface directly.
- `/chat` is the operator conversation surface and uses the same shared backend store.
- `/command-center` is the configuration, model routing, agents, and security surface.
- `/spine` is the event/history/counter surface.
- `/controls` is the setup/readiness and capability-limit surface.
- Room foundations can be created and persisted with seat participants.
- Provider-safe Round Table sessions can be created, run through deterministic local turns, assigned to seats, summarized by Seat 1, and saved as one wrap-up note.
- Workstation notes can be saved to shared backend state.
- Existing static preview components remain inert where still referenced by legacy docs or future planning, but they are not the primary Workstation route.

## Current status model

- Backend store: works today
- Chat sessions/messages: works today, narrow configured-provider execution active
- Workstation rooms/seats/notes/memory/events: works today
- Round Table provider-safe sessions/turns/assignments/summaries: works today
- Command Center model/seat/security configuration: works today
- Spine event log and counters: works today, task/project queues are empty-state placeholders
- Controls setup/readiness: works today as a reporting surface
- Chat provider/model execution: active only through the selected configured route
- Connector sends: deferred
- File/process/terminal execution: deferred
- Scheduler/background workers: deferred
- Device actions: deferred

## What is intentionally excluded

- Live provider-seat responses from Round Table
- Tool execution
- Connector sends or external delivery
- File/process/shell/terminal execution
- Scheduler/background workers
- Device actions
- Private platform internals

## Scope notes

The Workstation surface should represent the company/work floor: rooms, seats, shared context, Round Table sessions, and activity. Chat should remain the direct operator conversation channel. Command Center, Spine, and Controls should remain distinct and should not duplicate Chat or the Round Table workflow.
