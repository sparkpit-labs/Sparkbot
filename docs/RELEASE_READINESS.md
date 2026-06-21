# Release Readiness

This document tracks public shell readiness for review and phased release decisions.

## Current baseline

- Backend: local read-only health, capabilities, Chat status, provider configuration status, connector status, Guardian policy status, Round Table status, Model Seat status, Task Lane status, local Workstation export, and local runtime settings endpoints are present and validated.
- Frontend: static shell previews are present and can display backend capability and Chat status data with local fallback. The Workstation shell can download a read-only local JSON export and show read-only local runtime settings.
- Desktop readiness: `scripts/run-local-smoke-test.sh` provides a one-command local smoke path for alternate ports, temporary data-dir behavior, disabled local-model prompt behavior, and enabled local-model status behavior. No installer or desktop binary is included.
- Workstation, Chat, Round Table, Provider Setup, and Guardian Controls are preview or status surfaces with runtime behavior disabled.

## Not yet in scope

- Provider credential workflows
- Model execution and routing
- Approval token workflows
- Policy enforcement runtime
- Sensitive action execution
- Desktop packaging and install artifacts
- Installer, desktop framework, signing, and auto-update implementation
- Desktop binaries, installers, auto-update, and code signing
- Deployment workflows

## Readiness position

This repository is suitable for professional public review as an early shell baseline.

This repository does not claim production readiness or complete product functionality.

## V1.0.0 RC0 audit position

The `v1.0.0-rc0` checkpoint is a release-candidate audit tag, not a final production claim. It records full validation, dependency audit, public safety scans, branch hygiene cleanup, docs review, and local smoke evidence for the current public baseline.

A live Ollama prompt smoke is not required for the tag unless a local Ollama daemon is already running. The RC0 audit confirms the disabled path and the enabled-but-offline local status path without sending a prompt.

## Dependency hygiene checkpoint

The `public-v1-frontend-audit-fix-0` tag records a lockfile-only frontend audit advisory fix.

- Purpose: restore npm audit clean state after high-severity advisories.
- Scope: `frontend/package-lock.json` only.
- Runtime behavior: unchanged.
- Resolved packages: `form-data` to `4.0.6`, `vite` to `8.0.16`.
- Validation: npm audit, frontend tests/build, backend compile/tests, public safety scan, and full public shell validation passed.
- Known non-blocking warnings: Starlette/FastAPI `httpx` deprecation warning during backend tests; `whatwg-encoding` npm deprecation warning during frontend install.

This checkpoint does not broaden release readiness beyond the early public shell review baseline.

## Capabilities status checkpoint

The `public-v1-capabilities-status-0` checkpoint adds a read-only `GET /capabilities` backend endpoint and frontend capability status display with local fallback. It does not add model calls, provider credential handling, chat runtime, Guardian enforcement, connector sends, or desktop installer behavior.

## Capability safety contracts checkpoint

The public capability safety contracts define review gates for future runtime work. They do not add runtime behavior. The backend capabilities endpoint and frontend fallback status model are expected to use the same contract statuses. Future branches that introduce provider setup, model calls, credential handling, connector actions, tool execution, persistence, or Guardian enforcement must satisfy these contracts before public merge:

- `docs/PUBLIC_CAPABILITY_CONTRACTS.md`
- `docs/CONNECTOR_SAFETY_CONTRACT.md`
- `docs/PROVIDER_CONFIG_CONTRACT.md`
- `docs/GUARDIAN_POLICY_CONTRACT.md`

## Desktop packaging status

Desktop packaging is planned but not implemented. The current repository contains planning notes and release gates only. No installer, desktop binary, auto-update path, or code signing configuration is present.

## Contribution and security posture

The repository includes lightweight contribution and security reporting guidance for quiet public review. The current baseline does not provide a production support guarantee.
