# Release Readiness

This document tracks public Workstation MVP readiness for review and phased release decisions.

## Current baseline

- Backend: local FastAPI app with health, Command Center, Chat, Workstation, Round Table, memory, notes, events, Guardian confirmation, and task record routes.
- Frontend: React/Vite app with `/`, `/spine`, `/controls`, `/command-center`, `/workstation`, `/chat`, and `/roundtable` routes.
- Workstation: backend-backed rooms, seats, memory, notes, history, events, dashboard counters, and task records.
- Command Center: provider/model configuration, server-side credential entry, Agents Wing, invite routes, seats, local setup, and visible disabled Task Guardian state.
- Chat: backend-backed sessions/messages with shared context recall and narrow configured-provider execution.
- Round Table: backend-backed meeting sessions with Seat 1 Meeting Manager, assignments, summaries, wrap-up notes, configured provider routes when available, and deterministic fallback.
- Public safety: provider credentials stay server-side; event payloads and stored records are redacted; unsupported action paths fail closed.

## Not yet in scope

- Production deployment workflow or production support guarantee.
- Desktop installer, desktop binary, auto-update, and code signing.
- Background scheduler, automatic runner, reminders engine, or recurring jobs.
- Connector write flows, connector sends, external delivery, or third-party action execution.
- File mutation, process execution, terminal execution, browser automation, or device automation.
- Public CLI-backed OpenAI or Claude subscription-auth execution.
- Full private Guardian, Vault, or platform-internal control systems.
- Rich memory lifecycle automation such as stale/archive/delete-proposal/restore workflows.

## Readiness position

This repository is suitable for internal MVP review as a local AI Workstation. It is more than a static shell baseline, but it is not production-ready and does not claim complete product functionality or full parity with earlier research builds.

The next readiness step should be a manual end-to-end local MVP smoke branch before any release or announcement branch.

## Desktop packaging status

Desktop packaging is planned but not implemented. The current repository contains planning notes and release gates only. No installer, desktop binary, auto-update path, or code signing configuration is present.

## Contribution and security posture

The repository includes contribution and security reporting guidance for public review. The current MVP does not provide a production support guarantee. Contributions should stay narrow, public-safe, and aligned with the disabled automation boundaries above.
