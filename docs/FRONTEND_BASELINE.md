# Frontend Baseline

This repository now includes an early public v1.0.0 frontend foundation for Sparkbot.

## What Exists

- Minimal React and TypeScript frontend shell under `frontend/`.
- Vite-based build pipeline with `npm run build`.
- Health panel that can run a read-only request to backend `GET /health`.
- Configurable API base URL via `VITE_SPARKBOT_API_BASE_URL`.
- Minimal frontend test coverage with Vitest and Testing Library.
- Frontend-only continuous integration workflow.
- Static Workstation and Round Table preview surfaces.

## What Is Intentionally Excluded

- Active Workstation runtime behavior.
- Active Round Table runtime behavior.
- Desktop packaging.
- Provider setup and model runtime wiring.
- Guarded control runtimes.
- Production and staging deployment assumptions.

## Local Development Commands

From the repository root:

```bash
cd frontend
npm ci
npm test -- --run
npm run build
```

## Validation Commands

```bash
git status --short --branch
python3 -m compileall backend
cd frontend && npm test -- --run && npm run build
```

## Status Limitations

This frontend baseline is intentionally minimal. It does not claim release readiness and does not include active product runtimes. Public setup and release documentation will expand in later phases.

## Dependency Advisory Status

Frontend development tooling was updated to clear the Vite development server advisory chain during the Round Table shell slice. Current validation uses Node 22.22.0; contributors should use Node 20.19.0 or newer for the current Vite toolchain.
