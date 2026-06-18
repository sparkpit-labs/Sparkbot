# Release Readiness

This document tracks public shell readiness for review and phased release decisions.

## Current baseline

- Backend: local read-only health endpoint is present and validated.
- Frontend: static shell previews are present and validated.
- Workstation, Round Table, Provider Setup, and Guardian Controls are preview or skeleton surfaces.

## Not yet in scope

- Provider credential workflows
- Model execution and routing
- Approval token workflows
- Policy enforcement runtime
- Sensitive action execution
- Desktop packaging and install artifacts
- Desktop binaries, installers, auto-update, and code signing
- Deployment workflows

## Readiness position

This repository is suitable for professional public review as an early shell baseline.

This repository does not claim production readiness or complete product functionality.

## Dependency hygiene checkpoint

The `public-v1-frontend-audit-fix-0` tag records a lockfile-only frontend audit advisory fix.

- Purpose: restore npm audit clean state after high-severity advisories.
- Scope: `frontend/package-lock.json` only.
- Runtime behavior: unchanged.
- Resolved packages: `form-data` to `4.0.6`, `vite` to `8.0.16`.
- Validation: npm audit, frontend tests/build, backend compile/tests, public safety scan, and full public shell validation passed.
- Known non-blocking warnings: Starlette/FastAPI `httpx` deprecation warning during backend tests; `whatwg-encoding` npm deprecation warning during frontend install.

This checkpoint does not broaden release readiness beyond the early public shell review baseline.

## Desktop packaging status

Desktop packaging is planned but not implemented. The current repository contains planning notes and release gates only. No installer, desktop binary, auto-update path, or code signing configuration is present.

## Contribution and security posture

The repository includes lightweight contribution and security reporting guidance for quiet public review. The current baseline does not provide a production support guarantee.
