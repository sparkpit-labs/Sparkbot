# Sparkbot Public v1 Frontend Audit Advisory Fix

- Tag: `public-v1-frontend-audit-fix-0`
- Status: dependency hygiene checkpoint
- Date: 2026-06-18

This checkpoint restores the frontend npm audit clean state after high-severity advisories in the public shell baseline.

This is not a broader release-readiness claim. It does not add product functionality, runtime integrations, credential handling, model calls, external sends, or connector behavior.

## Scope

- Lockfile-only update.
- Changed file: `frontend/package-lock.json`.
- Runtime behavior: unchanged.
- `frontend/package.json`: unchanged.

## Packages Resolved

- `form-data` resolved to `4.0.6`.
- `vite` resolved to `8.0.16`.

## Validation Matrix

| Check | Result |
| --- | --- |
| `npm audit --audit-level=moderate` | Pass, 0 vulnerabilities |
| Frontend tests | Pass |
| Frontend production build | Pass |
| Backend compile | Pass |
| Backend tests | Pass |
| `bash scripts/check-public-safety.sh` | Pass |
| `bash scripts/validate-public-shell.sh` | Pass |

## Known Non-Blocking Warnings

- Starlette/FastAPI `httpx` deprecation warning during backend tests.
- `whatwg-encoding` npm deprecation warning during frontend install.

## Release Position

This checkpoint keeps the public shell baseline in a clean dependency-audit state. It does not change the current product boundary or move the repository beyond the early public shell review stage.
