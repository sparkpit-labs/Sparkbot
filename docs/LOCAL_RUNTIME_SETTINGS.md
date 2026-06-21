# Local Runtime Settings

Sparkbot includes a read-only local runtime settings surface for install, smoke testing, and support review.

## Endpoint

```text
GET /local/runtime/settings
```

The endpoint reports:

- The current local data directory in a user-facing display form.
- The SQLite database filename and display path.
- Whether local models are enabled by environment configuration.
- The configured local Ollama base URL and model name, when present.

Configuration remains environment-driven. The public shell does not write runtime settings from this endpoint or panel.

## Frontend Panel

The Workstation shell includes a Local Runtime Settings panel. It fetches `/local/runtime/settings` and renders status cards for local data paths, SQLite, local model enablement, and Ollama configuration.

The panel is intentionally read-only. It has no input fields, no save button, no secret button, and no provider test call.

## Safety Boundary

This surface does not add:

- Credential fields.
- Secret save actions.
- Runtime config writes.
- Cloud sync.
- External upload.
- Provider credential setup.
- Provider calls.
- Model calls beyond the existing disabled-by-default local Ollama adapter path.

Use environment variables such as `SPARKBOT_DATA_DIR`, `SPARKBOT_LOCAL_MODELS_ENABLED`, `SPARKBOT_OLLAMA_BASE_URL`, and `SPARKBOT_OLLAMA_MODEL` to configure the local runtime before starting the backend.
