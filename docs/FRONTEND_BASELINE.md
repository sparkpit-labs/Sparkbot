# Frontend Baseline

This repository now includes an early public v1.0.0 frontend foundation for Sparkbot.

## What Exists

- Minimal React and TypeScript frontend shell under `frontend/`.
- Vite-based build pipeline with `npm run build`.
- Health panel that can run a read-only request to backend `GET /health`.
- Configurable API base URL via `VITE_SPARKBOT_API_BASE_URL`.
- Minimal frontend test coverage with Vitest and Testing Library.
- Frontend-only continuous integration workflow.

## What Is Intentionally Excluded

- Product workstation surfaces.
- Round table surfaces.
- Desktop packaging.
- Provider setup and model runtime wiring.
- Guarded control runtimes.
- Production and staging deployment assumptions.

## Local Development Commands

From the repository root:

```bash
cd frontend
npm install
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

This frontend baseline is intentionally minimal. It does not claim release readiness and does not include full product surfaces. Public setup and release documentation will expand in later phases.
