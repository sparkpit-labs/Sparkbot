# Sparkbot Public v1 Clean Baseline

- Tag: `public-v1-clean-baseline-0`
- Status: early public shell baseline
- Date: 2026-05-30

Sparkbot Public v1 Clean Baseline is the first clean public baseline for the SparkPit Labs Sparkbot repository. It is suitable for review, local validation, and continued public development.

This is not a complete product release. It provides a professional repository foundation, local validation path, backend health skeleton, frontend shell, and static product-direction previews.

## What Is Included

- Local backend health endpoint at `GET /health`.
- Public React and TypeScript frontend shell.
- Read-only Workstation preview.
- Read-only Round Table preview.
- Read-only Provider Setup preview.
- Read-only Guardian Controls preview.
- Public validation script at `scripts/validate-public-shell.sh`.
- Public release-readiness documentation.
- MIT License.

## Validation Summary

The clean baseline has been validated with:

- Backend tests passing.
- Frontend tests and production build passing.
- `npm audit --audit-level=moderate` passing with zero vulnerabilities.
- `bash scripts/validate-public-shell.sh` passing.
- Strict public sanitation scans passing.
- Manual local browser smoke passed through the alternate-port localhost flow after `public-v1-local-smoke-ready-0`.

## License

Sparkbot is licensed under the MIT License.

Copyright (c) 2026 Spark Pit Labs Team

The license applies only to the contents of this public `sparkpit-labs/Sparkbot` repository.

## Known Limitations

- No desktop app or installer is included.
- No real provider setup is implemented.
- No credential storage is implemented.
- No model calls or model routing are implemented.
- No chat runtime is implemented.
- No Round Table meeting engine is implemented.
- No Guardian policy enforcement runtime is implemented.
- No terminal, tool execution, connector calls, external sends, or sensitive action paths are implemented.
- No deployment workflow is included.

## Next Likely Work

- README polish for public visitors.
- Local development user experience polish.
- Chat shell skeleton.
- Provider configuration contracts.
- Guardian policy contracts.
- Desktop packaging plan.
