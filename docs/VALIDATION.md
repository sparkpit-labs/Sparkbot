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

It does not start long-running development servers and does not require secrets.

## Public safety scan

```bash
bash scripts/check-public-safety.sh
```

This script performs:

- strict blocked-term scan for private or unsafe public-release references
- publishing identity scan with the expected release standards line allowed
- emoji and non-BMP character scan

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

## Local smoke check

After starting local development servers, verify them with:

```bash
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
