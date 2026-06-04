# Narrow Provider Model Execution Audit

- Audit verdict: `PASS`
- Branch audited: `audit-narrow-provider-model-execution`
- Provider slice commit audited: `fc12cef2232ede7576ccf25405ba7c6a68bc039e`
- Starting HEAD for provider slice: `6689eaa0ea0c9a9054916c61ce08c983223d2a30`
- Audit scope: Chat-only provider/model execution through Command Center configuration

## Files Inspected

- `backend/app/services/model_execution.py`
- `backend/app/api/workstation.py`
- `backend/app/api/command_center.py`
- `backend/app/services/workstation_store.py`
- `backend/tests/test_narrow_provider_model_execution.py`
- `backend/tests/test_chat_workstation_integration.py`
- `backend/tests/test_roundtable_workstation_integration.py`
- `backend/tests/test_command_center.py`
- `backend/tests/test_guardian_boundaries.py`
- `frontend/src/components/ChatWorkstation.tsx`
- `frontend/src/components/CommandCenter.tsx`
- `frontend/src/App.test.tsx`
- `frontend/src/api.ts`
- `docs/audits/NARROW_PROVIDER_MODEL_EXECUTION_REPORT.md`
- `docs/README.md`
- `docs/CHAT_SHELL.md`
- `docs/WORKSTATION_ARCHITECTURE_BOUNDARY.md`
- `docs/WORKSTATION_SHELL.md`
- `docs/ROUND_TABLE_SHELL.md`
- `docs/LOCAL_DEVELOPMENT.md`
- `docs/LOCAL_SMOKE_TEST.md`

## Provider Routing Assessment

`PASS`.

Chat resolves the selected Command Center `default_selection` first, then normalizes it through `resolve_model_route()`. The execution service reads the existing Command Center config and server-side secret store instead of introducing a separate `.env`-only setup path.

Supported execution paths are narrow: OpenRouter, OpenAI, Anthropic, Google, Groq, xAI, and Ollama. Subscription-only provider labels fail safely as unsupported. Provider routes visible in Command Center but not implemented for server-side public execution also fail safely instead of dispatching.

## Secret-Handling Assessment

`PASS`.

Provider credentials remain server-side in Command Center environment variables or local backend `secrets.json`. Config responses expose only provider readiness booleans and model labels. Chat responses include provider/model/status/event IDs and safe error labels, but do not include API keys, credential values, request headers, or raw provider request bodies.

Frontend Chat and Command Center show safe route labels and credential status only. Saved credential values are not returned to the browser.

## Event-Redaction Assessment

`PASS`.

Model-call events write only redacted metadata:

- provider
- model
- status
- message count
- output character count
- duration
- safe error label
- optional HTTP status

Model-call events do not store prompts, model outputs, authorization headers, request bodies, provider responses, or credential values. The shared Workstation event store still sanitizes sensitive payload keys such as `api_key`, `credential`, `password`, `secret`, and `token`.

## Guardian And Protected-Action Assessment

`PASS`.

Protected user requests fail closed before provider dispatch. Protected model output is treated as text only and is replaced with a safe refusal when it matches protected categories. A `guardian.action_blocked` event is recorded, and no action route is invoked.

Audit hardening patch: Chat protected-action detection was aligned with the Round Table boundary for scheduler and device-control categories, plus matching phrase coverage for external sends, connector actions, file mutation, and process actions. Tests now prove protected user requests do not dispatch to providers and protected model output is blocked for external-send, scheduler, and device-control examples.

No connector, tool, file, process, terminal, browser automation, background worker, scheduler, or device-control execution path was introduced.

## Round Table Non-Regression Assessment

`PASS`.

Round Table provider execution was not added. The route still calls `WorkstationStore.run_roundtable_session()` and stores deterministic provider-safe turns with `provider-safe` / `roundtable-local-skeleton`. Seat 1 remains the Meeting Manager, phase order remains fixed, and wrap-up notes remain manager-wrap-up only.

Round Table persistence tests still pass, including phase order, turn indexes, assignment response links, no duplicate rerun artifacts, no per-turn notes, and protected category fail-closed behavior.

## Shared Workstation State Assessment

`PASS`.

Chat messages, model execution metadata, events, memory, notes, Guardian confirmations, rooms, seats, and Round Table artifacts remain in the shared SQLite-backed Workstation store. The frontend still treats Chat and Round Table product state as backend-backed state rather than browser storage.

## Public Safety Assessment

`PASS`.

The audited branch contains no private repo names, private domains, real provider keys, private IP ranges, unsafe automation claims, or private runtime imports in changed files. Docs describe this as a narrow Chat provider/model execution slice and keep Round Table live provider seats, connectors, schedulers, file/process execution, and device control deferred.

## Validation Results

- `git diff --check`: pass
- `env PYTHONPATH=backend .venv-local/bin/pytest backend/tests -q`: 40 passed, 1 existing Starlette/httpx deprecation warning
- `npm test -- --run`: 7 passed
- `npm run build`: pass
- `npm audit --audit-level=moderate`: 0 vulnerabilities
- `bash scripts/check-public-safety.sh`: pass
- `bash scripts/validate-public-shell.sh`: pass; backend 40 passed, frontend 7 passed, build passed, npm audit 0 vulnerabilities
- Changed-file privacy scan for blocked private references, identity names, private IP ranges, and provider-key assignments: pass
- Manual route check on existing local servers: `/`, `/spine`, `/controls`, `/command-center`, `/workstation`, `/chat`, and `/roundtable` returned HTTP 200
- Manual backend health check on existing local server: `/health` returned `ok`

## Warnings And Blockers

No blockers remain after the audit hardening patch.

Warnings:

- Protected-action classification remains phrase based. That is acceptable for this narrow public slice because no action execution paths exist, but it should be centralized before any broader tool/action surface is added.
- Round Table live provider seats are still deferred and should be added only behind explicit tests, event redaction, and the same Guardian boundary.

## Recommendation

Merge the audit hardening patch into the provider execution slice before building the next feature branch. After that, it is safe to build on Chat provider execution.

Recommended next branch:

`port-rd-roundtable-provider-model-execution`
