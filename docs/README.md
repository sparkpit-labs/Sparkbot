# Sparkbot Documentation

This index groups the public Sparkbot documentation for first-time visitors, local developers, and release reviewers.

## Getting started

- [Contributing](../CONTRIBUTING.md): contribution scope, pull request expectations, and validation commands.
- [Security](../SECURITY.md): supported status, security report scope, and reporting guidance.
- [Development](DEVELOPMENT.md): prerequisites, backend workflow, frontend workflow, and current limitations.
- [Local Development](LOCAL_DEVELOPMENT.md): local runner scripts and what they do not enable.
- [Local Smoke Test](LOCAL_SMOKE_TEST.md): alternate-port local smoke testing without touching existing services.
- [Validation](VALIDATION.md): full validation, safety scans, backend checks, and frontend checks.

## Product surfaces

- [Workstation Surface](WORKSTATION_SHELL.md): backend-backed rooms, seats, shared context, activity, and Guardian state.
- [Chat Surface](CHAT_SHELL.md): backend-backed operator chat with shared context and narrow configured-provider execution.
- [Round Table Surface](ROUND_TABLE_SHELL.md): backend-backed meeting room sessions, configured-provider turns when available, assignments, summaries, and wrap-up notes.
- [Provider Setup Shell](PROVIDER_SETUP_SHELL.md): provider setup preview and current server-side credential boundary.
- [Guardian Controls Shell](GUARDIAN_CONTROLS_SHELL.md): planned control categories and current confirmation boundary notes.

## Release and readiness

- [Release Readiness](RELEASE_READINESS.md): current readiness position and out-of-scope runtime features.
- [Public Artifact Manifest](PUBLIC_ARTIFACT_MANIFEST.md): files included in the public baseline and excluded artifact types.
- [Release Standards](RELEASE_STANDARDS.md): public publishing identity and release standards.
- [Public v1 Clean Baseline Release Notes](RELEASE_NOTES_PUBLIC_V1_CLEAN_BASELINE.md): first published shell baseline notes.

## Roadmap and plans

- [Roadmap](ROADMAP.md): staged public v1.0.0 direction.
- [Desktop Packaging Plan](DESKTOP_PACKAGING_PLAN.md): planning-only desktop packaging direction and release gates.
- [Open Questions](OPEN_QUESTIONS.md): unresolved decisions for future public work.

## Current boundary

The current public app is safe for review and local validation. It includes backend-backed Chat, Workstation state, Round Table sessions, Command Center configuration, Spine event logging, and a fail-closed Guardian confirmation boundary for protected actions. It includes narrow Chat and Round Table model-call paths through configured provider routes. It does not include tool execution, connector calls, desktop packaging, deployment workflows, schedulers, file/process execution, device actions, or external/destructive action execution.
