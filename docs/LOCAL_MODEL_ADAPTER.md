# Local Model Adapter

Sparkbot includes a disabled-by-default local model adapter for Ollama running on the same machine.

This is a local-only foundation. It is not cloud provider support, not production model routing, and not LIMA AI OS integration.

## Endpoints

- `GET /local-models/status`
- `POST /local-models/ollama/prompt`

The status endpoint is safe to call in the default configuration. The prompt endpoint returns `403` unless local model calls are explicitly enabled.

## Environment Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `SPARKBOT_LOCAL_MODELS_ENABLED` | unset / false | Set to `true`, `1`, or `yes` to allow localhost-only prompt calls. |
| `SPARKBOT_OLLAMA_BASE_URL` | `http://127.0.0.1:11434` | Ollama server URL. Only `localhost` or `127.0.0.1` HTTP URLs are accepted. |
| `SPARKBOT_OLLAMA_MODEL` | unset | Optional default local model name. A model can also be supplied per prompt request. |

## Safety Boundary

- Non-localhost Ollama URLs are rejected.
- Credentials are not supported.
- API key, token, and password fields are not provided.
- No cloud provider SDK dependencies are added.
- No cloud model providers are called.
- No connector calls or external sends are implemented.
- No streaming, scheduler, background job, terminal execution, or Guardian enforcement is implemented.
- Tests mock the adapter and do not require Ollama to be installed or running.

## Local Chat Persistence

When a prompt request includes an existing local chat `session_id`, a successful local Ollama response is stored as an `assistant-local` message in the local SQLite Workstation store. The backend does not create chat sessions implicitly for model prompts.

A prompt request may also include `selected_memory_note_ids`. Only those explicitly selected local memory notes are read from SQLite and prepended to that one local prompt. Sparkbot does not retrieve memory automatically, does not write model memory, does not create embeddings, and does not add a vector database.

The frontend local model panel mirrors that boundary:

- It loads existing local chat sessions from `/local/chat/sessions`.
- It requires an existing selected session before the prompt button is enabled.
- It lets the operator check local memory notes to include in the current prompt only.
- It disables prompt controls when local models are disabled by configuration.
- It also disables prompt controls when local models are enabled but Ollama is unavailable on localhost.
- It does not stream, auto-send, create sessions implicitly, call cloud providers, or request credentials.

## Example Disabled-Mode Check

```bash
curl -i -X POST http://127.0.0.1:8000/local-models/ollama/prompt \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"hello","model":"llama3.2"}'
```

Expected default result: `403 Forbidden`.
