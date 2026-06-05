# Workstation Model Capability Boundary Report

## Branch And Base

- Branch: `mvp-workstation-model-capability-boundary`
- Base branch: `mvp-operator-review-polish`
- Base commit: `a342cd00c2102d682327c9aef2ac25dddf95a826`

## Decision Checked

The Workstation is for work. Chat and Round Table should let the configured model produce text work the model is capable of producing. Hidden keyword blockers should not prevent model dispatch just because the operator asks for drafting, planning, commands, email text, scheduling plans, connector plans, or other work outputs.

Actual external/tool execution is a separate product capability. This branch does not add connector sends, scheduler/runner execution, file/process/terminal/browser/device automation, local CLI subscription auth, or token bridges.

## What Changed

- Removed hardcoded Chat pre-dispatch keyword blocking for work requests such as external delivery, connector, file/process, scheduling, terminal, and device wording.
- Removed hardcoded Round Table session blocking for similar work-request wording.
- Removed model-output keyword replacement that converted action-language model text into a blocked/refusal response.
- Kept Chat and Round Table provider execution text-only.
- Added Command Center custom guardrail injection into Chat and Round Table prompts when `security_guardrails_enabled` is true and `custom_guardrails` is saved.
- Kept task run/write-mode execution routes disabled and fail-closed.
- Kept unsupported subscription-only provider routes fail-closed.
- Kept model-call events metadata-only, with no prompts, outputs, headers, credentials, or secrets.

## Current Boundary

| Area | Behavior |
| --- | --- |
| Chat text work | Dispatches to the selected supported provider route when configured. |
| Round Table text work | Runs provider-backed or deterministic text meetings, even if the goal mentions work that would require external execution later. |
| Command Center guardrails | Applied only when the operator enables security guardrails and saves custom guardrail text. |
| External/tool execution | Not implemented in this branch. |
| Task run/write mode | Still disabled and fail-closed. |
| Subscription-only local-session providers | Still unsupported and fail-closed. |
| Event payloads | Still redacted and metadata-only for model calls. |

## Tests Added Or Updated

- Chat work requests with external/action wording now dispatch to the configured model as text-only work.
- Chat model output containing action wording is returned as text and does not create execution or blocked-action events.
- Command Center custom guardrails are injected into Chat prompts only when enabled.
- Round Table custom guardrails are injected into provider-backed seat prompts when enabled.
- Round Table work-request goals complete as text-only meetings instead of blocking before turns/assignments/summaries/notes.
- Round Table model output containing action wording persists as text-only turns, while model-call events remain metadata-only.

## Validation Results

- `git diff --check`: PASS
- Backend tests, `.venv-local/bin/pytest backend/tests -q`: PASS, `53 passed`, one existing Starlette/httpx deprecation warning
- Focused backend tests, `.venv-local/bin/pytest backend/tests/test_narrow_provider_model_execution.py backend/tests/test_roundtable_workstation_integration.py -q`: PASS, `25 passed`, one existing Starlette/httpx deprecation warning
- Frontend tests, `npm test -- --run`: PASS, `10 passed`
- Frontend build, `npm run build`: PASS
- `npm audit --audit-level=moderate`: PASS, `0 vulnerabilities`
- `bash scripts/check-public-safety.sh`: PASS
- `bash scripts/validate-public-shell.sh`: PASS, backend `53 passed`, frontend `10 passed`, build PASS, audit PASS
- Changed-file privacy scan: PASS, no matches after case-sensitive provider-key scan

## Remaining Warnings

- This branch does not add live external execution, connector writes, scheduler/runner behavior, browser automation, terminal/process execution, or device control.
- If future execution-capable routes are added, they need explicit backend routes, Command Center controls, event redaction, tests, and confirmation gates before execution is enabled.
- Live provider smoke still depends on disposable/test provider credentials or an available local model.
