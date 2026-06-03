# Workstation Surface

The current public Workstation surface is no longer a disconnected static preview. `/workstation` is a backend-backed operating-floor view for rooms, model seats, shared memory, notes, Spine activity, and Guardian confirmation state.

## What exists

- `/workstation` shows shared rooms, seats, counters, recent memory, notes, events, and pending confirmations.
- `/chat` is the operator conversation surface and uses the same shared backend store.
- `/command-center` is the configuration, model routing, agents, and security surface.
- `/spine` is the event/history/counter surface.
- `/controls` is the setup/readiness and capability-limit surface.
- Room foundations can be created and persisted with seat participants.
- Workstation notes can be saved to shared backend state.
- Existing static Round Table, provider, and Guardian preview components remain inert where still referenced by legacy docs or future planning, but they are not the primary Workstation route.

## Current status model

- Backend store: works today
- Chat sessions/messages: works today, provider execution deferred
- Workstation rooms/seats/notes/memory/events: works today
- Command Center model/seat/security configuration: works today
- Spine event log and counters: works today, task/project queues are empty-state placeholders
- Controls setup/readiness: works today as a reporting surface
- Round Table turn engine: deferred
- Connector sends: deferred
- File/process/terminal execution: deferred
- Scheduler/background workers: deferred

## What is intentionally excluded

- Real provider/model calls from Chat or seats
- Round Table turn sequencing or Seat 1 meeting-manager loop
- Tool execution
- Connector sends or external delivery
- File/process/shell/terminal execution
- Scheduler/background workers
- Physical device control
- Private platform internals

## Scope notes

The Workstation surface should represent the company/work floor: rooms, seats, shared context, and activity. Chat should remain the direct operator conversation channel. Command Center, Spine, and Controls should remain distinct and should not duplicate Chat's conversation workflow.
