# Server Baseline

This repository contains an early public v1.0.0 server foundation for Sparkbot.

## What Exists

- Minimal FastAPI server under `backend/app`.
- Health endpoint at `GET /health`.
- Local settings with safe defaults in `backend/app/core/settings.py`.
- Minimal backend test coverage for the health route.
- Local scripts for backend startup and backend test execution.
- Backend-only continuous integration workflow.

## What Is Intentionally Excluded

- User interface and desktop packaging layers.
- External integration surfaces and automation bridges.
- Action orchestration, approval systems, and background workers.
- Data stores and migrations.
- Provider setup, model routing, and external API usage.
- Any production deployment wiring.

## Local Commands

From the repository root:

```bash
bash scripts/start-local-backend.sh
```

```bash
bash scripts/test-backend.sh
```

Manual validation:

```bash
python3 -m compileall backend
pytest backend/tests -q
```

