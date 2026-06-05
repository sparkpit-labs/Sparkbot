# Dashboard, Events, And Tasks Parity Report

## Branch And Base

- Branch: `port-rd-dashboard-events-tasks-parity`
- Base branch: `port-rd-notes-history-spine-polish`
- Base commit: `cd93fc3c25ea082900acd36e9d948d724ed79aaf`

## R&D Files And Docs Inspected

Read-only R&D source/docs inspected locally and by sidecar audit:

- `sources/Sparkbot/docs/capabilities.md`
- `sources/Sparkbot/docs/guardian-spine.md`
- `sources/Sparkbot/backend/app/models.py`
- `sources/Sparkbot/backend/app/crud.py`
- `sources/Sparkbot/backend/app/main.py`
- `sources/Sparkbot/backend/app/api/routes/chat/dashboard.py`
- `sources/Sparkbot/backend/app/api/routes/chat/tasks.py`
- `sources/Sparkbot/backend/app/api/routes/chat/guardian.py`
- `sources/Sparkbot/backend/app/api/routes/chat/spine.py`
- `sources/Sparkbot/backend/app/api/routes/chat/workstation.py`
- `sources/Sparkbot/backend/app/api/routes/chat/projects.py`
- `sources/Sparkbot/backend/app/api/routes/chat/audit.py`
- `sources/Sparkbot/backend/app/services/guardian/spine.py`
- `sources/Sparkbot/backend/app/services/guardian/task_guardian.py`
- `sources/Sparkbot/backend/app/services/guardian/task_master_adapter.py`
- `sources/Sparkbot/frontend/src/components/CommandCenter/OperationalPanels.tsx`
- `sources/Sparkbot/frontend/src/components/CommandCenter/SetupPanels.tsx`
- `sources/Sparkbot/frontend/src/lib/spine.ts`

R&D behavior summary:

- Dashboard summary counted rooms, open tasks, due tasks, reminders, pending approvals, Guardian jobs, meeting artifacts, and model-routing status.
- Chat room tasks were durable records with create/list/update/delete APIs and `open`/`done` lifecycle states.
- Guardian Spine had richer canonical task/event/project/approval/handoff tables and operator queues for open, blocked, approval waiting, stale, orphaned, missing-source, missing-project, resurfaced, and executive-directive work.
- Producer registry exposed safe subsystem metadata such as task master, memory, approval, meeting, room lifecycle, worker, and Task Guardian producers.
- Task Guardian supported job records, pause/resume, manual run, write-mode status/toggle, task run history, and selected write tools behind Guardian policy.
- R&D scheduler, manual run, write-mode execution, connector sends, approval resume paths, project executive mutations, and private Guardian internals are not public-safe for this branch.

## Dashboard Parity Restored

Public dashboard counters now include real shared-store task state:

- total task records
- open task records
- paused task records
- done task records
- canceled task records
- blocked task records
- task history count
- task execution enabled flag, always `false`

Updated surfaces:

- `GET /api/workstation/state`
- `GET /api/workstation/history`
- `GET /api/v1/chat/dashboard/summary`
- Workstation Floor counters
- Command Center Operations counters
- Spine counters

No fake counters were added. Scheduler/reminder counts remain disabled or zero because no public-safe scheduler was added.

## Event And Producer Parity Restored

Added safe producer metadata:

- `WorkstationStore.event_producers()`
- `GET /api/events/producers`
- `GET /api/v1/chat/spine/operator/producers` now reads the shared producer metadata
- `GET /api/workstation/history` includes producer metadata for the Spine UI

Producer records include subsystem, description, event types, event count, and last event timestamp. They do not expose event payloads, prompts, outputs, headers, request bodies, response bodies, credentials, or secrets.

Event visibility remains redacted through the existing payload sanitizer. Task state changes emit safe `task.*` events. Disabled task execution emits `guardian.action_blocked` with safe metadata only.

## Task Record And History Behavior Added

Added shared SQLite tables:

- `tasks`
- `task_history`

Added public-safe task APIs:

- `GET /api/tasks`
- `POST /api/tasks`
- `GET /api/tasks/{task_id}`
- `PATCH /api/tasks/{task_id}`
- `GET /api/tasks/{task_id}/history`
- `POST /api/tasks/{task_id}/pause`
- `POST /api/tasks/{task_id}/resume`
- `POST /api/tasks/{task_id}/done`
- `POST /api/tasks/{task_id}/cancel`

Task records support state-only lifecycle values:

- `open`
- `paused`
- `done`
- `canceled`
- `blocked`

Task records include source metadata:

- surface
- source id
- actor
- tags
- metadata
- created timestamp
- updated timestamp

Task title, notes, tags, metadata, history notes, API responses, events, and history aggregate responses use existing redaction paths.

## Task Guardian Visible State

Public Task Guardian visible state was restored as local task/dashboard/queue visibility only:

- Workstation Floor now has a manual task record panel.
- Command Center Task Guardian panel shows record/open/paused counts and disabled controls.
- Spine shows task queues backed by local task records and Guardian confirmations.
- Run and write-mode buttons are visible but disabled in frontend surfaces.
- Backend run/write-mode endpoints exist only to fail closed and log safe blocked events.

Private Task Guardian internals remain deferred:

- no scheduler
- no automatic runner
- no connector write tools
- no manual run execution
- no write-mode toggle
- no approval resume path
- no private Guardian Spine internals

## Disabled And Fail-Closed Operations

Added fail-closed routes:

- `POST /api/tasks/{task_id}/run`
- `POST /api/tasks/{task_id}/write-mode`

Behavior:

- returns `403`
- does not execute tools
- does not schedule work
- does not send externally
- does not mutate files/processes/devices
- writes `task.execution_blocked` history
- writes `guardian.action_blocked` safe event metadata

## Storage And Persistence Behavior

Task records and task history persist server-side in the shared Workstation SQLite store. Browser localStorage is not used as source of truth.

`GET /api/workstation/history` now includes:

- task items
- task counts by status
- recent task history
- execution enabled flag
- producer metadata

Task records persist across a second backend client/readback in tests.

## Frontend Panels Changed

Changed:

- `frontend/src/api.ts`
- `frontend/src/components/WorkstationFloor.tsx`
- `frontend/src/components/SpineSurface.tsx`
- `frontend/src/components/CommandCenter.tsx`
- `frontend/src/styles.css`
- `frontend/src/App.test.tsx`

Workstation changes:

- manual task create form
- task status counters
- task list with source metadata
- state-only pause/resume/done/cancel controls
- disabled run/write-mode controls

Spine changes:

- task queue counts use backend task state
- task record list in Spine queues panel
- event group labels include task events
- producer metadata panel

Command Center changes:

- operations counters include task records/open tasks
- Task Guardian panel shows task state counts
- run/write-mode controls remain disabled with clear public-boundary wording

## Tests Added Or Strengthened

Backend:

- `test_task_records_dashboard_spine_and_execution_fail_closed`
  - task create/list/read/update lifecycle
  - pause/resume/done/cancel as state-only operations
  - task history events
  - dashboard task counters
  - Spine task queues
  - producer metadata
  - run/write-mode fail closed
  - blocked execution events
  - task records in Workstation history
  - persistence after second client/readback
  - no secrets or raw protected prompt/header metadata in responses/events/history

Frontend:

- strengthened Workstation history test to render task records
- create task uses backend `POST /api/tasks`
- pause uses backend `POST /api/tasks/{id}/pause`
- run/write-mode buttons are disabled
- browser localStorage is not written

Existing Chat/Round Table/memory/notes tests continue to cover provider redaction, protected output blocks, deterministic fallback, manager-summary dedupe, and event payload safety.

## Validation Results

Validation run on this branch:

- `git diff --check`: PASS
- Focused backend tests (`.venv-local/bin/pytest backend/tests/test_workstation_services.py -q`): PASS, `7 passed`
- Backend tests: PASS, `52 passed`
- Frontend tests: PASS, `10 passed`
- Frontend build: PASS
- `npm audit --audit-level=moderate`: PASS, `0 vulnerabilities`
- `bash scripts/check-public-safety.sh`: PASS
- `bash scripts/validate-public-shell.sh`: PASS
- Changed-file privacy scan: PASS, expected provider env-name references only; no private references or concrete credentials

## Manual Smoke Checks

- Frontend routes returned HTTP 200: `/`, `/spine`, `/controls`, `/command-center`, `/workstation`, `/chat`, `/roundtable`.
- Backend task smoke with temporary local state: create returned `open`, pause returned `paused`, run returned `403` with disabled public-boundary message.

## Remaining Gaps And Warnings

- No scheduler, runner, connector write, or background execution was added.
- No R&D Guardian Spine project/handoff/approval tables were ported.
- Task Guardian write mode is visible only as disabled public UI and fail-closed backend behavior.
- Dashboard reminders remain deferred because they imply scheduling behavior.
- Approval approve/deny resume paths remain deferred because they can execute tool actions in R&D.
- Manual browser HTTP route checks were not run in this branch.

## Recommendation

Proceed to a focused product polish/public-readiness branch after this one.

Recommended next branch: `audit-public-mvp-route-and-copy-readiness`

Rationale: Workstation now has coherent persistent rooms, notes, memory, Chat history, Round Table history, task records, dashboard counters, event log, producer metadata, and fail-closed Guardian visibility. The next useful slice is to audit the public MVP routes and copy for consistency, broken states, and public-boundary clarity before adding more behavior.
