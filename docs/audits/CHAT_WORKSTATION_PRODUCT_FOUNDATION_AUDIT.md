# Chat Workstation Product Foundation Audit

## Branch and commit audited

- Audit branch: `audit-chat-workstation-product-foundation`
- Completed foundation branch audited: `port-rd-chat-workstation-integration`
- Completed foundation commit audited: `0afa7bc08d9971bc5300f57f312d8f4f969f9017`

## What currently works

- Chat sessions and messages persist in the shared SQLite Workstation store.
- Chat writes shared Spine/event entries for session creation, user turns, assistant acknowledgements, and context recall.
- Chat reads shared memory and notes context and can optionally save a user message to memory.
- Chat-requested memory deletion creates a Guardian confirmation and does not delete directly.
- Unsupported privileged Chat requests fail closed and log Guardian block events.
- Workstation state includes rooms, seats, notes, memory, events, chat counters, dashboard counters, and Guardian confirmation state.
- Command Center persists model routing, model stack, local endpoint, seat routing, custom agents, guardrails, PIN, and server-side provider credentials without echoing secret values.
- Spine reads shared event history and shared dashboard counters.

## What is shared-state backed

- Chat sessions and messages
- Workstation seats
- Room foundations and room participants
- Notes
- Memory entries
- Spine/event log entries
- Guardian action confirmations
- Dashboard counters derived from the shared store
- Command Center config and server-side credential storage

## What is frontend-only

No persistent product state was found to be frontend-only. Frontend state is limited to form drafts, loading flags, selected view state, fetched API snapshots, and local error/status messages. The audit found no `localStorage` or `sessionStorage` source of truth for Chat, Workstation, memory, notes, events, rooms, seats, or Guardian state.

## What is stubbed or deferred

- Provider/model execution from Chat or seats
- Streaming model responses
- Full Round Table turn engine
- Seat 1 meeting-manager loop
- Meeting turn artifacts and assignment execution
- Connector sends and external delivery
- File/process/shell/terminal execution
- Scheduler/background workers
- Physical device control
- Full task/project queue persistence beyond current empty-state Spine queues

The current UI labels these paths as deferred, disabled, setup-only, or no-execution paths.

## Chat operator-middle-person readiness

Chat is ready as Sparkbot's operator-facing middle-person foundation, but not yet as a real model-executing assistant. It now has the correct product shape: direct operator conversation, shared context recall, memory save option, event logging, selected route visibility, and Guardian-blocked privileged requests.

The next branch can safely use Chat as the operator command channel for provider-safe Round Table setup, as long as real model/provider execution remains deferred until an explicit provider execution branch.

## Workstation separation

Risk found: `/workstation` and `/chat` previously rendered the same backend-backed Chat component, while `/`, `/controls`, and `/command-center` normalized to `/spine`. That made the product surfaces less coherent than the backend foundation.

Fix made: the frontend now has distinct public routes:

- `/workstation`: operating floor for rooms, seats, shared context, events, and Guardian confirmations
- `/chat`: direct operator conversation surface
- `/command-center`: configuration, model routing, agents, security, and Guardian settings
- `/spine`: event/history/counter surface
- `/controls`: setup/readiness and explicit capability-limit surface

## Guardian enforcement summary

Guardian currently enforces the protected memory-delete route with fail-closed authorization. Confirmations are persisted, one-time use, action-bound, source-bound, expiry-bound, and visible through shared backend state. Missing, malformed, pending, denied, expired, already-used, and mismatched confirmations are rejected and logged.

Chat does not execute privileged requests. It creates confirmation requests for memory deletion and logs unsupported privileged requests as blocked events.

## Public safety summary

- No private implementation internals were imported.
- No model/provider execution was added.
- No connectors, external sends, schedulers, shell/process/file execution, or device-control paths were added.
- Server-side provider credential handling remains server-side and does not echo saved values to the browser.
- Event payload redaction remains in the shared store for sensitive-looking keys.
- Public docs were updated to remove stale preview-only claims for Chat and Workstation.

## Product-shape risks found

| Priority | Risk | Resolution |
| --- | --- | --- |
| P1_POLISH | Chat and Workstation rendered the same surface, making Workstation look like a message box. | Added a distinct Workstation floor route backed by shared state. |
| P1_POLISH | Command Center, Spine, and Controls collapsed into one route, making roles unclear. | Added distinct Command Center, Spine, and Controls surfaces. |
| P1_POLISH | User-facing copy referenced source/port lineage and could read as internal implementation notes. | Replaced with public product copy and explicit no-execution labels. |
| P1_POLISH | Docs still described Chat and Workstation as static previews. | Updated docs to describe backend-backed current behavior and deferred paths. |
| P2_LATER | Spine task/project queues are still empty-state placeholders. | Kept visible and labeled as non-executing placeholders. |

## Fixes made

- Added `WorkstationFloor`, `SpineSurface`, and `ControlsSurface` frontend components.
- Updated routing so `/workstation`, `/chat`, `/command-center`, `/spine`, and `/controls` are distinct.
- Updated Chat metadata to mark chat turns as `surface: "chat"`.
- Expanded Chat context panel to show recent events and Guardian confirmations.
- Clarified Command Center copy around provider setup, local model checks, connector placeholders, scheduler deferral, and Token Guardian monitor mode.
- Added frontend tests for distinct route roles.
- Added backend tests for shared state aggregation and restart-safe one-time Guardian authorization.
- Added `docs/WORKSTATION_ARCHITECTURE_BOUNDARY.md` with shared-store and Guardian requirements.
- Updated current docs for Chat, Workstation, development, local smoke, and docs index.

## Remaining blockers

No blockers remain for a provider-safe Round Table integration branch.

Remaining deferred work should stay deferred until explicit branches:

- Real provider/model execution
- Full Round Table turn engine and Seat 1 manager loop
- Meeting turn persistence/artifacts beyond current room foundation
- Memory and notes edit/delete frontend polish
- Full task/project state and scheduler gates
- Connectors, external sends, file/process execution, and device-control behavior


## Validation completed

- `git diff --check`: passed
- `bash scripts/check-public-safety.sh`: passed
- `bash scripts/validate-public-shell.sh`: passed
- Backend pytest count: 22 passed, 1 warning
- Frontend test count: 5 passed
- Frontend build: passed
- `npm audit --audit-level=moderate`: 0 vulnerabilities
- Changed-file privacy scan: passed across 16 modified/new files
- Manual frontend route check: `/`, `/spine`, `/controls`, `/command-center`, `/workstation`, and `/chat` returned HTTP 200 on isolated localhost dev server
- Manual API persistence/restart check: passed for room, note, chat session, chat messages, memory count, event count, and dashboard counters after backend restart on the same temp data store

## Recommendation

PROCEED to `port-rd-roundtable-workstation-integration` before real provider/model execution.

Reason: the public differentiator is now better shaped around Workstation plus Chat plus Guardian plus Spine state. The next branch should make rooms/seats/Round Table flow work safely with provider execution still deferred, then add real provider/model calls in a later provider execution branch once the meeting flow is correct.
