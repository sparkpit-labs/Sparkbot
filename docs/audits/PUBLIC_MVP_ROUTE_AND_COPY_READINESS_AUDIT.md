# Public MVP Route And Copy Readiness Audit

## A. Verdict

**READY_FOR_INTERNAL_MVP_REVIEW**

The public repo now presents Sparkbot as a working local AI Workstation MVP without claiming production readiness, full research parity, scheduler/runner execution, connector writes, write-mode execution, public CLI-backed subscription auth, or full private Guardian/Vault internals.

The main readiness issue found was stale underclaiming in root/readiness/provider/security docs that still described the app as a static shell with no provider setup, model calls, Chat runtime, or Round Table meeting flow. This branch corrects those claims and keeps unsupported execution limits explicit.

## Branch And Base

- Branch: `audit-public-mvp-route-and-copy-readiness`
- Base branch: `port-rd-dashboard-events-tasks-parity`
- Base commit: `e2dd0088dcc79ef1d711799ca165c85e71d619f4`

## B. Route Matrix

| Route | Status | Purpose | Backend data connected | Warnings/gaps |
| --- | --- | --- | --- | --- |
| `/` | Works, normalizes to `/workstation` | Default Workstation entry | Yes, Workstation state after normalization | Root is not a distinct landing page; this is acceptable for MVP. |
| `/spine` | Works | Spine events, counters, notes/history, task queues, producer metadata | Yes, `/api/workstation/history` and Spine overview | Queues are local task/confirmation state only; no scheduler. |
| `/controls` | Works | Local readiness, backend health, provider readiness, capability limits | Yes, health and Workstation state | Edits live in Command Center; Controls is reporting/status only. |
| `/command-center` | Works | Provider/model config, seats, Agents Wing, invite routes, security settings, task state | Yes, Command Center and Workstation APIs | Run/write-mode controls are disabled; subscription-only local-session routes fail closed. |
| `/workstation` | Works | Operating floor for rooms, seats, memory, notes, history, Round Table, tasks, events | Yes, shared Workstation history/state | Task records are state-only; room creation does not start provider calls by itself. |
| `/chat` | Works | Operator chat with sessions, notes, memory recall, selected provider route | Yes, Chat APIs and Workstation state | Provider execution depends on configured supported route; no streaming. |
| `/roundtable` | Works | Direct Round Table meeting room | Yes, Round Table sessions plus Workstation state | Provider execution uses configured routes where available and deterministic fallback otherwise. |

## C. Feature Reality Matrix

| Feature | User-facing claim after patch | Actual implementation | Accurate? | Fix needed |
| --- | --- | --- | --- | --- |
| Command Center | Working configuration surface | Provider/model setup, seats, agents, invite routes, security settings, task state | Yes | None |
| Provider/model setup | Server-side credentials and supported configured-provider execution | Credentials saved server-side; configured routes can execute Chat/Round Table text calls | Yes | None |
| Chat | Backend-backed Chat with configured-provider route and shared context | Sessions/messages persist; memory/notes recall; protected requests fail closed | Yes | None |
| Round Table | Backend-backed provider-capable meeting flow with deterministic fallback | Fixed phase order, Seat 1 manager, assignments, summaries, notes, agent/seat context | Yes | None |
| Agents Wing | Agent creation/edit/invite/seat assignment works | Agent identity/instructions persist and are used in Round Table context | Yes | None |
| Invite routes | Public invite-route parity for safe provider paths | Invite route state persists; unsupported subscription-only routes fail closed | Yes | None |
| Memory/context recall | Persistent source-labeled memory shared by Chat and Round Table | Server-side memory, recall, edit/delete, redaction, manager summary promotion | Yes | None |
| Notes/history | Backend-backed notes and session history | Workstation/Spine show notes, Chat/Round Table history, wrap-up links | Yes | None |
| Spine/events | Safe event log and producer metadata | Redacted events; filters/counters/producers visible | Yes | None |
| Dashboard counters | Real shared-store counters | Rooms, notes, memory, events, agents/seats, sessions, tasks | Yes | None |
| Task records | Manual state-only task records | Create/list/read/update, pause/resume/done/cancel, history | Yes | None |
| Task Guardian visible state | Public task controls and disabled execution state | Visibility only; run/write-mode fail closed | Yes | Copy labels softened in this branch |
| Disabled run/write-mode | Disabled and fail-closed | UI disabled; backend returns 403 and logs safe block event | Yes | None |
| Subscription auth | CLI-backed OpenAI/Claude subscription execution unsupported | Unsupported subscription-only routes fail closed; no subprocess or token bridge | Yes | None |
| Connectors | Not implemented | No connector sends or external delivery | Yes | None |
| Scheduler/reminders | Not implemented | No background runner, scheduler, reminders engine, or recurring jobs | Yes | None |
| Desktop/installer | Planning only | No desktop binary, installer, signing, or auto-update | Yes | None |

## D. Copy/Docs Changes

| File | Change | Why |
| --- | --- | --- |
| `README.md` | Replaced stale shell-baseline/status tables and limitations with current local Workstation MVP status. | The old README underclaimed active Chat, Round Table, provider setup, memory, notes, events, and task records. |
| `docs/RELEASE_READINESS.md` | Updated baseline and out-of-scope sections. | Readiness now reflects internal MVP review, not static preview readiness. |
| `docs/PROVIDER_SETUP_SHELL.md` | Reframed provider setup as active Command Center behavior with safe limits. | Provider setup is no longer only a static preview. |
| `docs/GUARDIAN_CONTROLS_SHELL.md` | Reframed Guardian controls as limited fail-closed safety boundary. | Avoids implying full private policy runtime while documenting current confirmations/blocks. |
| `docs/ROADMAP.md` | Replaced stale phased preview roadmap with completed foundation/current readiness/deferred work. | Keeps roadmap aligned with current MVP. |
| `docs/PUBLIC_ARTIFACT_MANIFEST.md` | Updated included/excluded artifact lists for current MVP. | Manifest now matches active backend/frontend surfaces. |
| `docs/FRONTEND_BASELINE.md` | Updated frontend baseline to active route surfaces. | Removes stale static-preview claims. |
| `docs/SERVER_BASELINE.md` | Updated backend baseline to active Workstation services. | Removes stale minimal-health-only claims. |
| `docs/DEVELOPMENT.md` | Added `/roundtable` to route list. | Route exists and is part of the MVP. |
| `docs/LOCAL_SMOKE_TEST.md` | Added Round Table to browser navigation copy. | Route exists and should be checked manually. |
| `docs/README.md` | Tightened current-boundary wording so external/destructive actions are not implied behind confirmation. | Avoids suggesting unsupported actions can execute today. |
| `CONTRIBUTING.md` | Updated contribution scope and current boundaries. | Contributors should not assume old preview-only state or add unsafe execution. |
| `SECURITY.md` | Updated security scope for server-side provider credentials and fail-closed action paths. | Security posture now includes supported provider credential handling. |
| `CHANGELOG.md` | Updated Unreleased section with MVP behavior and disabled limits. | Changelog now reflects current branch stack. |
| `frontend/src/components/CommandCenter.tsx` | Renamed active UI headings from private-sounding labels to `Model routing monitor` and `Task controls`; clarified placeholder metadata. | Public copy should not imply private Guardian/Vault internals or executable task controls. |
| `frontend/src/components/WorkstationFloor.tsx` | Clarified room creation message: no Round Table session, provider call, or task execution starts. | Avoids outdated “no meeting engine” underclaim while preserving safety boundary. |

## E. Public Safety Scan Summary

Validation results on this branch:

- `git diff --check`: PASS
- Backend tests, `.venv-local/bin/pytest backend/tests -q`: PASS, `52 passed`, one existing Starlette/httpx deprecation warning
- Frontend tests, `npm test -- --run`: PASS, `10 passed`
- Frontend build, `npm run build`: PASS
- `npm audit --audit-level=moderate`: PASS, `0 vulnerabilities`
- `bash scripts/check-public-safety.sh`: PASS after replacing hyphenated task record wording that matched the provider-key guard pattern
- `bash scripts/validate-public-shell.sh`: PASS, `52 passed`, `10 passed`, build PASS, `0 vulnerabilities`
- Changed-file privacy scan: PASS; one expected provider setup field-name reference, no private repo names, private domains/hosts/IPs, local private paths/usernames, concrete provider keys, or private-key blocks
- Manual HTTP route checks on temporary local servers: PASS, `/`, `/spine`, `/controls`, `/command-center`, `/workstation`, `/chat`, `/roundtable`, and backend `/health` returned `200`

Privacy review target terms included private repo names, private domains/hosts/IPs, local private paths/usernames, provider-key assignments, and real credential patterns. Expected provider field names in existing provider setup code are not concrete secrets.

## F. MVP Readiness Recommendation

Proceed to `manual-local-mvp-smoke-workstation`.

Rationale: route surfaces are connected, docs now describe the actual local Workstation MVP, disabled features are explicit, public safety boundaries remain clear, and no new product behavior was added in this audit branch.

## Remaining Warnings

- This is internal MVP review readiness, not release readiness.
- Desktop packaging remains planning-only.
- No scheduler, runner, connector write, external send, file/process/terminal/browser/device automation, or public CLI-backed subscription auth is implemented.
- Full private Guardian/Vault internals are not included.
- Legacy historical release-note docs still describe earlier baseline tags; they are intentionally historical, not current implementation docs.
