# Guardian Suite Wiring Pre-Chat Workstation Audit

## Summary

Branch under audit: `audit-guardian-suite-wiring-before-chat-workstation`

Starting point audited: `port-rd-command-center-room-spine-services` at `a9efb0d Add Workstation room and spine services`.

Recommendation: PROCEED to `port-rd-chat-workstation-integration` after review of this branch. The current public app now has a real fail-closed Guardian confirmation boundary for the only implemented destructive Workstation route, shared persistent confirmation state, shared event logging, and tests covering the major denial cases.

This is still a local confirmation foundation, not a complete advanced Guardian system. Chat and future Workstation action routes must call the same authorization boundary before any destructive or external action.

## What Is Wired Now

Backend Guardian and Security routes:

- `GET /api/v1/chat/guardian/status` returns public-safe Guardian availability, Security profile state, PIN state, and disabled scheduler/memory guard booleans.
- `GET /api/v1/chat/security/status` returns local Security profile, provider storage policy, custom guardrails, and operator guidance.
- `POST /api/v1/chat/security/operator-pin` stores a hashed local operator PIN and requires the current PIN before changing an existing PIN.
- `GET /api/guardian/actions/confirmations` lists confirmation records from the shared store.
- `POST /api/guardian/actions/confirmations` creates a pending confirmation record and writes a shared event.
- `POST /api/guardian/actions/confirmations/{confirmation_id}/decision` resolves a pending confirmation as approved or denied and writes a shared event.

Shared state and spine wiring:

- `GET /api/workstation/state` now includes `guardian.pending_confirmations` and `guardian.recent_confirmations`.
- `GET /api/v1/chat/dashboard/summary` reads pending confirmation counts from the shared store.
- `GET /api/v1/chat/spine/operator/events` reads the same shared event log used by Workstation actions and Guardian decisions.
- Command Center reads Guardian/Security state from backend routes and pending approval counts from backend dashboard/shared state. It does not use browser-only state as the source of truth.

## What Is Persistent

Persistent local SQLite state now includes:

- confirmation id
- action type
- status
- risk level
- prompt
- surface
- source id
- created timestamp
- expiry timestamp
- resolved timestamp
- used timestamp

The store also persists event records for confirmation creation, approval, denial, blocked actions, authorized actions, and memory deletion. Event payloads redact sensitive-looking keys before storage and before frontend exposure.

PIN data remains outside frontend state and is stored as a salted hash in the local backend data directory. Provider credential values remain server-side only.

## What Is Actually Enforced

The current privileged/destructive route is:

- `DELETE /api/memory/{memory_id}`

That route now fails closed unless the caller provides a Guardian confirmation id that matches all of these conditions:

- status is `approved`
- action type is exactly `memory.delete`
- surface is exactly `memory`
- source id is exactly the target memory id
- confirmation has not expired
- confirmation has not already been used

Successful authorization marks the confirmation as used and writes `guardian.action_authorized`. Any missing, malformed, pending, denied, expired, replayed, generic, or mismatched confirmation writes `guardian.action_blocked` and returns `403`.

## What Is Foundational Or Stubbed

These pieces are intentionally not full execution systems yet:

- Task scheduler actions remain disabled in Command Center.
- Connector cards remain disabled until public backend gates are ported.
- There is no note delete route.
- Note create/update, room create/update, seat changes, provider settings, and local notes are currently treated as local state edits, not privileged external actions. They still write shared events where implemented.
- No Chat engine, Round Table execution engine, connector sends, background workers, shell execution, or device-control routes are added in this branch.

## Gaps Found

Initial audit finding before the fix:

- Confirmation records were persisted and visible in dashboard/spine counters, but they did not authorize or block any action.
- `DELETE /api/memory/{memory_id}` deleted memory without a Guardian confirmation.

Fixes made in this branch:

- Added confirmation listing and decision routes.
- Added expiry and one-time-use fields to confirmation records with migration support for existing local databases.
- Added `authorize_action` in the shared Workstation store.
- Guarded memory deletion with an action-bound Guardian confirmation.
- Added shared events for approvals, denials, blocked attempts, and authorized actions.
- Added tests for persistence, shared state visibility, event redaction, missing confirmation, malformed confirmation id, pending confirmation, denied confirmation, expired confirmation, action mismatch, source mismatch, approval, and replay.

## Remaining Blockers Before Chat Integration

These are not blockers to starting `port-rd-chat-workstation-integration`, but they are hard requirements for that branch:

- Chat must not execute destructive or external actions directly.
- Any future action route must declare its action type, surface, source id, and required confirmation behavior.
- Chat should write action previews and confirmation requests before any risky state change.
- Chat should use shared events for every confirmation request, denial, approval, block, and completed action.
- Chat must keep provider credentials server-side and must not include secrets in memory, notes, events, or frontend state.

## Validation Run

Validation after the fixes passed locally:

- `python3 -m compileall backend`
- `git diff --check`
- `bash scripts/validate-public-shell.sh`
  - backend tests: 17 passed
  - frontend tests: 1 passed
  - frontend build: passed
  - npm audit: 0 vulnerabilities
- `bash scripts/check-public-safety.sh`: passed
- changed-file privacy scan: no findings
