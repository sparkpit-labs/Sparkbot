# Sparkbot Reconstruction Docs And Command Center Source Map

This audit is a public-safe reconstruction map. Internal remote names, hostnames,
absolute workstation paths, operator names, and credentials are intentionally not
copied into this file.

## A. Executive Summary

Implementation is paused. This branch performs documentation and source
inspection only.

The prior reconstruction plan was found, but it is distributed across source
docs, release-history notes, security docs, handoff notes, and LIMA-AI-OS
extraction docs. There is not one single public rebuild document in the support
shell repo. The authoritative direction is still clear: the R&D Sparkbot app is
the working source of truth, and LIMA-AI-OS is a future kernel/contracts layer,
not a current dependency for restoring the public Workstation.

The R&D Command Center is confirmed as the source of truth. The entry point is
`/spine`, implemented at `frontend/src/routes/_layout/spine.tsx`. The R&D
release history says Controls were merged into Command Center and `/controls`
redirects to `/spine`. The code confirms that: `frontend/src/routes/controls.tsx`
redirects to `/spine`, `frontend/src/routes/command-center.tsx` aliases to
`/spine`, and `spine.tsx` renders the Command Center title, setup panels,
operations panels, and Spine/Guardian inspector tabs.

The public repo should be rebuilt from the found docs and R&D source files, not
from guessed provider/chat slices or preview cards. The current public repo is a
clean public shell, not a functional reconstruction of the R&D Command Center.
It should not be released as the complete Sparkbot Workstation until the real
`/spine` Command Center and its dependent backend routes are restored.

Fastest credible path: port the R&D `/spine` Command Center as the first public
Workstation control surface, including its AI setup, provider/model persistence,
OpenRouter model refresh, local model status, Security controls, agent controls,
Task Guardian controls, and Spine inspector. Preserve behavior first. Clean only
what is required for public safety.

## B. Source Docs Found

| Repo | File | Title / section | Key instructions found | Reconstruction value | Status |
| --- | --- | --- | --- | --- | --- |
| R&D Sparkbot source | `FRESH_INSTALL_CHECKLIST.md` | First-run Controls, local/cloud/hybrid setup, restart behavior | First visit opens Controls, not the main workspace. Step 1 is "Connect AI". Cloud, local, and hybrid setup paths are validated. Local model setup checks the Ollama endpoint, lists installed models, and saves the selected local model. Provider/model config must persist after restart. Comms setup is deferred and must not block chat. | Defines the expected first-run Workstation/Command Center onboarding behavior. | Authoritative for install UX. |
| R&D Sparkbot source | `docs/capabilities.md` | Command Center | Command Center is the operator-facing operations page. It preserves `/spine`, adds `/command-center` as an alias, surfaces Room Persona, System Health, Security/operator controls, Token Guardian, Task Guardian, and keeps Spine queues, events, security, vault, and Task Guardian inspector panels below the main flow. Controls remain setup/configuration for provider keys, model stack, comms, agents, and routing. | Confirms Command Center shape and required backend-enforced sources. | Authoritative product capability doc. |
| R&D Sparkbot source | `docs/capabilities.md` | AI and model configuration | Supported providers include OpenAI, Anthropic, Google, Groq, MiniMax, xAI, OpenRouter, Ollama, plus a lower-case `openai_codex` subscription route in code. The four-model stack, `/model` selector, per-seat Invite Wing keys, and per-agent model overrides are documented. | Defines the provider/model surface that must be preserved instead of narrowed to three providers. | Authoritative but must be public-sanitized. |
| R&D Sparkbot source | `docs/capabilities.md` | Workstation | Workstation is the visual operations hub. It has Main Desk, Stack Desks, Invite Wing, Specialty Wing, Terminal Desk, Computer Control, and MCP/device control panels. Specialty Wing uses the same Controls agent registry and model override path. | Shows Command Center and Workstation share model/agent state. | Authoritative for Workstation linkage. |
| R&D Sparkbot source | `README.md` | Release history v1.6.50 through v1.6.77 | v1.6.50 made Controls a full page. v1.6.54 promoted Spine Ops to Command Center. v1.6.59 fixed persisted model routing and memory continuity. v1.6.60 stabilized Seat 1 meeting manager flow. v1.6.67 merged Controls into Command Center and redirected `/controls` to `/spine`. v1.6.70 fixed Command Center inspector API fetching in desktop mode. v1.6.71 added improvement proposals in Command Center. v1.6.72 added autonomous pause controls. v1.6.76 and v1.6.77 added owner-controlled Security and operator controls. | Establishes the sequence of decisions that created the current Command Center. | Authoritative release history. |
| R&D Sparkbot source | `SECURITY.md` | Security Mode and Security / Operator Control Panel | Command Center exposes Security beside PIN/break-glass controls. Security off is owner-local working mode; risky writes still require confirmation or PIN. Security on enables stricter guardrails, service/SSH allowlists, input blockers, and custom blockers. Command Center reads `/api/v1/chat/security/status` and writes through guarded security routes. | Defines how Guardian/Security controls must behave in the public Workstation. | Authoritative for Security behavior. |
| R&D Sparkbot source | `sparkbot_logbook_handoff.md` | v1.6.59 to v1.6.61 handoff | `/chat/model` must persist `SPARKBOT_MODEL`, default provider, and local/OpenRouter defaults through the same writer Controls uses. Agent/meeting overrides live in `SPARKBOT_AGENT_MODEL_OVERRIDES_JSON`. Locked provider routes must not silently cross providers. Seat 1 meeting manager flow runs initial ideas, assessment, assignments, assigned work, summary, and continue/operator-input decision. | Gives exact bug fixes and intended routing rules that public reconstruction must preserve. | Authoritative handoff. |
| R&D Sparkbot source | `consumer_readiness_checklist.md` | Current strengths and must-have items | R&D already has streaming chat, Memory Guardian recall, Token Guardian telemetry, policy-gated tool use, Task Guardian recurring work, Round Table/project meetings, persistent approvals, connector health, governance evals, and improvement records. Remaining work is onboarding polish and e2e tests, not replacing the product with previews. | Confirms R&D behavior is product-relevant, even if messy. | Partial readiness checklist. |
| R&D Sparkbot source | `docs/audits/sparkbot_guardian_spine_extraction_audit.md` | Guardian/Spine extraction audit | R&D contains a large Guardian/Spine ecosystem with Vault, policy, pending approvals, Task Guardian, Token Guardian, Memory Guardian, improvement loop, meeting recorder, meeting heartbeat, and many Guardian/Spine routes. The audit says extraction should start with Vault/Auth/Pending Approvals, policy, then Spine, and that LIMA support code was not standalone. | Shows which Command Center backend areas are real and why a public shell cannot ignore them. | Authoritative inventory; older extraction context. |
| R&D Sparkbot source | `docs/audits/guardian_spine_security_fix_plan.md` | Guardian/Spine security fix plan | Identifies public-safety risks around unredacted approval args, executive decision metadata, write-mode gates, Vault access, and frontend-only guards. It records that backend auth is the real gate and that extraction was blocked until security stabilization. | Defines what must be sanitized or verified during the public port. | Authoritative security gate. |
| Support shell repo | `README.md` | Sparkbot shell statement | The support shell repo only states it is intended as the open-source shell. No detailed Command Center reconstruction map was found there. | Useful as a historical shell marker, not as implementation authority. | Partial/outdated. |
| LIMA-AI-OS | `README.md` | Phase 0 status | LIMA-AI-OS is contracts, architecture, package skeleton, and import-only tests. It does not contain migrated Sparkbot behavior, live tool execution, production deploy wiring, credentials, or real model calls. | Confirms LIMA must not block public Sparkbot MVP parity. | Authoritative for LIMA scope. |
| LIMA-AI-OS | `ARCHITECTURE.md` | Runtime architecture and Spine | Sparkbot remains the spec until parity tests prove otherwise. The Spine is a process/task/event ledger. Phase 0 captures the contract boundary without migrating Sparkbot implementation. | Confirms "extract, do not rewrite" and future-kernel boundary. | Authoritative architecture. |
| LIMA-AI-OS | `docs/EXTRACTION_PLAN.md` | Extraction gates | The plan repeatedly blocks Sparkbot wiring, live adapters, model/tool execution, approval enforcement, persistence, and external calls unless a future phase explicitly approves them. | Confirms LIMA is not ready to plug into Sparkbot Command Center now. | Authoritative but not a public Workstation plan. |
| LIMA-AI-OS | `docs/CURRENT_PROJECT_STATE.md` | Current state | The project state is mostly docs/tests/fixtures and narrow non-executing helpers. Sparkbot integration remains blocked. | Confirms the current kernel layer is future work. | Authoritative state anchor. |
| LIMA-AI-OS | `docs/PHASE_38_3_SPARKBOT_TO_LIMA_GAP_AND_RISK_MATRIX.md` | Gap and risk matrix | Current LIMA support can inspect caller-provided state and preview candidate-shaped data in tests, but is not enough to implement Sparkbot integration. It explicitly does not recommend Sparkbot wiring, live adapters, approval enforcement, execution, audit persistence, external calls, or background work. | Directly supports treating LIMA as future kernel layer for this task. | Authoritative for current limitation. |
| Public Sparkbot target | `README.md` | Current repository status | Public repo says it is a validated shell baseline with preview Workstation, Chat, Round Table, Provider Setup, and Guardian Controls, and no provider credential storage or model calls. | Evidence of drift from R&D product behavior. | Accurate for current public repo, conflicting with desired reconstruction. |
| Public Sparkbot target | `docs/ROADMAP.md` and shell docs | Preview-only phases | Public roadmap and shell docs describe read-only previews for Workstation, Chat, Round Table, Provider Setup, and Guardian Controls. | Shows the public repo intentionally became a preview shell rather than a reconstruction. | Accurate but now off course. |

## C. Command Center Source Map

### R&D frontend source of truth

| Area | R&D source files | Behavior and controls | Public target |
| --- | --- | --- | --- |
| Route entry point | `frontend/src/routes/_layout/spine.tsx` | Main Command Center page at `/spine`; renders header/nav, setup rows, Comms, Agents, operations, Spine stats, queue tabs, project/event/producer/security/vault/task/improvement tabs, and inspector sheet. | Restore same route behavior under public frontend. Target path should preserve `frontend/src/routes/_layout/spine.tsx` if the R&D router is ported. |
| Command Center alias | `frontend/src/routes/command-center.tsx` | Redirects `/command-center` to `/spine`. | Add the alias after `/spine` exists. |
| Controls redirect | `frontend/src/routes/controls.tsx` | Redirects `/controls` to `/spine`; code comment says Controls merged into Command Center. | Preserve redirect so older links still land in Command Center. |
| Top navigation | `frontend/src/components/Common/SparkbotSurfaceTabs.tsx`, `frontend/src/components/Sidebar/AppSidebar.tsx` | Main navigation labels Command Center and points to `/spine`. | Public nav must expose Workstation and Command Center as real surfaces, not preview tabs. |
| Setup panels | `frontend/src/components/CommandCenter/SetupPanels.tsx` | `AISetupPanel`, `PinSecurityPanel`, `CommsSetupPanel`, and `AgentsPanel`. | Port panels directly if dependencies are brought over; sanitize public-unsafe connector text and secret handling. |
| Operations panels | `frontend/src/components/CommandCenter/OperationalPanels.tsx` | `CommandCenterOperations` loads room, model config, Guardian status, security status, dashboard summary, health, and task runs. Renders Room Persona, System Health, Token Guardian, Security, and Task Guardian cards. | Port after backend routes exist; keep disabled states only where backend context is genuinely missing. |
| Shared Controls state | `frontend/src/hooks/useControlsState.ts` | Central hook used by Command Center and DM controls. Loads model config, OpenRouter models, local model status, Guardian status, dashboard, skills, agents, room state, audit, tasks, runs. Saves provider credentials, default model, model stack, agent overrides, comms settings, custom guardrails, PIN, persona, Task Guardian jobs, and spawned agents. | Port or rebuild only as needed to match behavior. This is the core state spine for Command Center setup. |
| Controls config helpers | `frontend/src/lib/sparkbotControls.ts` | First-run onboarding keys, provider/model grouping, provider detection, route mapping, `fetchControlsConfig`, and chat-entry redirection to setup if onboarding is incomplete. | Port directly or rebuild from behavior if route framework differs. |
| Spine client | `frontend/src/lib/spine.ts` | Frontend client for `/api/v1/chat/spine/operator/*`, Guardian status, breakglass, Vault, Task Guardian write mode, improvement proposals, autonomous pauses, project workload, task detail, and events. | Port with `apiFetch` behavior preserved for desktop/local backend origin handling. |
| Workstation meeting integration | `frontend/src/lib/workstationMeeting.ts` | Prepares seats from Controls config, checks assigned provider readiness, ensures agent routes and invite routes, creates meeting rooms/artifacts, saves meeting metadata, and schedules meeting heartbeat. | Restore when Workstation/Round Table seat controls are ported. |
| Workstation surface | `frontend/src/pages/WorkstationPage.tsx`, `frontend/src/pages/MeetingRoomPage.tsx`, `frontend/src/config/workstationStations.ts` | Round Table seat assignment, Specialty Wing agent assignments, per-seat model/provider controls, meeting launch, project meeting launch, meeting notes/artifacts, and meeting room operator controls. | Do not replace with static Round Table cards. Port as the Workstation follow-on after Command Center routes load. |

### R&D Command Center sections, controls, and actions

| Section | User-facing controls | R&D state / action path | Notes |
| --- | --- | --- | --- |
| AI Setup | Provider selector, OpenRouter refresh, OpenRouter credential field, OpenRouter model dropdown, direct provider credential fields, direct provider model dropdowns, local model URL, local status check, local model picker, four-model stack, save credential, save default, save stack. | `useControlsState.ts` -> `/api/v1/chat/models/config`, `/api/v1/chat/openrouter/models`, `/api/v1/chat/ollama/status`, `/api/v1/chat/model`. | Preserve full provider set; do not narrow to three generic adapters. |
| PIN and Security | Security on/off, custom blocker text, save guardrails, current PIN, new PIN, confirm PIN, save/change PIN, status badges. | `useControlsState.ts`, `OperationalPanels.tsx` -> `/api/v1/chat/models/config`, `/api/v1/chat/guardian/pin`, `/api/v1/chat/security/*`. | Public port must keep secrets server-side and show only safe status. |
| Comms Setup | Accordion sections for chat bridges, source-control bridge, Google workspace, Microsoft workspace, enable toggles, setup fields, save comms. | `useControlsState.ts` -> `/api/v1/chat/models/config`. | Public port must sanitize any internal-only bridge language and keep credential fields server-side. |
| Agents | Spawn Agent template picker, name, description, prompt, spawn button, per-agent route selector, per-agent model selector, save overrides. | `useControlsState.ts` -> `/api/v1/chat/agents`, `/api/v1/chat/models/config`. | Required for Specialty Wing and meeting seat parity. |
| Operations | Room Persona, System Health, Token Guardian mode, Security/operator controls, Task Guardian jobs/runs, run now, pause/resume, write mode. | `OperationalPanels.tsx` -> `/api/v1/chat/users/bootstrap`, `/api/v1/chat/rooms/{id}`, `/api/v1/chat/models/config`, `/api/v1/chat/guardian/status`, `/api/v1/chat/security/status`, `/api/v1/chat/dashboard/summary`, `/api/v1/utils/health-check/`, room Guardian task APIs. | This is live backend wiring, not preview UI. |
| Spine inspector | Overview stats, queue tabs, projects, event log, producers, security, vault, Task Guardian, improvement proposals. | `spine.tsx`, `frontend/src/lib/spine.ts` -> `/api/v1/chat/spine/operator/*` and Guardian helper endpoints. | Restore after core model/security routes so Command Center can load without dead panels. |
| Workstation seats | Eight seats, stack seat autofill, Specialty Wing agent selector, per-seat model selector, per-seat invite credential, meeting launch, project meeting launch. | `WorkstationPage.tsx`, `workstationMeeting.ts` -> Controls config, room APIs, artifact APIs, agent APIs, room Guardian tasks. | Tied to Command Center model/provider/agent state. |

### R&D backend route and module map

| Area | R&D files / routes | Purpose | Public target |
| --- | --- | --- | --- |
| API registration | `backend/app/api/main.py`, `backend/app/main.py` | Registers chat routers and starts Guardian background jobs and Vault init. | Public backend must grow from health-only into the R&D route shape before Command Center can work. |
| Model/provider config | `backend/app/api/routes/chat/model.py` | `/models`, `/model`, `/models/config`, `/openrouter/models`, `/ollama/status`, `/models/latency`, `/performance`, `/system/watcher`; writes model stack, default provider/model, local defaults, provider credentials, comms config, agent overrides, Token Guardian mode, Security guardrails. | Port first. This is the Command Center AI Setup backbone. |
| Model routing | `backend/app/api/routes/chat/llm.py` | Available model catalog, provider detection, validation, local status, default provider, provider-authoritative routing, agent routing overrides, friendly provider errors. | Port with tests before frontend AI Setup is considered complete. |
| Agents | `backend/app/api/routes/chat/agents.py`, `backend/app/api/routes/chat/model.py` agent endpoints | Built-in and spawned agents, custom agent persistence, invite route setup. | Required for Agents panel and Workstation Specialty Wing. |
| Rooms and artifacts | `backend/app/api/routes/chat/rooms.py`, `backend/app/api/routes/chat/messages.py`, `backend/app/models.py`, `backend/app/crud.py` | Room create/update, messages, meeting artifacts, room persona, meeting mode, task associated rooms. | Required for operations cards and meeting launch. |
| Guardian status and controls | `backend/app/api/routes/chat/guardian.py`, `backend/app/api/routes/chat/security.py`, `backend/app/services/guardian/*` | Guardian status, PIN, breakglass, Vault, policy state, operator posture, permissions fix, Security feature toggles. | Port with sanitization and backend enforcement intact. |
| Dashboard | `backend/app/api/routes/chat/dashboard.py` | Summary counts for rooms, tasks, reminders, pending approvals, Token Guardian, Task Guardian, connector health, meeting artifacts. | Required by Command Center operations and home dashboards. |
| Spine | `backend/app/api/routes/chat/spine.py`, `backend/app/services/guardian/spine.py`, `task_master_adapter.py`, `project_executive.py` | Spine queue, project, event, producer, workload, lineage, improvement, autonomous pause, and project mutation routes. | Restore after model/security basics or mark blocked if data layer is not ready. |
| Audit and skills | `backend/app/api/routes/chat/audit.py`, `backend/app/api/routes/chat/skills.py` | Policy decision audit and skill inventory used by Controls/Command Center status surfaces. | Needed for full panel parity. |
| Task/reminder support | `backend/app/api/routes/chat/tasks.py`, `backend/app/api/routes/chat/reminders.py`, Guardian Task services | Task Guardian jobs, reminders, scheduled work, meeting heartbeat. | Required for Task Guardian and Round Table continuity. |
| Persistence | `backend/app/models.py`, `backend/app/crud.py`, `.env` writer in `model.py`, Guardian Vault/Spine/approval/memory data stores | SQLModel app data, local env persistence, Vault use-only credential storage, Spine SQLite, memory data dir, pending approvals. | Public port must keep secrets server-side and avoid browser localStorage for provider credentials. |
| MCP/device panels | R&D has additional control-plane route files and Workstation panels for device-driver style capabilities. | These are connected to Workstation but are higher risk than Command Center setup. | Defer or preserve disabled states unless backend safety gates are ported. Do not advertise unsupported action paths. |

## D. Existing Reconstruction Plan

The documented plan is not "build a new simplified public Command Center." It is:

- Treat R&D Sparkbot as the working spec until parity proves otherwise.
- Preserve the real Command Center/Controls workflow created by the v1.6.50 to
  v1.6.77 line.
- Use `/spine` as the Command Center route, with `/controls` and
  `/command-center` redirecting to it.
- Restore first-run AI setup before normal chat/workspace use.
- Preserve Cloud / Local / Hybrid setup behavior, OpenRouter model refresh,
  local model status, default provider/model persistence, four-model stack, and
  provider-authoritative routing.
- Preserve agent management and per-agent/per-seat model routing because
  Workstation Specialty Wing and Round Table depend on the same state.
- Preserve Command Center operations: Room Persona, System Health, Security,
  Token Guardian, Task Guardian, Spine queues, Vault/status, improvement
  proposals, and task/project/event inspection.
- Keep long-lived credentials server-side. R&D used env persistence and Vault
  use-only entries; the public port must not expose raw credentials in the
  browser or committed files.
- Treat LIMA-AI-OS as future kernel/contracts work. It documents boundaries and
  safety rules, but it is not ready to replace native Sparkbot behavior in this
  branch.
- Treat the support shell repo as historical/partial. It does not contain the
  complete rebuild map.

What should be ported as-is:

- R&D `/spine` route structure, route aliases, panel composition, and setup flow.
- `SetupPanels.tsx`, `OperationalPanels.tsx`, `useControlsState.ts`,
  `sparkbotControls.ts`, `spine.ts`, and `workstationMeeting.ts` where their
  dependencies can be brought over safely.
- Backend model/provider endpoints and their persistence semantics.
- OpenRouter model refresh and Ollama status behavior.
- Agent overrides and Workstation seat/provider readiness behavior.

What should be cleaned during port:

- Public-facing text that references internal deployment paths, private hosts,
  unsafe driver claims, or personal operator context.
- Any credential persistence path that would put raw credentials into frontend
  storage or public output.
- Desktop/server path assumptions that do not apply to public local installs.
- Any disabled action path must say it is unavailable or not configured; it must
  not look like a fake preview.

What should be excluded or deferred:

- Internal deployment docs and host-specific paths.
- Public claims about unfinished LIMA internals.
- High-risk device-driver control paths unless the matching Guardian/backend
  gates are ported and tested.
- Public release packaging or announcement work before the Workstation loop is
  functional.

## E. Conflicts / Drift

| Drift point | Public target evidence | Corrective note |
| --- | --- | --- |
| Preview-only UI replaced working R&D behavior | Public `README.md`, `docs/WORKSTATION_SHELL.md`, `docs/CHAT_SHELL.md`, `docs/ROUND_TABLE_SHELL.md`, `docs/PROVIDER_SETUP_SHELL.md`, and `docs/GUARDIAN_CONTROLS_SHELL.md` say the visible surfaces are read-only previews. | Replace the shell previews with the R&D Command Center and Workstation behavior. |
| Generic provider/chat slice was the wrong direction | The rejected provider/chat branch narrowed scope to three providers and a new adapter layer. | Do not merge or build on that branch for Command Center parity. |
| `/spine` is missing from public target | Public frontend has `WorkstationShell.tsx` and preview components, not R&D route files or Command Center panels. | Restore `/spine` first as the source-aligned Command Center. |
| Backend is health-only compared to R&D | Public backend has a health route and simple settings, not `/api/v1/chat/models/config`, `/openrouter/models`, `/ollama/status`, Guardian, Security, Dashboard, Spine, Agents, Room, Audit, or Task Guardian routes. | Backend routes must be ported before frontend parity can be real. |
| Provider/model onboarding was stripped | Public docs explicitly say no credential handling, no provider calls, no model routing. | Restore R&D AI Setup behavior with server-side credential handling. |
| OpenRouter model update behavior is missing | Public repo has no OpenRouter model refresh endpoint or model picker. | Port R&D `/api/v1/chat/openrouter/models` and frontend refresh flow. |
| Model seats and agent controls are missing | Public Round Table preview is inert and public Provider Setup is static. | Restore Controls agent overrides, Workstation Specialty Wing, Invite Wing, and seat readiness. |
| Security/Guardian controls are preview-only | Public Guardian Controls doc says no approvals, enforcement, or mutation. | Restore backend-enforced Security/operator status and safe controls. |
| LIMA was being treated as a possible blocker | LIMA docs say current support is not enough for Sparkbot integration. | Do not wire LIMA as a blocking dependency for MVP parity. |
| Shell support repo has no complete plan | Support shell repo only contains a minimal README. | Do not use it as the implementation guide unless new docs are added. |

## F. Corrected Build Plan

Recommended next implementation branch after review:

`port-rd-spine-command-center`

This branch should start from current public `main`, not from the rejected
generic provider/chat branch.

### Slice 1: source-aligned Command Center foundation

Acceptance gate:

- Public app has a real `/spine` Command Center route and `/controls` plus
  `/command-center` aliases.
- It uses the R&D layout and section order: AI Setup, Security/PIN, Comms,
  Agents, Operations, Spine/Guardian inspector.
- Missing backend contexts are visibly disabled or not configured, not fake.
- Public safety scan passes.

### Slice 2: AI Setup and model config parity

Acceptance gate:

- Backend exposes `/api/v1/chat/models/config`, `/api/v1/chat/model`,
  `/api/v1/chat/openrouter/models`, and `/api/v1/chat/ollama/status`.
- Frontend AI Setup loads provider status, refreshes OpenRouter models, checks
  local model status, saves default model, saves model stack, and persists
  settings across restart where R&D does.
- Credentials remain server-side and never appear in browser output.
- Tests cover model selection, OpenRouter refresh failure, local endpoint
  unavailable, missing credential, and persisted default route.

### Slice 3: Security and operations parity

Acceptance gate:

- Command Center operations load Room Persona, health, Token Guardian mode,
  Security/operator status, and Task Guardian summary.
- Security toggle, custom blockers, PIN change, operator controls, and Task
  Guardian write mode are either working with backend enforcement or explicitly
  disabled with a real blocker.
- Audit/public-safety scans pass.

### Slice 4: Spine inspector parity

Acceptance gate:

- Overview, queues, projects, events, producers, security, vault, Task Guardian,
  and improvement tabs load from backend routes.
- Project creation or mutation is either working through R&D backend paths or
  visibly blocked with the exact missing dependency.
- No panel falls back to HTML/SPA responses where JSON is expected.

### Slice 5: Workstation seat and meeting linkage

Acceptance gate:

- Workstation uses the same Controls model config and agent registry.
- Specialty Wing assignments, agent model overrides, Invite Wing seat routes,
  meeting provider readiness, and Round Table launch match R&D behavior.
- Seat 1 meeting manager flow, assignments, assigned work, final summary, and
  meeting notes/artifacts are restored or blocked with exact source blockers.

## G. Do-Not-Do List

- No more generic provider/chat slices as a replacement for Command Center.
- No preview-only Command Center cards.
- No simplified provider onboarding unless the R&D docs say so.
- No replacing OpenRouter/model update behavior with a generic adapter.
- No implementation based on assumptions when the R&D source files already show
  the behavior.
- No public release prep until actual R&D Command Center parity is restored.
- No LIMA internals as public product claims.
- No storing provider credentials in frontend localStorage.
- No exposed raw credentials, internal remotes, hostnames, absolute workstation
  paths, or operator names.
- No high-risk device action panels unless the backend safety gates are ported
  and validated.
