# Provider Setup

Provider Setup is now an environment-driven onboarding surface for local models, OpenRouter, API-key providers, and subscription CLI providers. It still does not collect or store credentials in the browser. Use `.env.example` as the public-safe local template, then fill only the backend env values needed for the providers you intend to test. The one-command local smoke wrapper verifies placeholder-backed onboarding for every API-key provider without exposing key values or enabling non-OpenRouter prompt dispatch.

## Current provider cards

- Local Ollama: localhost-only prompt adapter, disabled unless `SPARKBOT_LOCAL_MODELS_ENABLED=true`.
- OpenRouter: backend-owned env key with explicit prompt calls, disabled unless `SPARKBOT_PROVIDER_CALLS_ENABLED=true` and `OPENROUTER_API_KEY` is configured; `:free` models are enforced by default.
- OpenAI API: env-driven onboarding plus explicit prompt calls using `OPENAI_API_KEY` when provider calls are enabled.
- Anthropic API: env-driven onboarding plus explicit prompt calls using `ANTHROPIC_API_KEY` when provider calls are enabled.
- Google Gemini API: env-driven onboarding plus explicit prompt calls using `GOOGLE_API_KEY` when provider calls are enabled.
- Groq API: env-driven onboarding plus explicit prompt calls using `GROQ_API_KEY` when provider calls are enabled.
- MiniMax API: env-driven onboarding plus explicit prompt calls using `MINIMAX_API_KEY` when provider calls are enabled; `SPARKBOT_MINIMAX_CHAT_COMPLETIONS_URL` can override the OpenAI-compatible endpoint.
- xAI API: env-driven onboarding plus explicit prompt calls using `XAI_API_KEY` when provider calls are enabled.
- OpenAI Codex Subscription: reports whether the Codex CLI is available and whether local sign-in state is detected through `CODEX_HOME` or `SPARKBOT_CODEX_AUTH_FILE` without reading or returning the auth file.
- Claude Subscription: reports whether Claude Code is available and whether local sign-in state is detected through `CLAUDE_HOME`, `SPARKBOT_CLAUDE_AUTH_FILE`, or the operator-declared `SPARKBOT_CLAUDE_SUBSCRIPTION_ENABLED=true` flag without reading or returning auth contents.

## OpenRouter free model path

OpenRouter is the default cloud prompt path in the public shell because free `:free` model IDs are enforced by default. Other API-key providers also expose explicit guarded prompt endpoints when backend env keys and `SPARKBOT_PROVIDER_CALLS_ENABLED=true` are set. All provider prompt calls are off by default.

Required environment, usually copied from `.env.example` into a local `.env` file:

```bash
SPARKBOT_PROVIDER_CALLS_ENABLED=true
OPENROUTER_API_KEY=...
SPARKBOT_OPENROUTER_MODEL=meta-llama/llama-3.2-3b-instruct:free
```

The local development start scripts read `${repo}/.env` automatically through a plain `KEY=VALUE` parser. They do not execute `.env` contents, print provider values, or overwrite variables already exported in the shell. Set `SPARKBOT_ENV_FILE=/path/to/local.env` before launch when testing with an alternate local env file.

Sparkbot enforces OpenRouter model IDs ending in `:free` by default. To opt into paid OpenRouter models for a local test, set `SPARKBOT_ALLOW_PAID_OPENROUTER_MODELS=true` and use an explicit model ID.

Provider Setup includes a Provider Prompt Smoke panel. The panel defaults to OpenRouter and is enabled only when the selected provider reports available; it submits only provider ID, operator prompt, and model ID to the backend; it does not accept or display keys.

Manual OpenRouter smoke request:

```bash
curl -i -X POST http://127.0.0.1:8000/provider-config/openrouter/prompt \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Say OK.","model":"mistralai/mistral-7b-instruct:free"}'
```

## Subscription sign-in readiness

For Codex subscription readiness, install the Codex CLI, run `codex login`, choose ChatGPT sign-in, finish the browser login, and restart Sparkbot. If the backend runs under a different user or profile, set `CODEX_HOME` to the signed-in profile directory or `SPARKBOT_CODEX_AUTH_FILE` to the auth file path. Use `SPARKBOT_CODEX_CLI` only when the CLI is not on `PATH`. `SPARKBOT_CODEX_MODEL` is the public-shell default model setting; `SPARKBOT_CODEX_SUBSCRIPTION_MODEL` is accepted as a prototype-compatible alias.

For Claude subscription readiness, install Claude Code, run `claude auth login`, finish the browser sign-in, and restart Sparkbot. If the backend runs under a different user or profile, set `CLAUDE_HOME` to the signed-in profile directory or `SPARKBOT_CLAUDE_AUTH_FILE` to a local auth-state file whose presence should count as operator-declared sign-in. `SPARKBOT_CLAUDE_SUBSCRIPTION_ENABLED=true` remains available as an explicit operator readiness flag. Use `SPARKBOT_CLAUDE_CLI` only when the CLI is not on `PATH`. `SPARKBOT_CLAUDE_SUB_MODEL` is the public-shell default model setting; `SPARKBOT_CLAUDE_SUBSCRIPTION_MODEL` is accepted as a prototype-compatible alias.

## Subscription provider boundary

Codex and Claude subscription cards report CLI availability, sign-in detection, the current runtime gate, the LIMA adapter configuration state, and the next operator action. They never execute local CLIs from the public shell. When `SPARKBOT_PROVIDER_CALLS_ENABLED=true`, subscription sign-in is ready, and `SPARKBOT_LIMA_PROVIDER_ADAPTER_URL` points to an `http://localhost...` or `http://127.0.0.1...` adapter endpoint, explicit Provider Prompt Smoke requests delegate to the LIMA Guardian adapter. During LIMA/operator install testing, run the local smoke wrapper with `SPARKBOT_SMOKE_USE_HOST_SUBSCRIPTIONS=true SPARKBOT_SMOKE_REQUIRE_SUBSCRIPTIONS=true` to require both subscription cards to be ready while default validation still avoids real dispatch. Direct CLI dispatch must remain inside the LIMA Guardian boundary published by `GET /guardian/status`, with capability checks, operator approval, audit logs, secret redaction, timeout control, no shell expansion, and fail-closed behavior. The adapter request/response and audit expectations are documented in `LIMA_PROVIDER_GUARDIAN_ADAPTER.md`.

## Still not included

- Browser credential entry.
- Browser credential storage.
- Provider key save buttons.
- Hidden provider health checks.
- Automatic model calls from Chat, Round Table, startup, tests, or validation.
- Silent fallback from one provider to another.
