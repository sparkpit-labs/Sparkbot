# Provider Configuration Contract

This contract defines the public safety requirements for provider setup, model routing, and provider prompt work.

## Current Boundary

Provider Setup is an `available` capability for backend-owned, environment-driven onboarding/status. The browser may show whether a provider is configured, the configured source name, auth mode, default model, and model examples. The browser must not accept, store, echo, or transmit provider credentials.

API-key providers have guarded backend prompt endpoints for explicit operator calls. OpenRouter remains the default free-model path:

```text
POST /provider-config/{provider_id}/prompt
```

Provider prompt endpoints are disabled unless `SPARKBOT_PROVIDER_CALLS_ENABLED=true` and the selected provider env key is configured in the backend environment. OpenRouter model IDs ending in `:free` are enforced unless the operator explicitly sets `SPARKBOT_ALLOW_PAID_OPENROUTER_MODELS=true`. The frontend exposes an explicit provider smoke form for these endpoints, but it may send only provider ID, prompt text, and model ID; credentials remain backend environment values.

Codex and Claude subscription providers expose CLI availability, sign-in detection, runtime-gate status, LIMA adapter configuration state, and next operator action. Their prompt endpoints are supported only as fail-closed delegation to a configured localhost LIMA Guardian provider adapter. See `LIMA_PROVIDER_GUARDIAN_ADAPTER.md` for the public dispatch boundary.

## Provider Setup Rules

- Provider setup is backend-owned and environment-driven.
- Credential entry is not allowed in the browser until a storage boundary is designed, documented, tested, and approved.
- Credentials must not be stored in browser `localStorage`, `sessionStorage`, indexed browser databases, URL parameters, logs, screenshots, fixtures, or committed files.
- Provider calls must be opt-in and disabled by default.
- Model routing must be explicit, documented, and test-covered.
- OpenRouter defaults to free `:free` models to avoid accidental spend.
- Provider errors must avoid exposing secrets or private request content.
- The `GET /capabilities` response must identify provider setup and model-call status accurately.
- Subscription CLI execution must remain outside Sparkbot and route through LIMA Guardian or an equivalent explicit execution boundary, following the public adapter contract in `LIMA_PROVIDER_GUARDIAN_ADAPTER.md`.

## Required Gates Before Credential Handling

A future credential-handling branch must include:

- A documented storage boundary.
- Tests proving credentials are never returned to the frontend after save.
- Tests proving logs and errors do not expose secrets.
- Tests proving disabled and missing-config states do not call a provider.
- Documentation explaining where credentials are stored and how to remove them.
- A migration or cleanup story for failed experiments.

## Required Gates Before Additional Model Calls

A future model-call branch must include:

- Explicit provider selection behavior.
- Explicit model selection behavior.
- Tests for unsupported provider, missing configuration, failed provider call, and user-visible error handling.
- Tests proving preview Chat and preview Round Table surfaces do not call models automatically.
- A Guardian policy review for model calls that may include private user data.
- Public documentation that avoids overstating provider availability.

## Disallowed Until Gates Exist

- Credential fields that save or transmit values.
- Provider test buttons that call external services without explicit enablement.
- Hidden provider health checks.
- Automatic model calls from Chat, Round Table, startup, validation, or tests.
- Browser-side credential persistence.
- Silent fallback from one provider to another.
- Unguarded local CLI execution for Codex or Claude subscription routes.
