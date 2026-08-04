# Connector Safety Contract

This contract governs any future connector work in the public Sparkbot repository. Connectors are not implemented in the current public baseline.

## Default Rule

Connectors are `guarded-future` capabilities. They must begin as inert configuration and status surfaces. A connector branch must not introduce live sends, automatic external actions, credential collection, or connector calls until the gates below are satisfied.

## Public Connector Rules

- Connectors are disabled by default.
- No outbound send may occur without explicit user configuration.
- No outbound send may occur without an explicit user action.
- No credentials may be committed to the repository.
- No secrets may appear in logs, screenshots, fixtures, test output, or browser output.
- No connector may perform automatic external actions on startup, page load, import, or validation.
- Messaging connector send behavior is not allowed until the contract gates are implemented and reviewed.
- Connector work must start with read-only or inert config/status surfaces.
- Error states must avoid exposing sensitive request data.

## Live Action Gates

Before any connector can perform a live send or mutation, the branch must include:

- Explicit local configuration controls.
- A disabled-by-default state with tests proving no action occurs before configuration.
- An explicit user action requirement.
- A Guardian or policy approval design for sensitive actions.
- An audit trail design that records what action was requested without recording secrets.
- Tests proving blocked defaults, missing configuration behavior, and approval denial behavior.
- Public documentation explaining the user-visible risk and rollback path.
- `GET /capabilities` status updates that accurately label the connector state.

## Disallowed Until Gates Exist

- Live outbound sends.
- Background connector polling that changes external state.
- Connector credential entry or storage.
- Hidden test calls to external services.
- Connector execution through chat, tool, or automation surfaces.
- Fallback paths that bypass disabled-by-default or approval checks.

## Minimum Test Expectations

Future connector implementation branches must prove:

- Fresh clone default: connector disabled.
- Missing config: no external action.
- UI preview: no external action.
- Denied approval: no external action.
- Logs: no secrets.
- Capability status: accurately reports disabled, preview, or guarded state.
