# Chat Shell

The current public shell baseline includes a static Chat Shell preview in the public Sparkbot Workstation shell and a read-only backend `GET /chat/status` endpoint.

The main Chat Shell preview is intentionally read-only. Local Workstation chat drafts are implemented separately under `/local/chat/sessions`, and the disabled-by-default local Ollama panel can save an explicitly run local assistant response into an existing selected local session. This is not provider chat runtime, streaming, routing, credential handling, or auto-send behavior.

## Current behavior

- The Chat Shell preview renders inside the existing Workstation shell.
- The frontend can display `GET /chat/status` when the local backend is available.
- If the status endpoint is unavailable, the frontend uses the same static local fallback.
- Provider chat runtime, cloud model calls, streaming, and provider routing are labeled `not-implemented`.
- The planned composer is disabled and read-only.
- There is no send button and no endpoint that accepts user text.
- The Local Chat Drafts panel can store operator and note messages in local SQLite.
- The Local Ollama Adapter panel can persist an `assistant-local` response only when local models are explicitly enabled and an existing local session is selected.

## Excluded from this baseline

- Real chat runtime
- Provider chat message handling
- Provider chat message persistence
- Cloud model calls or provider routing
- Provider credentials or credential storage
- Streaming
- Guardian runtime controls
- Approval tokens or policy enforcement
- Terminal or tool execution
- External sends or connector calls
- File mutation

## Follow-up direction

A later slice should define public chat interaction contracts before enabling active message handling, provider calls, persistence, or runtime safety gates.
