# Workstation Architecture Boundary

Sparkbot public state must use the shared local backend store as the source of truth.

## Shared state source

The current shared store persists:

- Chat sessions and messages
- Workstation seats and rooms
- Round Table sessions, turns, assignments, summaries, and wrap-up note links
- Notes and memory entries
- Spine/event log entries
- Guardian action confirmations
- Dashboard counters derived from the same records

Frontend state should stay transient: loading flags, form drafts, selected tabs, and currently loaded API responses. Persistent product state should not be introduced through browser storage or page-local-only stores.

## Round Table persistence contract

Round Table durable state is limited to backend-backed rooms, participants, sessions, turns, assignments, summaries, wrap-up note links, notes, memory recall, events, and Guardian block records. The frontend may hold only form drafts, loading state, the selected session response, and status messages.

A blocked privileged Round Table request may update the session to `blocked` and write a Guardian block event. It must not create turns, assignments, summaries, or wrap-up notes.

## Surface roles

- Chat: direct operator conversation surface. It can read shared context counts, save chat turns, save optional memory, call the selected configured provider route, log model-call events, and request Guardian confirmations.
- Workstation: operating-floor surface for rooms, seats, shared context, Round Table activity, and pending confirmations.
- Round Table: provider-capable room workflow for persisted meeting sessions, Seat 1 manager checkpoints, assignments, summaries, wrap-up notes, and Spine events.
- Command Center: configuration, model routing, agent setup, server-side credential entry, and security/Guardian settings.
- Spine: event history, dashboard counters, and task/project queue empty states.
- Controls: local setup readiness, backend health, provider readiness, and explicit capability limits.

## Guardian rule

Any future feature that can destroy data, send externally, mutate files, execute commands, run scheduled work, invoke tools, control devices, or perform privileged behavior must use the shared Guardian confirmation boundary before execution.

Confirmations are expected to be:

- one-time use
- action-bound
- source-bound
- expiration-bound
- persisted in shared backend state
- visible through Workstation/Spine/Guardian state
- fail-closed when missing, pending, denied, expired, already used, or mismatched

Chat and Round Table fail closed for privileged requests and log Guardian block events. Model output is returned as text only and cannot execute protected actions.

## Deferred execution rule

Provider/model execution is currently limited to Chat and Round Table text generation through configured provider routes. Connector sends, schedulers, file/process execution, terminal execution, protected tool execution, and device-action behavior remain deferred until explicit backend routes, tests, user-visible labels, event logging, redaction, and Guardian gates are added.

Round Table turn sequencing reads shared context, writes shared state, keeps provider credentials server-side, falls back when routes are unavailable, and does not execute external actions.
