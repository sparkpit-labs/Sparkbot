# Manual Local MVP Smoke Workstation Report

## A. Verdict

**MVP_SMOKE_PASS_WITH_WARNINGS**

The current public repo can be used as a coherent local AI Workstation MVP through backend-backed routes and API workflows. The smoke passed with a mocked/local-safe OpenRouter provider transport. A live provider browser smoke remains pending because no real provider credential was used or exposed in this branch.

No product code changes were required.

## B. Environment

- Branch: `manual-local-mvp-smoke-workstation`
- Base branch: `audit-public-mvp-route-and-copy-readiness`
- Base commit: `ac9285d97af770f370993ff6d3deb96c102468c0`
- Backend command used for route smoke: `SPARKBOT_DATA_DIR=<temporary> SPARKBOT_BACKEND_PORT=18022 bash scripts/start-backend-dev.sh`
- Frontend command used for route smoke: `SPARKBOT_BACKEND_PORT=18022 VITE_SPARKBOT_API_BASE_URL=http://127.0.0.1:18022 SPARKBOT_FRONTEND_PORT=15174 bash scripts/start-frontend-dev.sh`
- API smoke path: FastAPI `TestClient` with temporary `SPARKBOT_DATA_DIR`
- Provider path used: mocked/local-safe OpenRouter route by monkeypatching the provider HTTP transport used by existing backend tests
- Live model call performed: no
- Browser-click UI e2e performed: no; HTTP route checks and API-level smoke were run

## C. Smoke Checklist

| Step | Status | Evidence | Notes/gaps |
| --- | --- | --- | --- |
| 1. Fresh local setup/run from public instructions | PASS | `bash scripts/validate-public-shell.sh` PASS; dev server scripts started on alternate ports | Existing local dependencies were present; validation also created a temporary backend venv. |
| 2. Backend starts successfully | PASS | `scripts/start-backend-dev.sh` served `/health` with HTTP 200 | Temporary local state used. |
| 3. Frontend starts successfully | PASS | `scripts/start-frontend-dev.sh` served Vite route responses | Frontend pointed to alternate backend URL. |
| 4. Main routes load | PASS | `/`, `/spine`, `/controls`, `/command-center`, `/workstation`, `/chat`, `/roundtable` returned HTTP 200 | HTTP route checks, not browser clicks. |
| 5. Command Center/Spine real state | PASS | API smoke read Command Center config, Workstation history, events, task records, notes, and counters | State came from shared backend store. |
| 6. Configure provider/model route | PASS | `POST /api/v1/chat/models/config` selected OpenRouter model and saved server-side credential flag | Mock credential value was not returned by API. |
| 7. Chat sends through selected provider route | PASS | `POST /api/chat/messages` returned `model_execution.status=success` | Provider transport was mocked/local-safe. |
| 8. Chat writes safe model events | PASS | `model.call.completed` events present; payloads did not include prompts, messages, outputs, headers, or credentials | Event scan passed. |
| 9. Create/edit agent | PASS | Custom `smoke_lens` agent created and edited | Instructions were redacted before API return. |
| 10. Assign agent to Round Table seat | PASS | `PATCH /api/seats/2` persisted `smoke_lens` | Readback after restart confirmed. |
| 11. Invite route/provider/model behavior | PASS | Agent invite route saved with OpenRouter model and credential configured flag | Secret was server-side and not echoed. |
| 12. Provider-backed Round Table meeting | PASS | `POST /api/roundtable/sessions/{id}/run` completed via mocked provider path | Live provider remains pending. |
| 13. Seat 1 remains Meeting Manager | PASS | Meeting-manager turns had `seat_index=1` and `agent=meetings_manager` | Preserved through persisted session. |
| 14. Assigned agent identity/instructions used | PASS | Captured provider prompt included Smoke Lens identity, seat, role, and redacted instructions | Prompt was inspected only in local smoke process, not persisted. |
| 15. Turns/assignments/summary/wrap-up saved | PASS | Round Table saved 16 turns, 7 assignments, 1 summary, and 1 wrap-up note | Summary linked to note id. |
| 16. No per-turn notes | PASS | Round Table note count for the session was 1 | Only manager wrap-up note created. |
| 17. Memory create/list/edit/delete | PASS | Memory created, patched, recalled, then deleted after Guardian confirmation | Delete used API confirmation flow. |
| 18. Chat memory recall path | PASS | Chat provider prompt included source-labeled redacted memory context | No secrets in API response/events. |
| 19. Round Table memory recall path | PASS | Round Table provider prompt included source-labeled redacted memory context | No secrets in persisted events. |
| 20. Notes/history/Spine/events real data | PASS | Workstation history included Chat, Round Table, notes, events, and task records | Spine route also returned HTTP 200. |
| 21. Task record lifecycle | PASS | Created task, paused, resumed, marked done; second task canceled | State only. |
| 22. Run/write-mode fail closed | PASS | Task run and write-mode routes returned HTTP 403 | Safe block events were present. |
| 23. Restart backend | PASS | Simulated restart/readback with a new backend client against same temporary store | Dev-server restart not required for API smoke; persistence used same disk store. |
| 24. Persistence after restart | PASS | Provider config, agent, invite route, seat assignment, Chat session, Round Table session, notes, events, and tasks survived readback | See persistence section. |
| 25. Unsupported/unsafe actions fail closed | PASS | Protected Chat input blocked as `external_send`; protected model output blocked as `process_action` | No action execution occurred. |
| 26. No secrets exposed | PASS | API/events/history scan excluded mock credentials, protected prompt fragments, model output text, headers, and raw provider payloads | Changed-file public scan also passed. |

## D. Persistence Verification

Survived restart/readback through a second backend client against the same temporary store:

- provider/model config: PASS, default provider stayed `openrouter`
- agents: PASS, custom `smoke_lens` agent persisted with redacted instructions
- seat assignments: PASS, Seat 2 stayed assigned to `smoke_lens`
- invite routes: PASS, invite route persisted with `credential_configured=true` and no secret echo
- chat sessions/history: PASS, chat session persisted with two messages
- Round Table room/session/turns/assignments/summary/wrap-up note: PASS, 16 turns, 7 assignments, 1 summary, 1 note
- memory: PASS for create/edit/recall before delete; delete removed the entry from future recall
- notes/history: PASS, workstation and Round Table notes persisted
- events: PASS, safe events persisted
- task records: PASS, done and canceled task records persisted
- rerun/idempotency: PASS, Round Table rerun kept 16 turns, 7 assignments, 1 summary, and 1 note without duplicating artifacts

## E. Safety Verification

- Secret exposure check: PASS. Mock provider/invite credentials and redaction markers were absent from API responses, events, history, and report text.
- Event redaction check: PASS. Model events stored provider/model/status/count/duration/phase metadata only; no prompts, messages, outputs, headers, or credentials.
- Unsupported automation fail-closed check: PASS. Protected Chat input for external send returned a blocked action and executed nothing.
- Task run/write-mode fail-closed check: PASS. Backend returned HTTP 403 for both task run and write-mode routes.
- Protected prompt/output fail-closed check: PASS. Protected model output was replaced by safe blocked-action handling before persistence.
- Browser localStorage source-of-truth check: covered by existing frontend tests and previous route/copy audit; this branch did not add product state.

## F. Issues Found

| Severity | Description | Fix applied | Remaining action |
| --- | --- | --- | --- |
| P2 | Live provider browser smoke was not run because no real provider credential was used. | None; used mocked/local-safe provider path as allowed. | Run a separate live-provider smoke with disposable credentials when available. |
| P2 | Browser-click UI e2e was not run; smoke used HTTP route checks plus API workflow. | None. | Add Playwright or equivalent local e2e later if desired. |
| P3 | Existing Starlette/httpx deprecation warning appears in backend tests. | None; unrelated to MVP smoke. | Track as dependency maintenance. |

## G. MVP Recommendation

Proceed to internal operator review and a narrow live-provider smoke branch when a disposable supported provider credential is available.

Recommended next branch: `live-provider-smoke-chat-roundtable` if credentials are available, otherwise `mvp-operator-review-polish` for issues found during hands-on use.

## Validation Results

- `git diff --check`: PASS
- Backend tests, `.venv-local/bin/pytest backend/tests -q`: PASS, `52 passed`, one existing Starlette/httpx deprecation warning
- Frontend tests, `npm test -- --run`: PASS, `10 passed`
- Frontend build, `npm run build`: PASS
- `npm audit --audit-level=moderate`: PASS, `0 vulnerabilities`
- `bash scripts/check-public-safety.sh`: PASS
- `bash scripts/validate-public-shell.sh`: PASS, backend `52 passed`, frontend `10 passed`, build PASS, audit PASS
- Changed-file privacy scan: PASS, no matches
- Manual HTTP route checks: PASS for `/`, `/spine`, `/controls`, `/command-center`, `/workstation`, `/chat`, `/roundtable`; backend `/health` returned HTTP 200
