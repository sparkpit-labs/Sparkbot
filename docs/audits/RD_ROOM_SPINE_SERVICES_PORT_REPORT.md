# R&D Room And Spine Services Port Report

## Summary

Branch `port-rd-command-center-room-spine-services` adds the shared Workstation state foundation needed for Command Center, Chat, Round Table, seats, notes, memory, events, and dashboard counters to operate as one local app instead of disconnected pages.

This branch does not implement the full Chat or Round Table meeting engine. It adds the persistent service layer and endpoint shape those slices should use next.

## R&D Files And Docs Inspected

- `frontend/src/routes/_layout/spine.tsx`
- `frontend/src/components/CommandCenter/SetupPanels.tsx`
- `frontend/src/components/CommandCenter/OperationalPanels.tsx`
- `frontend/src/hooks/useControlsState.ts`
- `frontend/src/lib/spine.ts`
- `frontend/src/lib/workstationMeeting.ts`
- `backend/app/api/routes/chat/rooms.py`
- `backend/app/api/routes/chat/model.py`
- `backend/app/api/routes/chat/guardian.py`
- `backend/app/api/routes/chat/security.py`
- `backend/app/api/routes/chat/dashboard.py`
- `backend/app/api/routes/chat/spine.py`
- `backend/app/api/routes/chat/memory.py`
- `backend/app/api/routes/chat/tasks.py`
- `backend/app/api/routes/chat/reminders.py`
- `backend/app/api/routes/chat/projects.py`

## Storage Mechanism

Storage uses SQLite through Python's standard library in `backend/app/services/workstation_store.py`.

Default location: `data/command-center/workstation.sqlite3`, under the already gitignored `data/` directory.

Why SQLite:

- Local-first persistence across restart.
- No external database service.
- More coherent and durable than browser state.
- Safe for a public MVP service foundation.
- Easy for Chat and Round Table endpoints to share next.

Provider credentials remain outside the Workstation state response and continue to use the server-side config/secret path from the prior Command Center branch.

## Service And Endpoints Added

Workstation state:

- `GET /api/workstation/state`

Seats:

- `GET /api/seats`
- `PATCH /api/seats/{seat_index}`
- `POST /api/seats/{seat_index}`

Rooms:

- `GET /api/rooms`
- `POST /api/rooms`
- `GET /api/rooms/{room_id}`
- `PATCH /api/rooms/{room_id}`

Notes:

- `GET /api/notes`
- `POST /api/notes`
- `GET /api/notes/{note_id}`
- `PATCH /api/notes/{note_id}`

Memory:

- `GET /api/memory`
- `POST /api/memory`
- `POST /api/memory/recall`
- `DELETE /api/memory/{memory_id}`

Events:

- `GET /api/events`
- `POST /api/events`

Guardian/action boundary foundation:

- `POST /api/guardian/actions/confirmations`

Existing Command Center status routes now read shared store counters where useful:

- `GET /api/v1/chat/dashboard/summary`
- `GET /api/v1/chat/spine/operator/overview`
- `GET /api/v1/chat/spine/operator/events`
- `GET /api/v1/chat/spine/operator/producers`
- `GET /api/v1/chat/spine/operator/projects`

## State Moved From Browser To Backend

Seat assignments moved from browser-local storage to the SQLite Workstation store.

Command Center now loads `/api/workstation/state` as the main backend snapshot and uses `PATCH /api/seats/{seat_index}` for seat assignment changes. The browser may still hold transient React state, but the source of truth is the backend store.

## Memory / Context Model

Memory entries persist with:

- content
- memory type
- source surface
- source id
- actor
- tags
- created timestamp
- updated timestamp

Recall is intentionally simple for this foundation branch: it matches query terms and tags against persisted memory content and metadata. Chat and Round Table should call `POST /api/memory/recall` before building model context in the next slices.

## Event Log Model

Events persist with:

- event type
- source surface
- source id
- actor
- summary
- JSON payload with sensitive-looking keys redacted before storage
- created timestamp

Events are recorded for:

- seat updates
- room creation and updates
- note save and update
- memory save and delete
- manual event appends
- action confirmation creation
- Command Center config updates
- model default updates
- custom agent creation
- PIN updates without storing PIN values

## Rooms / Notes / Artifacts Foundation

Rooms persist metadata, status, phase, goal, summary, timestamps, and the current seat participants at creation time.

Notes persist independently and can attach to:

- `workstation`
- `chat`
- `room`
- `meeting`
- any future surface using `surface` and `source_id`

Meeting artifacts are represented by the same note foundation for this branch. Full generated meeting artifacts and manager summaries remain a Round Table follow-up.

## Guardian / Action Boundary Foundation

This branch adds confirmation records and audit events for actions that should require operator approval later. It does not port the full Vault, break-glass, or advanced Guardian subsystem.

Existing Command Center Security profile, custom guardrails, and PIN behavior remain active from the previous branch.

## Features Intentionally Deferred

- Full Chat integration.
- Full Round Table meeting engine.
- Seat 1 manager execution flow.
- Meeting heartbeat and live multi-seat turns.
- Generated manager summaries.
- Full task/project/event Spine queue parity.
- Full Guardian Vault and break-glass behavior.
- Connector credential flows and write-capable connector actions.
- Advanced scheduler behavior.

## Remaining Gaps To Connect Chat

- Chat endpoint should load `/api/workstation/state` and selected seat/provider routing.
- Chat should call memory recall before provider calls.
- Chat messages should append events and optional notes/memory entries.
- Chat should attach notes to `surface=chat` and its session id.
- Chat should respect pending confirmation records for risky actions.

## Remaining Gaps To Connect Round Table

- Round Table should create/read rooms through `/api/rooms`.
- Meeting seats should come from `/api/seats` or room participants.
- Meeting turns should save events and notes.
- Seat 1 manager summaries should persist as notes or meeting artifacts.
- Round Table context should call memory recall before each phase.
- Meeting phase/status should update the room record.

## Public Safety Notes

- No secrets are returned by `/api/workstation/state`.
- Provider credentials remain server-side only.
- SQLite files live under gitignored `data/`.
- The branch does not add release tags, release packaging, or public announcement material.
