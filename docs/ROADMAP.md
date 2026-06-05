# Sparkbot Public Roadmap

This roadmap describes the staged path toward a public Sparkbot v1.0.0. It separates historical baseline work from the current local Workstation MVP.

## Completed foundation

- Clean public repository, documentation standards, release standards, validation scripts, and public safety scan.
- Local FastAPI backend and React/Vite frontend.
- Shared local Workstation store.
- Command Center configuration for providers, model routes, seats, Agents Wing, invite routes, and local safety state.
- Backend-backed Chat with shared context recall and configured-provider execution.
- Backend-backed Round Table with persisted sessions, Seat 1 Meeting Manager, assignments, summaries, wrap-up notes, configured provider routes, deterministic fallback, and agent/seat context.
- Persistent memory, notes, history, Spine events, dashboard counters, producer metadata, and manual task records.
- Disabled/fail-closed run and write-mode paths for public Task Guardian visibility.

## Current readiness phase

Audit route, copy, docs, and public-boundary accuracy, then run a manual local MVP smoke branch.

## Deferred public-safe work

- Manual end-to-end MVP smoke and route polish.
- Provider setup UX polish and clearer unsupported subscription labels.
- Notes/history polish after smoke findings.
- Optional public-safe memory lifecycle improvements after product review.
- Desktop packaging planning and installer work only after explicit release gates are met.

## Out of scope until explicitly approved

- Production deployment workflow.
- Background scheduler, automatic runner, reminders engine, or recurring jobs.
- Connector write flows or external sends.
- File/process/terminal/browser/device automation.
- Local CLI-backed OpenAI or Claude subscription-auth execution.
- Private platform internals or full commercial Guardian/Vault behavior.
