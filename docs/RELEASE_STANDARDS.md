# Release Standards

Sparkbot public releases should meet professional GitHub project standards.

## Publishing identity

Public project work should be published by Phil Lima or Spark Pit Team.

## Documentation standards

Public documentation must:

- Use a professional tone
- Avoid emojis
- Avoid private repository references
- Avoid private server paths, private domains, and private infrastructure details
- Avoid internal agent or automation instructions
- Match real functionality
- Clearly separate planned work from implemented work

## Security and privacy standards

Public commits must not include:

- Secrets or tokens
- Environment variable values
- Provider API keys
- Private hostnames or private paths
- Live deployment assumptions
- Personal infrastructure details

## Release readiness

Before a public release, the project should pass:

- Fresh clone setup test
- Dependency install test
- Backend smoke test, when backend code exists
- Frontend build test, when frontend code exists
- Desktop packaging smoke test, when desktop packaging exists
- Secret scan
- Private reference scan
- Documentation review
- License decision gate

## Licensing scope

The public repository license applies only to the contents of this public `sparkpit-labs/Sparkbot` repository and does not imply licensing terms for any separate proprietary or non-public Spark Pit Labs codebase.
