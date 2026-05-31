# Changelog

This changelog tracks public Sparkbot repository baselines and release-facing documentation.

## Unreleased

### Added

- Chat Shell preview with disabled read-only planned composer and no send action.
- Chat Shell documentation describing the public skeleton boundary.
- Local development runner scripts for backend and frontend dev servers.
- Public safety scan helper and local development documentation.
- Desktop packaging planning document with candidate paths, decision criteria, and release gates.
- Public visitor README polish and documentation index.

### Not Included

- No real chat runtime, message persistence, model calls, provider credentials, backend chat endpoint, desktop app, installer, auto-update path, or code signing setup.

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
