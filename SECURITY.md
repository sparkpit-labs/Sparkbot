# Security Policy

Sparkbot is currently an early public pre-release shell baseline. It is suitable for local validation and quiet public review, but it does not provide a production support guarantee yet.

## Supported status

The supported public baseline is the current `main` branch and its public checkpoint tags. Security review should focus on the public repository contents and currently implemented behavior.

The current baseline does not implement model calls, provider credential handling, credential storage, terminal or tool execution, connector calls, external sends, Guardian policy enforcement, or Round Table meeting runtime.

## What to report

Please report issues related to:

- Accidental secrets exposure.
- Dependency or supply-chain security concerns.
- Unsafe action paths that appear to execute commands, mutate files, call external services, or handle credentials.
- Credential handling concerns.
- Public/private boundary leaks.
- Documentation that could cause users to expose secrets or misunderstand current safety boundaries.

## Out of scope

The following are generally out of scope for security reports at this stage:

- Missing production features.
- Speculative issues in planned but unimplemented features.
- Requests for desktop packaging, provider setup, model routing, chat runtime, or Guardian enforcement before those features exist.
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

These scripts are intended to help keep the public baseline free of private references and to verify the backend/frontend shell baseline.
