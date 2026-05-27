# Workstation Shell

This branch adds a local Workstation shell skeleton for the Sparkbot public frontend.

## What Exists

- Read-only Workstation shell layout in the frontend.
- Structured status cards for implemented, skeleton, and planned product areas.
- Planned follow-up roadmap card for next product slices.
- Existing backend health panel retained in the same frontend app.

## Current Status Model

- Server baseline: implemented
- Frontend shell: implemented
- Workstation shell: skeleton
- Round Table: planned
- Provider setup: planned
- Guardian-gated controls: planned

## What Is Intentionally Excluded

- Workstation agent orchestration
- Round Table runtime implementation
- Chat implementation
- Model calls
- Tool execution
- Provider setup forms
- Guardian runtime controls
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

This is a product-direction shell slice only. It does not claim release readiness and does not activate runtime behavior beyond the existing read-only backend health fetch.
