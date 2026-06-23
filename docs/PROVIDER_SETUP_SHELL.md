# Provider Setup

Provider Setup is now an environment-driven onboarding surface for local models, OpenRouter, API-key providers, and subscription CLI providers. It still does not collect or store credentials in the browser. The one-command local smoke wrapper verifies placeholder-backed onboarding for every API-key provider without exposing key values or enabling non-OpenRouter prompt dispatch.

## Current provider cards

- Local Ollama: localhost-only prompt adapter, disabled unless `SPARKBOT_LOCAL_MODELS_ENABLED=true`.
- OpenRouter: backend-owned env key with explicit prompt calls, disabled unless `SPARKBOT_PROVIDER_CALLS_ENABLED=true` and `OPENROUTER_API_KEY` is configured.
- OpenAI API: env-driven onboarding/status using `OPENAI_API_KEY`.
- Anthropic API: env-driven onboarding/status using `ANTHROPIC_API_KEY`.
- Google Gemini API: env-driven onboarding/status using `GOOGLE_API_KEY`.
- Groq API: env-driven onboarding/status using `GROQ_API_KEY`.
- MiniMax API: env-driven onboarding/status using `MINIMAX_API_KEY`.
- xAI API: env-driven onboarding/status using `XAI_API_KEY`.
- OpenAI Codex Subscription: reports whether the Codex CLI is available and whether local sign-in state is detected through `CODEX_HOME` or `SPARKBOT_CODEX_AUTH_FILE` without reading or returning the auth file.
- Claude Subscription: reports whether Claude Code is available and whether local sign-in state is detected through `CLAUDE_HOME`, `SPARKBOT_CLAUDE_AUTH_FILE`, or the operator-declared `SPARKBOT_CLAUDE_SUBSCRIPTION_ENABLED=true` flag without reading or returning auth contents.

## OpenRouter free model path

OpenRouter is the first cloud prompt path in the public shell. It is guarded and off by default.

Required environment:

```bash
SPARKBOT_PROVIDER_CALLS_ENABLED=true
OPENROUTER_API_KEY=...
SPARKBOT_OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free
```

Sparkbot enforces OpenRouter model IDs ending in `:free` by default. To opt into paid OpenRouter models for a local test, set `SPARKBOT_ALLOW_PAID_OPENROUTER_MODELS=true` and use an explicit model ID.

Provider Setup also includes an OpenRouter Free Model Smoke panel. The panel is enabled only when the backend reports OpenRouter as available, and it submits only an operator prompt and model ID to the backend; it does not accept or display keys.

Manual smoke request:

```bash
curl -i -X POST http://127.0.0.1:8000/provider-config/openrouter/prompt \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Say OK.","model":"mistralai/mistral-7b-instruct:free"}'
```

## Subscription sign-in readiness

For Codex subscription readiness, install the Codex CLI, run `codex login`, choose ChatGPT sign-in, finish the browser login, and restart Sparkbot. If the backend runs under a different user or profile, set `CODEX_HOME` to the signed-in profile directory or `SPARKBOT_CODEX_AUTH_FILE` to the auth file path. Use `SPARKBOT_CODEX_CLI` only when the CLI is not on `PATH`. `SPARKBOT_CODEX_MODEL` is the public-shell default model setting; `SPARKBOT_CODEX_SUBSCRIPTION_MODEL` is accepted as a prototype-compatible alias.

For Claude subscription readiness, install Claude Code, run `claude auth login`, finish the browser sign-in, and restart Sparkbot. If the backend runs under a different user or profile, set `CLAUDE_HOME` to the signed-in profile directory or `SPARKBOT_CLAUDE_AUTH_FILE` to a local auth-state file whose presence should count as operator-declared sign-in. `SPARKBOT_CLAUDE_SUBSCRIPTION_ENABLED=true` remains available as an explicit operator readiness flag. Use `SPARKBOT_CLAUDE_CLI` only when the CLI is not on `PATH`. `SPARKBOT_CLAUDE_SUB_MODEL` is the public-shell default model setting; `SPARKBOT_CLAUDE_SUBSCRIPTION_MODEL` is accepted as a prototype-compatible alias.

## Subscription provider boundary

Codex and Claude subscription cards are onboarding/status surfaces in this branch. Each card reports CLI availability, sign-in detection, the current runtime gate, and the next operator action. They do not execute local CLIs from the public shell yet. During LIMA/operator install testing, run the local smoke wrapper with `SPARKBOT_SMOKE_USE_HOST_SUBSCRIPTIONS=true SPARKBOT_SMOKE_REQUIRE_SUBSCRIPTIONS=true` to require both subscription cards to be ready while still refusing direct dispatch. Direct CLI dispatch must go through the LIMA Guardian boundary published by `GET /guardian/status`, with capability checks, operator approval, audit logs, secret redaction, timeout control, no shell expansion, and fail-closed behavior before it is promoted. The adapter request/response and audit expectations are documented in `LIMA_PROVIDER_GUARDIAN_ADAPTER.md`.

## Still not included

- Browser credential entry.
- Browser credential storage.
- Provider key save buttons.
- Hidden provider health checks.
- Automatic model calls from Chat, Round Table, startup, tests, or validation.
- Silent fallback from one provider to another.
