# Agent Invite Route Parity Report

Branch: port-rd-agent-invite-route-parity
Base branch: audit-agents-wing-roundtable-provider-integration
Base commit: 41496dcd0709e1518b83598659c6753f87ed2c94

## Scope

This branch restores the R&D-style agent invite-route workflow in the public Command Center and Workstation path without adding connectors, external sends, tool execution, automation, schedulers, broader guarded storage behavior, or release copy. The existing Agents Wing to seat assignment to provider-backed Round Table behavior is preserved.

## R&D Files Inspected

- sources/Sparkbot/backend/app/api/routes/chat/model.py
- sources/Sparkbot/backend/app/api/routes/chat/llm.py
- sources/Sparkbot/frontend/src/lib/workstationMeeting.ts
- sources/Sparkbot/frontend/src/pages/WorkstationPage.tsx

## R&D Invite-Route Behavior Summary

The R&D path lets the operator configure an invited agent route with agent name, selected model, credential material, and auth mode. On meeting launch, the frontend ensures seated agents exist, posts an invite-route config for each invited agent, saves agent route overrides, and starts the meeting with the invited participant handles.

Backend route resolution prefers the invite-route model and credential over the generic agent override. The route credential is used only for provider dispatch. The R&D route state itself is runtime-only, while the frontend also stores layout and draft invite state in browser storage.

## Public Behavior Before This Branch

The audited public branch already had server-backed custom agents, agent_overrides, persistent seat-agent assignment, and provider-backed Round Table prompt construction using assigned agent identity, description, and instructions. The remaining gap was a dedicated invite-route workflow and endpoint. Public behavior effectively used agent_overrides as the closest equivalent, which was not enough for route parity.

## What Was Ported Or Rebuilt

- Added dedicated invite-route state under Command Center config as invite_routes.
- Added POST /api/v1/chat/agents/{agent_name}/invite-route.
- Added DELETE /api/v1/chat/agents/{agent_name}/invite-route.
- Added safe invite-route metadata to agent API responses.
- Stored invite credentials only in the existing server-side secrets store, keyed per agent invite route.
- Updated Round Table route resolution so default-provider seats use the assigned agent invite route before falling back to generic agent_overrides.
- Kept explicit seat provider/model assignment authoritative. Invite credentials are not applied when a seat explicitly selects another provider.
- Added Command Center Agents Wing controls to save and clear invite routes and assign an invited agent to a Round Table seat.

## Backend State And Endpoints

agent_overrides remains the generic provider/model override representation. This branch extends it with dedicated invite_routes for R&D-style invite-route parity. The public backend now has two separate concepts:

- agent_overrides: generic route/model override for an agent.
- invite_routes: invite workflow route metadata for an agent, with credentials stored outside API-visible config.

Safe invite-route responses include route, model, auth mode, and credential_configured. Raw credentials are not returned in API responses, model-call events, turn metadata, summaries, frontend config, or logs created by this path.

## UI Controls Added Or Changed

Command Center Agents Wing rows now include:

- Invite model selector.
- Auth mode selector.
- Write-only invite credential field.
- Save invite button.
- Clear invite button.
- Invite-to-seat selector.
- Assign invited agent button.

Specialty Wing and existing seat assignment controls remain usable. The new invite-to-seat control uses the existing persistent seat endpoint and does not use browser storage as source of truth.

## Mapping To Agent, Seat, And Round Table State

1. Agent identity, description, and instructions remain stored server-side in custom agent records.
2. Invite route metadata is stored server-side in Command Center config.
3. Invite credentials are stored server-side in the existing secrets payload.
4. Inviting an agent to a seat writes the existing persistent seat assignment.
5. Round Table resolves participant context from the assigned seat agent.
6. If the seat provider is default, Round Table uses the agent invite route first, then generic overrides, then deterministic fallback.
7. If the seat provider/model is explicit, that seat assignment stays authoritative and does not inherit an invite credential.
8. Prompt/context construction keeps seat role/name distinct from agent identity/instructions.
9. Seat 1 remains the Meeting Manager unless changed through existing supported seat state.

## Persistence Behavior

Invite-route metadata persists with Command Center config. Invite-route credentials persist through the existing server-side secrets store and are never echoed. Seat-agent links persist through the shared Workstation store. Round Table turns, assignments, summaries, wrap-up notes, and event links keep the correct seat and agent identifiers after restart-style readback. Reruns remain idempotent and do not duplicate agent-linked turns, assignments, summaries, or notes.

Browser localStorage and sessionStorage are not used as source of truth for invite routes, agents, seats, or meeting state.

## Tests Added Or Strengthened

- backend/tests/test_command_center.py
  - Invite-route create, read, and delete persistence.
  - Safe response shape without credential echo.
  - Restart-style readback of agent invite route.
  - Event payloads do not expose credential material.

- backend/tests/test_roundtable_workstation_integration.py
  - Invited agent assigned to a seat participates in provider-backed Round Table with mocked provider dispatch.
  - Prompt/context includes invited agent identity, description, and instructions.
  - Seat label/role stays distinct from agent identity.
  - Seat 1 Meeting Manager remains preserved.
  - Assignments and second-pass responses keep correct invited agent/seat links.
  - Restart-style readback restores agent, invite route, seat, session, and turn links.
  - Rerun idempotency does not duplicate agent-linked artifacts.
  - Protected input and protected output fail closed before unsafe persistence or provider dispatch.
  - Model-call events do not store prompts, outputs, or credentials.
  - Invite credential scoping does not apply the invite key to an explicit seat provider override.

- frontend/src/App.test.tsx
  - Command Center exposes invite save and invite-to-seat controls.

## Patches Made

- backend/app/api/command_center.py: added invite-route input model, safe route serialization, persistent route endpoints, credential storage integration, and agent response decoration.
- backend/app/api/workstation.py: added invite-route-aware agent context and Round Table route resolution.
- backend/app/services/model_execution.py: added in-memory route credential/auth support for provider dispatch without response/event exposure.
- frontend/src/api.ts: added invite-route API types and client helpers.
- frontend/src/components/CommandCenter.tsx: added Agents Wing invite controls and seat assignment workflow.
- frontend/src/styles.css: added layout support for invite controls.
- Tests updated as listed above.

## Validation Results

- git diff --check: PASS.
- Backend tests: PASS, 47 passed, one existing Starlette/httpx deprecation warning.
- Frontend tests: PASS, 8 passed.
- Frontend build: PASS.
- npm audit --audit-level=moderate: PASS, 0 vulnerabilities.
- bash scripts/check-public-safety.sh: PASS after neutralizing a public-facing auth-mode label that triggered the strict scan.
- bash scripts/validate-public-shell.sh: PASS.
- Changed-file privacy scan: PASS.

Manual HTTP/API checks: PASS. Isolated local servers were started on alternate ports with a temporary data directory. The routes /, /spine, /controls, /command-center, /workstation, /chat, and /roundtable returned HTTP 200. A custom agent was created and edited, an invite route was saved, the agent was assigned to Seat 2, a deterministic Round Table session was run, Seat 2 kept the invited agent, and Seat 1 kept the Meeting Manager role. After backend restart on the same temporary data directory, the invite route, seat assignment, and session turn links were restored. Provider-backed invite execution was covered by mocked backend integration tests.

## Remaining Gaps And Warnings

- R&D stored some invite-route state only at runtime and used browser storage for layout/draft workflow state. The public branch intentionally uses server-backed route and seat state instead.
- Subscription-style auth modes remain metadata only unless the public provider execution layer already supports the selected provider route. No connector, token exchange, or subscription bridge was added.
- The UI is a parity workflow inside the existing Command Center Agents Wing. It does not attempt to recreate the full R&D Workstation visual invite desk.

## Verdict

PASS_WITH_WARNINGS

## Recommendation

Continue from this branch. The next branch should stay narrow: either polish the Command Center invite workflow if product parity needs a closer visual match, or proceed to the next audited R&D behavior only after this branch is reviewed and pushed.
