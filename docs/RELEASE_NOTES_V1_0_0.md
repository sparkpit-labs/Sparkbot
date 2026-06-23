# Sparkbot Public v1.0.0

- Tag: `v1.0.0`
- Status: final public V1.0.0 shell baseline
- Date: 2026-06-21

Sparkbot Public v1.0.0 is the final validated public shell baseline for the SparkPit Labs Sparkbot repository. It is suitable for public review, local validation, and continued public development from a clean `main` branch.

This is not a complete production product. It provides a local-first Workstation shell baseline, local SQLite Workstation data surfaces, disabled-by-default localhost Ollama support, read-only status and preview surfaces, validation scripts, safety contracts, and release documentation.

## What Is Included

- Local FastAPI backend health and capability endpoints.
- React and TypeScript frontend shell.
- Local SQLite Workstation store for chat drafts, memory notes, and work lane cards.
- Manual local memory-note context selection for explicitly enabled local Ollama prompts.
- Optional local chat-session links on work lane cards.
- Read-only local JSON export for local Workstation data.
- Read-only local runtime settings display for data directory, SQLite path, and env-driven Ollama configuration.
- Disabled-by-default localhost-only Ollama adapter.
- Read-only status surfaces for Chat, Provider Setup, Connectors, Guardian Controls, Round Table, Model Seats, and Task Lanes.
- Public capability, connector, provider configuration, and Guardian policy contracts for future runtime gates.
- One-command local smoke test path at `scripts/run-local-smoke-test.sh`.
- Public safety scan and full validation scripts.
- Branch hygiene guardrail for keeping `main` as the only long-lived public branch.
- Release readiness, desktop readiness, validation, contribution, and security documentation.

## What Is Not Included

- No desktop installer or desktop binary.
- No desktop framework, signing, or auto-update behavior.
- No automatic cloud model calls, production model routing, broad provider routing, or provider SDK runtime.
- No browser provider credential setup or credential storage.
- No automatic provider runtime calls. API-key provider prompt smokes and Codex/Claude subscription delegation are explicit, disabled by default, and available only on provider-onboarding branches with backend env enablement; OpenRouter remains free-model-only by default, and subscription prompts require a localhost LIMA Guardian adapter.
- No connector sends or external actions.
- No terminal, tool execution, scheduler, reminders, background jobs, or task execution.
- No Round Table meeting engine or agent orchestration runtime.
- No Guardian policy enforcement runtime or approval-token workflow.
- No import path, cloud sync, external upload, or deployment workflow.

## Validation Matrix

| Check | Result |
| --- | --- |
| `bash scripts/validate-public-shell.sh` | Pass |
| Backend tests | Pass, 67 tests |
| Frontend tests | Pass, 19 tests |
| Frontend production build | Pass |
| `npm audit` | Pass, 0 vulnerabilities |
| `bash scripts/run-local-smoke-test.sh` | Pass |
| `bash scripts/check-public-safety.sh` | Pass |
| Private reference scan | Pass, only the documented release-standards publishing identity line remains |
| Private IP scan | Pass, no matches |
| Provider key scan | Pass, no matches |
| `bash scripts/check-branch-hygiene.sh` | Pass |

## Local Model Smoke Position

The final smoke pass verified the default disabled local-model prompt path and the enabled-but-offline local-model status path. A live Ollama prompt smoke was not run because no local Ollama daemon was reachable at `127.0.0.1:11434` during final validation.

## Known Non-Blocking Warnings

- Starlette/FastAPI emits an `httpx` deprecation warning during backend tests.
- `whatwg-encoding` emits an npm deprecation warning during frontend dependency installation.

## Public Safety Notes

- No secrets, provider keys, private paths, private hostnames, or credentials are required for validation.
- The public remote keeps `main` as the only long-lived branch after final branch hygiene cleanup.
- The MIT license applies only to the contents of this public `sparkpit-labs/Sparkbot` repository.

## Recommended Next Work

Future work should start from current `main` on a new branch. Runtime expansion should satisfy the public capability, connector, provider configuration, and Guardian policy contracts before claiming active behavior.
