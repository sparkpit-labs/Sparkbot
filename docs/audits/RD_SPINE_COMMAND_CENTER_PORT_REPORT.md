# R&D Spine Command Center Port Report

## Summary

Branch `port-rd-spine-command-center` restores the public Sparkbot app from a read-only shell toward the R&D `/spine` Command Center foundation. The public app now opens a real Workstation Command Center at `/spine` and the root path also lands on that Command Center. `/controls` and `/command-center` are normalized to `/spine` in the frontend.

The R&D route could not be copied verbatim because the public repo has a minimal Vite app instead of the R&D TanStack route tree and a health-only FastAPI backend instead of the R&D chat/Guardian backend. The implementation therefore rebuilds the R&D `/spine` behavior into the public architecture: same Command Center sections, real model/provider config endpoints, real OpenRouter refresh path, real Ollama status path, real server-side credential handling, Security/PIN controls, agent override controls, seat controls, dashboard summary route, and Spine overview route.

## R&D Files Inspected

- `frontend/src/routes/_layout/spine.tsx`
- `frontend/src/routes/controls.tsx`
- `frontend/src/routes/command-center.tsx`
- `frontend/src/components/CommandCenter/SetupPanels.tsx`
- `frontend/src/components/CommandCenter/OperationalPanels.tsx`
- `frontend/src/hooks/useControlsState.ts`
- `frontend/src/lib/sparkbotControls.ts`
- `frontend/src/lib/spine.ts`
- `frontend/src/lib/workstationMeeting.ts`
- `frontend/src/pages/WorkstationPage.tsx`
- `frontend/src/pages/MeetingRoomPage.tsx`
- `backend/app/api/routes/chat/model.py`
- `backend/app/api/routes/chat/llm.py`
- `backend/app/api/routes/chat/guardian.py`
- `backend/app/api/routes/chat/security.py`
- `backend/app/api/routes/chat/dashboard.py`
- `backend/app/api/routes/chat/spine.py`
- `backend/app/api/routes/chat/agents.py`
- `backend/app/api/routes/chat/rooms.py`
- `backend/app/services/guardian/*`

## Public Files Created Or Changed

- `backend/app/api/command_center.py`
- `backend/app/main.py`
- `backend/tests/test_command_center.py`
- `frontend/src/components/CommandCenter.tsx`
- `frontend/src/api.ts`
- `frontend/src/App.tsx`
- `frontend/src/App.test.tsx`
- `frontend/src/styles.css`
- `.env.example`
- `docs/audits/RD_SPINE_COMMAND_CENTER_PORT_REPORT.md`

## Direct Ports Versus Rebuilds

No R&D file was copied verbatim. The public app architecture is too different for a direct drop-in of `spine.tsx`, `SetupPanels.tsx`, or `useControlsState.ts`.

Rebuilt from R&D behavior:

- `/spine` Command Center route behavior and aliases.
- AI Setup section with provider selector, model picker, OpenRouter refresh, local model status, default save, credential save, and four-model stack.
- Local model route with configurable Ollama endpoint and model picker.
- Server-side provider credential handling with safe configured flags and no secret echo.
- Security profile toggle, custom guardrails, and operator PIN storage.
- Agent creation and model override controls.
- Specialty Wing / seat assignment controls using the same agent override state.
- Operations cards for health, model routing monitor, scheduled work status, dashboard summary, and Spine overview.

## Features Preserved

- Workstation Command Center is the first real screen instead of preview shell cards.
- `/spine` is the Command Center foundation.
- `/controls` and `/command-center` map to `/spine` in the public frontend.
- OpenRouter model refresh calls the OpenRouter model API through the backend.
- Ollama status checks the configured local endpoint through the backend.
- Default provider/model and four-model stack persist in local backend config.
- Provider credentials are accepted only by the backend and are not returned to the browser.
- Agent overrides use provider/model route validation.
- Security profile and custom guardrail state persist in backend config.
- Operator PIN is hashed before local storage.
- Dashboard and Spine status routes exist so Command Center panels call real backend paths.

## Features Sanitized

- Internal deployment paths and source repo names are not present.
- Public UI avoids private hostnames, real credentials, internal operator names, and internal product claims.
- Connector cards are visible but disabled until their public backend gates are restored.
- Higher risk device control paths are not advertised as working actions.
- Provider credential save messages confirm server-side storage without echoing values.

## Blocked Or Disabled

| Area | Status | Reason |
| --- | --- | --- |
| Full Spine task/project persistence | Disabled empty state | R&D uses a large Guardian/Spine service and data stores not yet ported. |
| Round Table meeting launch | Disabled button | Room, artifact, meeting heartbeat, and multi-seat runtime routes are follow-up ports. |
| Task Guardian scheduler mutation | Disabled button | R&D scheduler service was not ported in this branch. |
| Connector bridge saves | Disabled cards | Connector backends require public safety review before accepting write-capable credentials. |
| Full Guardian Vault behavior | Not ported | This branch stores local credentials server-side only; encrypted Vault parity is follow-up work. |
| Memory/context spine | Not ported | R&D memory services are outside this first Command Center foundation slice. |
| Full dashboard counters | Partial | Dashboard route exists with safe current counts; R&D room/task/reminder persistence is follow-up work. |

## OpenRouter / Model Refresh Status

Implemented. Public backend exposes `GET /api/v1/chat/openrouter/models`, calls the OpenRouter models API, sorts free models first, and returns safe model metadata only. If the network or provider fails, the frontend shows the exact backend error instead of fake model data.

## Ollama / Local Status Status

Implemented. Public backend exposes `GET /api/v1/chat/ollama/status`, checks the configured local endpoint, lists installed local model IDs when available, and returns a safe unavailable state when Ollama is not running.

## Model Seat / Specialty Wing / Agent Override Status

Partially implemented and functional for configuration. The public Command Center shows eight seats, agent assignment selectors, model selectors, and saves seat routing through the same agent override payload used by the Agents section. Launching a Round Table remains disabled until room/artifact/meeting heartbeat routes are ported.

## Guardian / Security Profile Status

Partially implemented. Security profile state, custom guardrails, and operator PIN storage are working in the public backend. Full R&D Guardian policy enforcement, approval queue, encrypted Vault, and action gates are documented as follow-up parity gaps.

## Dashboard / Status Route Status

Partially implemented. Public backend now exposes Command Center status routes:

- `/api/v1/chat/models/config`
- `/api/v1/chat/model`
- `/api/v1/chat/openrouter/models`
- `/api/v1/chat/ollama/status`
- `/api/v1/chat/agents`
- `/api/v1/chat/guardian/status`
- `/api/v1/chat/security/status`
- `/api/v1/chat/security/operator-pin`
- `/api/v1/chat/dashboard/summary`
- `/api/v1/chat/spine/operator/overview`
- `/api/v1/chat/spine/operator/events`
- `/api/v1/chat/spine/operator/producers`
- `/api/v1/chat/spine/operator/projects`
- `/api/v1/utils/health-check/`

## Remaining Gaps To Full R&D `/spine` Parity

- Port R&D room, message, artifact, and meeting heartbeat routes.
- Port Round Table Seat 1 manager runtime and meeting notes flow.
- Port Guardian/Spine persistence and task/project/event tables.
- Port Task Guardian job creation, pause/resume, run history, and write-mode gates.
- Port dashboard summaries backed by real room/task/reminder data.
- Port encrypted Vault behavior or replace it with a public-safe equivalent.
- Port memory/context recall and meeting artifact rollups.
- Port connector setup only after public safety review of each backend.
- Replace temporary Command Center empty states with real R&D data as each service lands.

## Recommended Next Branch

`port-rd-command-center-room-spine-services`

That branch should port the R&D room/artifact/Spine service layer needed to make the Command Center inspector and Round Table launch controls live.
