# Operator Review Guide

This guide is for hands-on internal review of the current local Sparkbot Workstation MVP. It is not a release checklist, packaging guide, or production-readiness claim.

## What This MVP Supports

- Local backend health, Command Center, Workstation, Chat, Round Table, Spine, and Controls routes.
- Backend-backed provider/model configuration with server-side credential storage outside the checkout by default.
- Chat sessions using the selected supported provider/model route for text work the model can perform, or a safe unconfigured response when no route is ready.
- Round Table meetings with fixed phases, Seat 1 Meeting Manager, assignments, manager summary, wrap-up note, provider-backed text turns when configured, and deterministic fallback.
- Agents Wing create/edit behavior, persistent agent identity/instructions, invite routes, and seat assignment.
- Shared local Workstation state for rooms, sessions, seats, agents, memory, notes, history, events, confirmations, and task records.
- Source-labeled memory/context recall into Chat and provider-backed Round Table prompts.
- Notes/history/Spine visibility with safe event metadata.
- Manual task records with create/list/update/pause/resume/done/cancel state transitions.
- Optional Command Center guardrails are injected into model prompts only when enabled and saved by the operator.
- Fail-closed backend behavior for task run/write-mode execution routes.

## What This MVP Does Not Support Yet

- No production deployment workflow or production support guarantee.
- No public release claim.
- No desktop installer, desktop binary, auto-update, or code signing.
- No background scheduler, automatic runner, reminders engine, or recurring job execution.
- No connector writes, connector sends, or external delivery actions.
- No file mutation, process execution, terminal execution, browser automation, or device automation.
- No public CLI-backed OpenAI or Claude subscription-auth execution path.
- No local CLI session bridge, browser sign-in scraping, connector auth bridge, or credential bridge.
- No full private Guardian, Vault, or platform-internal control systems.
- No richer memory lifecycle automation such as stale/archive/delete-proposal/restore workflows.

## Local Run Commands

Run all commands from the repository root unless noted otherwise.

### Validate Before Review

```bash
bash scripts/check-public-safety.sh
bash scripts/validate-public-shell.sh
```

### Start Backend

```bash
python3 -m venv .venv-local
. .venv-local/bin/activate
python -m pip install --upgrade pip
python -m pip install -e "backend[dev]"
bash scripts/start-backend-dev.sh
```

Expected backend health URL:

```text
http://127.0.0.1:8000/health
```

### Start Frontend

In a second terminal:

```bash
cd frontend
npm ci
cd ..
bash scripts/start-frontend-dev.sh
```

Expected frontend URL:

```text
http://127.0.0.1:5173
```

### Alternate Local Ports

Use alternate ports when defaults are already in use:

```bash
SPARKBOT_BACKEND_PORT=18000 bash scripts/start-backend-dev.sh
```

```bash
SPARKBOT_BACKEND_PORT=18000 \
VITE_SPARKBOT_API_BASE_URL=http://127.0.0.1:18000 \
SPARKBOT_FRONTEND_PORT=15173 \
bash scripts/start-frontend-dev.sh
```

```bash
SPARKBOT_BACKEND_URL=http://127.0.0.1:18000 \
SPARKBOT_FRONTEND_URL=http://127.0.0.1:15173 \
bash scripts/smoke-check-local.sh
```

## Provider Setup Options

Provider credentials should be disposable/test credentials for review. Do not commit provider credentials, paste them into docs, or print them in logs.

Saved Command Center credentials are server-side only. By default, Sparkbot stores provider credentials and operator auth metadata outside the checkout at `$XDG_DATA_HOME/sparkbot/command-center` when `XDG_DATA_HOME` is set, otherwise `~/.local/share/sparkbot/command-center`. Set `SPARKBOT_SECRETS_DIR` to choose another local sensitive data directory. `SPARKBOT_DATA_DIR` remains available for non-secret local config/store redirection and test isolation.

### OpenRouter Or OpenAI-Style Test Key Path

1. Start backend and frontend.
2. Open `/command-center`.
3. Choose a supported provider/model route.
4. Enter a disposable/test provider key in the Command Center credential field.
5. Save the provider/model configuration.
6. Confirm the UI shows the route as configured without revealing the key value.
7. Use `/chat` for a small live prompt, then inspect `/spine` or `/workstation` events for safe metadata only.
8. Use `/roundtable` for a small meeting and confirm Seat 1 remains Meeting Manager.

Subscription-only OpenAI/Claude local-session providers are intentionally unsupported in the public path and should fail closed.

### Ollama Or Local Endpoint Path

1. Start a local Ollama-compatible server outside Sparkbot.
2. Confirm it is reachable on the expected localhost endpoint.
3. Open `/command-center`.
4. Use the local-model check and select an available local model if listed.
5. Run a small Chat or Round Table check.

Sparkbot does not start or install local models for the operator.

### Mocked/Local-Safe Test Path

Use the automated validation path when disposable provider credentials are not available:

```bash
bash scripts/validate-public-shell.sh
```

Backend tests cover mocked/local-safe provider execution for Chat and Round Table. This validates the Workstation path without calling a live provider.

## Routes To Inspect

| Route | What to inspect |
| --- | --- |
| `/` | App landing route, navigation, backend health panel |
| `/spine` | Safe events, counters, producers, history, task and confirmation state |
| `/controls` | Local controls and disabled protected-operation boundaries |
| `/command-center` | Provider/model setup, Agents Wing, seat assignment, invite routes, disabled task execution |
| `/workstation` | Rooms, notes, history, memory, task records, dashboard state |
| `/chat` | Backend-backed Chat sessions, model route behavior, memory and note surfaces |
| `/roundtable` | Room/session flow, assigned agents, Seat 1 Meeting Manager, turns, assignments, summary, wrap-up note |

## Operator Review Checklist

| Area | Review steps | Expected result |
| --- | --- | --- |
| Command Center | Open `/command-center`, refresh status, inspect provider/model state and custom guardrails | Shows real backend-backed status; custom guardrails are operator-controlled |
| Provider/model setup | Save a supported test route or confirm unconfigured/local state | Credentials stay server-side and are not echoed |
| Chat | Start a chat and send a small work request through configured or fallback path | Message persists; configured models can answer text work; events remain metadata-only |
| Agents Wing | Create or edit an agent with identity and instructions | Agent persists server-side; instructions remain redacted in unsafe surfaces |
| Round Table | Assign an agent to a seat and run a small session | Seat 1 remains Meeting Manager; assigned agent context and optional Command Center guardrails are used |
| Invite routes | Save or inspect invite-route/provider/model state for an agent | Safe routes persist; unsupported subscription-only routes fail closed |
| Memory | Create/list/edit/delete memory if the UI/API exposes it | Memory persists server-side, recalls safely, and deletes after confirmation |
| Notes/history | Save or edit a note and inspect history | Notes persist, history links to sessions, no per-turn Round Table notes are created |
| Spine/events | Inspect recent events and producer/source filters | Events show safe metadata only, not prompts, outputs, headers, or credentials |
| Task records | Create/update/pause/resume/done/cancel a task record | Task changes persist as state only |
| Fail-closed execution | Try disabled run/write-mode controls or backend routes in a safe test | Execution UI remains disabled and backend returns fail-closed responses; Chat/Round Table text prompts still dispatch when a model route is configured |
| Restart persistence | Restart backend and reload frontend | Provider config, agents, seats, invite routes, sessions, memory, notes, events, and tasks remain available |

## Known Warnings

- Live provider smoke was not run on the previous branch because no disposable/test provider credential was available and no local model was reachable.
- CLI-backed OpenAI/Claude subscription auth is not enabled in the public path.
- Scheduler/runner/connectors/external sends are not implemented.
- File/process/terminal/browser/device automation is not implemented.
- Desktop installer and packaging are not implemented.
- Full private Guardian/Vault internals are not included.
- Richer memory lifecycle behavior is deferred.
- Browser-click end-to-end automation has not been added; current smoke coverage uses HTTP/API checks plus backend and frontend tests.
- If an older checkout already contains `backend/data/command-center/secrets.json` from a prior local run, move it out of the repository before running public safety scans. New normal credential saves use the outside-checkout sensitive store by default.

## Review Recommendation

Use this branch for hands-on internal operator review. Treat live-provider behavior as pending until disposable/test credentials or an already available local model are provided.
