# Workstation Shell

The current public shell baseline includes a local Workstation shell skeleton for the Sparkbot public frontend.

## What Exists

- Local SQLite Workstation runtime for chat drafts, memory notes, and work lane cards.
- Manual local memory note selection for the disabled-by-default local Ollama prompt panel.
- Optional local chat-session links on local work lane cards.
- Read-only local Workstation JSON export for backup and testing.
- Read-only local runtime settings panel for data paths and env-driven Ollama configuration.
- Disabled-by-default local Ollama adapter status and prompt panel.
- Workstation shell layout in the frontend with local create, read, update, and delete flows.
- Read-only public baseline status panel summarizing health, capability status counts, and local status endpoints.
- Structured status cards using the public contract statuses: Available, Preview, Planned, Disabled by default, and Guarded future.
- Grouped capability lanes for available, preview, planned, disabled-by-default, and guarded-future surfaces.
- Read-only section selector for Workstation, Chat, Round Table, Provider Setup, and Guardian Controls surfaces.
- Planned follow-up roadmap card for next product slices.
- Read-only Chat status surface with a disabled read-only planned composer and no send action.
- Read-only Round Table status surface with inert Operator, Assistant, Research, Builder, and Reviewer seats.
- Read-only Model Seat status surface with inert Default Assistant, Research, Builder, and Reviewer seats.
- Read-only Task Lane status surface with inert Inbox, Planned, Active, and Review lanes.
- Read-only Provider Setup status surface with inert local, compatible provider, and custom endpoint cards.
- Read-only Connector Status surface with connectors disabled and no outbound actions.
- Read-only Guardian Controls status surface with inert local action, provider access, workspace, connection, checkpoint, and audit cards.
- Existing backend health panel retained in the same frontend app.
- Local data is stored under `SPARKBOT_DATA_DIR` when set, otherwise in the user app data directory.

## Current Status Model

- Backend health endpoint: Available
- Frontend shell: Available
- Local Workstation store: Available
- Local chat drafts: Available
- Local memory notes: Available
- Local work lane cards: Available
- Local data export: Available
- Local runtime settings: Available
- Local model adapter: Disabled by default
- Local Ollama: Disabled by default
- Workstation shell: Preview
- Chat shell: Preview
- Round Table: Preview
- Provider setup: Preview
- Model seats: Preview
- Task lanes: Preview
- Connector status: Guarded future
- Guardian-gated controls: Preview
- Desktop packaging: Planned
- Model calls, credential storage, and tool execution: Guarded future

Status labels in the UI mean:

- Available: implemented in the public repo, validated, documented, and safe by default.
- Preview: shape is visible, but runtime behavior is intentionally inactive.
- Planned: public direction is shown without input handling or integrations.
- Guarded future: not implemented; future runtime work requires contract gates and review.

## What Is Intentionally Excluded

- Workstation agent orchestration
- Model-generated chat runtime implementation
- Round Table runtime implementation
- Automatic cloud model calls and production model routing
- Model seat assignment or persistence
- Task scheduling, reminders, notifications, background jobs, or execution
- Tool execution
- Local data import, cloud sync, external upload, credential export, or settings writes
- Runtime settings credential fields or secret save buttons
- Provider credential forms or browser-side credential storage
- Guardian runtime controls and policy enforcement
- Desktop and Tauri surfaces

## Validation Commands

```bash
cd frontend
npm ci
npm test -- --run
npm run build
```

```bash
python3 -m compileall backend
pytest backend/tests -q
```

## Scope Notes

This is a product-direction shell slice only. It does not claim release readiness and activates only local SQLite CRUD for Workstation drafts, notes, and planning cards. It activates only optional links between local work lane cards and local chat sessions. It activates only a read-only JSON export of local Workstation data for backup and testing; it does not activate import, cloud sync, external upload, or credential export. It activates only read-only runtime settings display for local paths and env-driven Ollama configuration; it does not activate credential fields, secret save buttons, or runtime config writes. It activates only default-off localhost Ollama prompt calls when explicitly enabled by environment variable. It also exposes env-driven provider onboarding and a default-off OpenRouter prompt endpoint for explicit free-model calls when `SPARKBOT_PROVIDER_CALLS_ENABLED=true` and a backend env key is configured. Local memory notes are added to a prompt only when the operator selects them manually. It does not activate automatic memory retrieval, model memory writes, embeddings, vector databases, automatic cloud model calls, broad provider routing, browser credential storage, external sends, connectors, schedulers, reminders, background jobs, task execution, tool execution, Guardian runtime enforcement, or LIMA AI OS integration.
