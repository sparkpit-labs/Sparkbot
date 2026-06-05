# Frontend Baseline

This repository now includes a functional local Workstation MVP frontend for Sparkbot.

## What Exists

- React and TypeScript frontend under `frontend/`.
- Vite-based build pipeline with `npm run build`.
- Health panel for backend `GET /health`.
- Configurable API base URL via `VITE_SPARKBOT_API_BASE_URL`.
- Frontend test coverage with Vitest and Testing Library.
- Routes for `/workstation`, `/chat`, `/roundtable`, `/command-center`, `/spine`, and `/controls`.
- Backend-backed Workstation, Chat, Round Table, Command Center, Spine, notes/history, task records, and Controls views.
- Disabled/fail-closed UI for unsupported run/write-mode execution paths.

## What Is Intentionally Excluded

- Desktop packaging.
- Production or staging deployment assumptions.
- Connector write flows and external sends.
- File/process/terminal/browser/device automation.
- Scheduler/runner execution.
- Local CLI-backed subscription-auth execution.
- Full private Guardian/Vault/platform-internal UI.

## Local Development Commands

From the repository root:

```bash
cd frontend
npm ci
npm test -- --run
npm run build
```

## Validation Commands

```bash
git status --short --branch
python3 -m compileall backend
cd frontend && npm test -- --run && npm run build
```

## Status Limitations

The frontend is ready for internal MVP review, not production release. Public setup and release documentation should continue to distinguish active local Workstation behavior from disabled automation and future packaging work.

## Dependency Advisory Status

Frontend development tooling was updated to clear the Vite development server advisory chain during earlier shell work. Contributors should use Node 20.19.0 or newer for the current Vite toolchain.
