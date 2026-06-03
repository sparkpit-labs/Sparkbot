# Chat Workstation Integration Port Report

## Branch

- Branch: `port-rd-chat-workstation-integration`
- Base: Guardian confirmation hardening branch at `45de6e1`
- Implementation commit: this branch commit

## What Was Ported

This branch restores the public Chat and Workstation integration as shared Workstation state rather than a separate page-local message loop. The work follows the existing R&D behavior shape: Chat is a Workstation surface, selected model route comes from Command Center and Seat 1 state, context comes from memory and notes, and all meaningful state changes write to the shared Spine event log.

Implemented pieces:

- Backend chat sessions and messages in the shared SQLite Workstation store.
- `GET /api/chat/sessions`, `POST /api/chat/sessions`, `GET /api/chat/sessions/{session_id}`, and `POST /api/chat/messages`.
- Chat session/message counters in `/api/workstation/state` and dashboard summaries.
- Chat context recall from shared memory and notes.
- Optional user-message memory save through the existing memory service.
- Shared event logging for chat session creation, user messages, assistant messages, context recall, and memory saves.
- A real `/workstation` and `/chat` frontend surface backed by the same backend store used by Command Center.
- Guardian confirmation creation for chat-requested memory deletes without executing the delete.
- Fail-closed handling for unsupported privileged chat requests; they are logged and not executed.

## Deferred Or Stubbed

These pieces intentionally remain out of scope for this branch:

- Real provider/model execution from Chat. The assistant response is a local Workstation acknowledgement that reports selected route and context counts.
- Full Round Table engine and Seat 1 meeting-manager loop.
- Connector actions, external sends, file mutation, process execution, background workers, and schedulers.
- Full task engine.
- Provider-specific streaming responses.

## Shared Memory, Notes, Spine, And Guardian Use

Chat reads relevant memory through the existing recall service, reads notes from the shared notes service, and can save a user message as memory with source metadata pointing back to the chat session. Each chat turn records events in the same event log used by Command Center, rooms, notes, memory, seats, and Guardian confirmations. Sensitive payload keys continue to be redacted by the store.

Destructive or privileged requests do not execute through Chat. A memory-delete request creates a one-time action-bound Guardian confirmation for `memory.delete`, and the memory remains intact until the existing protected memory delete endpoint receives a matching approved confirmation. Unsupported privileged requests are recorded as blocked Guardian events and remain non-executing.

## Workstation State Use

The frontend Workstation view uses `/api/workstation/state`, `/api/chat/*`, and existing note APIs. It displays selected route, shared counters, recent memory, recent notes, and active chat history from backend state. It does not use browser storage as the source of truth for sessions, messages, memory, notes, or Guardian state.

## Public Safety Summary

- No provider secrets are returned to the frontend.
- No private implementation internals were imported.
- No live connectors, external sends, process execution, or file mutation were added.
- Guardian boundaries remain fail-closed for current privileged routes.

## Remaining Blockers Before Round Table Integration

- Connect real provider calls to the selected model route under the same shared state and Guardian rules.
- Add room turn records and meeting heartbeat services before the Round Table UI is activated.
- Wire Seat 1 manager flow to rooms, notes, memory recall, and event logging.
- Define task execution boundaries before any task route can execute work.

## Recommendation

Proceed to `port-rd-roundtable-workstation-integration` only after reviewing this branch and deciding whether real provider calls should be connected first in a narrow provider execution branch.
