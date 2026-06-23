# Sparkbot

Sparkbot is an early public, local-first AI workstation shell from SparkPit Labs. It is for builders, hobbyists, and technical users who want a self-hosted workspace for future chat, model seats, Round Table collaboration, provider setup, and safety-gated controls.

The current repository is a validated shell baseline. It is useful for review, local validation, and continued public development, but it is not a complete product release.

## Who this is for

- Hobbyists and tinkerers who want to inspect and run the local shell baseline.
- Developers evaluating the project structure, validation path, and public roadmap.
- Security-conscious users who want clear boundaries around provider credentials, explicitly enabled model calls, and sensitive actions.
- Future contributors who want to understand what is implemented, what is preview-only, and what is intentionally excluded.

## Current status at a glance

| Area | Current status | Notes |
| --- | --- | --- |
| Backend health endpoint | Available | FastAPI exposes local `GET /health`. |
| Backend capabilities endpoint | Available | FastAPI exposes static read-only `GET /capabilities`. |
| Frontend shell | Available | React/Vite shell builds and tests successfully. |
| Local Workstation store | Available | SQLite-backed local storage under `SPARKBOT_DATA_DIR` or the user app data directory. |
| Local chat drafts | Available | Stores operator and note messages locally; local Ollama responses can be saved when explicitly run from a selected session. |
| Local memory notes | Available | Stores local notes only; notes can be manually selected for one local Ollama prompt. Not automatic retrieval, model memory, embeddings, vector DB, or cloud sync. |
| Local work lane cards | Available | Stores planning cards locally with optional links to local chat sessions; no scheduler, reminders, notifications, or execution. |
| Local data export | Available | Downloads a read-only JSON backup of local chat sessions, memory notes, and work lane cards. No import, cloud sync, external upload, credentials, or provider calls. |
| Local runtime settings | Available | Shows the current local data directory, SQLite file path, local model enablement, and env-driven Ollama model/base URL. No credential fields or save actions. |
| Local Ollama adapter | Disabled by default | Localhost-only prompt adapter for Ollama; enable with `SPARKBOT_LOCAL_MODELS_ENABLED=true`. Responses are persisted only to an explicitly selected existing local chat session. No cloud providers or credentials. |
| Workstation shell | Preview | Read-only dashboard with public baseline status, capability grouping, and product shell layout. |
| Chat shell | Preview | Read-only status surface; local Workstation chat drafts and manual local Ollama response capture are separate from cloud/provider chat runtime. No streaming, provider routing, or send action. |
| Round Table | Preview | Read-only status surface; no meeting engine, agent orchestration, model calls, or turn persistence. |
| Model Seats | Preview | Read-only model seat status surface; no model assignment, routing, calls, credentials, or seat persistence. |
| Task Lanes | Preview | Read-only task lane status surface; no scheduler, background jobs, notifications, task execution, or persistence. |
| Provider Setup | Available | Env-driven provider onboarding/status for local Ollama, OpenRouter, API-key providers, and Codex/Claude subscription sign-in. No browser credential fields or save action. |
| Guardian Controls | Preview | Read-only Guardian policy status surface; no approvals, enforcement, or sensitive actions. |
| Desktop packaging | Planned | No installer or desktop binary exists yet. |
| Connectors | Guarded future | Read-only connector status surface; no connector calls or external sends. |
| Model calls | Disabled by default | Local Ollama and OpenRouter prompt calls are disabled unless explicitly enabled by environment. Chat and Round Table do not auto-call models. |
| Credential storage | Guarded future | No secrets are accepted, stored, or transmitted. |
| Tool execution | Guarded future | No terminal, tool execution, connector calls, or external sends. |

## Release and checkpoint status

The latest public release tag on `main` is `v1.0.0`. The previous release-candidate checkpoint tag is `v1.0.0-rc0`, and the latest pre-RC phase checkpoint tag is `public-v1-desktop-readiness-0`.

The GitHub pre-release `public-v1-shell-baseline-0` remains the first published shell baseline release. Development continues on `main` through checkpoint tags, so `main` may include newer docs and planning checkpoints than the first pre-release page.

## Quickstart

### Prerequisites

- Python 3.12 or newer
- Node.js 20.19.0 or newer
- npm

### 1. Validate the full shell baseline

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

### 3. Run the one-command local smoke test

```bash
bash scripts/run-local-smoke-test.sh
```

This prepares missing local dev dependencies, starts backend and frontend dev servers on alternate localhost ports, uses a temporary `SPARKBOT_DATA_DIR`, isolates Codex/Claude subscription homes by default, checks the default Ollama-disabled and OpenRouter-disabled paths, restarts the backend with placeholder backend provider keys to verify API-key provider onboarding, OpenRouter guarded-manual status, and the free-model enforcement gate, restarts again with local models enabled, verifies the enabled local-model status path, and then stops the smoke servers. The OpenRouter smoke phase does not send a successful cloud prompt; it submits one intentionally rejected non-free model request so validation stops before provider dispatch. Set `SPARKBOT_SMOKE_USE_HOST_SUBSCRIPTIONS=true` only when intentionally checking host Codex/Claude sign-in readiness. Add `SPARKBOT_SMOKE_REQUIRE_SUBSCRIPTIONS=true` during a LIMA/operator install smoke to fail unless both Codex and Claude subscription cards report CLI availability and sign-in detection while remaining LIMA-gated.

Default smoke ports:

```text
Backend: 127.0.0.1:18080
Frontend: 127.0.0.1:15180
```

Override them with `SPARKBOT_SMOKE_BACKEND_PORT` and `SPARKBOT_SMOKE_FRONTEND_PORT` when needed.

### 4. Start the backend manually in terminal 1

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

Expected backend capabilities URL:

```text
http://127.0.0.1:8000/capabilities
```

Expected Chat status URL:

```text
http://127.0.0.1:8000/chat/status
```

Expected Model Seat status URL:

```text
http://127.0.0.1:8000/model-seats/status
```

Expected Task Lane status URL:

```text
http://127.0.0.1:8000/work-lanes/status
```

Expected provider configuration status URL:

```text
http://127.0.0.1:8000/provider-config/status
```

Expected connector status URL:

```text
http://127.0.0.1:8000/connector-status
```

Expected Guardian policy status URL:

```text
http://127.0.0.1:8000/guardian/status
```

The Guardian status payload includes a read-only `provider_adapter_contract` object for LIMA install smoke checks. It documents the future Codex/Claude subscription dispatch contract without enabling runtime dispatch.

Expected Round Table status URL:

```text
http://127.0.0.1:8000/round-table/status
```

Expected local chat sessions URL:

```text
http://127.0.0.1:8000/local/chat/sessions
```

Expected local memory notes URL:

```text
http://127.0.0.1:8000/local/memory-notes
```

Expected local work lane cards URL:

```text
http://127.0.0.1:8000/local/work-lane-cards
```

Expected local data export URL:

```text
http://127.0.0.1:8000/local/export
```

Expected local runtime settings URL:

```text
http://127.0.0.1:8000/local/runtime/settings
```

Expected local model status URL:

```text
http://127.0.0.1:8000/local-models/status
```

Local Ollama prompt calls remain disabled by default. To test the local-only response flow, create or select a local chat session, optionally check local memory notes to include in that one prompt, start Ollama locally, and run the backend with `SPARKBOT_LOCAL_MODELS_ENABLED=true` plus a configured or typed local model name. Successful responses are stored as `assistant-local` messages in the selected session.

OpenRouter prompt calls also remain disabled by default. To test the guarded free-model path, configure backend environment values and submit an explicit prompt to the OpenRouter endpoint:

```bash
SPARKBOT_PROVIDER_CALLS_ENABLED=true \
OPENROUTER_API_KEY=... \
SPARKBOT_OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free \
bash scripts/start-backend-dev.sh
```

```bash
curl -i -X POST http://127.0.0.1:8000/provider-config/openrouter/prompt \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Say OK.","model":"mistralai/mistral-7b-instruct:free"}'
```

OpenRouter defaults to model IDs ending in `:free`. Paid OpenRouter models require `SPARKBOT_ALLOW_PAID_OPENROUTER_MODELS=true` plus an explicit model selection.

### 5. Start the frontend manually in terminal 2

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

### 6. Optional manual alternate-port smoke test

When the default ports are already in use, run the shell on alternate localhost ports and verify both surfaces:

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
- Desktop readiness is limited to local development, validation, and smoke-test paths. No installer, desktop framework, signing, or auto-update behavior is included.
- No automatic cloud model calls or production model routing.
- Local Ollama prompt calls are disabled by default and require `SPARKBOT_LOCAL_MODELS_ENABLED=true`.
- OpenRouter prompt calls are disabled by default and require `SPARKBOT_PROVIDER_CALLS_ENABLED=true`, `OPENROUTER_API_KEY`, and an explicit operator prompt.
- Local chat drafts, local assistant responses, memory notes, and work lane cards are stored only in the local SQLite Workstation store. Work lane card links point only to local chat sessions.
- Local data export is a read-only JSON download for backup/testing. There is no import path, cloud sync, external upload, credential export, or provider call.
- Local runtime settings are read-only and environment-driven. There are no credential fields, secret save buttons, or runtime config writes.
- Local memory notes are included in prompts only when explicitly selected; there is no automatic memory retrieval, model memory write, embeddings service, or vector database.
- No model seat assignment or seat persistence.
- No provider SDK dependencies.
- Provider setup is environment-driven only; there are no browser credential fields or save buttons.
- No credential storage.
- No Round Table meeting engine.
- No Guardian policy enforcement runtime.
- No terminal, tool execution, connector calls, external sends, or file mutation controls.
- No production deployment workflow.

## Documentation map

Start with `docs/README.md` for a grouped documentation index.

Key docs:

- `CONTRIBUTING.md` for contribution scope and validation expectations.
- `SECURITY.md` for reporting security concerns.
- `docs/DEVELOPMENT.md` for local development workflow.
- `docs/VALIDATION.md` for validation commands.
- `docs/LOCAL_DEVELOPMENT.md` for local runner scripts.
- `docs/LOCAL_SMOKE_TEST.md` for alternate-port local smoke testing.
- `docs/DESKTOP_SMOKE_READINESS.md` for the current desktop-readiness smoke path and packaging boundary.
- `docs/LOCAL_MODEL_ADAPTER.md` for the disabled-by-default localhost Ollama adapter.
- `docs/LOCAL_DATA_EXPORT.md` for the read-only local Workstation JSON export.
- `docs/LOCAL_RUNTIME_SETTINGS.md` for the read-only local runtime settings surface.
- `docs/PUBLIC_CAPABILITY_CONTRACTS.md` for capability status definitions and promotion gates.
- `docs/CONNECTOR_SAFETY_CONTRACT.md` for future connector safety gates.
- `docs/PROVIDER_CONFIG_CONTRACT.md` for provider setup and model-call gates.
- `docs/PROVIDER_SETUP_SHELL.md` for OpenRouter, API-key provider, and subscription sign-in setup boundaries.
- `docs/LIMA_PROVIDER_GUARDIAN_ADAPTER.md` for the future Codex/Claude subscription dispatch boundary through LIMA Guardian.
- `docs/GUARDIAN_POLICY_CONTRACT.md` for future sensitive-action policy gates.
- `docs/ROADMAP.md` for staged product direction.
- `docs/RELEASE_READINESS.md` for current release-readiness boundaries.
- `docs/PUBLIC_ARTIFACT_MANIFEST.md` for included and excluded public artifacts.
- `docs/DESKTOP_PACKAGING_PLAN.md` for desktop packaging planning only.

## Security and privacy posture

Current validation does not require secrets. The repository does not accept or store provider credentials in the browser. Provider credentials, when used, are backend environment values owned by the operator. Local Workstation CRUD stores user-entered drafts, notes, and planning cards in SQLite only. The local data export reads that SQLite data and downloads JSON in the browser without import, sync, or upload behavior. Local runtime settings show local paths and env-driven Ollama configuration without accepting credentials or writing settings. Local Ollama and OpenRouter prompt calls are disabled by default and require explicit environment enablement. Codex and Claude subscription cards report CLI availability, sign-in readiness, and next operator action; unguarded CLI dispatch remains out of scope until the LIMA Guardian execution boundary is defined.

Future connector, broad model routing, credential storage, and Guardian runtime work must satisfy the public contracts in `docs/` before implementation branches can claim active behavior.

## Repository standards

This repository is maintained as a professional public project. Public documentation should describe only supported or planned public functionality and should avoid private infrastructure details, internal operating notes, or unsupported claims.

## License

This repository is licensed under the MIT License. The license applies to the contents of this public `sparkpit-labs/Sparkbot` repository only.

## Maintainers

Maintained by Spark Pit Labs Team.
