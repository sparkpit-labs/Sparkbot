# Changelog

This changelog tracks public Sparkbot repository baselines and release-facing documentation.

## Unreleased

### Added

- Local Workstation MVP surfaces for Command Center, Chat, Round Table, Workstation, Spine, and Controls.
- Shared local SQLite Workstation store for rooms, seats, agents, invite routes, memory, notes, events, Chat, Round Table, confirmations, and task records.
- Provider/model configuration with server-side credential storage and configured-provider execution for Chat and Round Table.
- Agents Wing creation/editing and seat assignment for Round Table participation.
- Persistent memory/context recall, notes/history visibility, Spine events, dashboard counters, producer metadata, and manual task records.
- Fail-closed public Task Guardian visibility for run/write-mode requests.
- Local smoke readiness checkpoint with alternate localhost ports and confirmed manual browser smoke.
- Public safety scan helper and local development documentation.
- Desktop packaging planning document with candidate paths, decision criteria, and release gates.
- Lightweight contribution and security reporting docs for public review.

### Not Included

- No production deployment or production support guarantee.
- No desktop app, installer, auto-update path, or code signing setup.
- No background scheduler, automatic runner, reminders engine, connector write flow, external send, file/process/terminal/browser/device automation, or local CLI-backed subscription-auth execution.
- No full private Guardian, Vault, or platform-internal control system.

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
