# Sparkbot

Sparkbot is an early local-first AI workstation shell from SparkPit Labs.

The project is focused on private, self-hosted AI workflows for builders, hobbyists, and technical users.

## Project status

Sparkbot is in early public v1.0.0 planning and bootstrap.

A minimal public server skeleton exists in this repository, including a FastAPI health endpoint at `GET /health`.
A minimal public frontend shell exists, including a health panel that can query the backend health endpoint.
A local Workstation shell skeleton now exists as a read-only product layout in the frontend.
The Workstation shell includes a static Round Table preview with inert Operator, Assistant, Research, Builder, and Reviewer seats.
The Workstation shell includes a static Provider Setup preview with inert Local model, OpenAI-compatible, Anthropic-compatible, Google-compatible, and Custom endpoint cards.
The Workstation shell includes a static Guardian Controls preview with inert Local actions, Provider access, Files and workspace, External connections, Approval checkpoints, and Audit trail cards.

Active multi-agent collaboration, provider setup, guardian-gated controls, desktop packaging, and broader runtime integration are still in progress for later phases.
Install and release instructions are not final and will be published after broader validation. The current frontend toolchain is validated with Node 22.22.0 and should be run with Node 20.19.0 or newer.

## Direction

- Build a stable public local server and frontend foundation first.
- Expand the Workstation shell into broader product surfaces in phased follow-up branches.

## Repository standards

This repository is maintained as a professional public project. Public documentation should describe only supported or planned public functionality and should avoid private infrastructure details, internal operating notes, or unsupported claims.

## Maintainers

Maintained by Spark Pit Team.
