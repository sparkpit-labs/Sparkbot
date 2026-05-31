# Sparkbot

Sparkbot is an early public, local-first AI workstation shell from SparkPit Labs. It is for builders, hobbyists, and technical users who want a self-hosted workspace for future chat, model seats, Round Table collaboration, provider setup, and safety-gated controls.

The current repository is a validated shell baseline. It is useful for review, local validation, and continued public development, but it is not a complete product release.

## Who this is for

- Hobbyists and tinkerers who want to inspect and run the local shell baseline.
- Developers evaluating the project structure, validation path, and public roadmap.
- Security-conscious users who want clear boundaries before provider credentials, model calls, or sensitive actions exist.
- Future contributors who want to understand what is implemented, what is preview-only, and what is intentionally excluded.

## Current status at a glance

| Area | Current status | Notes |
| --- | --- | --- |
| Backend health endpoint | Works | FastAPI exposes local `GET /health`. |
| Frontend shell | Works | React/Vite shell builds and tests successfully. |
| Workstation shell | Preview | Read-only product layout. |
| Chat shell | Preview | Disabled planned composer; no send action. |
| Round Table | Preview | Inert planned seats for future collaboration. |
| Provider Setup | Preview only | No API key fields, save action, or provider calls. |
| Guardian Controls | Preview only | No approvals, enforcement, or sensitive actions. |
| Desktop packaging | Planning only | No installer or desktop binary exists yet. |
| Model calls | Not implemented | No model routing or provider runtime is active. |
| Credential storage | Not implemented | No secrets are accepted, stored, or transmitted. |
| Tool execution | Not implemented | No terminal, tool execution, connector calls, or external sends. |

## Release and checkpoint status

The latest public checkpoint tag on `main` is `public-v1-desktop-packaging-plan-0`.

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

## What this repository does not do yet

- No desktop installer or desktop binary.
- No real chat runtime.
- No model calls or model routing.
- No provider credential setup.
- No credential storage.
- No Round Table meeting engine.
- No Guardian policy enforcement runtime.
- No terminal, tool execution, connector calls, external sends, or file mutation controls.
- No production deployment workflow.

## Documentation map

Start with `docs/README.md` for a grouped documentation index.

Key docs:

- `docs/DEVELOPMENT.md` for local development workflow.
- `docs/VALIDATION.md` for validation commands.
- `docs/LOCAL_DEVELOPMENT.md` for local runner scripts.
- `docs/ROADMAP.md` for staged product direction.
- `docs/RELEASE_READINESS.md` for current release-readiness boundaries.
- `docs/PUBLIC_ARTIFACT_MANIFEST.md` for included and excluded public artifacts.
- `docs/DESKTOP_PACKAGING_PLAN.md` for desktop packaging planning only.

## Security and privacy posture

Current validation does not require secrets. The repository does not accept provider credentials, store credentials, call models, execute tools, run connectors, or send data to external services. Product surfaces beyond the backend health endpoint and frontend shell are previews until explicit public contracts and runtime gates are added.

## Repository standards

This repository is maintained as a professional public project. Public documentation should describe only supported or planned public functionality and should avoid private infrastructure details, internal operating notes, or unsupported claims.

## License

This repository is licensed under the MIT License. The license applies to the contents of this public `sparkpit-labs/Sparkbot` repository only.

## Maintainers

Maintained by Spark Pit Team.
