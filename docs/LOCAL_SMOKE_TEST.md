# Local Smoke Test

This guide verifies that the public Sparkbot shell can run locally on alternate localhost ports without touching existing development or server processes.

The smoke test starts only local development servers that you launch for the test. It does not configure provider credentials, call models, run connectors, execute tools, or start deployment infrastructure. Chat and Workstation state are local backend features when the backend is running.

## Default ports

By default, the development scripts use:

- Backend: `127.0.0.1:8000`
- Frontend: `127.0.0.1:5173`
- Frontend API base URL: `http://127.0.0.1:8000`

Use alternate ports when either default port is already occupied.

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

Expected result:

```text
PASS: local Sparkbot shell smoke check completed
```

## Browser check

Open:

```text
http://127.0.0.1:15173
```

The page should show Sparkbot navigation for Workstation, Chat, Command Center, Spine, and Controls, plus the backend health panel. Chat and Workstation should be labeled as backend-backed local surfaces. Chat model execution should be limited to the selected configured provider route; connector sends and Round Table live provider seats should remain deferred.

## Cleanup

Stop only the backend and frontend processes that you started for the smoke test. Do not stop unrelated local services.
