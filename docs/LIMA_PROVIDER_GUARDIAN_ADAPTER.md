# LIMA Guardian Provider Adapter Contract

This document defines the public Sparkbot contract for Codex and Claude subscription prompt dispatch through the LIMA Guardian boundary. Sparkbot includes only a fail-closed client for a configured localhost adapter. The public Sparkbot shell must not execute Codex or Claude CLIs directly.

## Current Status

Provider Setup can report subscription readiness today:

- Codex subscription: CLI availability plus sign-in state through `CODEX_HOME` or `SPARKBOT_CODEX_AUTH_FILE`.
- Claude subscription: CLI availability plus sign-in state through `CLAUDE_HOME`, `SPARKBOT_CLAUDE_AUTH_FILE`, or `SPARKBOT_CLAUDE_SUBSCRIPTION_ENABLED=true`.

When all of these are true, Sparkbot can delegate an explicit operator-submitted Provider Setup prompt to LIMA:

- `SPARKBOT_PROVIDER_CALLS_ENABLED=true`
- `SPARKBOT_LIMA_PROVIDER_ADAPTER_URL=http://127.0.0.1:<port>/<path>` or `http://localhost:<port>/<path>`
- The selected subscription provider reports CLI and sign-in readiness
- The operator submits a prompt through the Provider Prompt Smoke form or the matching backend endpoint

The one-command smoke wrapper can assert host subscription readiness during LIMA/operator install testing:

```bash
SPARKBOT_SMOKE_USE_HOST_SUBSCRIPTIONS=true SPARKBOT_SMOKE_REQUIRE_SUBSCRIPTIONS=true bash scripts/run-local-smoke-test.sh
```

Default smoke validation does not dispatch real Codex or Claude prompts. It verifies disabled and fail-closed states unless a LIMA-side adapter is configured and invoked explicitly.

`GET /guardian/status` exposes a read-only `provider_adapter_contract` object with contract version, covered provider IDs, required request fields, allowed response statuses, audit posture, and this document path. That object is machine-readable install-test metadata only; it is not a dispatch endpoint.

## Boundary Rule

Sparkbot may call only a configured localhost LIMA Guardian provider adapter. Sparkbot must not expose a direct subprocess, terminal, shell, or local CLI dispatch path for subscription providers.

Required Guardian controls:

- Capability check before dispatch.
- Explicit operator approval for the prompt request.
- Audit log record for allow, deny, timeout, and failure outcomes.
- Secret redaction for auth state, environment, process output, and logs.
- Timeout enforcement.
- No shell expansion.
- Fail-closed behavior when approval, capability, adapter health, timeout, or audit writing fails.

## Provider IDs

The adapter contract covers these Sparkbot provider IDs:

| Provider ID | Runtime | Readiness source |
| --- | --- | --- |
| `openai-codex-subscription` | Codex CLI subscription runtime through LIMA Guardian | `CODEX_HOME`, `SPARKBOT_CODEX_AUTH_FILE`, `SPARKBOT_CODEX_CLI` |
| `claude-subscription` | Claude Code subscription runtime through LIMA Guardian | `CLAUDE_HOME`, `SPARKBOT_CLAUDE_AUTH_FILE`, `SPARKBOT_CLAUDE_SUBSCRIPTION_ENABLED`, `SPARKBOT_CLAUDE_CLI` |

OpenRouter remains a separate backend API-key prompt path and is not a subscription CLI adapter.

## Sparkbot To Guardian Request

For an explicit subscription prompt, Sparkbot sends a structured HTTP JSON request to `SPARKBOT_LIMA_PROVIDER_ADAPTER_URL`. The URL must be an `http://localhost...` or `http://127.0.0.1...` endpoint.

```json
{
  "contract_version": 1,
  "request_id": "operator-visible-unique-id",
  "provider_id": "openai-codex-subscription",
  "model": "openai-codex/gpt-5.3-codex",
  "prompt": "operator supplied prompt text",
  "context": {
    "source_surface": "provider-setup",
    "chat_session_id": null,
    "work_lane_card_id": null,
    "selected_memory_note_ids": []
  },
  "operator_approval": {
    "approval_id": "guardian-approval-id",
    "approved_by": "local-operator",
    "approved_at": "ISO-8601 timestamp"
  },
  "limits": {
    "timeout_seconds": 120,
    "max_output_chars": 20000
  },
  "audit": {
    "redaction_required": true,
    "store_prompt": false,
    "store_response": false
  }
}
```

Rules:

- `provider_id` must be one of the subscription provider IDs listed above.
- `model` must be explicit; Sparkbot must not silently fall back to another provider or model.
- `prompt` must be operator supplied or explicitly assembled from user-selected local context.
- Automatic memory retrieval is out of scope until a separate memory contract exists.
- `operator_approval` must be present before dispatch.
- `store_prompt=false` and `store_response=false` are the default public-shell posture unless a later persistence contract is approved.

## Guardian To Sparkbot Response

Guardian should return a structured response that never includes secrets, auth file content, raw environment, full command lines, or unredacted process diagnostics.

```json
{
  "contract_version": 1,
  "request_id": "operator-visible-unique-id",
  "provider_id": "openai-codex-subscription",
  "status": "succeeded",
  "model": "openai-codex/gpt-5.3-codex",
  "response_text": "assistant response text",
  "usage": null,
  "audit_id": "guardian-audit-id",
  "redactions_applied": true,
  "runtime": {
    "adapter": "lima-guardian-provider-runtime",
    "dispatch": "guarded",
    "timeout_seconds": 120
  }
}
```

Allowed status values:

| Status | Meaning |
| --- | --- |
| `succeeded` | Guardian approved and completed the prompt dispatch. |
| `denied` | Guardian or operator denied the request before dispatch. |
| `blocked` | Capability, readiness, policy, or contract validation blocked dispatch. |
| `timeout` | Guardian stopped the request after the timeout. |
| `failed` | Adapter failed without exposing secrets. |

Sparkbot accepts only `succeeded` as a successful prompt response. Other statuses are returned as safe unavailable errors. Sparkbot requires a matching `request_id`, `provider_id`, `model`, contract version `1`, and non-empty `audit_id`.

## Manual Subscription Smoke

After the LIMA adapter is running locally and subscription sign-in readiness is detected, a manual smoke can be run with:

```bash
SPARKBOT_PROVIDER_CALLS_ENABLED=true \
SPARKBOT_LIMA_PROVIDER_ADAPTER_URL=http://127.0.0.1:18099/provider-adapter/dispatch \
bash scripts/start-backend-dev.sh
```

Then submit:

```bash
curl -i -X POST http://127.0.0.1:8000/provider-config/openai-codex-subscription/prompt \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Say OK.","model":"openai-codex/gpt-5.3-codex"}'
```

Use `/provider-config/claude-subscription/prompt` with a `claude-sub/...` model for Claude subscription testing.

## Audit Requirements

Guardian must record an audit event for every request outcome before Sparkbot treats the outcome as final. The audit record should include:

- `request_id`
- `provider_id`
- selected `model`
- approval outcome
- dispatch status
- timeout value
- redaction status
- timestamp
- non-secret error category when applicable

The audit record must not include provider credentials, auth file content, raw environment variables, unredacted prompts, unredacted responses, private filesystem paths, or shell command strings.

## Fail-Closed Cases

Sparkbot treats these as non-dispatch outcomes:

- Provider calls disabled.
- Missing Guardian adapter URL.
- Non-local Guardian adapter URL.
- Missing provider readiness.
- Unknown provider ID.
- Missing explicit model.
- Guardian policy denial.
- Audit write failure.
- Timeout.
- Any adapter error that cannot be safely redacted.

## Public Repo Non-Goals

This public repo does not include:

- LIMA Guardian runtime implementation.
- Codex or Claude CLI subprocess execution.
- Subscription auth-file parsing.
- Credential storage.
- Background prompt jobs.
- Automatic model routing.
- Shell expansion or terminal execution.

## Promotion Gate

Before release-candidate promotion, validation must include:

- Tests proving direct Sparkbot shell CLI execution is impossible.
- Tests proving missing Guardian adapter fails closed.
- Tests proving missing approval fails closed at the LIMA adapter boundary.
- Tests proving unknown provider/model fails closed.
- Tests proving audit write failure fails closed at the LIMA adapter boundary.
- Tests proving prompts and responses are redacted according to the active persistence contract.
- Updated local smoke instructions for LIMA-side install testing.
- Documentation that clearly states which behavior is active and which remains planned.
