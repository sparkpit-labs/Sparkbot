# Local Development

This guide covers the local-only developer runner scripts for the current public Sparkbot shell baseline.

## What the scripts do

- `scripts/start-backend-dev.sh` starts the FastAPI development server on `127.0.0.1:8000`.
- `scripts/start-frontend-dev.sh` starts the Vite development server on `127.0.0.1`.
- `scripts/check-public-safety.sh` runs public sanitation checks without starting services.
- `scripts/validate-public-shell.sh` runs backend and frontend validation without starting long-running development servers.

## What the scripts do not do

- They do not configure provider credentials.
- They do not store secrets.
- They do not run models.
- They do not enable chat runtime behavior.
- They do not start deployment infrastructure.
- They do not configure desktop packaging.

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
