# Workstation Shell

The current public shell baseline includes a local Workstation shell skeleton for the Sparkbot public frontend.

## What Exists

- Read-only Workstation shell layout in the frontend.
- Read-only public baseline status panel summarizing health, capability status counts, and local status endpoints.
- Structured status cards using the public contract statuses: Available, Preview, Planned, Disabled by default, and Guarded future.
- Grouped capability lanes for available, preview, planned, disabled-by-default, and guarded-future surfaces.
- Read-only section selector for Workstation, Chat, Round Table, Provider Setup, and Guardian Controls surfaces.
- Planned follow-up roadmap card for next product slices.
- Read-only Chat status surface with a disabled read-only planned composer and no send action.
- Read-only Round Table status surface with inert Operator, Assistant, Research, Builder, and Reviewer seats.
- Read-only Model Seat status surface with inert Default Assistant, Research, Builder, and Reviewer seats.
- Read-only Provider Setup status surface with inert local, compatible provider, and custom endpoint cards.
- Read-only Connector Status surface with connectors disabled and no outbound actions.
- Read-only Guardian Controls status surface with inert local action, provider access, workspace, connection, checkpoint, and audit cards.
- Existing backend health panel retained in the same frontend app.

## Current Status Model

- Backend health endpoint: Available
- Frontend shell: Available
- Workstation shell: Preview
- Chat shell: Preview
- Round Table: Preview
- Provider setup: Preview
- Model seats: Preview
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
- Chat runtime implementation
- Round Table runtime implementation
- Model calls
- Model seat assignment or persistence
- Tool execution
- Provider setup runtime forms
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

This is a product-direction shell slice only. It does not claim release readiness and does not activate Chat, Round Table, Model Seat, Provider Setup, Connector Status, or Guardian Controls runtime behavior beyond existing read-only local status fetches.
