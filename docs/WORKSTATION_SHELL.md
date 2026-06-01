# Workstation Shell

The current public shell baseline includes a local Workstation shell skeleton for the Sparkbot public frontend.

## What Exists

- Read-only Workstation shell layout in the frontend.
- Structured status cards for Works Today, Preview, Planned, and Not Implemented product areas.
- Read-only section selector for Workstation, Chat, Round Table, Provider Setup, and Guardian Controls surfaces.
- Planned follow-up roadmap card for next product slices.
- Static Chat Shell preview with a disabled read-only planned composer and no send action.
- Static Round Table preview with inert Operator, Assistant, Research, Builder, and Reviewer seats.
- Static Provider Setup preview with inert local, compatible provider, and custom endpoint cards.
- Static Guardian Controls preview with inert local action, provider access, workspace, connection, checkpoint, and audit cards.
- Existing backend health panel retained in the same frontend app.

## Current Status Model

- Server baseline: Works Today
- Frontend shell: Works Today
- Workstation shell: Works Today
- Chat shell: Preview
- Round Table: Preview
- Provider setup: Planned
- Guardian-gated controls: Planned

Status labels in the UI mean:

- Works Today: visible shell surface or local read-only utility exists now.
- Preview: shape is visible, but runtime behavior is intentionally inactive.
- Planned: public direction is shown without input handling or integrations.
- Not Implemented: no public runtime capability is active in this shell slice.

## What Is Intentionally Excluded

- Workstation agent orchestration
- Chat runtime implementation
- Round Table runtime implementation
- Model calls
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

This is a product-direction shell slice only. It does not claim release readiness and does not activate Chat, Round Table, Provider Setup, or Guardian Controls runtime behavior beyond the existing read-only backend health fetch.
