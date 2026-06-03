# Round Table Workstation Integration Audit

## Branch and Commit Audited

- Audit branch: `audit-roundtable-workstation-integration`
- Integration branch audited: `port-rd-roundtable-workstation-integration`
- Commit audited: `0a480e45ab33d59ab18ff1733d6b19dfb2f2d250`

## What Currently Works

- Round Table sessions can be created through backend routes.
- Session creation creates or reuses a shared Workstation room.
- Persisted Workstation seats populate the meeting room.
- Seat 1 is shown and stored as the Meeting Manager.
- The provider-safe meeting flow runs deterministically: first pass, manager assessment, assignments, second pass, and manager wrap-up.
- Assignments are linked to second-pass response turns.
- The manager wrap-up creates one summary and one linked wrap-up note.
- Round Table events appear in the shared Spine/event log.
- Restart-safe reads restore sessions, turns, assignments, summaries, and wrap-up notes from the shared store.

## Backend-Backed State

The following Round Table state is backend-backed through the shared Workstation store:

- rooms and room participants
- seats
- `roundtable_sessions`
- `roundtable_turns`
- `roundtable_assignments`
- `roundtable_summaries`
- wrap-up note links
- shared memory and note recall
- shared events
- Guardian block records
- dashboard counters

No separate Round Table state system was found.

## Frontend-Only State

Frontend-only state is limited to loading state, form drafts, selected API responses, busy flags, status messages, and error messages. These are transient UI concerns.

The audit added a frontend test to confirm the Round Table route does not write persistent meeting state to browser storage.

## Provider-Safe, Stubbed, and Deferred

Provider-safe behavior is clearly active for deterministic local meeting turns. The UI and docs label the current path as provider-safe and local.

Still deferred:

- real provider/model execution
- live model-seat responses
- connector sends or external delivery
- scheduled/background work
- file/process/shell/terminal execution
- device actions

## Seat 1 Meeting Manager Flow Assessment

Seat 1 is coherent as the Meeting Manager. The backend normalizes Seat 1 to `meeting_manager`, the UI labels Seat 1 as Meeting Manager, and tests now assert manager assessment and manager summary turns are both created by Seat 1.

The deterministic sequence is narrow and testable:

1. Seven participant first-pass turns.
2. One Seat 1 manager assessment.
3. Seven assignments.
4. Seven participant second-pass turns linked to assignments.
5. One Seat 1 manager summary.

## Assignment, Summary, and Wrap-Up Note Assessment

Assignments persist with status and response-turn links. Summaries persist separately and link to the wrap-up note. Notes are not generated after every turn.

The audit hardened tests to assert:

- exact turn order and turn indexes
- assignment response links match second-pass turns
- one summary and one wrap-up note
- rerunning a complete session does not duplicate turns, assignments, summaries, or notes

## Spine/Event Logging Assessment

Round Table writes useful shared event entries for session creation, context recall, turns, assignments, summaries, note save, and Guardian blocks. Sensitive-looking payload fields are redacted before persistence. Existing and hardened tests assert redaction for nested payload values on Round Table session-created events.

## Guardian Enforcement Summary

Guardian behavior remains fail-closed for privileged Round Table requests. A blocked request marks the session blocked and writes a Guardian block event. It does not create turns, assignments, summaries, or notes.

The audit hardened coverage for multiple protected categories: external sends, connector actions, file mutation requests, process actions, scheduled work, and device actions.

## Public Safety Summary

No real provider execution, live connector path, scheduler, file/process execution, terminal execution, device action, secrets, private source names, private domains, or local personal paths were added. Public copy remains scoped to what works today.

## Product-Shape Risks Found

- P1_POLISH: Workstation now embeds a full Round Table surface. It is coherent, but future UI polish should keep Workstation scannable as more room history accumulates.
- P1_POLISH: Deterministic local turns prove the shape, not reasoning quality. Provider execution needs separate safety and error-handling work.
- P2_LATER: The direct `/roundtable` route is useful, but Workstation should remain the primary operating-floor context.

No P0 blockers were found.

## Fixes Made

- Hardened backend tests for exact phase order, manager role, turn indexes, assignment response links, idempotent reruns, and no duplicate notes.
- Added blocked-category backend coverage for protected Round Table requests.
- Added frontend test coverage that Round Table does not persist meeting state to browser storage.
- Added a Round Table persistence contract section to the architecture boundary docs.

## Remaining Blockers

Before real provider/model execution:

- define a narrow provider-call contract
- keep provider keys server-side only
- add no-secret-response tests
- add provider error and timeout handling tests
- define how model output that asks for protected actions is routed through Guardian
- audit provider execution after it lands

## Recommendation

Proceed to a narrow provider/model execution slice after this audit branch is validated and merged. The recommended next branch is `port-narrow-provider-model-execution`.
