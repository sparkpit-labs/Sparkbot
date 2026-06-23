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
- Restarts the backend with provider calls enabled and a placeholder OpenRouter backend key.
- Verifies OpenRouter reports guarded-manual status and rejects a non-free model with `400` before provider dispatch.
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
| `SPARKBOT_SMOKE_OPENROUTER_MODEL` | Free `:free` OpenRouter model name used only for guarded status configuration. |
| `SPARKBOT_SMOKE_USE_HOST_SUBSCRIPTIONS` | Defaults to `false`; set `true` only to let the smoke backend report host Codex/Claude sign-in readiness. |
| `SPARKBOT_SMOKE_REQUIRE_SUBSCRIPTIONS` | Defaults to `false`; set `true` with host subscriptions during LIMA/operator install smoke to require Codex and Claude readiness while keeping dispatch LIMA-gated. |

## Scope Boundary

This smoke path is not an installer. It does not add:

- Desktop framework code.
- Desktop binary output.
- Installer generation.
- Code signing.
- Auto-update behavior.
- Browser provider credential entry or storage.
- Enabled cloud model calls.
- Enabled Ollama prompt calls.
- Connector sends or tool execution.

The enabled local-model check only verifies the read-only local status path with `SPARKBOT_LOCAL_MODELS_ENABLED=true`. It does not send a prompt to Ollama. The OpenRouter guarded-mode check uses a placeholder backend key and intentionally rejected non-free model request; it does not send a successful cloud prompt by default. The subscription-readiness assertion only reads provider status from Sparkbot and does not dispatch Codex or Claude CLI prompts.

## Manual Smoke Path

For manual alternate-port testing, see `LOCAL_SMOKE_TEST.md`.
