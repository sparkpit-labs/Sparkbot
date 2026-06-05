# Local Development

This guide covers the local-only developer runner scripts for the current public Sparkbot Workstation MVP.

## What the scripts do

- `scripts/start-backend-dev.sh` starts the FastAPI development server on `127.0.0.1:8000` by default.
- `scripts/start-frontend-dev.sh` starts the Vite development server on `127.0.0.1:5173` by default.
- `scripts/check-public-safety.sh` runs public sanitation checks without starting services.
- `scripts/validate-public-shell.sh` runs backend and frontend validation without starting long-running development servers.
- `scripts/smoke-check-local.sh` checks already-running local backend and frontend development servers.

## What the scripts do not do

- They do not configure provider credentials automatically.
- They do not print or expose saved secrets.
- They do not call providers by themselves; Chat model calls occur only after a configured provider route receives a Chat turn.
- They do not start deployment infrastructure.
- They do not configure desktop packaging.

## Alternate ports

The development scripts support alternate localhost ports for local smoke tests:

- Backend: `SPARKBOT_BACKEND_HOST`, default `127.0.0.1`; `SPARKBOT_BACKEND_PORT`, default `8000`.
- Frontend: `SPARKBOT_FRONTEND_HOST`, default `127.0.0.1`; `SPARKBOT_FRONTEND_PORT`, default `5173`.
- Frontend API base URL: `VITE_SPARKBOT_API_BASE_URL`, default `http://127.0.0.1:${SPARKBOT_BACKEND_PORT}`.

The server scripts reject non-local bind hosts. See `LOCAL_SMOKE_TEST.md` for a complete alternate-port smoke flow.

## Backend setup

```bash
python3 -m venv .venv-local
. .venv-local/bin/activate
python -m pip install --upgrade pip
python -m pip install -e "backend[dev]"
bash scripts/start-backend-dev.sh
```

## Frontend setup

```bash
cd frontend
npm ci
cd ..
bash scripts/start-frontend-dev.sh
```

## Local validation

```bash
bash scripts/check-public-safety.sh
bash scripts/validate-public-shell.sh
```

Use the validation commands before opening public review branches.
