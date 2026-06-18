# Provider Configuration Contract

This contract defines the minimum safety requirements for future provider setup, model routing, and provider status work. The current public baseline does not accept credentials, store credentials, call providers, or route model requests.

## Current Boundary

Provider Setup is a `preview` capability. It may describe planned provider categories and local-first setup direction, and may expose read-only status through `GET /provider-config/status`, but it must not include credential entry, credential storage, provider test calls, model calls, or model routing.

## Provider Setup Rules

- Provider setup starts as inert UI and read-only documentation.
- Credential entry is not allowed until a storage boundary is designed, documented, tested, and approved.
- Credentials must not be stored in browser `localStorage`, `sessionStorage`, indexed browser databases, URL parameters, logs, screenshots, fixtures, or committed files.
- Provider calls are not allowed before configuration and guardrail tests exist.
- Model routing must be explicit, documented, and test-covered.
- Cloud provider support must be opt-in.
- Local provider support should be preferred first where practical, because it can reduce external data flow.
- Provider errors must avoid exposing secrets or private request content.
- The `GET /capabilities` response must identify provider setup and model-call status accurately.

## Required Gates Before Credential Handling

A future credential-handling branch must include:

- A documented storage boundary.
- Tests proving credentials are never returned to the frontend after save.
- Tests proving logs and errors do not expose secrets.
- Tests proving disabled and missing-config states do not call a provider.
- Documentation explaining where credentials are stored and how to remove them.
- A migration or cleanup story for failed experiments.

## Required Gates Before Model Calls

A future model-call branch must include:

- Explicit provider selection behavior.
- Explicit model selection behavior.
- Tests for unsupported provider, missing configuration, failed provider call, and user-visible error handling.
- Tests proving preview chat and preview Round Table surfaces do not call models.
- A Guardian policy review for model calls that may include private user data.
- Public documentation that avoids overstating provider availability.

## Disallowed Until Gates Exist

- Credential fields that save or transmit values.
- Provider test buttons that call external services.
- Hidden provider health checks.
- Automatic model calls from chat, Round Table, startup, validation, or tests.
- Browser-side credential persistence.
- Silent fallback from one provider to another.
