# Development

This repository is an early public shell baseline for local development and review.

## Prerequisites

- Python 3.11 or newer
- Node.js 20.19.0 or newer
- npm

## Backend local workflow

```bash
python3 -m venv .venv-local
. .venv-local/bin/activate
python -m pip install --upgrade pip
python -m pip install -e "backend[dev]"
python -m compileall backend
pytest backend/tests -q
```

The backend currently exposes a local read-only health endpoint at `GET /health`.

## Frontend local workflow

```bash
cd frontend
npm ci
npm audit --audit-level=moderate
npm test -- --run
npm run build
cd ..
```

The frontend currently presents static shell previews for Workstation, Round Table, Provider Setup, and Guardian Controls.

## Current limitations

- No provider credentials are accepted, stored, or transmitted.
- No model calls or model routing are active.
- No approval or policy enforcement runtime is active.
- No sensitive action execution path is active.
- Desktop packaging and release artifacts are future work.
