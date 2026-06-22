import type { ProviderConfigStatusPayload, ProviderStatusItem } from "../api";

export type ProviderPreviewItem = ProviderStatusItem;

export const providerPreviewItems: ProviderPreviewItem[] = [
  {
    id: "local-ollama",
    label: "Local Ollama",
    status: "disabled-by-default",
    configured: false,
    auth_mode: "none",
    configuration: "environment-localhost",
    credential_source: "not-required",
    default_model: null,
    model_examples: ["llama3.2", "qwen2.5-coder", "mistral"],
    runtime: "Active localhost-only adapter when SPARKBOT_LOCAL_MODELS_ENABLED=true and Ollama is reachable.",
    notes: "Uses only localhost or 127.0.0.1. No cloud provider credentials are used."
  },
  {
    id: "openrouter",
    label: "OpenRouter",
    status: "planned",
    configured: false,
    auth_mode: "env-api-key",
    configuration: "environment",
    credential_source: "OPENROUTER_API_KEY",
    default_model: "meta-llama/llama-3.2-3b-instruct:free",
    model_examples: ["meta-llama/llama-3.2-3b-instruct:free", "mistralai/mistral-7b-instruct:free"],
    runtime: "Guarded backend prompt endpoint for explicit operator calls. Free :free models are enforced by default.",
    notes: "Uses OpenRouter through a backend-only env key. Set SPARKBOT_PROVIDER_CALLS_ENABLED=true to enable explicit OpenRouter prompt calls."
  },
  {
    id: "openai",
    label: "OpenAI API",
    status: "planned",
    configured: false,
    auth_mode: "env-api-key",
    configuration: "environment",
    credential_source: "OPENAI_API_KEY",
    default_model: "gpt-5-mini",
    model_examples: ["gpt-5-mini", "gpt-5.3-codex", "codex-mini-latest"],
    runtime: "Onboarding/status only in this public branch; direct provider calls remain behind future routing gates.",
    notes: "Matches the prototype provider slot for OpenAI API keys without adding browser credential entry or storage."
  },
  {
    id: "anthropic",
    label: "Anthropic API",
    status: "planned",
    configured: false,
    auth_mode: "env-api-key",
    configuration: "environment",
    credential_source: "ANTHROPIC_API_KEY",
    default_model: "claude-sonnet-4-5",
    model_examples: ["claude-sonnet-4-5", "claude-haiku-4-5", "claude-opus-4-6"],
    runtime: "Onboarding/status only in this public branch; direct provider calls remain behind future routing gates.",
    notes: "Matches the prototype Anthropic provider slot without adding browser credential entry or storage."
  },
  {
    id: "google",
    label: "Google Gemini API",
    status: "planned",
    configured: false,
    auth_mode: "env-api-key",
    configuration: "environment",
    credential_source: "GOOGLE_API_KEY",
    default_model: "gemini/gemini-2.0-flash",
    model_examples: ["gemini/gemini-2.0-flash", "gemini/gemini-3-flash"],
    runtime: "Onboarding/status only in this public branch; direct provider calls remain behind future routing gates.",
    notes: "Matches the prototype Google provider slot without adding browser credential entry or storage."
  },
  {
    id: "groq",
    label: "Groq API",
    status: "planned",
    configured: false,
    auth_mode: "env-api-key",
    configuration: "environment",
    credential_source: "GROQ_API_KEY",
    default_model: "groq/llama-3.3-70b-versatile",
    model_examples: ["groq/llama-3.3-70b-versatile"],
    runtime: "Onboarding/status only in this public branch; direct provider calls remain behind future routing gates.",
    notes: "Matches the prototype Groq provider slot without adding browser credential entry or storage."
  },
  {
    id: "minimax",
    label: "MiniMax API",
    status: "planned",
    configured: false,
    auth_mode: "env-api-key",
    configuration: "environment",
    credential_source: "MINIMAX_API_KEY",
    default_model: "minimax/MiniMax-M2.5",
    model_examples: ["minimax/MiniMax-M2.5"],
    runtime: "Onboarding/status only in this public branch; direct provider calls remain behind future routing gates.",
    notes: "Matches the prototype MiniMax provider slot without adding browser credential entry or storage."
  },
  {
    id: "xai",
    label: "xAI API",
    status: "planned",
    configured: false,
    auth_mode: "env-api-key",
    configuration: "environment",
    credential_source: "XAI_API_KEY",
    default_model: "xai/grok-4",
    model_examples: ["xai/grok-4", "xai/grok-3-mini"],
    runtime: "Onboarding/status only in this public branch; direct provider calls remain behind future routing gates.",
    notes: "Matches the prototype xAI provider slot without adding browser credential entry or storage."
  },
  {
    id: "openai-codex-subscription",
    label: "OpenAI Codex Subscription",
    status: "planned",
    configured: false,
    auth_mode: "codex-cli-sign-in",
    configuration: "local-cli-sign-in",
    credential_source: "CODEX_HOME auth file",
    default_model: "openai-codex/gpt-5.3-codex",
    model_examples: ["openai-codex/gpt-5.3-codex", "openai-codex/gpt-5.5", "openai-codex/gpt-5.4"],
    runtime: "Sign-in readiness only in this public branch. CLI dispatch requires the LIMA Guardian execution boundary.",
    notes: "Run codex login with a ChatGPT/Codex subscription, then restart Sparkbot. Auth presence is detected without reading or returning the auth file.",
    cli_available: false,
    sign_in_detected: false,
    runtime_gate: "lima-guardian-required",
    operator_action: "Install the Codex CLI and make it available on PATH or SPARKBOT_CODEX_CLI."
  },
  {
    id: "claude-subscription",
    label: "Claude Subscription",
    status: "planned",
    configured: false,
    auth_mode: "claude-cli-sign-in",
    configuration: "local-cli-sign-in",
    credential_source: "Claude Code local sign-in",
    default_model: "claude-sub/sonnet",
    model_examples: ["claude-sub/sonnet", "claude-sub/opus", "claude-sub/haiku", "claude-sub/opus-1m"],
    runtime: "Sign-in readiness only in this public branch. CLI dispatch requires the LIMA Guardian execution boundary.",
    notes: "Install Claude Code, sign in locally, and set SPARKBOT_CLAUDE_SUBSCRIPTION_ENABLED=true when using this public shell status path.",
    cli_available: false,
    sign_in_detected: false,
    runtime_gate: "lima-guardian-required",
    operator_action: "Install Claude Code and make it available on PATH or SPARKBOT_CLAUDE_CLI."
  }
];

export const fallbackProviderConfigStatus: ProviderConfigStatusPayload = {
  service: "sparkbot-server",
  mode: "local",
  status: "disabled-by-default",
  credential_storage: "not-implemented",
  provider_calls: "disabled-by-default",
  model_routing: "env-driven",
  providers: providerPreviewItems
};

export const providerPreviewSummary =
  "Provider onboarding is env-driven and backend-owned. OpenRouter supports explicit free-model prompt calls when enabled; other provider and subscription routes are shown as configured status without browser credential storage.";
