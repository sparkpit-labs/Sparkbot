# Memory Governance Lifecycle Parity Audit

## A. Verdict

CURRENT_PUBLIC_MEMORY_OK_FOR_NEXT_MILESTONE

The current public Workstation memory path is good enough for the next product milestone. R&D lifecycle governance was real and useful, but its full implementation depends on heavier Guardian memory machinery: lifecycle state machines, pending approvals, scheduled hygiene, ranked retrieval metrics, conflict detection, and append-only ledger archives. Those are not required before the next public feature branch because public memory now has persistent server-side storage, visible entries, source labels, edit/correction, confirmation-backed delete, redacted recall into Chat and Round Table, and manager-summary promotion dedupe.

No product code patch was made in this audit branch.

## B. R&D Memory Lifecycle Summary

Files and docs inspected from the read-only source checkout:

- `sources/Sparkbot/docs/capabilities.md`
- `sources/Sparkbot/docs/release-notes/v1.6.45.txt`
- `sources/Sparkbot/docs/release-notes/v1.6.59.txt`
- `sources/Sparkbot/backend/app/models.py`
- `sources/Sparkbot/backend/app/crud.py`
- `sources/Sparkbot/backend/app/api/routes/chat/memory.py`
- `sources/Sparkbot/backend/app/services/guardian/memory.py`
- `sources/Sparkbot/backend/app/services/guardian/memory_hygiene.py`
- `sources/Sparkbot/backend/app/services/guardian/memory_taxonomy.py`
- `sources/Sparkbot/backend/app/services/guardian/memory_os/retrieve.py`

Lifecycle lanes found:

- `active`
- `stale`
- `archived`
- `delete_proposed`
- `soft_deleted`
- `deprecated`
- `rejected`

User-facing behavior:

- `/memory` listed active stored facts.
- `/memory clear` removed facts from normal recall through governed soft-delete.
- Memory APIs supported list, inspect, delete proposals, restore, delete, clear, query-forget, and correction.
- Inspect responses included lifecycle state, memory type, confidence, pinned flag, use counts, stale reason, and delete proposal reason.

Backend behavior:

- Durable memory records used `user_memories` with memory type, scope type/id, lifecycle state, stale/archive/delete proposal fields, retention policy, deprecated-by fields, expiration, pinned state, usage/retrieval/injection timestamps, use counts, mention counts, and soft-delete fields.
- Normal prompt memory only included active, non-expired, non-deprecated, non-soft-deleted, non-secret memory.
- Correction soft-deleted the old memory and added a new fact.
- Explicit delete soft-deleted memory rather than hard-deleting it.
- Restore returned soft-deleted memory to its prior state when tracked, otherwise archived.
- Conflicting facts could deprecate older active memories or queue conflict approvals.

Guardian/governance behavior:

- Local taxonomy classified identity, preference, project context/decision, active task, tool pattern, meeting action, relationship note, debug state, temporary context, do-not-store, secret-blocked, and unknown memory candidates.
- Secret-like and low-value candidates were blocked from durable memory and normal indexes.
- Weekly hygiene marked stale/archive candidates; monthly cleanup proposed deletion for low-risk archived memory.
- Pinned and protected types were skipped by automatic hygiene.
- Lifecycle decisions were audit logged.
- Scheduled Task Guardian hooks could run verification/evaluation and hygiene jobs.

Retriever/ranking behavior:

- R&D used a retriever interface with FTS/BM25, optional embedding search, and hybrid rerank.
- Structured recall returned score, source, confidence, timestamp, scope match, memory type, lifecycle state, and why-selected metadata.
- Archived/deep recall was available separately and was not part of normal prompt context.

Archive/restore/delete-proposal behavior:

- Archive was a non-prompt lifecycle lane, generally for stale or low-weight memory.
- Delete proposal was a review lane before soft deletion.
- Approval soft-deleted by default; rejection moved memory back to archived.
- Restore recovered soft-deleted memory.
- Hard purge was not the default.

Stale behavior:

- Stale marking was automatic and age/type driven.
- Protected types such as identity, preference, project decisions, and relationship notes were protected unless deprecated/conflicted.
- Stale, archived, delete-proposed, soft-deleted, deprecated, rejected, expired, and secret-blocked memory was excluded from normal prompt context.

Meeting artifact promotion:

- Meeting transcripts and normal room chat stayed room-scoped.
- Meeting artifacts of type notes/action-items/decisions/agenda could promote concise rollups to shared work memory.
- Duplicate rollups were skipped using fingerprints.

Sparkbot_shell and LIMA-AI-OS check:

- No direct public-safe implementation dependency was found. LIMA references are planning/test artifacts rather than the R&D memory lifecycle implementation source for this branch.

## C. Public Memory Current Assessment

Endpoints and services present:

- `GET /api/memory`
- `POST /api/memory`
- `PATCH /api/memory/{id}`
- `POST /api/memory/recall`
- `DELETE /api/memory/{id}` with server-side Guardian confirmation
- Chat memory save and recall
- Round Table memory recall
- Workstation state aggregation

Storage/persistence behavior:

- Public memory persists server-side in the shared Workstation SQLite store.
- Memory entries include content, memory type, source surface, source id, actor, tags, created timestamp, and updated timestamp.
- Browser storage is not the source of truth.

Recall behavior:

- Recall uses simple local text/tag matching against persistent memory.
- Chat and provider-backed Round Table receive a small redacted, source-labeled context block.
- Deterministic Round Table fallback remains unchanged and still recalls counts/context safely.
- Ranked retrieval is not present.

Source metadata behavior:

- Source surface/source id/actor/tags are stored directly.
- Seat/agent context for manager-summary memory is recoverable through tags such as `seat:1` and `agent:meetings_manager`.
- Round Table turns, assignments, summaries, and notes retain session/room/seat/agent links separately.

Edit/delete behavior:

- Edit is available through `PATCH /api/memory/{id}`.
- Delete requires a server-side confirmation and then hard-deletes the memory row.
- No public restore endpoint exists.
- No archive/stale/delete-proposal lane exists.

Manager-summary promotion behavior:

- Manager summaries promote one `manager_summary` memory entry at wrap-up only.
- The entry is source-labeled to the Round Table session and tagged with room, manager seat, and manager agent.
- Rerun/idempotency tests verify duplicate manager-summary memory is not created.
- Per-turn notes/memory promotion were not added.

Redaction behavior:

- Public memory now redacts sensitive-looking text at write/read/prompt boundaries across memory, notes, chat messages, rooms, sessions, turns, summaries, events, confirmations, and context injection.
- Model-call events do not store prompts, outputs, or provider secrets.

Event logging behavior:

- Memory save/update/delete events are logged with metadata that excludes raw content and secrets.
- Round Table context recall and summary events include counts and IDs, not prompt/output payloads.
- Provider model-call events log status/count/routing metadata, not prompt text or model text.

Current risk assessment:

- Over-retention risk: moderate but acceptable for local MVP because entries are visible, editable, deletable, source-labeled, and redacted.
- Incorrect deletion risk: low to moderate because delete is hard delete, but requires server confirmation and visible memory id/path. Restore would improve operator recovery but is not blocking.
- Recall quality risk: acceptable for MVP. Simple recall may miss nuanced context, but it is safer and easier to reason about than prematurely porting R&D hybrid retrieval.

## D. Gap Classification

| Missing R&D behavior | Classification | Decision |
| --- | --- | --- |
| Lifecycle states: active/stale/archived/delete-proposed/soft-deleted/deprecated/rejected | DEFER_NOT_BLOCKING | Useful later, not needed before next feature because public memory is visible/editable/deletable and local. |
| Soft delete instead of hard delete | PORT_NOW_SAFE for a later small branch | Safe and useful, but not required in this audit branch. Best as a narrow patch when product wants restore. |
| Restore soft-deleted memory | DEFER_NOT_BLOCKING | Should accompany soft delete if added; not needed immediately. |
| Delete proposal lane | DEFER_PRIVATE_OR_COMPLEX | R&D proposal flow tied to pending approvals and hygiene jobs. Public already has explicit confirmation for delete. |
| Stale/archive hygiene jobs | DEFER_PRIVATE_OR_COMPLEX | Depends on schedulers/background jobs, which are out of scope. Manual archive could be considered later. |
| Pinned/protected memory types | DEFER_NOT_BLOCKING | Valuable once archive/stale automation exists. Not needed without automatic cleanup. |
| Memory taxonomy/classification | DEFER_NOT_BLOCKING | Useful for quality and retention policy, but current `memory_type` is operator/provenance supplied and sufficient for MVP. |
| Conflict detection/deprecation | DEFER_PRIVATE_OR_COMPLEX | Depends on user/account scopes and approval queues; too much for this public slice. |
| Pending approval integration | DEFER_PRIVATE_OR_COMPLEX | Broader Guardian behavior; not needed for current public memory MVP. |
| Ranked FTS/BM25/hybrid retrieval | DEFER_NOT_BLOCKING | Better recall quality later; simple safe recall is acceptable now. |
| Retrieval metrics and eval jobs | DEFER_PRIVATE_OR_COMPLEX | Depends on scheduled evaluation and metrics stack. |
| Ledger archive/rotation | UNSAFE_FOR_PUBLIC_NOW | Adds archive files, rotation policy, and possible retention confusion without clear public UX. |
| Shared work memory rollup fingerprinting | PORT_NOW_SAFE already partly done | Public manager-summary promotion dedupes by session/type; broader artifact fingerprinting can wait. |
| Memory wipe/reset | PORT_NOW_SAFE for a later small branch | Public has delete one-at-a-time; a full wipe/reset endpoint may be useful but needs clear confirmation UX. |
| Memory export | DEFER_NOT_BLOCKING | Useful for transparency but not required before the next feature branch. |

## E. Product Recommendation

Recommended next branch: `port-rd-notes-history-spine-polish`

Rationale: public memory recall is now safe enough for the next milestone. The next highest-leverage Workstation improvement is notes/history/spine polish: make saved notes, manager summaries, memory entries, chat history, Round Table artifacts, and event logs feel like one coherent Workstation history surface.

Do not start full R&D lifecycle port yet. If memory lifecycle becomes the next priority, use a small branch scoped to manual soft-delete/restore only, without scheduled hygiene, delete-proposal automation, or ranked retrieval.

## F. Safety Recommendation

Explicit archive instead of hard delete:

- Not needed now. Consider manual archive later if users need non-destructive removal from recall.

Restore:

- Not needed now. Restore should be paired with a future soft-delete patch.

Stale marking:

- Defer. Automatic stale marking implies retention policy, jobs, timestamps, and user education.

Delete proposal/confirmation:

- Current server-side confirmation is enough now. R&D delete proposals can wait.

Memory export:

- Defer. Useful for transparency but not blocking.

Memory wipe/reset:

- Consider as a later small safety/UX branch with explicit server confirmation.

Stronger redaction:

- Current redaction is adequate for the next milestone. Continue testing any new memory source for no secrets in API responses, events, frontend, prompt context, and reports.

User-facing memory visibility warnings:

- Add later if the memory UI grows. Current UI already shows entries and delete controls; broader warnings can be part of notes/history/spine polish.

## Validation Results

Validation was run on this audit branch after the report-only commit was prepared:

- `git diff --check`: PASS
- Backend tests: PASS, `50 passed`
- Frontend tests: PASS, `9 passed`
- Frontend build: PASS
- `npm audit --audit-level=moderate`: PASS, `0 vulnerabilities`
- `bash scripts/check-public-safety.sh`: PASS
- `bash scripts/validate-public-shell.sh`: PASS
- Changed-file privacy scan: PASS, no matches

## Remaining Warnings

- Public delete is currently hard delete after confirmation, not soft delete. This is acceptable for the next milestone but should be revisited before any heavier autonomous memory promotion.
- Public recall is simple keyword/tag matching, not ranked FTS/hybrid retrieval. This is acceptable for MVP but may miss nuanced context.
- Public memory lacks lifecycle state visibility. Avoid automatic stale/archive/delete behavior until the UI and backend lifecycle model are explicitly designed.

## Final Decision

Current public memory is good enough for the next milestone. Defer rich R&D lifecycle governance. Port only manual soft-delete/restore later if memory recovery becomes product-critical.
