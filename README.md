# Sparkbot

Sparkbot is an early public, local-first AI workstation from SparkPit Labs. It is for builders, hobbyists, and technical users who want a self-hosted workspace for chat, provider routing, future model seats, Round Table collaboration, and safety-gated controls.

The current repository now includes the first real runtime slice: backend-configured provider routing and chat. Round Table, persistent provider settings, memory, and Guardian action confirmations remain future slices.

## Who this is for

- Hobbyists and tinkerers who want to inspect and run the local shell baseline.
- Developers evaluating the project structure, validation path, and public roadmap.
- Security-conscious users who want clear boundaries before provider credentials, model calls, or sensitive actions exist.
- Future contributors who want to understand what is implemented, what is preview-only, and what is intentionally excluded.

## Current status at a glance

| Area | Current status | Notes |
| --- | --- | --- |
| Backend health endpoint | Works | FastAPI exposes local `GET /health`. |
| Backend chat endpoint | Works | FastAPI exposes local `POST /api/chat`. |
| Provider status endpoint | Works | FastAPI exposes local `GET /api/providers/status`. |
| Frontend workstation | Works | React/Vite workstation builds and tests successfully. |
| Chat runtime | Works | Composer sends messages to the backend provider router and displays responses. |
| Provider runtime | Works | Supports backend-configured `openai`, `openai_compatible`, and `ollama`. |
| Round Table | Preview | Inert planned seats for future collaboration. |
| Guardian Controls | Preview only | No approvals, enforcement, or sensitive actions. |
| Desktop packaging | Planning only | No installer or desktop binary exists yet. |
| Credential storage | Env only | Secrets stay server-side in local backend environment/config. |
| Tool execution | Not implemented | No terminal, tool execution, connector calls, or external sends. |

## Release and checkpoint status

The latest public checkpoint tag on `main` is `public-v1-local-smoke-ready-0`.

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

### 3. Configure a provider

Copy `.env.example` to `.env` and configure one provider path. Keep `.env` local; it is gitignored.

OpenAI:

```bash
SPARKBOT_PROVIDER=openai
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

OpenAI-compatible endpoint:

```bash
SPARKBOT_PROVIDER=openai_compatible
OPENAI_COMPATIBLE_BASE_URL=http://127.0.0.1:1234/v1
OPENAI_COMPATIBLE_MODEL=local-model-name
OPENAI_COMPATIBLE_API_KEY=
```

Ollama:

```bash
SPARKBOT_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=llama3.1
```

### 4. Start the backend in terminal 1

```bash
python3 -m venv .venv-local
. .venv-local/bin/activate
python -m pip install --upgrade pip
python -m pip install -e "backend[dev]"
bash scripts/start-backend-dev.sh
```

Expected backend URLs:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/api/providers/status
http://127.0.0.1:8000/api/chat
```

### 5. Start the frontend in terminal 2

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

### 6. Optional alternate-port smoke test

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
- No browser-side provider credential setup.
- No persisted provider settings UI.
- No Round Table meeting engine.
- No memory or meeting notes persistence.
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
- `docs/ROADMAP.md` for staged product direction.
- `docs/RELEASE_READINESS.md` for current release-readiness boundaries.
- `docs/PUBLIC_ARTIFACT_MANIFEST.md` for included and excluded public artifacts.
- `docs/DESKTOP_PACKAGING_PLAN.md` for desktop packaging planning only.

## Security and privacy posture

Current validation does not require secrets. Provider credentials are read only by the backend from local environment/config values and are never exposed to the browser. Chat requests call the configured provider selected by the local developer. Tool execution, connectors, and sensitive actions remain unavailable.

## Repository standards

This repository is maintained as a professional public project. Public documentation should describe only supported or planned public functionality and should avoid private infrastructure details, internal operating notes, or unsupported claims.

## License

This repository is licensed under the MIT License. The license applies to the contents of this public `sparkpit-labs/Sparkbot` repository only.

## Maintainers

Maintained by Spark Pit Labs Team.
