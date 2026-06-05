# Security Policy

Sparkbot is currently an early public local Workstation MVP. It is suitable for local validation and internal MVP review, but it does not provide a production support guarantee yet.

## Supported status

The supported public baseline is the current `main` branch and its public checkpoint tags. Security review should focus on the public repository contents and currently implemented behavior.

The current MVP includes provider credential handling for supported server-side routes. Credentials must stay server-side and must not appear in browser responses, events, prompts, notes, memory, history, logs, or reports. Chat and Round Table model calls are text-only and use configured provider routes where supported. Unsupported action and subscription-only execution paths should fail closed.

## What to report

Please report issues related to:

- Accidental secrets exposure.
- Dependency or supply-chain security concerns.
- Unsafe action paths that appear to execute commands, mutate files, call external services, or handle credentials incorrectly.
- Credential handling concerns.
- Public/private boundary leaks.
- Documentation that could cause users to expose secrets or misunderstand current safety boundaries.
- Any route that appears to bypass the fail-closed boundary for connector sends, file/process/terminal/browser/device automation, scheduler execution, or external delivery.

## Out of scope

The following are generally out of scope for security reports at this stage:

- Missing production features.
- Speculative issues in planned but unimplemented features.
- Requests for desktop packaging, scheduler execution, connector writes, tool execution, local CLI-backed subscription auth, or full private Guardian/Vault behavior before those features are explicitly scoped.
- Vulnerabilities that require adding unsupported private code, secrets, or deployment infrastructure to reproduce.

## Reporting guidance

Use GitHub Security Advisories for this repository if available. If that is not available, open a minimal public issue only if it does not disclose sensitive exploit details.

Do not include secrets, tokens, provider keys, private paths, private domains, or live credentials in reports. If a report involves a suspected secret, describe the location and impact without copying the secret value.

## Current safety posture

Current validation does not require secrets. The repository includes public safety scans and local validation scripts:

```bash
bash scripts/check-public-safety.sh
bash scripts/validate-public-shell.sh
```

These scripts are intended to help keep the public MVP free of private references and to verify the backend/frontend Workstation behavior.
