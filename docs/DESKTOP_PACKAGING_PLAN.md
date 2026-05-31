# Desktop Packaging Plan

This document describes the planned desktop packaging direction for Sparkbot. Desktop packaging is not implemented in the current repository state.

## Current status

- No desktop app exists yet.
- No installer exists yet.
- No desktop binary exists yet.
- No auto-update path exists yet.
- No code signing setup exists yet.
- The current supported path is local development mode with the backend and frontend run separately.

## Target platforms

1. Windows first
2. Linux later
3. macOS later, if the packaging path and signing requirements are justified

Windows is the first target because it is the most important local-first desktop path for the intended public workstation audience.

## Candidate packaging paths

### Tauri

Tauri is a candidate because it can provide a smaller desktop wrapper around the existing frontend while keeping the backend/frontend split explicit. It would require a clear decision on how the local backend process is started, supervised, updated, and stopped.

### Electron

Electron is a candidate because it has broad packaging maturity and familiar desktop distribution patterns. It would likely have a larger install footprint and should be chosen only if the development and support tradeoffs justify it.

### Web app plus local backend runner

This path keeps the current architecture closest to the existing public baseline. The frontend remains a web app, and the backend runs as an explicit local service started by the user or a future local runner. This is the simplest near-term validation path.

### Plain local development mode

This is the current baseline. Users install backend and frontend dependencies, run validation, then start local backend and frontend development servers explicitly. This is not a packaged desktop release.

## Decision criteria

- Smallest reasonable install footprint
- Local-first operation
- Simple user install path
- Compatibility with the backend/frontend split
- Clear process lifecycle for the local backend
- Code signing requirements and cost
- Update strategy
- Security posture
- Fresh install reliability
- Uninstall and reinstall behavior
- Public build reproducibility

## Release gates

Desktop packaging should not be claimed until these gates pass:

- Fresh clone validation passes.
- Backend build and tests pass.
- Frontend install, audit, tests, and build pass.
- Local runtime smoke test passes.
- Installer smoke test passes on the target platform.
- Uninstall and reinstall test passes.
- No secrets are present in artifacts.
- Public safety scan is clean.
- Code signing decision is documented.
- Versioning and artifact naming are documented.
- Update strategy is documented, even if automatic updates are intentionally deferred.

## Explicit exclusions for the current branch

- No installer is added.
- No desktop binary is added.
- No desktop framework is added.
- No auto-update implementation is added.
- No code signing configuration is added.
- No production packaging claim is made.
- No provider setup, credential storage, model calls, chat runtime, Guardian runtime, terminal, tool execution, connector calls, or deployment behavior is added.

## Next planning steps

1. Decide whether the first packaged path should be Tauri, Electron, or a web app plus local backend runner.
2. Define the local backend process lifecycle for a packaged app.
3. Define Windows smoke tests for install, launch, local health check, shutdown, uninstall, and reinstall.
4. Define artifact naming, versioning, and signing expectations.
5. Keep the local development mode as the fallback path until a packaged path is validated.
