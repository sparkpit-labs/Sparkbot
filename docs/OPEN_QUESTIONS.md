# Open Questions

These questions must be resolved before Sparkbot public v1.0.0 release.

- What should the first public package layout be?
- What local model path should be documented first?
- What release artifacts should be published?
- What is the Windows installer path?
- What code signing approach is required?
- Which research features belong in public v1.0.0?
- Which features should wait until after v1.0.0?

## Resolved provider setup direction

- Public V1 provider setup is env-driven and local-first: Local Ollama, OpenRouter free-model path, OpenAI API, Anthropic API, Google Gemini API, Groq API, MiniMax API, xAI API, OpenAI Codex Subscription, and Claude Subscription. Browser credential entry and credential storage remain out of scope.

## External install-test TODOs

These are not Sparkbot repo implementation blockers, but they are required evidence before claiming operator-installed provider runtime completion:

- Run `SPARKBOT_PROVIDER_INSTALL_ENV_FILE=.env bash scripts/run-openrouter-free-smoke.sh` with an operator-owned `OPENROUTER_API_KEY` and a `:free` model to prove real OpenRouter free-model dispatch.
- Run `SPARKBOT_PROVIDER_INSTALL_ENV_FILE=.env bash scripts/run-lima-install-provider-smoke.sh` against the real localhost LIMA Guardian provider adapter to prove Codex and Claude subscription dispatch through the guarded adapter boundary.
- Return only sanitized smoke reports and PASS/FAIL lines; do not return provider keys, auth files, raw prompts, raw model responses, private paths, or adapter credentials.
