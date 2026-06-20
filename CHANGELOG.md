# Changelog

This changelog tracks public Sparkbot repository baselines and release-facing documentation.

## Unreleased

### Added

- Read-only Task Lane status endpoint and frontend status display with local fallback.
- Read-only Model Seat status endpoint and frontend status display with local fallback.
- Public capability, connector safety, provider configuration, and Guardian policy contracts for future implementation gates.
- Capabilities endpoint and frontend status model alignment with public contract statuses, including guarded-future capability entries.
- Workstation dashboard polish with a read-only public baseline status panel and clearer capability grouping.
- Read-only Chat status endpoint and frontend status display with local fallback.
- Read-only Guardian policy status endpoint and frontend status display with local fallback.
- Public branch hygiene check script and documentation for detecting unexpected remote branches.
- Read-only Round Table status endpoint and frontend status display with local fallback.
- Read-only connector status endpoint and frontend status display with local fallback.
- Read-only provider configuration status endpoint and frontend status display with local fallback.
- Read-only backend `GET /capabilities` endpoint and frontend capability status display with local fallback.
- Full public validation GitHub Action for pushes to `main` and pull requests.
- Release notes for the `public-v1-frontend-audit-fix-0` dependency hygiene checkpoint.
- Local smoke readiness checkpoint with alternate localhost ports and confirmed manual browser smoke.
- Chat Shell preview with disabled read-only planned composer and no send action.
- Chat Shell documentation describing the public skeleton boundary.
- Local development runner scripts for backend and frontend dev servers.
- Public safety scan helper and local development documentation.
- Desktop packaging planning document with candidate paths, decision criteria, and release gates.
- Public visitor README polish and documentation index.
- Lightweight contribution and security reporting docs for quiet public review.

### Not Included

- No real chat runtime, message persistence, model calls, provider credentials, backend chat endpoint, connector runtime, Guardian enforcement runtime, desktop app, installer, auto-update path, or code signing setup.

## public-v1-frontend-audit-fix-0 - 2026-06-18

This tag is a dependency hygiene checkpoint for the public shell baseline. It restores the frontend npm audit clean state after high-severity advisories without changing runtime behavior.

### Changed

- Updated `frontend/package-lock.json` only.
- Resolved `form-data` to `4.0.6`.
- Resolved `vite` to `8.0.16`.

### Validation

- `npm audit --audit-level=moderate`: 0 vulnerabilities.
- Frontend tests and production build: pass.
- Backend compile and tests: pass.
- `bash scripts/check-public-safety.sh`: pass.
- `bash scripts/validate-public-shell.sh`: pass.

### Known Non-Blocking Warnings

- Starlette/FastAPI `httpx` deprecation warning during backend tests.
- `whatwg-encoding` npm deprecation warning during frontend install.

## public-v1-clean-baseline-0 - 2026-05-30

This tag is an early public shell baseline for review, validation, and continued public development. It is not a complete product release.

### Added

- Backend health endpoint skeleton with a local read-only `GET /health` route.
- Frontend shell for the public Sparkbot workstation baseline.
- Workstation preview as a read-only product layout.
- Round Table preview with inert planned seats.
- Provider Setup preview with planned provider cards and no credential handling.
- Guardian Controls preview with planned control categories and no runtime enforcement.
- Public validation script for backend and frontend checks.
- MIT License with repository-only scope.
- Public release-readiness docs, validation docs, and artifact manifest.

### Not Included

- No desktop app or installer.
- No real provider setup or credential storage.
- No model calls or model routing.
- No chat runtime.
- No Round Table meeting engine.
- No Guardian policy enforcement runtime.
- No tool execution or sensitive action paths.
