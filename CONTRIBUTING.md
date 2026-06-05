# Contributing to Sparkbot

Sparkbot is currently an early public local Workstation MVP for review and local validation. Contributions are welcome, but the project is intentionally keeping changes small, public-safe, and aligned with the current validated behavior.

## Good contributions for this stage

- Documentation corrections and clarity improvements.
- Validation script improvements that do not start services or require secrets.
- Public safety scan improvements.
- Small frontend or backend test improvements for existing Workstation behavior.
- Issues that clearly separate current behavior from planned future work.

## Current contribution boundaries

The current public MVP includes backend-backed Chat, Round Table, Command Center, Agents Wing, memory, notes/history, events, dashboard counters, and task records. It does not include:

- Production deployment or production support.
- Desktop installer or packaged app.
- Background scheduler, automatic runner, reminders engine, or recurring jobs.
- Connector write flows, connector sends, or external delivery.
- File mutation, process execution, terminal execution, browser automation, or device automation.
- Public CLI-backed OpenAI or Claude subscription-auth execution.
- Full private Guardian, Vault, or platform-internal control systems.

Please do not submit changes that enable those behaviors unless a future maintainer-approved task explicitly opens that scope.

## Pull request expectations

- Keep pull requests narrow and easy to review.
- Avoid generated artifacts, build outputs, cache files, and local environment files.
- Do not include secrets, tokens, provider keys, private paths, private domains, or personal server details.
- Keep public documentation professional and conservative.
- Do not claim product readiness beyond what is implemented and validated.
- Do not add license, governance, or contributor agreement terms without an explicit maintainer decision.

## Validation before opening a pull request

Run these commands from the repository root:

```bash
bash scripts/check-public-safety.sh
bash scripts/validate-public-shell.sh
```

The validation path should pass without secrets and without starting long-running development servers.

## Issues

Please keep issues focused and specific. Good issues include:

- A reproducible validation failure.
- A documentation gap that affects first-time users.
- A public safety concern.
- A mismatch between README instructions and actual behavior.

A contribution or issue may be declined if it is out of scope for the current public MVP, too broad to review safely, or depends on unsupported runtime features.
