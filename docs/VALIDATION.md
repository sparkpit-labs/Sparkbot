# Validation

Validation commands in this repository are intended for local development checks only.

## Full public-shell validation

```bash
bash scripts/validate-public-shell.sh
```

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
