# R&D Subscription Auth Parity Audit

Branch: audit-rd-subscription-auth-parity
Base branch: port-rd-agent-invite-route-parity
Base commit: 31ff949

## A. Verdict

REAL_RND_AUTH_FOUND_PUBLIC_MISSING

R&D subscription-style auth was not only UI metadata. It included real model-call paths for OpenAI subscription routing through the local codex CLI session and Anthropic subscription routing through the local Claude CLI session. R&D also supported an Anthropic OAuth bearer-token mode for direct Anthropic API calls. The public repo does not implement the CLI-backed OpenAI or Claude subscription execution paths. Public code only supports ordinary server-side provider API routes plus Anthropic OAuth bearer headers when a token is supplied through an invite route.

## B. R&D Auth Behavior

### Files And Docs Inspected

- sources/Sparkbot/backend/app/api/routes/chat/llm.py
- sources/Sparkbot/backend/app/api/routes/chat/model.py
- sources/Sparkbot/backend/tests/api/routes/test_chat_models_openrouter.py
- sources/Sparkbot/frontend/src/components/CommandCenter/SetupPanels.tsx
- sources/Sparkbot/frontend/src/pages/SparkbotDmPage.tsx
- sources/Sparkbot/frontend/src/pages/WorkstationPage.tsx
- sources/Sparkbot/frontend/src/lib/sparkbotControls.ts
- sources/Sparkbot/frontend/src/hooks/useControlsState.ts
- sources/Sparkbot/docs/capabilities.md
- sources/Sparkbot/docs/systemd-single-node.md
- sources/Sparkbot/docs/public-downloads.md
- sources/Sparkbot/docs/release-notes/v1.6.32.txt
- sources/Sparkbot/docs/release-notes/v1.6.56.txt
- sources/Sparkbot/docs/release-notes/v1.6.57.txt
- sources/Sparkbot/docs/release-notes/v1.6.58.txt
- sources/Sparkbot/docs/release-notes/v1.6.64.txt
- sources/Sparkbot/docs/release-notes/v1.6.75.txt
- sources/Sparkbot_shell search: no direct subscription auth execution found
- LIMA-AI-OS search: no direct subscription auth execution found

### Exact Behavior Found

OpenAI subscription provider:

- R&D models with prefix openai-codex/ map to provider openai_codex.
- Readiness checks look for CODEX_API_KEY or a local codex CLI auth JSON payload containing access or refresh tokens.
- Model calls for openai_codex do not call the OpenAI Platform chat endpoint directly. They call codex exec as a subprocess with read-only sandbox, ephemeral mode, selected model, a working directory, and an output file for the final assistant message.
- The app converts chat messages into a prompt and sends it to the codex CLI stdin. The CLI owns the subscription-backed model call.
- Failure messages tell the operator to sign in with the codex CLI and restart the app.

Claude subscription provider:

- R&D models with prefix claude-sub/ map to provider claude_sub.
- Readiness checks look for CLAUDE_SUB_API_KEY or run claude auth status and parse logged-in status.
- Model calls for claude_sub call the Claude CLI as a subprocess using print/text mode, selected model, no session persistence, and dontAsk permission mode.
- R&D tests covered the Claude CLI stdout path and confirmed the old output-file path was removed after a CLI compatibility failure.

Anthropic OAuth token mode:

- R&D direct Anthropic provider supports auth_mode oauth in addition to api_key.
- Invite-route auth_mode oauth stores the supplied token as the invite credential for that runtime route.
- During model dispatch, Anthropic OAuth mode sends Authorization: Bearer plus the oauth beta header instead of the x-api-key header.
- R&D UI instructed operators to generate or copy an Anthropic OAuth access token externally, then paste it into Controls or Invite Wing.

OpenAI auth_mode codex_sub on the regular OpenAI provider:

- R&D also had OPENAI_AUTH_MODE=codex_sub metadata for the regular openai provider.
- The implementation path for regular OpenAI still used a supplied OpenAI-style key through normal OpenAI-compatible routing. The real ChatGPT-plan subscription path was the separate openai_codex provider and codex CLI execution.

### Providers Supported

- OpenAI subscription: openai_codex through local codex CLI execution.
- Claude subscription: claude_sub through local Claude CLI execution.
- Anthropic subscription token: anthropic through OAuth bearer-token headers.
- OpenRouter, OpenAI API key, Anthropic API key, Google, Groq, MiniMax, xAI, and Ollama remained separate provider routes.

### Storage Mechanism

- OpenAI subscription credentials live in the local codex CLI auth profile, or optionally CODEX_API_KEY. R&D docs also describe mounting only the auth JSON file read-only for server/container use.
- Claude subscription state lives in the local Claude CLI account/session. R&D also checks CLAUDE_SUB_API_KEY.
- Anthropic OAuth token mode stores the pasted token as provider or invite-route credential material, similar to API key handling.
- R&D invite-route config itself is runtime-only for invite agents and clears on process restart.

### Model Execution Path

- openai_codex: subprocess call to codex exec.
- claude_sub: subprocess call to Claude CLI print/text mode.
- anthropic with oauth: direct Anthropic Messages API through bearer auth and beta header.
- anthropic with api_key: direct Anthropic API key path.
- openai with codex_sub auth mode: ordinary OpenAI-compatible key path, not the real subscription CLI path.

### Round Table And Invite Route Usage

R&D route resolution included openai_codex and claude_sub in valid agent routes and provider inference. Invite routes could set model, api key, and auth mode. Round Table and Workstation seat flows used get_agent_route_context, so seated or invited agents could resolve to subscription providers. For openai_codex and claude_sub candidates, the actual model dispatch went through the local CLI subprocess paths. For Anthropic OAuth invite routes, dispatch used bearer-token headers.

## C. Public Current Behavior

### Stored Metadata

The public repo currently has model/provider labels and provider ids for openai_codex and claude_sub in backend Command Center config. The frontend can infer those providers from model ids. Before this audit patch, invite routes also accepted auth_mode codex_sub as stored metadata.

This audit branch hardened that behavior:

- Public invite routes now accept only api_key and oauth auth modes.
- oauth is accepted only for Anthropic provider models.
- openai_codex and claude_sub invite-route models are rejected as unsupported for server-side execution.
- The invite UI no longer offers metadata-only provider subscription auth mode.
- The invite UI only shows Anthropic subscription token mode for Anthropic API models.

### Public Provider Execution Today

Public backend execution supports:

- OpenRouter chat completions.
- OpenAI-compatible chat completions for OpenAI, Groq, and xAI.
- Anthropic Messages API with API key or invite-route OAuth bearer token.
- Google generateContent.
- Ollama local chat endpoint.

Public backend execution does not support:

- openai_codex CLI execution.
- claude_sub CLI execution.
- reading CLI auth files.
- launching subscription provider subprocesses.
- browser sign-in flows.
- cookie or session scraping.
- private token bridges.

### What Happens If A Seat Or Invite Selects The Mode

After this audit hardening patch:

- Saving an invite route with auth_mode codex_sub returns HTTP 400.
- Saving an invite route for openai_codex or claude_sub returns HTTP 400.
- Saving oauth for a non-Anthropic invite model returns HTTP 400.
- Saving oauth for an Anthropic invite model succeeds and keeps the credential server-side.
- If a public default route or agent override still selects openai_codex or claude_sub, the provider execution service returns unsupported and does not dispatch a provider request.

### User Visible Impact

The public UI no longer implies that invite-route provider subscription metadata can execute. Anthropic OAuth invite-token mode remains available where the public execution service can actually use it. Subscription-only default or agent override routes still appear in the public model catalog, but execution fails closed with a user-safe unsupported-route message.

## D. Gap Analysis

| Gap | Classification | Notes |
| --- | --- | --- |
| R&D openai_codex real CLI execution | DEFER_PRIVATE_UNSAFE | True parity requires subprocess execution, local CLI auth profile access, timeout handling, and auth-file mounting. This violates the current public branch constraints against process execution and private auth bridges. |
| R&D claude_sub real CLI execution | DEFER_PRIVATE_UNSAFE | True parity requires subprocess execution through the Claude CLI and local CLI account/session readiness checks. This is not safe to add without explicit scope and policy review. |
| Anthropic OAuth bearer-token dispatch | PORT_NOW_SAFE | Public model execution already supports this for invite routes after the previous branch. This audit keeps it and constrains it to Anthropic models only. |
| Global Anthropic OAuth provider setup in public Controls | REBUILD_PUBLIC_SAFE | Could be added as a narrow server-side credential mode, but it needs explicit UI copy, tests, and safe token storage. It should not auto-read CLI credential files. |
| Public openai_codex and claude_sub catalog visibility | DOC_ONLY_WARNING | Current execution fails closed. UI/catalog polish can make unsupported status clearer without adding auth. |
| Regular OpenAI auth_mode codex_sub wrapper | DOC_ONLY_WARNING | R&D treated this as setup metadata around an OpenAI-style key. It is not the real subscription model-call path. |
| Reading local CLI auth files | DEFER_PRIVATE_UNSAFE | Not appropriate for public parity without explicit approval and a narrowly reviewed local-only boundary. |
| Browser sign-in or cookie/session scraping | DEFER_PRIVATE_UNSAFE | Not found as an in-app R&D model-call mechanism and remains forbidden for public parity. |

## E. Recommendation

Do not implement full OpenAI or Claude subscription auth parity in the next public branch. The R&D behavior is real, but the real paths depend on local CLI account/session state and subprocess model execution. That is outside the current public-safe Workstation boundary.

Recommended next branch:

1. Keep CLI-backed subscription providers unsupported in public execution unless an explicit auth/process-execution safety branch is approved.
2. Keep the hardening from this audit branch so invite routes cannot silently save metadata-only subscription auth for active execution.
3. Optionally open a narrow UI clarity branch that labels openai_codex and claude_sub as unavailable in the public slice, or hides them from active route selection while keeping model catalog notes.
4. If public-safe parity is desired now, focus only on Anthropic OAuth token mode as a server-side credential option, with no auto-reading of CLI files and no browser automation.

## Patch In This Branch

- backend/app/api/command_center.py rejects unsupported invite-route auth modes, rejects openai_codex and claude_sub invite-route execution, and restricts oauth to Anthropic invite routes.
- frontend/src/components/CommandCenter.tsx removes the metadata-only provider subscription invite auth option, shows Anthropic OAuth only for Anthropic invite models, normalizes stale auth drafts, and warns when a subscription-only invite model is selected.
- backend/tests/test_command_center.py adds invite-route auth validation coverage.
- backend/tests/test_narrow_provider_model_execution.py adds fail-closed no-dispatch coverage for unsupported subscription-only provider execution.

## Validation Results

- git diff --check: PASS.
- Backend tests: PASS, 49 passed, one existing Starlette/httpx deprecation warning.
- Frontend tests: PASS, 8 passed.
- Frontend build: PASS.
- npm audit --audit-level=moderate: PASS, 0 vulnerabilities.
- bash scripts/check-public-safety.sh: PASS.
- bash scripts/validate-public-shell.sh: PASS, including isolated backend tests, frontend tests, frontend build, and audit.
- Changed-file privacy scan: PASS.
