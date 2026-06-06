# Local Secret Store Outside Repo Report

## Branch And Base

- Branch: `fix-local-secret-store-outside-repo`
- Base branch: `fix-openrouter-provider-setup-parity`
- Base commit: `d368a959bfc2e0b1e74ac1c4c2d68abd63bb6781`

## Problem

The OpenRouter provider setup flow now works, but normal local credential save previously wrote the server-side credential file under the checked-out repository by default:

- Old default: `data/command-center/secrets.json`

That file was ignored by git, but the public safety scan intentionally scans the full checkout. A local operator could save a provider credential and then fail the public safety scan until the local runtime secret file was moved out manually.

## New Storage Behavior

Command Center now separates non-secret config from sensitive local storage.

- Non-secret config and model catalog continue to use `SPARKBOT_DATA_DIR` when set.
- The default non-secret development path remains `data/command-center` under the checkout.
- Provider credentials and operator auth metadata now use `SPARKBOT_SECRETS_DIR` when set.
- Without `SPARKBOT_SECRETS_DIR`, sensitive data is stored outside the checkout:
  - `$XDG_DATA_HOME/sparkbot/command-center` when `XDG_DATA_HOME` is set.
  - `~/.local/share/sparkbot/command-center` otherwise.

Sensitive files in that directory include:

- `secrets.json`
- `operator_pin.json`

For test isolation and explicit development overrides, when `SPARKBOT_DATA_DIR` is set but `SPARKBOT_SECRETS_DIR` is not set, sensitive storage follows `SPARKBOT_DATA_DIR`. This preserves current test behavior and makes temporary test directories self-contained.

## Path Override Behavior

- `SPARKBOT_DATA_DIR`: redirects non-secret Command Center config and the shared Workstation store.
- `SPARKBOT_SECRETS_DIR`: redirects provider credentials and operator auth metadata.
- `.env.example` now documents both variables without providing credential values.

## OpenRouter Setup Preservation

The OpenRouter parity behavior from the prior branch is preserved:

- Credential save remains server-side only.
- OpenRouter model refresh still works after credential save.
- Refreshed OpenRouter model metadata still persists in the Command Center config/model catalog.
- API responses and events still expose configured flags and model metadata, not credential values.

## Tests Added

Added backend tests in `backend/tests/test_command_center.py`:

- Default sensitive storage writes outside a simulated checkout after credential save.
- No `data/command-center/secrets.json` is created in the checkout under default normal usage.
- `SPARKBOT_SECRETS_DIR` can store sensitive data separately from `SPARKBOT_DATA_DIR`.
- Existing provider credential save/readback tests continue to verify no credential echo.

## Validation Results

- `git diff --check`: pass
- Backend tests: `56 passed, 1 warning`
- Frontend tests: `10 passed`
- Frontend build: pass
- `npm audit --audit-level=moderate`: `0 vulnerabilities`
- `bash scripts/check-public-safety.sh`: pass
- `bash scripts/validate-public-shell.sh`: pass, including backend tests, frontend tests, build, and audit
- Changed-file privacy scan: pass

## Safety Result

Normal local provider credential save no longer creates a repo-local `secrets.json` by default, so the public safety scan should not fail because of newly saved Command Center credentials in normal local usage.

Credential values remain server-side only and were not printed, committed, or written into docs. No frontend localStorage source of truth was added.

## Remaining Warnings

- Existing older local checkouts may still contain a stale `backend/data/command-center/secrets.json` from previous runs. That local file should be moved out of the repository before public safety scans.
- This branch does not implement live provider smoke, new provider behavior, connector behavior, background execution, CLI subscription auth, or write-mode execution.

## Verdict

`PASS`

The local sensitive store now defaults outside the checked-out repository while preserving Command Center config, OpenRouter model refresh, test isolation, and server-side-only credential handling.
