# Desktop Smoke Readiness

Sparkbot does not include a desktop installer or desktop binary yet. This document defines the current local-first smoke path used before any packaging work is approved.

## One-Command Smoke Path

From the repository root:

```bash
bash scripts/run-local-smoke-test.sh
```

The script:

- Prepares missing local backend dev dependencies in `.venv-local`.
- Prepares missing frontend dependencies with `npm ci`.
- Starts the backend on an alternate localhost port.
- Starts the frontend on an alternate localhost port.
- Uses a temporary local data directory by default.
- Runs `scripts/smoke-check-local.sh` against the running services.
- Verifies `/local/runtime/settings` reports the smoke data directory.
- Verifies the default Ollama-disabled prompt path returns `403`.
- Restarts the backend with local models enabled.
- Verifies enabled local-model status is still localhost-only.
- Stops the smoke backend and frontend processes that it started.

Default smoke ports:

```text
Backend: 127.0.0.1:18080
Frontend: 127.0.0.1:15180
```

Use these environment variables to override the defaults:

| Variable | Purpose |
| --- | --- |
| `SPARKBOT_SMOKE_BACKEND_PORT` | Backend smoke port. |
| `SPARKBOT_SMOKE_FRONTEND_PORT` | Frontend smoke port. |
| `SPARKBOT_SMOKE_DATA_DIR` | Optional data directory to preserve after the run. |
| `SPARKBOT_SMOKE_OLLAMA_MODEL` | Model name used only for enabled local-model status configuration. |

## Scope Boundary

This smoke path is not an installer. It does not add:

- Desktop framework code.
- Desktop binary output.
- Installer generation.
- Code signing.
- Auto-update behavior.
- Provider credentials.
- Cloud model calls.
- Enabled Ollama prompt calls.
- Connector sends or tool execution.

The enabled local-model check only verifies the read-only local status path with `SPARKBOT_LOCAL_MODELS_ENABLED=true`. It does not send a prompt to Ollama.

## Manual Smoke Path

For manual alternate-port testing, see `LOCAL_SMOKE_TEST.md`.
