# Public Artifact Manifest

## Included in current public shell baseline

- backend/
- frontend/
- docs/
  - includes desktop packaging planning notes only
- scripts/
- .github/workflows/
- CHANGELOG.md
- README.md
- LICENSE
- .gitignore

## Excluded from current baseline scope

- Desktop packaging artifacts
- Desktop binaries, installers, auto-update files, and signing configuration
- Deployment artifacts
- Runtime provider integrations
- Runtime approval or policy enforcement integrations
- Any secret-bearing environment files

## Notes

This manifest reflects the current review baseline and can be revised as future public slices are validated.

The final public V1.0.0 release notes are tracked in `docs/RELEASE_NOTES_V1_0_0.md`.

The clean baseline release notes are tracked in `docs/RELEASE_NOTES_PUBLIC_V1_CLEAN_BASELINE.md`.

The frontend audit advisory fix checkpoint is tracked in `docs/RELEASE_NOTES_PUBLIC_V1_FRONTEND_AUDIT_FIX.md`.
