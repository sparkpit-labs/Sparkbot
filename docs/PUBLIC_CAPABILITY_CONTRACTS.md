# Public Capability Contracts

This document defines how public Sparkbot capabilities are described, promoted, and gated. It is a contract for future implementation branches, not a claim that guarded runtime features are implemented today.

## Status Definitions

| Status | Meaning |
| --- | --- |
| `available` | Implemented in the public repo, covered by validation, documented, and safe by default. |
| `preview` | Visible as an inert shell or read-only surface. It must not execute sensitive actions. |
| `planned` | Documented direction with no active runtime behavior. |
| `disabled-by-default` | Implemented only behind a default-off control with tests proving the disabled state. |
| `guarded-future` | Not implemented. Future work requires a safety contract, explicit tests, and review before runtime behavior is added. |

## Promotion Rules

A capability may move to a more active status only when all of the following are true:

- The behavior is covered by focused backend, frontend, or integration tests.
- Public documentation describes what the capability does and does not do.
- `bash scripts/check-public-safety.sh` passes.
- `bash scripts/validate-public-shell.sh` passes.
- The implementation avoids secrets in source files, logs, fixtures, and browser output.
- The default state is safe for a fresh clone.
- The backend `GET /capabilities` response uses only these status values and represents the status before frontend UI claims are made.
- Any sensitive action has an applicable connector, provider, or Guardian contract before runtime work is merged.

## Current Public Capabilities

| Capability | Current status | Contract notes |
| --- | --- | --- |
| Backend health endpoint | `available` | Local read-only `GET /health`. |
| Backend capabilities endpoint | `available` | Local read-only `GET /capabilities`. |
| Frontend shell | `available` | Buildable React/Vite shell with local status display. |
| Local Workstation store | `available` | SQLite-backed local storage for public Workstation data. No cloud sync or provider calls. |
| Local chat drafts | `available` | Stores operator and note messages locally. No model-generated response, streaming, or provider routing. |
| Local memory notes | `available` | Stores local notes only. Not model memory and not cloud sync. |
| Local work lane cards | `available` | Stores local planning cards. No scheduler, reminders, notifications, or execution. |
| Workstation shell | `preview` | Product shell preview only. |
| Chat shell | `preview` | Read-only status may be shown; no send action, chat runtime, model call, streaming, provider routing, or message persistence. |
| Round Table shell | `preview` | Read-only status may be shown; no meeting engine, agent orchestration, model calls, or turn persistence. |
| Provider Setup shell | `preview` | Read-only provider status is allowed. No credential entry, storage, test call, or provider call. |
| Model Seat preview | `preview` | Read-only seat status is allowed. No model assignment, routing, calls, credentials, or seat persistence. |
| Task Lane preview | `preview` | Read-only lane status is allowed. No scheduler, background jobs, task execution, notifications, or task persistence. |
| Guardian Controls shell | `preview` | Read-only policy status may be shown; no runtime approval or enforcement path. |
| Desktop packaging | `planned` | No installer, desktop binary, signing, or auto-update path. |
| Connectors | `guarded-future` | Read-only status may be shown; must satisfy `CONNECTOR_SAFETY_CONTRACT.md` before any runtime behavior. |
| Model calls | `guarded-future` | Must satisfy provider configuration and Guardian policy contracts before runtime behavior. |
| Credential storage | `guarded-future` | Must satisfy provider configuration and secret handling gates before any storage path. |
| Tool execution | `guarded-future` | Must satisfy Guardian policy gates before any execution path. |

## Review Checklist

Future branches that change capability status must include:

- The `GET /capabilities` status change.
- Tests proving the new status and default behavior.
- Documentation updates matching the implemented behavior.
- A self-audit showing no unsupported runtime claims were introduced.
- A clear rollback path if validation fails.
