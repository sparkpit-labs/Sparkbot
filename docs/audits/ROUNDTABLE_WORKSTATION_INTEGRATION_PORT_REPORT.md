# Round Table Workstation Integration Port Report

## Branch and Commit

- Branch: `port-rd-roundtable-workstation-integration`
- Base commit: `9abe903788764af467096f07227b96747edb381c`
- Implementation commit: recorded in the final branch output for this work

## Reference Behavior Ported

The public shell now has a provider-safe Round Table meeting-room foundation:

- Operator creates a room session with a task or problem statement.
- Persisted Workstation seats populate the room.
- Seat 1 is treated as the Meeting Manager.
- Other seats contribute first-pass ideas.
- Seat 1 creates an assessment.
- The manager assigns work to participant seats.
- Participant seats answer assignments in a second pass.
- Seat 1 creates a manager wrap-up and next-step plan.

This is deterministic and local. It does not call providers or execute tools.

## Backend-Backed State

Round Table uses the same shared Workstation store as Chat, Workstation, Command Center, Spine, memory, notes, rooms, seats, events, and Guardian confirmations. New persisted tables cover:

- `roundtable_sessions`
- `roundtable_turns`
- `roundtable_assignments`
- `roundtable_summaries`

The shared Workstation state endpoint now reports Round Table sessions, turns, assignments, summaries, and dashboard counters.

## Provider-Safe and Deferred

Provider-safe now works:

- Session creation
- Room participant use
- First-pass turns
- Manager assessment
- Assignments
- Second-pass turns
- Manager summary
- One wrap-up note
- Spine/event logging

Still deferred:

- Real provider/model execution
- Live model-seat responses
- Connector sends or external delivery
- Scheduled or background work
- File/process/shell/terminal execution
- Device actions

## Seat 1 Meeting Manager Flow

Seat 1 is normalized as `meeting_manager` for Round Table participants. The provider-safe run path creates the flow in this order:

1. First-pass participant turns.
2. Seat 1 manager assessment.
3. Assignments for participant seats.
4. Second-pass participant answers linked to assignments.
5. Seat 1 manager summary and next-step plan.

The flow is intentionally deterministic enough to test and inspect.

## Assignments, Summaries, and Notes

Assignments persist with status and response-turn links. Summaries persist separately and link to the wrap-up note.

Notes are not generated after every turn. The current flow creates one note at manager wrap-up only, scoped to the Round Table session.

## Shared Memory, Notes, and Spine

Round Table recalls shared memory and Workstation or room notes before writing turns. It records activity in the shared event log for session creation, context recall, turns, assignments, summaries, note save, and Guardian blocks.

Sensitive-looking event payload keys continue to be redacted before persistence.

## Guardian Enforcement

Round Table does not execute destructive, external, privileged, scheduled, connector-based, file/process-related, terminal-related, or device-related requests. Matching requests fail closed, mark the session blocked, and log a `guardian.action_blocked` event.

Any future action-capable Round Table behavior must use the shared Guardian confirmation boundary before execution.

## Public Safety Summary

The branch keeps secrets server-side, adds no provider execution, adds no connectors, starts no background workers, executes no files or processes, and imports no private runtime internals. Public copy labels the current behavior as provider-safe and deferred where appropriate.

## Fixes Made

- Added shared-store Round Table persistence tables and counters.
- Added backend Round Table session list/create/get/run routes.
- Added provider-safe meeting-manager flow skeleton.
- Added Workstation-embedded Round Table UI and direct `/roundtable` route.
- Updated Command Center and Controls copy to reflect what works and what remains deferred.
- Added backend tests for persistence, events, redaction, wrap-up notes, restart-safe reads, and Guardian fail-closed behavior.
- Added frontend route tests for the Round Table surface.
- Updated public architecture and surface docs.

## Product-Shape Risks

- The deterministic local responses are useful for product shape, but they are not a substitute for real provider reasoning.
- The Workstation page now contains a full Round Table surface; future UI polish should keep it scannable without turning Workstation into another chat page.
- Real provider execution will need careful route selection, server-side secret handling, rate/error handling, event redaction, and Guardian review for protected actions.

## Remaining Blockers Before Real Provider/Model Execution

- Provider-safe integration audit.
- Narrow provider-call contract for selected model routes.
- Safe provider error handling and no-secret-response tests.
- Seat-level provider/model selection rules for Round Table.
- Explicit Guardian handling for any provider output that asks for protected actions.

## Recommendation

Proceed to `audit-roundtable-workstation-integration` next. After that audit passes, choose between a narrow provider/model execution slice and model-seat/provider configuration polish.
