# Notes, History, And Spine Polish Report

## Branch And Base

- Branch: `port-rd-notes-history-spine-polish`
- Base branch: `audit-rd-memory-governance-lifecycle-parity`
- Base commit: `cf1fda6877b25016af9d376fb46607028c53bc7e`

## R&D Files And Docs Inspected

Read-only R&D source/docs inspected:

- `sources/Sparkbot/backend/app/models.py`
- `sources/Sparkbot/backend/app/crud.py`
- `sources/Sparkbot/backend/app/api/routes/chat/rooms.py`
- `sources/Sparkbot/backend/app/api/routes/chat/spine.py`
- `sources/Sparkbot/backend/app/services/guardian/spine.py`
- `sources/Sparkbot/docs/architecture/roundtable_meeting_flow_v1.6.60.md`
- `sources/Sparkbot/docs/release-notes/v1.6.46.txt`
- `sources/Sparkbot/docs/release-notes/v1.6.59.txt`
- `sources/Sparkbot/docs/release-notes/v1.6.60.txt`

R&D behavior summary:

- Meeting artifacts were durable backend records linked to rooms.
- Artifact types included agenda, notes, decisions, and action items.
- Meeting artifact routes supported list/create, and generated meeting notes were explicit/manual.
- Created meeting artifacts emitted Spine events such as meeting summary/decision/action-item events.
- Meeting output events carried source references, room linkage, artifact ids, and safe metadata.
- The later Roundtable meeting flow kept Seat 1 as meeting manager and explicitly documented manual-only notes generation.
- Meeting artifact rollups could promote useful decisions/actions into shared memory, while transcripts stayed room-scoped.

## Public Behavior Before This Branch

Public Sparkbot already had the shared Workstation store and these backend-backed records:

- Rooms and seats
- Chat sessions and messages
- Round Table sessions, turns, assignments, summaries, and wrap-up notes
- Notes
- Memory entries
- Event log entries
- Guardian confirmations
- Dashboard counters from the shared store

Gaps before this branch:

- Workstation/Spine visibility was shallow even though the data existed.
- Notes were listable and editable by API, but the Workstation UI did not expose edit/read behavior well.
- Round Table wrap-up notes were visible in the Round Table page, but not clearly presented as history/artifacts in the Workstation/Spine surfaces.
- Spine mostly showed recent event summaries and placeholder queues, not notes/artifacts/session history together.
- Event listing could not filter by surface/source id, and arbitrary event payloads did not fail closed for prompt/output/message/header fields.

## Notes Behavior Restored/Polished

Public notes remain the public-safe equivalent of R&D meeting artifacts for this slice.

Changes:

- Workstation now shows recent notes/artifacts with source labels.
- Workstation exposes inline note editing through the existing server-backed note PATCH route.
- Round Table manager wrap-up notes are visible as Round Table artifacts through the Workstation and Spine views.
- Note edits continue to log safe `note.updated` events.
- Notes remain persistent in the local Workstation SQLite store.
- Per-turn notes were not added.

## History Behavior Restored/Polished

Added a compact shared history aggregate:

- `GET /api/workstation/history`

The response includes:

- rooms
- notes
- memory count/items
- recent safe events
- Chat sessions with message counts and last message metadata
- Round Table sessions with turns, assignments, summaries, notes, room metadata, and note links
- real dashboard counters
- storage metadata

The Workstation surface now shows:

- Round Table session history with status/phase, turn count, assignment count, and wrap-up note link
- Chat session history with message counts and last-message previews
- links back to the dedicated Chat and Round Table surfaces

The Round Table phase order and idempotency behavior were not changed.

## Spine/Event Visibility Added/Polished

Changes:

- Spine now uses `GET /api/workstation/history` for its primary history/counter view.
- Spine shows notes/artifacts with backend source labels.
- Spine shows Chat and Round Table session history together.
- Spine groups recent event rows by safe event category: provider/model, memory, notes, Round Table, Chat, Guardian, rooms, and Workstation.
- Event rows show event type, summary, surface, and source id only.
- Prompts, model outputs, message arrays, headers, credentials, and secrets are not displayed.

Event endpoint cleanup:

- `GET /api/events` now accepts optional `surface` and `source_id` filters in addition to `event_type`.
- Event payload sanitization now redacts protected payload keys such as `prompt`, `messages`, `output`, `headers`, `authorization`, request/response bodies, and secret-like keys.

## Dashboard Counters Added/Polished

No fake counters were added.

The existing real dashboard counters remain the source for:

- rooms
- notes
- memory
- events
- seats
- Chat sessions/messages
- Round Table sessions/turns/assignments/summaries
- pending confirmations

The Workstation and Spine panels now expose more of those real counters, including Chat turns and Round Table sessions.

## Endpoints And Services Added Or Changed

Added:

- `WorkstationStore.workstation_history(limit=25)`
- `GET /api/workstation/history`
- frontend `fetchWorkstationHistory()`
- frontend `fetchNote()`
- frontend `updateNote()`
- frontend `fetchEvents()` helper with filters

Changed:

- `WorkstationStore.list_events()` supports `event_type`, `surface`, and `source_id` filters.
- `GET /api/events` accepts `surface` and `source_id` filters.
- Event payload sanitization redacts prompt/output/message/header/request/response fields.

## Frontend Panels/Components Changed

Changed:

- `frontend/src/components/WorkstationFloor.tsx`
- `frontend/src/components/SpineSurface.tsx`
- `frontend/src/api.ts`
- `frontend/src/styles.css`
- `frontend/src/App.test.tsx`

Workstation UI changes:

- Editable backend-backed note/artifact list.
- Shared context panel split into recent memory and notes/artifacts.
- Session history panel for Chat and Round Table.
- Safe activity panel with recent Spine events and Guardian confirmations.

Spine UI changes:

- Notes/artifacts panel.
- Room/session history panel.
- Recent events panel with safe metadata and event category labels.
- Expanded real counters.

## Redaction And Safety Behavior

Safety behavior preserved or tightened:

- Notes are redacted at write/read boundaries.
- Event payloads redact secret-like keys and protected prompt/output/header/message keys.
- History aggregate reuses existing redacted serializers for notes, memory, chat messages, rooms, Round Table turns, assignments, summaries, and events.
- No browser localStorage source of truth was added.
- No connector sends, schedulers, file/process/terminal/device automation, token bridges, or local CLI subscription auth were added.
- No Round Table phase logic was changed.
- No per-turn notes were added.
- Manager wrap-up notes remain the only Round Table note generated by the session run path.

## Tests Added Or Strengthened

Backend:

- `test_workstation_history_links_notes_sessions_and_safe_events`
  - Chat history persists and appears in `/api/workstation/history`.
  - Note read/update works and redacts secrets.
  - Round Table history includes turns, assignments, summaries, and wrap-up note link.
  - Round Table manager wrap-up creates one note, not per-turn notes.
  - Event filtering by `event_type` and `surface` works.
  - Protected event payload keys are redacted.
  - History persists across a second client/readback.

Frontend:

- `renders backend history and edits notes without browser storage`
  - Workstation history renders backend Chat/Round Table records.
  - Note edit uses the server PATCH route.
  - Browser localStorage is not written.

Existing Chat/Round Table integration tests continue to validate:

- no provider secrets in model-call event payloads
- protected model output blocks before persistence
- provider-backed Round Table prompt safety
- deterministic fallback idempotency
- manager-summary note/memory dedupe

## Validation Results

Validation run on this branch:

- `git diff --check`: PASS
- Focused backend tests (`.venv-local/bin/pytest backend/tests/test_workstation_services.py -q`): PASS, `6 passed`
- Backend tests: PASS, `51 passed`
- Frontend tests: PASS, `10 passed`
- Frontend build: PASS
- `npm audit --audit-level=moderate`: PASS, `0 vulnerabilities`
- `bash scripts/check-public-safety.sh`: PASS
- `bash scripts/validate-public-shell.sh`: PASS
- Changed-file privacy scan: PASS, no matches

## Remaining Gaps

- Public notes are used as the public-safe artifact representation; a separate R&D-style artifact table was not added.
- Manual meeting-note generation from transcript was not ported because it would require broader model/meeting-recorder behavior.
- Task/project queues in Spine remain honest empty-state placeholders.
- No note delete UI was added in this branch; memory delete continues to use Guardian confirmation.
- No automatic note-to-memory promotion beyond existing Round Table manager-summary promotion was added.

## Recommendation

Proceed to a focused dashboard/events/tasks parity branch after this one.

Recommended next branch: `port-rd-dashboard-events-tasks-parity`

Rationale: notes, history, and Spine visibility now expose the shared Workstation state coherently enough for MVP. The next useful parity slice is to decide which R&D dashboard/task/event queue concepts can be rebuilt in a public-safe local Workstation boundary without adding schedulers, connectors, tool execution, or private Guardian internals.
