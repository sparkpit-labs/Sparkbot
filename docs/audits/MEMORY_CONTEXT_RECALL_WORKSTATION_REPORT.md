# Memory Context Recall Workstation Report

## Branch And Base

- Branch: `port-rd-memory-context-recall-workstation`
- Base commit: `496a2aa`
- Scope: targeted memory/context recall parity for the public Workstation.

## Source Files Inspected

R&D source references inspected from the read-only source checkout:

- `sources/Sparkbot/docs/capabilities.md`
- `sources/Sparkbot/backend/app/api/routes/chat/memory.py`
- `sources/Sparkbot/backend/app/services/guardian/memory.py`
- `sources/Sparkbot/backend/app/api/routes/chat/rooms.py`
- `sources/Sparkbot/backend/app/services/guardian/meeting_heartbeat.py`
- `sources/Sparkbot/docs/release-notes/v1.6.45.txt`
- `sources/Sparkbot/docs/release-notes/v1.6.59.txt`

Public files inspected and changed:

- `backend/app/services/workstation_store.py`
- `backend/app/api/workstation.py`
- `backend/tests/test_workstation_services.py`
- `backend/tests/test_chat_workstation_integration.py`
- `backend/tests/test_roundtable_workstation_integration.py`
- `frontend/src/api.ts`
- `frontend/src/components/ChatWorkstation.tsx`
- `frontend/src/App.test.tsx`
- `frontend/src/styles.css`

## R&D Behavior Found

R&D used a guarded memory layer with durable user memory, room memory, and shared work memory. Prompt context was built through a memory-context builder that appended learned user facts, active workflow context, shared work memory, and relevant room memory. Normal prompt assembly excluded inactive, rejected, expired, deprecated, and secret-blocked memory.

R&D memory APIs supported listing, inspection, deletion, delete proposals, restore, and correction. Chat and room flows called memory recall before model dispatch. Meeting artifact rollups could be promoted to shared work memory when they represented useful notes, decisions, action items, agenda, open questions, or next steps, while duplicate rollups were skipped.

## Public Memory Source Of Truth

The public Workstation already had a persistent SQLite-backed store for memory, notes, chat sessions, Round Table sessions, turns, assignments, summaries, and events. Browser storage is not used as the source of truth.

This branch keeps that backend store as the public-safe memory source of truth and avoids adding connectors, schedulers, background workers, tool execution, browser automation, file/process execution, or CLI-backed provider bridges.

## Public Service And Endpoints

Existing public endpoints retained:

- `GET /api/memory`
- `POST /api/memory`
- `DELETE /api/memory/{id}` with server-side confirmation
- `POST /api/memory/recall`

Added endpoint:

- `PATCH /api/memory/{id}` for practical edit/correction behavior.

Added shared backend behavior:

- source-labeled recall formatter shared by Chat and Round Table provider prompt construction
- memory/note/room/session/turn/summary/event/confirmation readback redaction
- memory and note write redaction
- manager summary to memory linkage at wrap-up only
- duplicate avoidance for Round Table manager-summary memory on rerun

## Storage And Persistence

Memory entries persist in `memory_entries` with:

- content
- memory type
- source surface
- source id
- actor
- tags
- timestamps

Round Table manager summaries now create one `manager_summary` memory entry at wrap-up with `source_surface=roundtable`, `source_id=<session_id>`, and tags including `roundtable`, `summary`, `manager_summary`, `room:<room_id>`, `seat:1`, and `agent:meetings_manager`. Rerunning a completed session does not create duplicate manager-summary memory.

## Chat Integration

Chat now recalls shared memory and notes before provider dispatch and includes a small redacted source-labeled context block in the transient model request. The context includes memory type, source surface, source id, actor, tags, and redacted content.

Chat still blocks protected input before provider dispatch and blocks protected model output before persistence. Chat model-call events continue to store counts and route metadata only, not prompts or outputs.

## Round Table Integration

Round Table provider-backed mode uses the same safe recall formatter. The provider prompt includes redacted memory and notes with source labels while preserving assigned seat agent identity/instructions, seat role/name separation, invite route behavior, and Seat 1 Meeting Manager behavior.

The deterministic fallback phase order is unchanged:

1. first pass
2. manager assessment
3. assignments
4. second pass
5. manager summary

No per-turn notes were added. Wrap-up note creation remains manager-summary only.

## Notes And History Linkage

Manager summary/wrap-up notes are now also eligible for shared recall through one linked manager-summary memory entry. Automatic memory creation is intentionally limited to the final manager summary. Ordinary notes can still be viewed and recalled; broader automatic note promotion remains deferred for a later, governed policy if needed.

## Safety And Redaction

Added redaction for sensitive-looking text in memory, notes, chat messages, room/session text, Round Table turns, summaries, event readback, confirmation prompts, and prompt context. Redaction covers key-value patterns and token-like values.

Provider secrets are not included in prompt context, events, API responses, frontend state, or logs. Model-call events continue to omit prompt bodies and model outputs. Memory recall does not execute tools or actions. Unsupported privileged requests still fail closed before provider dispatch, and protected model output still fails closed before persistence.

## UI Changes

Chat now shows recent memory entries with a server-backed delete workflow. Delete creates a server-side confirmation, then approval calls the existing memory delete endpoint. No browser storage is used.

## Tests Added Or Strengthened

Backend tests now cover:

- memory update/correction with redaction
- Chat provider prompt includes redacted recalled memory and notes
- Chat model-call events omit prompts, outputs, and credentials
- Round Table provider prompt includes redacted recalled memory and notes
- manager summary creates one source-labeled memory entry
- rerun/idempotency does not duplicate manager-summary memory
- existing protected input/output and deterministic fallback coverage remains passing

Frontend tests now cover:

- memory list renders from backend state
- memory delete uses server confirmation and delete endpoints
- browser storage is not used for memory state
- secret-like raw values are not displayed in the mocked backend-backed memory list

## Validation Results

Final validation completed before commit:

- `git diff --check`: PASS
- Backend tests, `./.venv-local/bin/pytest backend/tests -q`: PASS, `50 passed`
- Frontend tests, `npm test -- --run`: PASS, `9 passed`
- Frontend build, `npm run build`: PASS
- Dependency audit, `npm audit --audit-level=moderate`: PASS, `0 vulnerabilities`
- Public safety scan, `bash scripts/check-public-safety.sh`: PASS
- Public shell validation, `bash scripts/validate-public-shell.sh`: PASS
- Changed-file privacy scan for private source names, private domains, local paths, personal names, private IP ranges, and provider-key literals: PASS, no matches

## Remaining Gaps

- Public memory is intentionally simpler than the R&D guarded memory lifecycle. It does not implement stale/archive/delete-proposal/restore lifecycle lanes.
- Automatic promotion is limited to Round Table manager summaries. Broader automatic note/artifact promotion is deferred.
- Recall uses simple local matching rather than the R&D guarded retriever stack. This is acceptable for the public-safe slice but may need a later retrieval-quality branch.

## Verdict

PASS_WITH_WARNINGS

## Recommendation

Continue. The next branch can build on this shared Workstation memory spine. A later memory-governance branch should decide whether to add lifecycle states, restore/proposal flows, and richer retrieval ranking.
