# Provider Setup

Provider setup is now an active Command Center surface, not only a static preview.

## Current behavior

- Command Center lists supported provider routes and local model readiness.
- Provider credentials can be entered through the frontend and are stored server-side in the local sensitive data directory, outside the checked-out repository by default.
- Saved credentials are represented to the browser as configured/not configured flags; raw secret values are not returned.
- The default sensitive data path is `$XDG_DATA_HOME/sparkbot/command-center` when `XDG_DATA_HOME` is set, otherwise `~/.local/share/sparkbot/command-center`. Set `SPARKBOT_SECRETS_DIR` to override it.
- Chat uses the selected Command Center provider/model route when that route is configured and supported.
- Round Table uses configured seat/default provider routes when available and falls back deterministically when routes are unavailable.
- OpenRouter, OpenAI, Anthropic, Google, Groq, MiniMax, xAI, and local Ollama-style routes are represented in the public configuration surface.
- Anthropic invite-route OAuth token mode is available only for Anthropic invite models.
- Subscription-only OpenAI/Claude local-session routes remain unsupported for public server-side execution and fail closed.

## Current limits

- No browser sign-in flow is implemented.
- No local CLI session bridge is implemented.
- No token bridge, connector bridge, or browser-cookie/session scraping is implemented.
- No provider secret is displayed in API responses, frontend state, events, notes, memory, or history.
- No model-call event stores prompts, model outputs, headers, raw request bodies, raw response bodies, credentials, or secrets.

## Follow-up direction

Future provider work should stay narrow: improve supported provider UX, clarify unsupported subscription labels, and add any new auth path only when it can run through a public-safe server-side route without subprocess execution or private credential bridges.
