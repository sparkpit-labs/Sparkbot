# Server Baseline

This repository now includes a functional local Workstation MVP backend for Sparkbot.

## What Exists

- FastAPI server under `backend/app`.
- Health endpoint at `GET /health`.
- Local settings with safe defaults in `backend/app/core/settings.py`.
- Shared local SQLite Workstation store.
- Command Center routes for provider/model configuration, seats, agents, invite routes, and local safety state.
- Chat routes for sessions, messages, shared context recall, and configured-provider execution.
- Round Table routes for rooms, sessions, provider-capable meeting flow, deterministic fallback, assignments, summaries, notes, and events.
- Memory, notes, events, history, confirmations, and task record routes.
- Backend test coverage for public-safe persistence, redaction, fail-closed behavior, provider routing, memory, notes/history, Round Table, and task records.

## What Is Intentionally Excluded

- Desktop packaging layers.
- Production deployment wiring.
- Background workers, schedulers, recurring jobs, or automatic runners.
- Connector write flows or external sends.
- File/process/terminal/browser/device automation.
- Local CLI-backed subscription-auth execution.
- Full private Guardian/Vault/platform-internal services.

## Local Commands

From the repository root:

```bash
bash scripts/start-backend-dev.sh
```

Manual validation:

```bash
python3 -m compileall backend
pytest backend/tests -q
```
