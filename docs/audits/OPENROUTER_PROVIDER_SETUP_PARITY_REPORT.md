# OpenRouter Provider Setup Parity Report

## Branch And Base

- Branch: `fix-openrouter-provider-setup-parity`
- Base branch: `mvp-workstation-model-capability-boundary`
- Base commit: `1c6a42232c28281bf37eb1bce3ae159afd03537b`

## Issue

Operator review found that the public Command Center did not behave like the expected OpenRouter setup flow. Credentials could be saved server-side, but the UI did not automatically refresh OpenRouter models after saving a key, and refreshed model rows were only held in transient browser state. A reload returned the static preloaded model list, which made setup feel stale and disconnected.

## Reference Behavior Inspected

R&D reference files inspected:

- `backend/app/api/routes/chat/model.py`
- `frontend/src/hooks/useControlsState.ts`
- Command Center setup panels that trigger OpenRouter model refresh

Observed behavior:

- OpenRouter model refresh calls the OpenRouter models API through the backend.
- The frontend refreshes OpenRouter models after saving an OpenRouter credential.
- The model picker is expected to update from the fetched OpenRouter catalog instead of only showing a static preload list.

## Public Behavior Before This Branch

- `POST /api/v1/chat/models/config` saved provider credentials server-side without echoing values.
- `GET /api/v1/chat/openrouter/models` fetched OpenRouter rows but returned them only to the current browser session.
- `GET /api/v1/chat/models/config` continued to expose the static OpenRouter model list after refresh.
- Command Center did not auto-refresh OpenRouter models after saving the OpenRouter key.
- Provider cards displayed `Ready` when static models existed, which blurred the difference between a saved credential and a preloaded model list.

## Changes Made

Backend:

- Added a persisted `provider_model_catalog` section in Command Center config.
- Persisted refreshed OpenRouter model rows in server-side config without storing credentials in that catalog.
- Merged refreshed OpenRouter model IDs and labels into the controls response.
- Returned an updated controls snapshot from `/api/v1/chat/openrouter/models`.
- Logged a safe `provider.model_catalog.refreshed` event with provider name and model count only.

Frontend:

- Updated `fetchOpenRouterModels` to accept the optional controls snapshot returned by the backend.
- Made Command Center apply refreshed controls and model rows after manual OpenRouter refresh.
- Made OpenRouter credential save trigger model refresh automatically.
- Updated provider status labels so saved credentials are distinct from static/preloaded model availability.

Tests:

- Added backend regression coverage for OpenRouter credential save plus model refresh.
- Verified refreshed OpenRouter models persist into subsequent controls readback.
- Verified dynamic labels appear in model labels.
- Verified selecting a refreshed OpenRouter model as default succeeds.
- Verified the credential is not echoed in refresh responses, controls responses, or events.

## Safety Behavior

- Provider credentials remain server-side only in the existing secrets file.
- Refreshed model catalog stores model metadata only.
- Event payloads store provider name and model count only.
- No prompt, model output, request body, response body, headers, or credential values are stored in events.
- No new provider execution, connector behavior, background work, subprocess execution, or subscription auth behavior was added.

## Validation Results

- `git diff --check`: pass
- `backend tests`: `54 passed, 1 warning`
- `frontend tests`: `10 passed`
- `frontend build`: pass
- `npm audit --audit-level=moderate`: `0 vulnerabilities`
- `bash scripts/check-public-safety.sh`: pass
- `bash scripts/validate-public-shell.sh`: pass, including backend tests, frontend tests, build, and audit

## Remaining Warnings

- Live OpenRouter behavior still requires the operator to provide a valid local test credential. No live credential was used or committed in this branch.
- If OpenRouter is unreachable or the key is invalid, the key can still be saved but the model refresh reports a user-visible refresh failure.
- The public app still does not implement CLI-backed subscription auth, connectors, schedulers, or write-mode execution.

## Verdict

`PASS_WITH_WARNINGS`

The OpenRouter setup path now matches the expected MVP behavior more closely: save a server-side key, refresh the live OpenRouter catalog through the backend, persist the refreshed catalog into shared controls state, and expose refreshed model choices after reload without leaking credentials.
