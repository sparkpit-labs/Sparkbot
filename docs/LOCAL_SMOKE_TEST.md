# Local Smoke Test

This guide verifies that the public Sparkbot shell can run locally on alternate localhost ports without touching existing development or server processes.

The manual smoke test starts only local development servers that you launch for the test. It does not configure real provider credentials, call cloud models by default, enable chat runtime behavior, run connectors, execute tools, or start deployment infrastructure. The provider check verifies the OpenRouter disabled gate unless the backend was explicitly started with provider calls enabled. The one-command wrapper additionally starts a backend with short placeholder keys for every API-key provider to verify all provider cards configure cleanly, OpenRouter reports guarded-manual availability, non-OpenRouter API providers remain onboarding/status-only, and free-model enforcement rejects one intentionally non-free OpenRouter request before provider dispatch. The local model check verifies disabled-mode behavior by default.

For the current one-command desktop-readiness path, run:

```bash
bash scripts/run-local-smoke-test.sh
```

That wrapper prepares missing local dev dependencies, starts backend and frontend on alternate localhost ports, uses a temporary local data directory, runs this smoke check, verifies the reported data directory, restarts the backend with provider calls enabled and placeholder backend provider keys to prove API-key provider onboarding plus the guarded OpenRouter free-model path, restarts again with local models enabled, verifies the enabled local-model status path, and stops the smoke servers. It isolates Codex and Claude subscription homes by default so validation does not depend on the host user. It does not run an Ollama prompt and does not send a successful cloud prompt.

## Default ports

By default, the development scripts use:

- Backend: `127.0.0.1:8000`
- Frontend: `127.0.0.1:5173`
- Frontend API base URL: `http://127.0.0.1:8000`

Use alternate ports when either default port is already occupied. The one-command smoke wrapper defaults to backend port `18080` and frontend port `15180`; override those with `SPARKBOT_SMOKE_BACKEND_PORT` and `SPARKBOT_SMOKE_FRONTEND_PORT`.

## Subscription sign-in smoke option

The one-command wrapper isolates `CODEX_HOME` and `CLAUDE_HOME` by default so local validation is reproducible and does not depend on host subscription sign-ins. To verify an already signed-in host Codex or Claude setup during a LIMA/operator test, opt in explicitly:

```bash
SPARKBOT_SMOKE_USE_HOST_SUBSCRIPTIONS=true bash scripts/run-local-smoke-test.sh
```

This still does not dispatch Codex or Claude prompts. It only allows Provider Setup to report host CLI/sign-in readiness. To make this an assertion during LIMA/operator install testing, require both subscription cards to be ready:

```bash
SPARKBOT_SMOKE_USE_HOST_SUBSCRIPTIONS=true \
SPARKBOT_SMOKE_REQUIRE_SUBSCRIPTIONS=true \
bash scripts/run-local-smoke-test.sh
```

That mode fails unless Codex and Claude each report CLI availability, sign-in detection, `configured=true`, `status=disabled-by-default`, and `runtime_gate=lima-guardian-required`. It confirms readiness for the LIMA Guardian adapter without running either CLI.

## Start backend on an alternate port

From the repository root:

```bash
SPARKBOT_BACKEND_PORT=18000 bash scripts/start-backend-dev.sh
```

The backend script supports:

- `SPARKBOT_BACKEND_HOST`, default `127.0.0.1`
- `SPARKBOT_BACKEND_PORT`, default `8000`

The script only allows `127.0.0.1` or `localhost` as the bind host.

## Start frontend on an alternate port

In a second terminal, from the repository root:

```bash
SPARKBOT_BACKEND_PORT=18000 \
VITE_SPARKBOT_API_BASE_URL=http://127.0.0.1:18000 \
SPARKBOT_FRONTEND_PORT=15173 \
bash scripts/start-frontend-dev.sh
```

The frontend script supports:

- `SPARKBOT_FRONTEND_HOST`, default `127.0.0.1`
- `SPARKBOT_FRONTEND_PORT`, default `5173`
- `SPARKBOT_BACKEND_PORT`, default `8000`
- `VITE_SPARKBOT_API_BASE_URL`, default `http://127.0.0.1:${SPARKBOT_BACKEND_PORT}`

The script only allows `127.0.0.1` or `localhost` as the bind host.

## Run the smoke check

In a third terminal, from the repository root:

```bash
SPARKBOT_BACKEND_URL=http://127.0.0.1:18000 \
SPARKBOT_FRONTEND_URL=http://127.0.0.1:15173 \
bash scripts/smoke-check-local.sh
```

The smoke check script supports:

- `SPARKBOT_BACKEND_URL`, default `http://127.0.0.1:8000`
- `SPARKBOT_FRONTEND_URL`, default `http://127.0.0.1:5173`

It verifies backend `/health`, backend `/capabilities`, backend `/chat/status`, backend `/provider-config/status`, provider cards for local Ollama, OpenRouter, API-key providers, Codex subscription, and Claude subscription, disabled-mode `POST /provider-config/openrouter/prompt` returning 403 when provider calls are off, backend `/connector-status`, backend `/guardian/status` including the LIMA provider execution boundary, backend `/round-table/status`, backend `/model-seats/status`, `/work-lanes/status`, `/local/chat/sessions`, `/local/memory-notes`, `/local/work-lane-cards`, `/local/export`, `/local/runtime/settings`, `/local-models/status`, disabled-mode `POST /local-models/ollama/prompt` returning 403, and the frontend HTTP response. The one-command wrapper also verifies all API-key provider cards with placeholder backend keys, OpenRouter guarded-manual status with `SPARKBOT_PROVIDER_CALLS_ENABLED=true`, non-OpenRouter API providers staying `disabled-by-default`, and a non-free OpenRouter model request returning 400 before provider dispatch.

Expected result:

```text
PASS: local Sparkbot shell smoke check completed
```

## Browser check

Open:

```text
http://127.0.0.1:15173
```

The page should show the Sparkbot shell with Workstation navigation, local runtime panels, local data export, local runtime settings, disabled-by-default Local Ollama adapter status, preview-only Chat status, Round Table, Model Seats, Provider Setup with the OpenRouter Free Model Smoke panel and Codex/Claude subscription readiness cards, Connector Status, Guardian Controls with the LIMA provider execution boundary, backend capability statuses when available, and the read-only backend health panel.

## Cleanup

Stop only the backend and frontend processes that you started for the smoke test. Do not stop unrelated local services.

Use `SPARKBOT_DATA_DIR` with a temporary directory when smoke testing local runtime CRUD so test data stays outside the repository. The one-command wrapper creates a temporary data directory automatically unless `SPARKBOT_SMOKE_DATA_DIR` is set.
