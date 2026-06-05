# Public Artifact Manifest

## Included in current public Workstation MVP

- `backend/`
  - FastAPI app, shared local Workstation store, Command Center, Chat, Round Table, memory, notes, events, confirmations, and task record routes.
- `frontend/`
  - React/Vite app with Workstation, Chat, Round Table, Command Center, Spine, and Controls routes.
- `docs/`
  - Current docs, audit reports, validation notes, and desktop packaging planning notes only.
- `scripts/`
  - local validation, public safety, and local development helpers.
- `.github/workflows/`
- `CHANGELOG.md`
- `README.md`
- `LICENSE`
- `.gitignore`

## Excluded from current public MVP scope

- Desktop packaging artifacts.
- Desktop binaries, installers, auto-update files, and signing configuration.
- Production deployment artifacts.
- Background scheduler/runner artifacts.
- Connector write integrations and external-send integrations.
- File/process/terminal/browser/device automation integrations.
- Public CLI-backed subscription-auth bridges.
- Full private Guardian/Vault/platform-internal implementations.
- Any secret-bearing environment files.

## Notes

This manifest reflects the current review baseline and can be revised as future public slices are validated.

The clean baseline release notes remain tracked in `docs/RELEASE_NOTES_PUBLIC_V1_CLEAN_BASELINE.md` as a historical checkpoint, not as the current implementation summary.
