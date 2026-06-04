# Agents Wing Round Table Provider Integration Audit

- Verdict: `PASS_WITH_WARNINGS`
- Audit branch: `audit-agents-wing-roundtable-provider-integration`
- Base commit: `d38717edb3ed8e7a8be4556e0270dddf6768bce8`
- Provider branch pushed: `yes`, `port-rd-roundtable-provider-model-execution` pushed to `origin`
- Scope: targeted Agents Wing -> seat assignment -> Round Table provider execution audit and hardening

## Primary Answer

Agents Wing agents now work correctly inside provider-backed Round Table meetings for the public implementation path.

The audited path creates and edits a custom agent server-side, assigns that agent to a persisted Round Table seat, resolves provider/model routing from the assigned agent when the seat uses the default route, includes the assigned agent identity, description, and instructions in provider-backed Round Table prompt context, and persists turns/assignments with recoverable seat and agent links.

Seat name/role remains distinct from agent identity/instructions. Seat 1 remains the Meeting Manager for manager assessment and manager summary unless the persisted seat state is explicitly changed through supported seat state.

## R&D Reference Files Inspected

- `sources/Sparkbot/frontend/src/lib/workstationMeeting.ts`
  - `prepareMeetingSeats()`
  - `ensureMeetingSeatAgents()`
  - `ensureInviteAgentRoutes()`
  - `ensureMeetingAgentOverrides()`
  - `buildCustomSeatSystemPrompt()`
  - meeting manifest participant handling
- `sources/Sparkbot/frontend/src/pages/MeetingRoomPage.tsx`
  - `prepareMeetingSeats(seatedParticipants)` before meeting stream dispatch
  - participant handle derivation from seated agents
- `sources/Sparkbot/docs/architecture/roundtable_meeting_flow_v1.6.60.md`
  - Seat 1 Meeting Manager role
  - first pass, manager assessment, assignments, assigned work pass, manager summary
  - manual notes behavior
  - provider readiness limited to assigned seats

## Public Files Inspected

- `backend/app/api/command_center.py`
- `backend/app/api/workstation.py`
- `backend/app/services/model_execution.py`
- `backend/app/services/workstation_store.py`
- `backend/tests/test_command_center.py`
- `backend/tests/test_roundtable_workstation_integration.py`
- `frontend/src/components/CommandCenter.tsx`
- `frontend/src/components/RoundTableRoom.tsx`
- `frontend/src/components/WorkstationFloor.tsx`
- `frontend/src/api.ts`
- `frontend/src/App.test.tsx`
- `frontend/src/styles.css`
- `docs/audits/ROUNDTABLE_PROVIDER_MODEL_EXECUTION_REPORT.md`
- `docs/audits/ROUNDTABLE_WORKSTATION_INTEGRATION_AUDIT.md`

## Agents Wing Data Flow

Custom agents are backend-backed through Command Center config. `POST /api/v1/chat/agents` creates a slug, label, description, and `system_prompt`. The audit patch now persists the submitted instructions instead of dropping them.

Custom agent edits are backend-backed through `PATCH /api/v1/chat/agents/{agent_name}`. Packaged agents remain read-only in this public slice. Sensitive-looking text is redacted before persistence and before API responses. Agent create/update events store only the agent slug, not instructions or prompt text.

The frontend Agents Wing now treats description/instruction fields as editable drafts and saves them through the backend patch route. Browser state is transient form state only.

## Seat Assignment Data Flow

Seats remain SQLite-backed through `PATCH /api/seats/{seat_index}` and `GET /api/seats`. Round Table session creation copies current persisted seats into room participants. Seat 1 is normalized to the `meeting_manager` role when Round Table participants are built.

Agent/provider/model overrides remain server-backed through `/api/v1/chat/models/config`. When a seat uses the default route, the Round Table provider path now resolves the assigned agent override route/model before dispatch.

## Round Table Prompt And Context Behavior

Provider-backed Round Table messages now include:

- assigned agent identity label and slug
- assigned agent description
- assigned agent instructions
- seat label as a separate field
- seat role as a separate field
- assigned agent as a separate field in the user prompt

This means Seat 2 assigned to `risk_lens` is prompted as Seat 2 with the Risk Lens identity and instructions, while Seat 1 manager prompts remain Meetings Manager prompts.

Provider execution remains text-only. The system prompt continues to prohibit connector operations, external delivery, file/process operations, scheduler work, terminal work, device control, and protected work without a Guardian-confirmed backend route. Model output is still checked before persistence.

## Persistence Behavior

Provider-backed turns persist:

- `seat_index`
- `agent` slug
- `role`
- `provider`
- `model`
- safe metadata including `agent_name`, `agent_label`, and `agent_instructions_present`

Provider-backed turns do not persist prompt text, agent instructions, provider headers, provider credentials, or raw provider payloads.

Assignments persist seat index, assigned agent slug, instruction, status, and response turn link. Second-pass turns link back to their assignment. Manager assessment and manager summary remain Seat 1 / Meetings Manager turns. The manager summary creates the single wrap-up note; per-turn notes are not generated.

Rerunning a complete, blocked, or partially persisted session remains idempotent and does not duplicate turns, assignments, summaries, or notes.

## Tests Added Or Strengthened

- `backend/tests/test_command_center.py`
  - custom agent create persists description and instructions server-side
  - custom agent update persists description and instructions server-side
  - sensitive-looking custom agent text is redacted
  - packaged agent edit attempts fail
  - create/update events do not store instructions or sensitive values
- `backend/tests/test_roundtable_workstation_integration.py`
  - custom agent assigned to Seat 2 uses assigned agent identity/instructions in first-pass prompt
  - Seat 2 default route resolves provider/model from the assigned agent override
  - Meeting Manager prompts remain Seat 1 / Meetings Manager
  - second-pass prompt uses the assigned agent and seat context
  - persisted turns include correct seat/agent links and safe agent metadata
  - assignments preserve assigned seat/agent roles and response links
  - restart readback restores agent, seat, session, turn, assignment, summary, and note links
  - rerun idempotency does not duplicate agent-linked data
  - model-call events do not store prompts, model output text, instructions, or credentials
- `frontend/src/App.test.tsx`
  - Command Center / Agents Wing does not persist agent or seat state to browser storage

Existing tests still cover deterministic fallback mode, protected request blocks before provider dispatch, protected model output blocks before persistence, no per-turn notes, no duplicate rerun artifacts, provider-secret event redaction, frontend route rendering, and Round Table browser-storage behavior.

## Patches Made

- Added custom agent update support in `backend/app/api/command_center.py`.
- Persisted custom agent `system_prompt` on create and update.
- Normalized custom agent records so older custom agents are editable in the public UI.
- Redacted sensitive-looking custom agent description/instruction text before persistence and API echo.
- Added Round Table agent-context resolution in `backend/app/api/workstation.py`.
- Updated Round Table route resolution to honor assigned agent overrides when the seat uses the default route.
- Added assigned agent identity, description, and instructions to provider-backed Round Table messages.
- Added safe agent metadata to persisted provider-backed turns and model-call event metadata.
- Added frontend API helper and UI controls for editing custom agent profiles server-side.
- Added frontend browser-storage test coverage for Agents Wing and seats.

## Validation Results

- `git diff --check`: pass
- `.venv-local/bin/pytest backend/tests/test_command_center.py backend/tests/test_roundtable_workstation_integration.py -q`: 12 passed, 1 existing Starlette/httpx deprecation warning
- `.venv-local/bin/pytest backend/tests -q`: 44 passed, 1 existing Starlette/httpx deprecation warning
- `npm test -- --run`: 8 passed
- `npm run build`: pass
- `npm audit --audit-level=moderate`: 0 vulnerabilities
- `bash scripts/check-public-safety.sh`: pass
- `bash scripts/validate-public-shell.sh`: pass; backend 44 passed, frontend 8 passed, npm audit 0 vulnerabilities, build passed
- Manual HTTP route checks on isolated current-branch servers: `/`, `/spine`, `/controls`, `/command-center`, `/workstation`, `/chat`, and `/roundtable` returned HTTP 200
- Manual backend health check on isolated current-branch backend: `/health` returned `ok`
- Manual API smoke on isolated current-branch backend: custom agent create/edit, Seat 2 assignment, deterministic Round Table run, and seat-agent links passed
- Manual restart readback on isolated current-branch backend: custom agent profile, Seat 2 assignment, and Round Table artifacts persisted

## Remaining Warnings And Gaps

- The R&D implementation has a dedicated invite-route endpoint for custom meeting agents. The public slice uses Command Center `agent_overrides` as the server-backed equivalent route mechanism. That is sufficient for the current public UI path, but a dedicated invite-route compatibility endpoint should be considered only if future public UI code calls that R&D route directly.
- Browser-click UI e2e was not run. Manual checks were HTTP/API based, with frontend tests covering route rendering and browser-storage behavior.
- Protected-action detection remains phrase based. This is acceptable for this public slice because no connector, file/process, terminal, scheduler, background worker, browser/device automation, or tool execution path exists.

## Verdict

`PASS_WITH_WARNINGS`.

The core Agents Wing -> seat assignment -> Round Table provider execution path is fixed and covered. Assigned agent identity/instructions are used correctly in provider-backed Round Table prompts. Seat-agent links persist. Meeting Manager remains Seat 1. Deterministic fallback remains intact. Provider/model execution remains text-only and fail-closed for protected input/output.

## Recommendation

Continue after merging this audit hardening branch. If future public UI work needs R&D invite-route parity, do that as a narrow compatibility branch before adding broader Round Table features.

Recommended next branch:

`port-rd-agent-invite-route-parity`
