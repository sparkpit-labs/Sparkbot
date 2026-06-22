# Guardian Policy Contract

This contract defines the public safety boundary for future Guardian behavior. Guardian Controls are currently preview only. The current public baseline includes only a read-only Guardian policy status surface. It does not include runtime policy enforcement, approval execution, sensitive action execution, or audit persistence.

## Current Boundary

The Guardian Controls shell may describe planned categories and blocked future work. It must not imply that policy enforcement is active today.

- `GET /guardian/status` may report static read-only posture, not-implemented runtime enforcement, guarded-future sensitive action categories, and a read-only provider execution boundary.
- The provider execution boundary must remain `guarded-future` and `fail-closed` until LIMA Guardian provides capability checks, operator approval, audit logging, secret redaction, timeout control, and no-shell-expansion dispatch for subscription CLIs.

## Sensitive Action Classes

Future runtime work must classify sensitive actions before execution. Sensitive actions include:

- External sends.
- Connector calls.
- Credential usage.
- File writes.
- Terminal or tool execution.
- Model-provider calls that include private user data.
- Persistence or memory writes.
- Any action that mutates local or external state.

## Future Runtime Requirements

Before Guardian moves beyond preview, the implementation must support:

- Deny by default for sensitive actions.
- Explicit approval for sensitive actions.
- A durable audit trail design.
- Tests proving blocked defaults.
- Tests proving approval denial blocks execution.
- Tests proving there are no bypass paths through alternate routes, UI shortcuts, or background jobs.
- Documentation explaining what Guardian does, what it does not do, and how users can inspect decisions.
- Accurate status reporting through `GET /capabilities`.

## Design Rules

- Policy checks must happen server-side for runtime actions.
- Frontend disabled states are useful but must not be the only guard.
- Approval records must not store secrets.
- Logs must not expose credentials, private prompts, or sensitive connector payloads.
- Preview UI must remain inert until backend enforcement exists.
- Unsupported actions must fail closed with clear user-facing status.
- Codex and Claude subscription CLI dispatch must not be exposed as direct Sparkbot shell subprocess execution.

## Integration Boundary

Future policy integrations may define a runtime boundary with external policy systems, but this public repository does not include proprietary policy-system code or claim that such enforcement is active.
