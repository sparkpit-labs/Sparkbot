# R&D to Public Parity and Corrective Plan

Date: 2026-06-02

Scope: inspection and corrective planning only. No product runtime changes were made for this audit.

## A. Executive Summary

Public Sparkbot is currently a clean shell, not a functional reconstruction of the working R&D Sparkbot. It has a working FastAPI health endpoint, a Vite/React shell, smoke scripts, public hygiene scripts, and preview panels that honestly label missing runtime behavior. It does not yet have a real chat runtime, provider configuration flow, model routing, Round Table execution, persistence spine, memory, reminders, tool execution, Guardian confirmations, or desktop packaging wired into the public product.

The R&D Sparkbot is messy and too broad to port wholesale, but it is much closer to the intended product. It contains real FastAPI chat routes, streaming model calls, provider/model routing, Ollama/local model support, SQLModel persistence, memory/task/reminder APIs, Guardian policy and confirmation paths, Round Table launch code, Meeting Manager behavior, meeting artifacts, and Tauri packaging. Some of that code is unsafe or too private/broad for direct public use, especially connector/tool execution and server operations. The product behavior, however, is recoverable.

Public Sparkbot should not be released next as a functional Sparkbot. It can only be described as a shell baseline until a new user can configure a provider or local endpoint, chat with Sparkbot, start a Round Table, see seats respond, receive Meeting Manager assignments and a final summary, and reopen notes/history after restart.

The fastest credible path is to stop preview/docs/packaging work and rebuild functional parity in narrow vertical slices, starting with `public-runtime-chat-provider-slice`. Do not wait for LIMA-AI-OS to become the runtime kernel. LIMA-AI-OS should remain a future contract/kernel layer while public Sparkbot restores a native MVP runtime from R&D behavior.

## B. Repo Inventory

| Repo | Remote | Current branch | Current commit | Clean/dirty status at inspection | Relevant tags | Role |
| --- | --- | --- | --- | --- | --- | --- |
| R&D Sparkbot | Internal R&D GitHub remote, redacted in this public-safe audit artifact | `main` | `9ebedb23548d16fd085e5d959d5c82fa0148a9ae` | Clean | R&D/source tags include desktop/runtime version history such as `v1.6.81` lineage | Source of truth for working behavior |
| Public Sparkbot | `git@github.com:sparkpit-labs/Sparkbot.git` | `audit-rd-to-public-parity-corrective-plan` from `main` | base `6158669778b44b8bea03aff89310095fef4b1de2` | Clean before this report | Remote public tags: `public-v1-shell-baseline-0`, `public-v1-visitor-docs-polish-0`, `public-v1-local-smoke-ready-0` | Public clean target |
| LIMA-AI-OS | Internal R&D GitHub remote, redacted in this public-safe audit artifact | `main` | `8328bfe99452a32d54e6659f0e099e450699d901` | Clean | Phase 0 contract/kernel checkpoint history | Future kernel/contracts layer |
| Sparkbot_shell | Internal R&D GitHub remote, redacted in this public-safe audit artifact | `main` | `26c501347010b842fc15eabe70e23ea6ae3751ac` | Clean | Shell extraction history | Historical/support shell reference |

## C. Feature Parity Matrix

| Feature area | R&D status | R&D evidence/files/routes/components | Public repo status | Public evidence/files/routes/components | Gap | Classification | Recommended next action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Main chat runtime | Working/partial | `backend/app/api/routes/chat/rooms.py`; `frontend/src/pages/SparkbotDmPage.tsx`; streaming and non-streaming message paths | Preview only | `frontend/src/components/ChatShellPreview.tsx`; `README.md` says no model calls | Public has no real send/receive loop | REBUILD_FROM_BEHAVIOR | Build minimal persisted chat loop with one streaming backend route and one frontend chat surface |
| Backend chat endpoint/API | Working/partial | `POST /api/v1/chat/rooms/{room_id}/messages`; `POST /messages/stream`; artifacts routes in `rooms.py`; routers aggregated in `backend/app/api/main.py` | Missing | `backend/app/main.py` only includes health router; `backend/app/api/health.py` | No chat routes or room/message API | REBUILD_FROM_BEHAVIOR | Recreate simplified room/message/stream API from R&D route shape |
| Frontend chat UI wiring | Working/partial | `SparkbotDmPage.tsx` loads bootstrap, rooms, messages, model config, memory, tasks, reminders; streams SSE | Preview only | `ChatShellPreview.tsx` disabled composer; `frontend/src/App.tsx` shell | UI cannot send messages or display live model output | REBUILD_FROM_BEHAVIOR | Build functional chat panel before more Workstation polish |
| Provider setup | Working/partial | `frontend/src/components/CommandCenter/SetupPanels.tsx`; `frontend/src/lib/sparkbotControls.ts`; `GET/POST /models/config` in `model.py` | Preview only | `ProviderSetupPreview.tsx`; docs say no key fields/save/test | Public cannot configure providers | REBUILD_FROM_BEHAVIOR | Rebuild a small provider settings panel and backend config API |
| Provider credential storage/validation | Working/unsafe breadth | `model.py` `_write_env_updates`, `_apply_env_updates`, vault credential helper, provider credential env mapping | Missing | No public config store or validation route | No credential persistence or test call | REBUILD_FROM_BEHAVIOR | Use public-safe local settings storage; do not port vault/private paths wholesale |
| Model selector | Working/partial | `GET /model`; `POST /model`; `GET /models`; `SparkbotDmPage.tsx` model controls | Preview only | Provider/model panels say planned | No selectable active model | REBUILD_FROM_BEHAVIOR | Add model dropdown backed by provider catalog and persisted default |
| Model routing | Working/partial | `llm.py` `AVAILABLE_MODELS`, `get_model_stack`, `set_model_stack`, `get_agent_route_context`, fallback helpers | Missing | No model routing code | No route from request to provider/model | REBUILD_FROM_BEHAVIOR | Recreate small routing layer for OpenAI/OpenRouter/Ollama first |
| Local model support | Working/partial | `llm.py` Ollama constants and `get_ollama_status`; `model.py` `GET /ollama/status`; frontend provider readiness checks | Missing | No local endpoint config | No local/Ollama path | PORT_DIRECTLY | Port the Ollama status pattern and add local endpoint as first-class provider |
| Round Table runtime | Working/partial | `frontend/src/lib/workstationMeeting.ts`; `frontend/src/pages/MeetingRoomPage.tsx`; `backend/app/services/guardian/meeting_heartbeat.py` | Preview only | `RoundTablePreview.tsx`; `shellSections.ts` labels Round Table planned | No real meeting creation or seat execution | REBUILD_FROM_BEHAVIOR | Rebuild minimal meeting runtime after chat/provider slice |
| Seat turn loop | Working/partial | `MeetingRoomPage.tsx` prepares participants and streams agent events; `meeting_heartbeat.py` iterates agent messages | Missing | No seat data model or execution engine | No sequenced seat turns | REBUILD_FROM_BEHAVIOR | Implement deterministic seat loop using same provider router as chat |
| Meeting Manager / Seat 1 | Working/partial | `workstationMeeting.ts` persona says Seat 1 is meeting manager; `meeting_heartbeat.py` chair/manager flow | Missing | Round Table preview only | No manager/chair role | REBUILD_FROM_BEHAVIOR | Encode Seat 1 manager prompt and control flow in public meeting service |
| Assignment generation | Working/partial | `meeting_heartbeat.py` manager assessment and assigned work pass; notes/artifact updates | Missing | No assignments | No job assignment pass | REBUILD_FROM_BEHAVIOR | Add second-pass manager assignment after first seat responses |
| Final summary loop | Working/partial | `meeting_heartbeat.py` manager summary/refinement path; artifact generation in `rooms.py` | Missing | No final summary | No meeting conclusion output | REBUILD_FROM_BEHAVIOR | Add manager final summary/plan as acceptance gate for Round Table slice |
| Meeting notes save/edit | Working/partial | `ChatMeetingArtifact` in `backend/app/models.py`; artifact routes in `rooms.py`; `MeetingRoomPage.tsx` notes actions | Missing | Preview shell has no persistence | No meeting artifacts or notes | REBUILD_FROM_BEHAVIOR | Rebuild simple meeting notes artifact table/API and frontend editor |
| Memory/context spine | Working/partial | `backend/app/api/routes/chat/memory.py`; `UserMemory` model; Guardian memory services; memory context in meeting heartbeat | Missing | No memory API or UI | No saved/recalled context | REBUILD_FROM_BEHAVIOR | Build simple memory CRUD/context injection; defer advanced memory lifecycle |
| Persistence layer | Working/partial | `backend/app/models.py`; SQLModel entities for users, rooms, messages, tasks, reminders, memory, artifacts, audit, agents | Missing | Public backend has no DB models or migrations | No durable product state | REBUILD_FROM_BEHAVIOR | Introduce minimal SQLite-backed persistence for chat, settings, notes, memory, audit |
| Task/reminder behavior | Working/partial | `tasks.py`; `reminders.py`; `ChatTask`; `Reminder`; reminder scheduler and delivery hooks | Missing | No task/reminder routes | No reminders or task tracking | DEFER | Rebuild after chat/Round Table unless the project owner requires it for first release |
| Guardian/security confirmation behavior | Working/partial | `services/guardian/policy.py`; `rooms.py` `confirm_id` flow; audit/security routes | Preview only | `GuardianControlsPreview.tsx` says no enforcement | Public cannot distinguish preview/action or require confirmation | REBUILD_FROM_BEHAVIOR | Implement basic confirmation/audit gate before risky actions; defer advanced Guardian suite |
| Tool execution hooks | Working but unsafe breadth | `backend/app/api/routes/chat/tools.py`; Guardian tool policy; server/browser/workspace integrations | Missing | No tool executor | No tools, but broad R&D tools are too risky for public MVP | PRIVATE_ONLY | Do not port wholesale; later rebuild explicit safe tool allowlist |
| Connectors | Working/partial/unsafe | Slack, GitHub, Google, Notion, Confluence, email/calendar and other hooks in R&D routes/services | Missing | Public docs/components list connectors as future | No connector runtime | DEFER | Defer public connectors until core chat/Round Table works and provider storage policy is settled |
| Desktop/Tauri/install packaging | Working/partial | `src-tauri/`; `build-desktop.sh`; `quickstart.sh`; installer workflows | Missing/partial docs only | Public has dev scripts and release docs, no Tauri app | No desktop installable product | DEFER | Resume packaging only after real runtime loop passes release gate |
| Local smoke/dev setup | Working | R&D has quickstart/start scripts; public has validation/smoke scripts | Working for shell | `scripts/validate-public-shell.sh`; `scripts/check-public-safety.sh`; health smoke | Public smoke proves shell only | PORT_DIRECTLY | Expand smoke tests as each runtime slice lands |
| Public safety/hygiene | Risky in R&D, clean in public | R&D has private/source-specific references and broad execution hooks | Working for current shell | Public safety script passes before this internal audit report | Current public hygiene is strong, but functionality is absent | PORT_DIRECTLY | Keep hygiene gates; do not let tool/connector code bypass them |

## D. LIMA-AI-OS Reality Check

LIMA-AI-OS is best understood today as a Phase 0 contract/kernel scaffold, not a ready Sparkbot runtime. Its package metadata identifies `lima-runtime` at version `0.0.1`, and its README states that Phase 0 does not include migrated Sparkbot runtime behavior, live tool execution, production deployment wiring, credentials, real model calls, or hardware control paths.

Callable/importable pieces exist, but they are narrow and mostly non-executing:

- `lima.adapters.sparkbot_humaninput.SparkbotHumanInputAdapter` converts neutral Sparkbot-like payloads into `HumanInput` contract objects.
- `lima.kernel.intake_candidate`, `lima.kernel.candidate_status`, and `lima.kernel.runtime_state` provide candidate/status/runtime-state scaffolding.
- `lima.contracts.*` provides contract types.
- `lima.guardian.*fakes` provides test/fake Guardian behavior, not production Guardian enforcement.

LIMA-AI-OS does not currently provide a model-calling runtime, provider router, Sparkbot chat loop, Round Table execution engine, production memory manager, production Guardian decision engine, connector executor, or drop-in Sparkbot integration. It should not block the Sparkbot MVP.

Integrate now only where a contract is useful and costs almost nothing, such as shaping future human-input or Guardian event boundaries. Restore Sparkbot MVP functionality natively first, then replace or wrap those native pieces with LIMA kernel contracts later.

## E. Corrective Course Plan

### 1. `public-runtime-chat-provider-slice`

Goal: restore the smallest complete Sparkbot chat loop.

Build from R&D behavior in `rooms.py`, `llm.py`, `model.py`, and `SparkbotDmPage.tsx`, but do not port broad tool execution. Implement a minimal persisted room/message model, one backend chat endpoint, optional streaming, provider/model selection visibility, and a real frontend composer.

Acceptance gate:

- Fresh local run.
- Configure provider or environment key.
- Send user chat message.
- Receive model response.
- Selected model/provider is visible.
- Settings survive restart if persistence exists in scope.
- Tests pass.
- Safety scan passes.

### 2. `public-provider-settings-persistence-slice`

Goal: make provider setup a real user workflow instead of a preview.

Rebuild a public-safe subset of R&D provider controls: provider catalog, default model, key/local endpoint validation, Ollama status, and user-friendly error display. Avoid direct port of vault/private setup paths unless sanitized and simplified.

Acceptance gate:

- Provider settings can be configured/tested.
- Local endpoint supported if feasible.
- Default model persists.
- Provider errors are user-friendly.

### 3. `public-roundtable-runtime-slice`

Goal: restore the R&D core meeting experience.

Use `workstationMeeting.ts`, `MeetingRoomPage.tsx`, and `meeting_heartbeat.py` as behavioral references. Rebuild a clean minimal Round Table runtime: start meeting, create seats, run Seat 1 as Meeting Manager, run seats in sequence, perform an assignment pass, run assigned responses, and produce a final summary.

Acceptance gate:

- User starts a meeting.
- Seats respond in sequence.
- Seat 1 Meeting Manager runs the flow.
- Manager assigns jobs after first pass.
- Seats answer assigned jobs.
- Manager produces final summary/plan.
- Meeting notes save.

### 4. `public-memory-notes-slice`

Goal: restore durable context after the chat and Round Table loops work.

Rebuild simple DB-backed memory and notes APIs from R&D behavior, not the full advanced memory/Guardian system. Memory should be visible, editable, deletable, and included in relevant chat/Round Table prompts.

Acceptance gate:

- Chat/meeting notes persist.
- Memory can be saved/recalled/viewed/deleted.
- Relevant memory appears in chat/Round Table context.

### 5. `public-guardian-basic-action-slice`

Goal: restore basic user trust boundaries before any real tools/connectors.

Rebuild a minimal Guardian confirmation/audit layer from R&D behavior. Keep unsupported actions blocked. Clearly separate preview/planning output from executable actions. Do not port broad R&D tool execution.

Acceptance gate:

- Clear preview vs action distinction.
- Confirm before risky actions.
- Unsupported actions blocked.
- Basic audit log visible.

## F. Stop-Doing List

Stop unless the project owner explicitly approves:

- Preview-only UI branches.
- Docs-only polish not tied to runtime.
- Public release packaging before real functionality.
- New branding/marketing copy before parity.
- Adding more empty tabs/cards.
- Expanding advanced Guardian/LIMA internals before chat/provider/Round Table work.
- Public announcement prep before a complete working loop.

## G. Release Gate

Sparkbot is not release-ready until a new user can:

- Install/run locally.
- Configure at least one provider or local endpoint.
- Chat with Sparkbot.
- Start a Round Table.
- See multiple seats respond.
- Receive Meeting Manager assignments and final summary.
- Save and reopen notes/history after restart.
- Understand Guardian confirmations/basic safety behavior.

## H. Immediate Next Recommendation

Create the next branch:

`public-runtime-chat-provider-slice`

That branch should ignore release packaging, preview UI, new docs, branding, connector expansion, and LIMA internals. The only job should be to make a fresh local public Sparkbot run, configure a provider or local endpoint, send a chat message, receive a model response, display the selected provider/model, persist the relevant settings/state, and pass tests plus safety scan.

Project owner decisions needed before or during the next branch:

- Which providers are mandatory for first public MVP: OpenAI, OpenRouter, Ollama/local, or another minimum set.
- Whether this internal audit report, which necessarily names the R&D source repo and internal parity details, should ever be pushed to the public remote or kept as a local/private audit artifact.
- Whether desktop/Tauri packaging is part of first functional release or starts only after the web/local runtime release gate passes.
- What local credential storage policy is acceptable for the public app.
