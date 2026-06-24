# LIMA AI OS Install Handoff

This handoff is for LIMA AI OS operators validating Sparkbot provider onboarding and guarded subscription dispatch. It is intentionally limited to public Sparkbot behavior and the localhost LIMA Guardian provider adapter contract.

## Current Sparkbot Readiness

Sparkbot is ready for LIMA-side install smoke testing when these local checks pass from the repository root:

```bash
bash scripts/run-local-smoke-test.sh
bash scripts/run-lima-provider-adapter-contract-smoke.sh
```

The first command verifies local startup, local data isolation, provider setup status, OpenRouter free-model enforcement, API-key provider onboarding with placeholder backend keys, and disabled-by-default model-call gates. The second command verifies Sparkbot's subscription-provider client against a local mock adapter, including sanitized report generation and fail-closed handling for `denied`, `blocked`, `timeout`, and `failed` adapter statuses.

These checks prove Sparkbot-side wiring only. They do not prove real Codex or Claude subscription dispatch.

## LIMA Team Setup

Before running the real install smoke, the LIMA side needs:

- A localhost LIMA Guardian provider adapter listening on `http://127.0.0.1:<port>/<path>` or `http://localhost:<port>/<path>`.
- Host Codex CLI installed and signed in with the operator's subscription.
- Host Claude Code installed and signed in with the operator's subscription, or an explicit local readiness flag if that is the approved LIMA-side posture.
- Adapter behavior matching `docs/LIMA_PROVIDER_GUARDIAN_ADAPTER.md`.
- Audit records for all allowed, denied, blocked, timeout, and failed outcomes.

Sparkbot must not receive provider credentials, auth-file contents, raw environment values, full command lines, or unredacted process output.

## Required LIMA Install Smoke

Run this from the Sparkbot repository root after the real adapter is running:

```bash
SPARKBOT_LIMA_PROVIDER_ADAPTER_URL=http://127.0.0.1:<port>/<path> \
bash scripts/run-lima-install-provider-smoke.sh
```

The script starts a temporary Sparkbot backend on `127.0.0.1:18280`, enables explicit provider calls, uses host subscription readiness, dispatches explicit smoke prompts through the configured localhost adapter, validates response metadata, prints adapter audit IDs, and shuts the backend down. It does not execute Codex or Claude CLIs directly from Sparkbot.

Use `SPARKBOT_LIMA_INSTALL_SMOKE_BACKEND_PORT=<port>` if `18280` is already occupied.

To create a sanitized evidence file for handoff, add `SPARKBOT_LIMA_INSTALL_SMOKE_REPORT_PATH`:

```bash
SPARKBOT_LIMA_PROVIDER_ADAPTER_URL=http://127.0.0.1:<port>/<path> \
SPARKBOT_LIMA_INSTALL_SMOKE_REPORT_PATH=./lima-install-smoke-report.txt \
bash scripts/run-lima-install-provider-smoke.sh
```

The report contains provider IDs, selected model IDs, PASS/FAIL markers, and adapter audit IDs. It does not include prompt text, model response text, auth files, provider keys, or adapter credentials.

## Evidence To Return

Return this evidence to SparkPit Labs:

| Check | Evidence |
| --- | --- |
| Sparkbot local smoke | `bash scripts/run-local-smoke-test.sh` exits `PASS`. |
| Sparkbot adapter contract smoke | `bash scripts/run-lima-provider-adapter-contract-smoke.sh` exits `PASS`. |
| Real LIMA install smoke | `SPARKBOT_LIMA_PROVIDER_ADAPTER_URL=... bash scripts/run-lima-install-provider-smoke.sh` exits `PASS`. |
| Sanitized evidence file | `SPARKBOT_LIMA_INSTALL_SMOKE_REPORT_PATH=...` creates a report with provider PASS lines and audit IDs. |
| Codex subscription dispatch | Smoke output includes a `PASS` line for `openai-codex-subscription` with a non-empty `audit_id`. |
| Claude subscription dispatch | Smoke output includes a `PASS` line for `claude-subscription` with a non-empty `audit_id`. |
| Fail-closed posture | LIMA adapter can return safe `denied`, `blocked`, `timeout`, and `failed` statuses without leaking secrets. |
| No direct CLI execution | Sparkbot-side logs show adapter delegation only, not Codex or Claude subprocess execution. |

Do not send secrets, auth files, provider keys, private paths, raw prompts that contain sensitive content, or raw model responses.

## Current Blocker For Release Sign-Off

Sparkbot-side provider onboarding and adapter wiring are implemented and validated against local contract tests. Public V1.0.0 subscription-provider sign-off still requires the real LIMA install smoke above to pass against the actual LIMA Guardian provider adapter with real host Codex and Claude subscription sign-in state.
