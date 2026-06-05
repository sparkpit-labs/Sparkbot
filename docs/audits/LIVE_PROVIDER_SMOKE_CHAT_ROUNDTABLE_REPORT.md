# Live Provider Smoke Chat Roundtable Report

## A. Verdict

**LIVE_PROVIDER_NOT_RUN_CREDENTIALS_UNAVAILABLE**

The live provider smoke was not run. The branch checked for explicitly disposable/test OpenRouter and OpenAI provider credentials without printing values, and none were present. The branch also checked the local Ollama endpoint, which was not reachable and had no available model list.

No live Chat or Round Table model call was attempted. No product code changes were made.

## B. Provider Used

| Field | Result |
| --- | --- |
| Provider name | None |
| Model name | None |
| Auth mode used | None |
| Disposable/test credentials available | No |
| Credentials committed or printed | No |
| Local model alternative | Ollama unavailable on the default local endpoint |

Only environment variable presence was inspected. Values were not printed, copied, committed, or stored in this report.

## C. Chat Live Smoke

| Check | Status | Evidence | Warnings |
| --- | --- | --- | --- |
| Live provider route configured | NOT_RUN | No explicitly disposable/test credential was available | Do not use personal or long-lived production keys for this smoke |
| Live Chat message sent | NOT_RUN | No live provider call was attempted | Run later with a disposable/test provider key or confirmed local model |
| Real model response received | NOT_RUN | No live provider call was attempted | Mocked/local-safe Chat smoke already passed on the previous branch |
| Chat model-call event redaction | NOT_RUN | No live model-call event was created on this branch | Existing mocked/local-safe event redaction remains covered by tests and prior smoke |

## D. Round Table Live Smoke

| Check | Status | Evidence | Warnings |
| --- | --- | --- | --- |
| Live provider-backed meeting run | NOT_RUN | No explicitly disposable/test credential or local model was available | Do not fake the live provider result |
| Number of turns | NOT_RUN | No live Round Table run occurred | Prior mocked/local-safe smoke saved 16 turns |
| Assignments | NOT_RUN | No live Round Table run occurred | Prior mocked/local-safe smoke saved assignments and summary |
| Summary | NOT_RUN | No live Round Table run occurred | Prior mocked/local-safe smoke created the manager summary |
| Wrap-up note | NOT_RUN | No live Round Table run occurred | Prior mocked/local-safe smoke created one wrap-up note only |
| Agent/seat behavior | NOT_RUN | No live Round Table run occurred | Prior mocked/local-safe smoke verified assigned agent context |
| Meeting Manager behavior | NOT_RUN | No live Round Table run occurred | Prior mocked/local-safe smoke verified Seat 1 remained Meeting Manager |

## E. Persistence

No new live provider artifacts were created on this branch, so provider-backed Chat and Round Table live persistence was not tested.

The current branch still inherits the previously validated server-side persistence behavior for:

- provider/model config
- agents
- seat assignments
- invite routes
- Chat sessions/history
- Round Table rooms/sessions/turns/assignments/summaries/wrap-up notes
- memory entries
- notes/history
- safe events
- task records

Persistence after restart remains pending for a real live provider run.

## F. Safety Verification

| Check | Status | Evidence |
| --- | --- | --- |
| Credential exposure check | PASS | Only boolean credential availability was printed; no values were printed or committed |
| Prompt/output in model-call events | NOT_RUN | No live model-call event was created |
| Task run/write mode fail-closed | PASS | Backend validation confirmed task run and write-mode requests return HTTP 403 |
| Protected action fail-closed | PASS | Backend validation confirmed protected request and model-output blocking before dispatch/persistence |
| Subscription CLI auth not used | PASS | No CLI-backed subscription auth path, local CLI session, connector auth, or bridge was used |
| Route health | PASS | Backend `/health` returned HTTP 200; `/`, `/spine`, `/controls`, `/command-center`, `/workstation`, `/chat`, and `/roundtable` returned HTTP 200 |

## G. Issues/Fixes

| Severity | Description | Fix applied or deferred |
| --- | --- | --- |
| P2 | No explicitly disposable/test live provider credential was available. | Deferred. Run this smoke later with a disposable/test provider key or a confirmed local model. |
| P2 | Ollama was not reachable on the default local endpoint. | Deferred. A local-model live smoke can run later if a model is already available. |
| P3 | No live provider persistence artifacts were created on this branch. | Expected result of the no-credential path. |

## H. Manual Checks

| Route | Status |
| --- | --- |
| Backend `/health` | HTTP 200 |
| `/` | HTTP 200 |
| `/spine` | HTTP 200 |
| `/controls` | HTTP 200 |
| `/command-center` | HTTP 200 |
| `/workstation` | HTTP 200 |
| `/chat` | HTTP 200 |
| `/roundtable` | HTTP 200 |

## I. Validation Results

- `git diff --check`: PASS
- Backend tests, `.venv-local/bin/pytest backend/tests -q`: PASS, `52 passed`, one existing Starlette/httpx deprecation warning
- Frontend tests, `npm test -- --run`: PASS, `10 passed`
- Frontend build, `npm run build`: PASS
- `npm audit --audit-level=moderate`: PASS, `0 vulnerabilities`
- `bash scripts/check-public-safety.sh`: PASS
- `bash scripts/validate-public-shell.sh`: PASS, backend `52 passed`, frontend `10 passed`, build PASS, audit PASS
- Manual HTTP route checks: PASS for backend `/health`, `/`, `/spine`, `/controls`, `/command-center`, `/workstation`, `/chat`, and `/roundtable`
- Changed-file privacy scan: PASS, no matches

## J. MVP Recommendation

Do not proceed with a live provider claim until a disposable/test provider credential or a confirmed already-available local model is available.

Recommended next branch: `mvp-operator-review-polish`.
