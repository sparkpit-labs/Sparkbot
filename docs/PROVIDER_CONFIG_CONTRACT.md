# Provider Configuration Contract

This contract defines the public safety requirements for provider setup, model routing, and provider prompt work.

## Current Boundary

Provider Setup is an `available` capability for backend-owned, environment-driven onboarding/status. The browser may show whether a provider is configured, the configured source name, auth mode, default model, and model examples. The browser must not accept, store, echo, or transmit provider credentials.

OpenRouter has one guarded backend prompt endpoint for explicit operator calls:

```text
POST /provider-config/openrouter/prompt
```

That endpoint is disabled unless `SPARKBOT_PROVIDER_CALLS_ENABLED=true` and `OPENROUTER_API_KEY` is configured in the backend environment. OpenRouter model IDs ending in `:free` are enforced unless the operator explicitly sets `SPARKBOT_ALLOW_PAID_OPENROUTER_MODELS=true`. The frontend may expose an explicit OpenRouter smoke form for this endpoint, but it may send only prompt text and model ID; credentials remain backend environment values.

Other API-key providers are onboarding/status only in this branch. Codex and Claude subscription providers expose CLI availability, sign-in detection, runtime-gate status, and next operator action until LIMA Guardian execution contracts are available.

## Provider Setup Rules

- Provider setup is backend-owned and environment-driven.
- Credential entry is not allowed in the browser until a storage boundary is designed, documented, tested, and approved.
- Credentials must not be stored in browser `localStorage`, `sessionStorage`, indexed browser databases, URL parameters, logs, screenshots, fixtures, or committed files.
- Provider calls must be opt-in and disabled by default.
- Model routing must be explicit, documented, and test-covered.
- OpenRouter defaults to free `:free` models to avoid accidental spend.
- Provider errors must avoid exposing secrets or private request content.
- The `GET /capabilities` response must identify provider setup and model-call status accurately.
- Subscription CLI execution must be routed through LIMA Guardian or an equivalent explicit execution boundary before public promotion.

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
- Tests proving preview Chat and preview Round Table surfaces do not call models.
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
