# R&D Spine Command Center Parity Audit

## A. Verdict

PASS_WITH_GAPS

## B. Executive Summary

Implementation remains paused for this audit. Branch `port-rd-spine-command-center` at commit `1c668ff` is a valid foundation for continuing because it moves the public app away from a read-only shell and restores `/spine` as the Workstation Command Center entry point with real setup and status calls.

It is not full R&D `/spine` parity. The public branch rebuilds the setup/control half of the R&D Command Center into the public Vite/FastAPI app, but the deeper R&D operator console remains mostly shallow: Spine queue tabs, project workload, event/producers lists, task inspectors, project mutations, Vault, break-glass, room persona, Task Guardian jobs, autonomous turn pacing, and improvement proposal flows are missing or represented as disabled/empty states.

Branch decision: ready to merge after maintainer review if the merge goal is to establish the public Command Center foundation. It should not be treated as complete R&D Command Center parity or release-ready.

## C. Parity Matrix

| R&D Command Center item | R&D evidence/file/route | Public implementation | Status | Notes | Required fix if any |
| --- | --- | --- | --- | --- | --- |
| `/spine` route | `frontend/src/routes/_layout/spine.tsx` | `frontend/src/App.tsx`, `frontend/src/components/CommandCenter.tsx` | MATCH | Public app serves Command Center for `/spine`. | None for foundation. |
| `/controls` alias | `frontend/src/routes/controls.tsx` redirects to `/spine` | `normalizeCommandPath('/controls')` maps to `/spine` | MATCH | Same user destination, implemented client-side instead of router redirect. | None. |
| `/command-center` alias | `frontend/src/routes/command-center.tsx` redirects to `/spine` | `normalizeCommandPath('/command-center')` maps to `/spine` | MATCH | Same user destination. | None. |
| Root behavior | R&D root is separate app shell; `/spine` is explicit Command Center | Public root normalizes to `/spine` | PARTIAL | Good for workstation-first public app, but not identical to R&D navigation. | Confirm desired root behavior before merge. |
| Header and surface tabs | R&D uses `SparkbotSurfaceTabs` and info dialog | Public has simpler top nav and no info dialog | PARTIAL | Command Center is reachable, but the R&D surface switcher is simplified. | Restore full surface navigation if maintainer wants exact UI parity. |
| AI Setup panel | `SetupPanels.tsx` `AISetupPanel` | AI Setup section with provider buttons, model picker, credential save, model refresh, local model card, stack | MATCH | Core controls are present and call backend endpoints. | None. |
| Provider set | `useSetupHelpers` provider order includes OpenRouter, OpenAI, Anthropic, Google, Groq, MiniMax, xAI, local, subscription routes | `backend/app/api/command_center.py` `PROVIDERS` and `PROVIDER_MODELS` | PARTIAL | Main providers are present; subscription routes are visible but not actually detected. | Add the R&D subscription detection or disable with clearer copy. |
| Provider credential save | `useControlsState.saveProviderTokens`, `POST /api/v1/chat/models/config` | `saveProviderCredential`, server-side `secrets.json`, no secret echo | MATCH | Public implementation is safer for local public use and does not return saved values. | None. |
| OpenRouter model refresh | `GET /api/v1/chat/openrouter/models` in R&D model route | Same public endpoint calls provider model list through backend | MATCH | Sorts free models first and returns safe metadata. | None. |
| OpenRouter auto-select first free model | R&D `useControlsState` auto-selects first free model when no model selected | Public refresh loads options but does not auto-select first free when blank | PARTIAL | User can still choose/save manually. | Add auto-select behavior if needed for exact onboarding parity. |
| Ollama/local endpoint status | `GET /api/v1/chat/ollama/status` | Same public endpoint checks local endpoint and model IDs | MATCH | Public supports configurable base URL and model save. | None. |
| Default model selection | R&D validates provider/model and persists through config/env updates | Public validates provider/model and persists to local backend config | PARTIAL | Behavior is present; persistence target differs from R&D env-backed behavior. | Decide whether public should keep local JSON config or use `.env` updates. |
| Four-model stack | R&D `ModelStackForm`, `saveModelStack` | Public stack draft and `POST /models/config` | MATCH | Primary/backups/heavy hitter are present and persisted. | None. |
| Routing policy option | R&D includes `cross_provider_fallback` in default save | Public backend stores policy but UI does not expose the toggle | PARTIAL | Hidden from user. | Add the R&D cross-provider fallback toggle. |
| Model seat assignment | R&D has agent override controls; Round Table seat behavior is downstream | Public has eight seat cards with agent/model selectors | PARTIAL | Visible and saves route overrides, but seat state itself is browser-local. | Move seat config to backend persistence with Round Table routes. |
| Specialty Wing controls | R&D Agents panel routes specialty agents and spawned agents | Public agent override and seat controls preserve the workflow path | PARTIAL | Basic route selection works; templates and identity metadata are simplified. | Port agent templates and metadata fields. |
| Agent creation | R&D `POST /api/v1/chat/agents` stores custom agents with emoji, identity, scopes, tools | Public `POST /api/v1/chat/agents` stores name/label/description only | PARTIAL | Creation works but loses system prompt, emoji, identity, tool scope, delete flow, invite route. | Port full agent schema or public-safe subset. |
| Agent override controls | `saveAgentOverrides`, `POST /models/config` | Same public config path | MATCH | Route/model validation is present. | None. |
| Comms setup | R&D Comms accordion includes chat, source control, email, calendar, drive, and workspace connector fields | Public shows disabled connector cards only | INTENTIONALLY_DISABLED | This avoids committing write-capable connector credential flows before safety review. | Port public-safe connector gates later. |
| Security profile save | `security_guardrails_enabled`, `custom_guardrails` | Same fields in public config | MATCH | Toggle and custom guardrail save are present. | None. |
| Operator PIN | R&D uses Guardian PIN route and status | Public has `POST /api/v1/chat/security/operator-pin`, PBKDF2 hash in local file | PARTIAL | PIN save works; route differs and full Guardian PIN behavior is not present. | Align route with R&D or keep public route and document compatibility. |
| Passphrase rotation | R&D `POST /api/v1/chat/security/passphrase` | Missing | MISSING | Visible in R&D Security card. | Port only after public safety review. |
| Operator user controls | R&D `POST /api/v1/chat/security/operator-users` | Missing | MISSING | Public security status returns empty usernames only. | Port public-safe operator controls or remove from parity target. |
| Env permission fix | R&D `POST /api/v1/chat/security/fix-permissions` | Missing | MISSING | Public safety scan passes, but UI parity is absent. | Add guarded local action if public-approved. |
| Break-glass controls | R&D `GET/POST/DELETE /api/v1/chat/guardian/breakglass` | Public status hardcodes inactive; no activate/deactivate UI | MISSING | User-visible Security tab in R&D is not restored. | Port after action gate design. |
| Vault tab | R&D `GET/POST/DELETE /api/v1/chat/guardian/vault` | Public stores provider credentials in local backend config but has no Vault UI | MISSING | This is a major R&D Command Center tab. | Port public-safe Vault or keep disabled with full UI explanation. |
| Room persona | `OperationalPanels.tsx` loads bootstrap room and patches `/rooms/{room_id}` | Missing | MISSING | R&D shows Room Persona at top of operations. | Port room bootstrap and room patch route. |
| System Health card | R&D uses health, Guardian, provider count, default model, approvals | Public has simplified health metrics | PARTIAL | Basic health/default provider/approvals visible. | Add Guardian detail and provider readiness parity. |
| Token Guardian card | R&D shows mode, usage, live routes, suggestions, last route | Public exposes mode save only | PARTIAL | Mode persists; usage telemetry is absent. | Port dashboard usage fields or show explicit empty telemetry. |
| Task Guardian jobs | R&D create/pause/run jobs and run history via room Guardian routes | Public shows job counts and disabled Run button | INTENTIONALLY_DISABLED | Correctly blocked as service-layer follow-up, but not parity. | Port room Guardian task routes. |
| Task write mode | R&D toggles write mode through Guardian route | Public does not expose working write-mode toggle | MISSING | R&D Task Guardian tab has this control. | Port guarded toggle or public-safe equivalent. |
| Dashboard summary | R&D `GET /api/v1/chat/dashboard/summary` backed by rooms/tasks/approvals/usage | Public endpoint returns safe zeros and config mode | PARTIAL | Route exists but is shallow. | Back with real room/task/reminder data. |
| Spine overview | R&D operator overview helpers | Public `GET /api/v1/chat/spine/operator/overview` returns empty queues | PARTIAL | Route exists, but no task/project/event data. | Port Spine persistence/service layer. |
| Spine queue tabs | R&D queue tabs: open, blocked, approval, stale, orphaned, resurfaced, executive, missing source, missing project | Public shows stat tiles and follow-up cards only | MISSING | maintainer will notice lack of clickable queue tabs and task rows. | Port queue endpoints and UI tables. |
| Task inspector | R&D `TaskInspector` fetches task detail, lineage, dependencies, approvals | Missing | MISSING | Major operator workflow not present. | Port task detail endpoints and inspector sheet. |
| Project workload | R&D `SpineWorkloadTable`, `/projects/workload` | Missing | MISSING | Public only has empty route card. | Port workload endpoint and table. |
| Projects list/create/archive | R&D `SpineProjectTable`, `NewProjectButton`, archive action | Public has no projects table or mutation path | MISSING | R&D create button is disabled in one path but list/archive UI exists. | Port project list and safe mutation behavior. |
| Events log | R&D `SpineEventsPanel`, recent events route with limit selector | Public has no event list | MISSING | Only an empty card exists. | Port events route and UI. |
| Producer registry | R&D `SpineProducersPanel` | Public has no producer list | MISSING | Only an empty card exists. | Port producers route and UI. |
| Improvement proposals | R&D proposal tab with status filter and approve/reject actions | Missing | MISSING | Full tab absent. | Port read path first; gate approve/reject. |
| Autonomous turn pacing | R&D card lists paused/backoff pairs and resume action | Missing | MISSING | User-visible operations safety control absent. | Port read path first, resume action only with confirmation. |
| Round Table launch | R&D route references room/meeting pathways outside first foundation | Public Launch button disabled | INTENTIONALLY_DISABLED | Correctly blocked pending room/artifact/meeting routes. | Port in room/service branch. |
| Persistence | R&D uses DB/env/runtime service state depending on route | Public uses local JSON files for config/secret/PIN and browser localStorage for seats | PARTIAL | Safe but not equivalent; browser-local seat state will not survive across browsers. | Move seat and room-linked config to backend. |
| Public safety | R&D contains source-only and operator-only paths not suitable for public copy | Public safety scan passes; secrets not echoed | MATCH | No public-safety issue found in audited branch. | Continue scan before every commit. |

## D. User-visible Gaps

1. R&D top-level Spine tabs are not real tabs in public: Overview, Queues, Projects, Events, Producers, Security, Vault, Task Guardian, and Improvement are shown as follow-up cards instead of interactive panels.
2. The R&D queue selector and queue rows are missing, including Open, Blocked, Approval, Stale, Orphaned, Resurfaced, Executive, Missing Source, and Missing Project.
3. The task/project/event inspector sheet is missing.
4. Project workload and project list tables are missing.
5. Recent events and producer registry lists are missing.
6. Vault and break-glass workflows are absent.
7. Room Persona is absent.
8. Comms setup was reduced from real credential forms and toggles to disabled connector cards.
9. Security diagnostics are simplified; passphrase, explicit operators, frontend exposure, CORS, headers, env file permission repair, and risky feature details are not shown.
10. Task Guardian job creation, pause/resume, run now, run history, and write-mode toggle are absent or disabled.
11. Token Guardian usage metrics are simplified to mode only.
12. Agent spawn is simplified; templates, emoji, identity, tool scope, delete, and invite route behavior are missing.
13. Seat assignment exists but seat state is browser-local instead of backend persisted.
14. OpenRouter refresh works, but the R&D auto-select-first-free-model behavior is not fully reproduced.
15. The R&D info dialog and richer surface navigation are not restored.

## E. Backend / Service Gaps

Missing or shallow backend capabilities needed for full Command Center parity:

- Room bootstrap and room update path for persona: `/api/v1/chat/users/bootstrap`, `/api/v1/chat/rooms/{room_id}`.
- Room artifact and meeting routes needed to make Round Table launch live.
- Room Guardian task routes for list/create/update/run/history.
- Guardian write-mode route.
- Guardian break-glass status, activate, and deactivate routes.
- Guardian Vault list/add/delete routes.
- Security passphrase, operator user, feature toggle, and permission-fix routes.
- Skills list route used by R&D Controls state.
- Audit/policy decision route used by R&D Controls state.
- Dashboard summary backed by real rooms, tasks, reminders, approvals, model routing, and usage data.
- Spine operator queue routes for all queue types.
- Spine task detail and lineage route.
- Spine recent events route with limit.
- Spine producer registry route.
- Spine project list, workload, create, status, owner, archive, cancel, reopen, attach, and detach routes.
- Spine signal routes used by the operator console.
- Improvement proposal list, approve, and reject routes.
- Autonomous pause list and resume routes.
- Backend persistence for seat routing and room-associated Command Center state.

Endpoints present but shallow in public:

- `/api/v1/chat/dashboard/summary` returns safe zero counts.
- `/api/v1/chat/spine/operator/overview` returns empty queues.
- `/api/v1/chat/spine/operator/events` returns an empty list.
- `/api/v1/chat/spine/operator/producers` returns an empty list.
- `/api/v1/chat/spine/operator/projects` returns an empty list.
- `/api/v1/chat/guardian/status` reports local config status but not the full R&D Guardian subsystem.
- `/api/v1/chat/security/status` reports a minimal local posture only.

## F. Branch Decision

ready to merge after maintainer review

Rationale: the branch is a real improvement and a valid foundation for the public Workstation Command Center. It should merge only with the explicit understanding that it is not final R&D `/spine` parity. The merge should be followed immediately by the service-layer branch, not by polish or release prep.

## G. Next Branch Recommendation

`port-rd-command-center-room-spine-services`

Scope for that branch:

- Port room bootstrap, room persona, room artifacts, and meeting service routes.
- Replace empty Spine overview/routes with real queue, project, event, producer, task detail, and workload services.
- Restore the R&D top-level Spine tabs and inspector sheet.
- Restore Task Guardian job list/create/run/pause and write-mode controls behind public-safe gates.
- Restore Round Table launch only after room/artifact routes are working.

## Validation Notes

Validation requested for this audit:

- `git diff --check`
- backend tests
- frontend tests
- frontend build
- `npm audit`
- `bash scripts/check-public-safety.sh`
- `bash scripts/validate-public-shell.sh`
- manual route checks for `/`, `/spine`, `/controls`, `/command-center`

Results are recorded in the final response for this audit run.
