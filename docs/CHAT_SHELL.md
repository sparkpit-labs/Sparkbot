# Chat Shell

The current public shell baseline includes a static Chat Shell preview in the public Sparkbot Workstation shell and a read-only backend `GET /chat/status` endpoint.

The preview is intentionally read-only. It does not implement chat runtime behavior, message sending, message persistence, model calls, model routing, streaming, provider credential handling, or any endpoint that accepts user text.

## Current behavior

- The Chat Shell preview renders inside the existing Workstation shell.
- The frontend can display `GET /chat/status` when the local backend is available.
- If the status endpoint is unavailable, the frontend uses the same static local fallback.
- Chat runtime, message persistence, model calls, streaming, and provider routing are labeled `not-implemented`.
- The planned composer is disabled and read-only.
- There is no send button and no endpoint that accepts user text.

## Excluded from this baseline

- Real chat runtime
- User-entered message handling
- Message persistence
- Local storage
- Model calls or routing
- Provider credentials or credential storage
- Streaming
- Guardian runtime controls
- Approval tokens or policy enforcement
- Terminal or tool execution
- External sends or connector calls
- File mutation

## Follow-up direction

A later slice should define public chat interaction contracts before enabling active message handling, provider calls, persistence, or runtime safety gates.
