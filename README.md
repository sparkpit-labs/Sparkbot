# Sparkbot

Sparkbot is an early public, local-first AI Workstation MVP from SparkPit Labs. It is for builders, hobbyists, and technical users who want a self-hosted workspace for Chat, provider/model routing, Round Table meetings, Agents Wing setup, shared memory, notes/history, dashboard counters, safe task records, and guarded local controls.

The current repository is suitable for internal MVP review, local validation, and continued public development. It is not a production release and does not claim full parity with earlier research builds.

## Who this is for

- Hobbyists and tinkerers who want to inspect and run a local AI Workstation MVP.
- Developers evaluating the project structure, validation path, and public roadmap.
- Security-conscious users who want clear boundaries before entering provider credentials or attempting sensitive actions.
- Future contributors who want to understand what is implemented, what is disabled, and what is intentionally excluded.

## Current status at a glance

| Area | Current status | Notes |
| --- | --- | --- |
| Backend health endpoint | Works | FastAPI exposes local `GET /health`. |
| Frontend app routes | Works | `/`, `/spine`, `/controls`, `/command-center`, `/workstation`, `/chat`, and `/roundtable` render through the React app. |
| Shared Workstation store | Works | Local SQLite-backed rooms, seats, notes, memory, events, Chat, Round Table, confirmations, and task records. |
| Command Center | Works | Provider/model config, server-side credential entry, seats, Agents Wing, invite routes, local readiness, and disabled Task Guardian state. |
| Chat | Works | Backend-backed sessions/messages with shared memory and notes recall; provider calls run only through configured supported routes. |
| Round Table | Works | Backend-backed sessions, fixed phase order, Seat 1 Meeting Manager, assignments, summaries, wrap-up notes, provider routes when configured, and deterministic fallback. |
| Agents Wing | Works | Create/edit agents, persist identity/instructions, invite/assign agents to seats, and use assigned agents in Round Table context. |
| Memory/context | Works | Persistent source-labeled memory with create/list/edit/delete and safe recall into Chat and Round Table. |
| Notes/history/Spine | Works | Notes, wrap-up artifacts, session history, safe events, producer metadata, and dashboard counters are visible from Workstation/Spine. |
| Task records | Works as state only | Manual task records/history and pause/resume/done/cancel are local state only. |
| Run/write-mode execution | Disabled | UI controls are disabled and backend run/write-mode routes fail closed. |
| Desktop packaging | Planning only | No installer or desktop binary exists yet. |
| Tool/connector execution | Not implemented | No terminal, process, file, connector, browser, scheduled, external-send, or device automation is active. |

## Release and checkpoint status

The earlier GitHub pre-release `public-v1-shell-baseline-0` remains a historical shell-baseline checkpoint. The current branch line has moved beyond that baseline into a local Workstation MVP. Use the current docs and audit reports for present behavior.

## Quickstart

### Prerequisites

- Python 3.12 or newer
- Node.js 20.19.0 or newer
- npm

### 1. Validate the local Workstation MVP

From the repository root:

```bash
bash scripts/validate-public-shell.sh
```

This runs backend compile/tests, frontend install/audit/tests/build, and does not start long-running services.

### 2. Run the public safety scan

```bash
bash scripts/check-public-safety.sh
```

This checks for blocked private references, unexpected publishing identity references, and non-BMP characters.

### 3. Start the backend in terminal 1

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

### 4. Start the frontend in terminal 2

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

Vite may print the exact local URL when the frontend server starts.

### 5. Optional alternate-port smoke test

When the default ports are already in use, run the app on alternate localhost ports and verify both surfaces:

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

Open `http://127.0.0.1:15173` for the browser check. See `docs/LOCAL_SMOKE_TEST.md` for details.

## What this repository does not do yet

- No desktop installer or desktop binary.
- No production deployment workflow or production support guarantee.
- No background scheduler, automatic runner, reminders engine, or recurring job execution.
- No connector write flows, connector sends, or external delivery actions.
- No file mutation, process execution, terminal execution, browser automation, or device automation.
- No public CLI-backed OpenAI or Claude subscription-auth execution path.
- No full private Guardian, Vault, or platform-internal control system.
- No rich memory lifecycle automation such as stale/archive/delete proposals or scheduled hygiene.
- No guarantee that every earlier research feature has public parity.

## Documentation map

Start with `docs/README.md` for a grouped documentation index.

Key docs:

- `CONTRIBUTING.md` for contribution scope and validation expectations.
- `SECURITY.md` for reporting security concerns.
- `docs/DEVELOPMENT.md` for local development workflow.
- `docs/VALIDATION.md` for validation commands.
- `docs/LOCAL_DEVELOPMENT.md` for local runner scripts.
- `docs/LOCAL_SMOKE_TEST.md` for alternate-port local smoke testing.
- `docs/ROADMAP.md` for staged product direction.
- `docs/RELEASE_READINESS.md` for current readiness boundaries.
- `docs/PUBLIC_ARTIFACT_MANIFEST.md` for included and excluded public artifacts.
- `docs/DESKTOP_PACKAGING_PLAN.md` for desktop packaging planning only.

## Security and privacy posture

Validation does not require secrets. Provider credentials may be entered through Command Center and are stored server-side in local configuration, not echoed to the browser. Chat and Round Table model calls use only configured supported provider routes. Unsupported subscription-only routes fail closed. Product events store safe metadata, not prompts, model outputs, headers, credentials, or secrets.

Sparkbot does not execute tools, run connectors, mutate files, start schedulers, run terminal commands, automate browsers, control devices, or send data externally from task or Guardian surfaces.

## Repository standards

This repository is maintained as a professional public project. Public documentation should describe only supported or planned public functionality and should avoid private infrastructure details, internal operating notes, or unsupported claims.

## License

This repository is licensed under the MIT License. The license applies to the contents of this public `sparkpit-labs/Sparkbot` repository only.

## Maintainers

Maintained by Spark Pit Labs Team.
