# Validation

Validation commands in this repository are intended for local development checks only.

## Full public-shell validation

```bash
bash scripts/validate-public-shell.sh
```

This script performs:

- backend bytecode compilation
- temporary backend virtual environment creation outside the repository
- backend development dependency install
- backend tests
- frontend dependency install
- frontend moderate-level npm audit
- frontend tests
- frontend production build

It does not start long-running development servers and does not require secrets. Backend and frontend tests include capability contract checks that keep guarded-future surfaces from being promoted accidentally.

## Public safety scan

```bash
bash scripts/check-public-safety.sh
```

This script performs:

- strict blocked-term scan for private or unsafe public-release references
- publishing identity scan with the expected release standards line allowed
- emoji and non-BMP character scan

## Branch hygiene check

```bash
bash scripts/check-branch-hygiene.sh
```

This release-manager check verifies that the public remote has only `main` by default. It is intentionally separate from `validate-public-shell.sh` so normal feature-branch and fork review workflows do not fail only because a temporary review branch exists. Use `SPARKBOT_ALLOWED_BRANCH_REGEX` only for intentional active review branches.

## Manual backend validation

```bash
python3 -m compileall backend

rm -rf /tmp/sparkbot-public-readiness-backend-venv
python3 -m venv /tmp/sparkbot-public-readiness-backend-venv
. /tmp/sparkbot-public-readiness-backend-venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e "backend[dev]"
pytest backend/tests -q
deactivate
rm -rf /tmp/sparkbot-public-readiness-backend-venv
```

## Manual frontend validation

```bash
cd frontend
npm ci
npm audit --audit-level=moderate
npm test -- --run
npm run build
cd ..
```

## Public validation workflow

The `.github/workflows/validate-public-shell.yml` workflow runs on pull requests and pushes to `main`. It uses Python 3.12 and Node 20.19.0, then runs the public safety scan and full public shell validation without secrets, deployment, containers, or production assumptions.

## Local smoke check

After starting local development servers, verify `/health`, `/capabilities`, `/chat/status`, `/provider-config/status`, `/connector-status`, `/guardian/status`, `/round-table/status`, `/model-seats/status`, `/work-lanes/status`, `/local/chat/sessions`, `/local/memory-notes`, `/local/work-lane-cards`, `/local/export`, `/local-models/status`, disabled-mode `POST /local-models/ollama/prompt` returning 403, and the frontend URL. The capabilities response must use the public contract statuses `available`, `preview`, `planned`, `disabled-by-default`, and `guarded-future`:

```bash
SPARKBOT_DATA_DIR="$(mktemp -d)" \
SPARKBOT_BACKEND_URL=http://127.0.0.1:18000 \
SPARKBOT_FRONTEND_URL=http://127.0.0.1:15173 \
bash scripts/smoke-check-local.sh
```

See `LOCAL_SMOKE_TEST.md` for the complete alternate-port flow.

## Development server scripts

The development server scripts are opt-in only and are not part of full validation:

```bash
bash scripts/start-backend-dev.sh
bash scripts/start-frontend-dev.sh
```
