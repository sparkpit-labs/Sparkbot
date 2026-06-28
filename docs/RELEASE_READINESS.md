# Release Readiness

This document tracks public shell readiness for review and phased release decisions.

## Current baseline

- Backend: local read-only health, capabilities, Chat status, provider configuration status, connector status, Guardian policy status, Round Table status, Model Seat status, Task Lane status, local Workstation export, and local runtime settings endpoints are present and validated.
- Frontend: static shell previews are present and can display backend capability and Chat status data with local fallback. The Workstation shell can download a read-only local JSON export and show read-only local runtime settings.
- Desktop readiness: `scripts/run-local-smoke-test.sh` provides a one-command local smoke path for alternate ports, temporary data-dir behavior, disabled local-model prompt behavior, and enabled local-model status behavior. No installer or desktop binary is included.
- Workstation, Chat, Round Table, and Guardian Controls remain bounded public-shell surfaces. Provider Setup includes guarded explicit prompt smoke paths, but provider calls are disabled by default and credential storage remains out of scope.

## Not yet in scope

- Browser credential entry or credential storage
- Automatic model execution, broad routing, and provider fallback
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

## Provider runtime evidence position

Sparkbot repo-side provider onboarding is wired and validated for OpenRouter free-model enforcement, API-key provider status, prototype-aligned model examples, Codex/Claude subscription aliases, and fail-closed LIMA adapter delegation.

Two operator install-test evidence items remain TODO-later and are intentionally outside default validation because they require external credentials or an external localhost adapter:

- Real OpenRouter free-model smoke with an operator-owned `OPENROUTER_API_KEY`: `scripts/run-openrouter-free-smoke.sh`.
- Real Codex/Claude subscription dispatch through the localhost LIMA Guardian provider adapter: `scripts/run-lima-install-provider-smoke.sh`.

Until those sanitized reports are collected, release notes should describe those paths as supported guarded smoke paths rather than completed install evidence.

## V1.0.0 final release position

The `v1.0.0` checkpoint finalizes the validated public shell baseline after the RC0 audit. It records final release notes, final validation, dependency audit, public safety scans, branch hygiene, and local smoke evidence.

This final tag does not broaden the product boundary. It does not add an installer, desktop binary, cloud provider runtime, credential storage, connector sends, tool execution, Guardian enforcement runtime, or production deployment workflow.

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
