import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";

const capabilitiesPayload = {
  service: "sparkbot-server",
  mode: "local",
  capabilities: [
    {
      id: "backend-health",
      label: "Backend health endpoint",
      status: "available",
      notes: "Read-only local health check."
    },
    {
      id: "frontend-shell",
      label: "Frontend shell",
      status: "available",
      notes: "Public shell interface."
    },
    {
      id: "local-workstation-store",
      label: "Local Workstation store",
      status: "available",
      notes: "Local SQLite storage for Workstation data."
    },
    {
      id: "local-chat-drafts",
      label: "Local chat drafts",
      status: "available",
      notes: "Stores operator and note messages locally without model calls."
    },
    {
      id: "local-memory-notes",
      label: "Local memory notes",
      status: "available",
      notes: "Stores local notes and supports explicit per-prompt selection without automatic retrieval or model memory."
    },
    {
      id: "local-work-lane-cards",
      label: "Local work lane cards",
      status: "available",
      notes: "Stores local planning cards and optional local chat-session links without scheduler or task execution."
    },
    {
      id: "local-data-export",
      label: "Local data export",
      status: "available",
      notes: "Downloads a read-only JSON backup of local Workstation data without import, sync, or upload."
    },
    {
      id: "local-runtime-settings",
      label: "Local runtime settings",
      status: "available",
      notes: "Shows env-driven local runtime paths and Ollama settings without credential fields or save actions."
    },
    {
      id: "local-model-adapter",
      label: "Local model adapter",
      status: "disabled-by-default",
      notes: "Localhost-only Ollama adapter; prompt calls require explicit operator enablement."
    },
    {
      id: "local-ollama",
      label: "Local Ollama",
      status: "disabled-by-default",
      notes: "Uses only localhost or 127.0.0.1 and no credentials or cloud providers."
    },
    {
      id: "workstation",
      label: "Workstation shell",
      status: "preview",
      notes: "Navigation and product shell preview."
    },
    {
      id: "chat",
      label: "Chat shell",
      status: "preview",
      notes: "No model calls or message persistence."
    },
    {
      id: "round-table",
      label: "Round Table",
      status: "preview",
      notes: "No meeting engine or agent orchestration."
    },
    {
      id: "provider-setup",
      label: "Provider Setup shell",
      status: "available",
      notes: "Env-driven provider onboarding and CLI sign-in status without browser credential storage."
    },
    {
      id: "model-seats",
      label: "Model Seat preview",
      status: "preview",
      notes: "No model assignment, routing, calls, credentials, or seat persistence."
    },
    {
      id: "work-lanes",
      label: "Task Lane preview",
      status: "preview",
      notes: "No scheduler, background jobs, task execution, notifications, or task persistence."
    },
    {
      id: "guardian-controls",
      label: "Guardian Controls shell",
      status: "preview",
      notes: "No policy enforcement runtime."
    },
    {
      id: "desktop-packaging",
      label: "Desktop packaging",
      status: "planned",
      notes: "No installer or desktop binary yet."
    },
    {
      id: "connectors",
      label: "Connectors",
      status: "guarded-future",
      notes: "No connector calls or external sends."
    },
    {
      id: "model-calls",
      label: "Cloud model calls",
      status: "disabled-by-default",
      notes: "Only explicit OpenRouter prompt calls are available when SPARKBOT_PROVIDER_CALLS_ENABLED=true and an env key is configured."
    },
    {
      id: "credential-storage",
      label: "Credential storage",
      status: "guarded-future",
      notes: "No credential entry or storage path."
    },
    {
      id: "tool-execution",
      label: "Tool execution",
      status: "guarded-future",
      notes: "No terminal, tool, or automation execution."
    },
    {
      id: "future-local-action",
      label: "Future local action",
      status: "disabled-by-default",
      notes: "Requires explicit enablement before any action exists."
    }
  ]
};

const chatStatusPayload = {
  service: "sparkbot-server",
  mode: "local",
  status: "preview",
  chat_runtime: "not-implemented",
  message_persistence: "not-implemented",
  model_calls: "not-implemented",
  streaming: "not-implemented",
  provider_routing: "not-implemented",
  supported_surfaces: [
    {
      id: "chat-shell",
      label: "Chat shell",
      status: "preview",
      notes: "Static chat shell preview. No messages are sent."
    },
    {
      id: "message-input",
      label: "Message input",
      status: "disabled-by-default",
      notes: "Input remains disabled until chat runtime and safety gates exist."
    },
    {
      id: "model-response",
      label: "Model response",
      status: "guarded-future",
      notes: "No model calls are implemented."
    },
    {
      id: "message-history",
      label: "Message history",
      status: "guarded-future",
      notes: "No message persistence is implemented."
    }
  ]
};

const roundTableStatusPayload = {
  service: "sparkbot-server",
  mode: "local",
  status: "preview",
  meeting_engine: "not-implemented",
  agent_orchestration: "not-implemented",
  model_calls: "not-implemented",
  turn_persistence: "not-implemented",
  seats: [
    {
      id: "operator",
      label: "Operator",
      status: "preview",
      notes: "Human operator role shown as part of the shell preview."
    },
    {
      id: "assistant",
      label: "Assistant seat",
      status: "preview",
      notes: "Assistant role preview only. No model calls are made."
    },
    {
      id: "research",
      label: "Research seat",
      status: "planned",
      notes: "Research role is planned. No agent runtime is implemented."
    },
    {
      id: "builder",
      label: "Builder seat",
      status: "planned",
      notes: "Builder role is planned. No tool execution is implemented."
    },
    {
      id: "reviewer",
      label: "Reviewer seat",
      status: "planned",
      notes: "Reviewer role is planned. No review workflow runtime is implemented."
    }
  ]
};

const modelSeatsStatusPayload = {
  service: "sparkbot-server",
  mode: "local",
  status: "preview",
  model_calls: "not-implemented",
  model_routing: "not-implemented",
  provider_credentials: "not-implemented",
  seat_persistence: "not-implemented",
  seats: [
    {
      id: "default-assistant",
      label: "Default Assistant Seat",
      status: "preview",
      notes: "Read-only seat preview. No model is assigned or called."
    },
    {
      id: "research-seat",
      label: "Research Seat",
      status: "planned",
      notes: "Future seat for research workflows. No runtime behavior is implemented."
    },
    {
      id: "builder-seat",
      label: "Builder Seat",
      status: "planned",
      notes: "Future seat for implementation workflows. No tool execution is implemented."
    },
    {
      id: "reviewer-seat",
      label: "Reviewer Seat",
      status: "planned",
      notes: "Future seat for review workflows. No model routing is implemented."
    }
  ]
};

const taskLanesStatusPayload = {
  service: "sparkbot-server",
  mode: "local",
  status: "preview",
  task_runtime: "not-implemented",
  task_persistence: "not-implemented",
  scheduler: "not-implemented",
  background_jobs: "not-implemented",
  notifications: "not-implemented",
  lanes: [
    {
      id: "inbox",
      label: "Inbox Lane",
      status: "preview",
      notes: "Read-only lane preview. No tasks are stored or executed."
    },
    {
      id: "planned",
      label: "Planned Lane",
      status: "planned",
      notes: "Future planning lane. No scheduler is implemented."
    },
    {
      id: "active",
      label: "Active Lane",
      status: "planned",
      notes: "Future active work lane. No task runtime is implemented."
    },
    {
      id: "review",
      label: "Review Lane",
      status: "planned",
      notes: "Future review lane. No workflow runtime is implemented."
    }
  ]
};

const providerConfigStatusPayload = {
  service: "sparkbot-server",
  mode: "local",
  status: "disabled-by-default",
  credential_storage: "not-implemented",
  provider_calls: "disabled-by-default",
  model_routing: "env-driven",
  providers: [
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
      credential_source: "CODEX_HOME or SPARKBOT_CODEX_AUTH_FILE",
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
      credential_source: "CLAUDE_HOME or SPARKBOT_CLAUDE_AUTH_FILE",
      default_model: "claude-sub/sonnet",
      model_examples: ["claude-sub/sonnet", "claude-sub/opus", "claude-sub/haiku", "claude-sub/opus-1m"],
      runtime: "Sign-in readiness only in this public branch. CLI dispatch requires the LIMA Guardian execution boundary.",
      notes: "Install Claude Code and sign in locally. Sparkbot detects CLAUDE_HOME, SPARKBOT_CLAUDE_AUTH_FILE, or the operator-declared SPARKBOT_CLAUDE_SUBSCRIPTION_ENABLED=true flag without reading or returning auth contents.",
      cli_available: false,
      sign_in_detected: false,
      runtime_gate: "lima-guardian-required",
      operator_action: "Install Claude Code and make it available on PATH or SPARKBOT_CLAUDE_CLI."
    }
  ]
};

const openRouterPromptResponsePayload = {
  provider: "openrouter",
  model: "mistralai/mistral-7b-instruct:free",
  request_model: "mistralai/mistral-7b-instruct:free",
  response: "OK from OpenRouter",
  usage: { prompt_tokens: 3, completion_tokens: 4 }
};

const connectorStatusPayload = {
  service: "sparkbot-server",
  mode: "local",
  status: "guarded-future",
  connectors_enabled: false,
  outbound_actions: "not-implemented",
  credential_storage: "not-implemented",
  audit_trail: "planned",
  connectors: [
    {
      id: "messaging",
      label: "Messaging connectors",
      status: "guarded-future",
      notes: "Messaging connectors are planned for future guarded configuration. No outbound sends are implemented."
    },
    {
      id: "calendar",
      label: "Calendar connectors",
      status: "guarded-future",
      notes: "Calendar connectors are planned for future guarded configuration."
    },
    {
      id: "email",
      label: "Email connectors",
      status: "guarded-future",
      notes: "Email connectors are planned for future guarded configuration. No external sends are implemented."
    },
    {
      id: "files",
      label: "File connectors",
      status: "guarded-future",
      notes: "File connectors are planned for future guarded configuration. No file mutation is implemented."
    }
  ]
};

const guardianStatusPayload = {
  service: "sparkbot-server",
  mode: "local",
  status: "preview",
  runtime_enforcement: "not-implemented",
  approval_tokens: "not-implemented",
  policy_decisions: "not-implemented",
  audit_trail: "planned",
  default_posture: "deny-sensitive-actions",
  provider_execution_boundary: {
    id: "lima-guardian-provider-runtime",
    label: "LIMA Guardian provider runtime boundary",
    status: "guarded-future",
    runtime_gate: "lima-guardian-required",
    dispatch: "fail-closed",
    required_controls: ["capability-check", "operator-approval", "audit-log", "secret-redaction", "timeout", "no-shell-expansion"],
    blocked_until: "Codex and Claude subscription CLI dispatch requires a LIMA Guardian execution adapter.",
    notes:
      "Sparkbot may report subscription sign-in readiness, but direct Codex or Claude CLI execution remains disabled until LIMA provides guarded dispatch with audit and fail-closed behavior."
  },
  sensitive_action_categories: [
    {
      id: "external-sends",
      label: "External sends",
      status: "guarded-future",
      notes: "No external sends are implemented."
    },
    {
      id: "connector-calls",
      label: "Connector calls",
      status: "guarded-future",
      notes: "No connector calls are implemented."
    },
    {
      id: "credential-use",
      label: "Credential use",
      status: "guarded-future",
      notes: "No credential use or storage is implemented."
    },
    {
      id: "model-provider-calls",
      label: "Model provider calls",
      status: "guarded-future",
      notes: "No model provider calls are implemented."
    },
    {
      id: "file-writes",
      label: "File writes",
      status: "guarded-future",
      notes: "No file mutation workflow is implemented."
    },
    {
      id: "tool-execution",
      label: "Tool execution",
      status: "guarded-future",
      notes: "No terminal or tool execution is implemented."
    }
  ]
};

const localChatSessionsPayload = {
  sessions: [
    {
      id: "session-1",
      title: "Seeded local chat",
      created_at: "2026-06-20T00:00:00Z",
      updated_at: "2026-06-20T00:00:00Z",
      message_count: 1
    }
  ]
};

const localChatSessionPayload = {
  id: "session-1",
  title: "Seeded local chat",
  created_at: "2026-06-20T00:00:00Z",
  updated_at: "2026-06-20T00:00:00Z",
  messages: [
    {
      id: "message-1",
      session_id: "session-1",
      role: "operator",
      content: "Stored locally.",
      created_at: "2026-06-20T00:00:00Z"
    }
  ]
};

const localMemoryNotesPayload = {
  notes: [
    {
      id: "note-1",
      title: "Seeded memory",
      body: "Stored local note.",
      source: "operator",
      created_at: "2026-06-20T00:00:00Z",
      updated_at: "2026-06-20T00:00:00Z"
    }
  ]
};

const localWorkLaneCardsPayload = {
  cards: [
    {
      id: "card-1",
      lane: "inbox",
      title: "Seeded card",
      body: "Stored local card.",
      status: "open",
      chat_session_id: "session-1",
      linked_chat_session_title: "Seeded local chat",
      created_at: "2026-06-20T00:00:00Z",
      updated_at: "2026-06-20T00:00:00Z"
    }
  ]
};

const localExportPayload = {
  service: "sparkbot-server",
  mode: "local",
  export_type: "local-workstation-data",
  schema_version: 1,
  exported_at: "2026-06-21T00:00:00Z",
  import_supported: false,
  cloud_sync: "not-supported",
  external_upload: "not-supported",
  data: {
    chat_sessions: [localChatSessionPayload],
    memory_notes: localMemoryNotesPayload.notes,
    work_lane_cards: localWorkLaneCardsPayload.cards
  }
};

const localRuntimeSettingsPayload = {
  service: "sparkbot-server",
  mode: "local",
  status: "available",
  configuration: "env-driven",
  settings_writes: "not-supported",
  credentials: "not-supported",
  data_directory: {
    configured_by: "SPARKBOT_DATA_DIR",
    display_path: "~/.local/share/sparkbot-public"
  },
  sqlite_database: {
    filename: "sparkbot_public.sqlite3",
    display_path: "~/.local/share/sparkbot-public/sparkbot_public.sqlite3"
  },
  local_models: {
    enabled: false,
    status: "disabled-by-default",
    adapter: "ollama",
    base_url: "http://127.0.0.1:11434",
    base_url_policy: "localhost-only",
    configured_model: null,
    prompt_calls: "disabled",
    credentials: "not-supported",
    configuration_error: null
  }
};

const localModelDisabledStatusPayload = {
  service: "sparkbot-server",
  mode: "local",
  status: "disabled-by-default",
  local_models_enabled: false,
  adapter: "ollama",
  base_url: "http://127.0.0.1:11434",
  base_url_policy: "localhost-only",
  configured_model: null,
  prompt_calls: "disabled",
  credentials: "not-supported",
  external_network: "not-supported"
};

const localModelEnabledStatusPayload = {
  ...localModelDisabledStatusPayload,
  status: "available-local-only",
  local_models_enabled: true,
  configured_model: "llama3.2",
  prompt_calls: "enabled-local-only",
  ollama_reachable: true
};

const localPromptResponsePayload = {
  adapter: "ollama",
  base_url_policy: "localhost-only",
  model: "llama3.2",
  response: "Local-only Ollama response.",
  done: true,
  memory_context: "explicit-selected",
  selected_memory_note_count: 1,
  stored_message: {
    id: "message-2",
    session_id: "session-1",
    role: "assistant-local",
    content: "Local-only Ollama response.",
    created_at: "2026-06-20T00:00:01Z"
  }
};

function enabledOpenRouterProviderConfigStatusPayload() {
  return {
    ...providerConfigStatusPayload,
    status: "available",
    provider_calls: "guarded-manual",
    providers: providerConfigStatusPayload.providers.map((provider) =>
      provider.id === "openrouter"
        ? {
            ...provider,
            status: "available",
            configured: true,
            default_model: "mistralai/mistral-7b-instruct:free"
          }
        : provider
    )
  };
}

function mockJsonResponse(payload: unknown) {
  return Promise.resolve(
    new Response(JSON.stringify(payload), {
      status: 200,
      headers: { "Content-Type": "application/json" }
    })
  );
}

function mockBackendStatusFetch() {
  return vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = input.toString();
    const method = init?.method ?? "GET";

    if (url.includes("/local/export")) {
      return mockJsonResponse(localExportPayload);
    }

    if (url.includes("/local/runtime/settings")) {
      return mockJsonResponse(localRuntimeSettingsPayload);
    }

    if (url.includes("/local/chat/sessions/session-1/messages")) {
      return mockJsonResponse(localChatSessionPayload.messages[0]);
    }

    if (url.includes("/local/chat/sessions/session-1")) {
      return mockJsonResponse(localChatSessionPayload);
    }

    if (url.includes("/local/chat/sessions")) {
      return mockJsonResponse(method === "POST" ? localChatSessionPayload : localChatSessionsPayload);
    }

    if (url.includes("/local/memory-notes/note-1")) {
      return mockJsonResponse(localMemoryNotesPayload.notes[0]);
    }

    if (url.includes("/local/memory-notes")) {
      return mockJsonResponse(method === "POST" || method === "PATCH" ? localMemoryNotesPayload.notes[0] : localMemoryNotesPayload);
    }

    if (url.includes("/local/work-lane-cards/card-1")) {
      return mockJsonResponse(localWorkLaneCardsPayload.cards[0]);
    }

    if (url.includes("/local/work-lane-cards")) {
      return mockJsonResponse(method === "POST" || method === "PATCH" ? localWorkLaneCardsPayload.cards[0] : localWorkLaneCardsPayload);
    }

    if (url.includes("/local-models/ollama/prompt")) {
      return mockJsonResponse(localPromptResponsePayload);
    }

    if (url.includes("/local-models/status")) {
      return mockJsonResponse(localModelDisabledStatusPayload);
    }

    if (url.includes("/chat/status")) {
      return mockJsonResponse(chatStatusPayload);
    }

    if (url.includes("/round-table/status")) {
      return mockJsonResponse(roundTableStatusPayload);
    }

    if (url.includes("/model-seats/status")) {
      return mockJsonResponse(modelSeatsStatusPayload);
    }

    if (url.includes("/work-lanes/status")) {
      return mockJsonResponse(taskLanesStatusPayload);
    }

    if (url.includes("/guardian/status")) {
      return mockJsonResponse(guardianStatusPayload);
    }

    if (url.includes("/connector-status")) {
      return mockJsonResponse(connectorStatusPayload);
    }

    if (url.includes("/provider-config/openrouter/prompt")) {
      return mockJsonResponse(openRouterPromptResponsePayload);
    }

    if (url.includes("/provider-config/status")) {
      return mockJsonResponse(providerConfigStatusPayload);
    }

    if (url.includes("/capabilities")) {
      return mockJsonResponse(capabilitiesPayload);
    }

    return Promise.reject(new Error(`Unexpected fetch ${url}`));
  });
}

describe("App", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("capabilities unavailable")));
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it("renders workstation navigation, preview-only shell sections, fallback statuses, and read-only health panel", async () => {
    render(<App />);

    expect(screen.getByRole("heading", { level: 1, name: "Sparkbot" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Workstation Shell" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "System Status" })).toBeDefined();
    expect(screen.getByText(/Read-only dashboard for the current local shell/i)).toBeDefined();
    expect(screen.getByRole("heading", { name: "Backend health" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "API base" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Capability source" })).toBeDefined();
    expect(screen.getByText("Not checked")).toBeDefined();
    expect(screen.getByText("Local read-only status requests only.")).toBeDefined();
    expect(screen.getByText("22 public capability entries loaded.")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Health" })).toBeDefined();
    expect(screen.getByText("GET /health")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Capabilities" })).toBeDefined();
    expect(screen.getByText("GET /capabilities")).toBeDefined();
    expect(screen.getByText("GET /chat/status")).toBeDefined();
    expect(screen.getByText("GET /round-table/status")).toBeDefined();
    expect(screen.getByText("GET /model-seats/status")).toBeDefined();
    expect(screen.getByText("GET /work-lanes/status")).toBeDefined();
    expect(screen.getByText("GET /local/export")).toBeDefined();
    expect(screen.getByText("GET /local/runtime/settings")).toBeDefined();
    expect(screen.getByText("GET /provider-config/status")).toBeDefined();
    expect(screen.getByText("GET /connector-status")).toBeDefined();
    expect(screen.getByText("GET /guardian/status")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Shell Sections" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Workstation Overview" })).toBeDefined();
    expect(screen.getAllByText("Using local fallback status list.").length).toBeGreaterThanOrEqual(2);
    expect(screen.getByRole("button", { name: /Workstation.*Preview/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /Chat.*Preview/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /Round Table.*Preview/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /Model Seats.*Preview/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /Task Lanes.*Preview/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /Provider Setup.*Available/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /Guardian Controls.*Preview/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /Local Chat.*Available/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /Memory Notes.*Available/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /Work Cards.*Available/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /Export.*Available/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /Settings.*Available/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /Local Models.*Disabled by default/i })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Local Chat Drafts" })).toBeDefined();
    expect(screen.getByText(/manual Local Ollama Adapter flow/i)).toBeDefined();
    expect(screen.getByRole("heading", { name: "Local Memory Notes" })).toBeDefined();
    expect(screen.getByText(/not model memory and are not synced/i)).toBeDefined();
    expect(screen.getByRole("heading", { name: "Local Work Lane Cards" })).toBeDefined();
    expect(screen.getByText(/do not run, schedule, remind, notify, or execute tasks/i)).toBeDefined();
    expect(screen.getByRole("heading", { name: "Local Data Export" })).toBeDefined();
    expect(screen.getByText(/No import, cloud sync, external upload/i)).toBeDefined();
    expect(screen.getByRole("heading", { name: "Local Runtime Settings" })).toBeDefined();
    expect(screen.getByText(/Configuration remains environment-driven/i)).toBeDefined();
    expect(screen.getByRole("heading", { name: "Local Ollama Adapter" })).toBeDefined();
    expect(screen.getByText(/Local-only prompt adapter for Ollama on localhost/i)).toBeDefined();
    expect(screen.getAllByText(/SPARKBOT_LOCAL_MODELS_ENABLED=true/).length).toBeGreaterThanOrEqual(1);
    expect((screen.getByRole("button", { name: "Run local prompt" }) as HTMLButtonElement).disabled).toBe(true);
    expect(screen.getAllByText("Available").length).toBeGreaterThanOrEqual(2);
    expect(screen.getByRole("heading", { name: "Backend health endpoint" })).toBeDefined();
    expect(screen.getByText("Read-only local health check.")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Connectors" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Cloud model calls" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Credential storage" })).toBeDefined();
    expect(screen.getAllByRole("heading", { name: "Tool execution" }).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Planned").length).toBeGreaterThanOrEqual(6);
    expect(screen.getByText("No connector calls or external sends.")).toBeDefined();
    expect(screen.getAllByText(/Only explicit OpenRouter prompt calls are available/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("No credential entry or storage path.")).toBeDefined();
    expect(screen.getByText("No terminal, tool, or automation execution.")).toBeDefined();
    expect(screen.getAllByRole("heading", { name: "Chat shell" }).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByRole("heading", { name: "Chat Shell Preview" })).toBeDefined();
    expect(screen.getByText(/Chat status is read-only/i)).toBeDefined();
    expect(screen.getByText("Using local Chat status fallback.")).toBeDefined();
    expect(screen.getByText("Chat runtime")).toBeDefined();
    expect(screen.getByText("Message persistence")).toBeDefined();
    expect(screen.getAllByText("Model calls").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Streaming")).toBeDefined();
    expect(screen.getByText("Provider routing")).toBeDefined();
    expect(screen.getAllByText("not implemented").length).toBeGreaterThanOrEqual(5);
    expect(screen.getByRole("heading", { name: "Message input" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Model response" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Message history" })).toBeDefined();
    expect(screen.getByText("Input remains disabled until chat runtime and safety gates exist.")).toBeDefined();
    expect(screen.getByText("No model calls are implemented.")).toBeDefined();
    expect(screen.getByText("No message persistence is implemented.")).toBeDefined();
    expect(screen.getByText(/Empty state: chat history will appear here/i)).toBeDefined();
    expect(screen.getByText(/no enabled send action/i)).toBeDefined();
    expect(screen.getByText(/no user-entered text handling/i)).toBeDefined();
    const plannedComposer = screen.getByLabelText("Chat message composer planned") as HTMLTextAreaElement;
    expect(plannedComposer.disabled).toBe(true);
    expect(plannedComposer.readOnly).toBe(true);
    expect(screen.getAllByRole("heading", { name: "Round Table" }).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByRole("heading", { name: "Round Table Preview" })).toBeDefined();
    expect(screen.getByText("Using local Round Table status fallback.")).toBeDefined();
    expect(screen.getByText("Meeting engine")).toBeDefined();
    expect(screen.getByText("Agent orchestration")).toBeDefined();
    expect(screen.getAllByText("Model calls").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Turn persistence")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Operator" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Assistant seat" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Research seat" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Builder seat" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Reviewer seat" })).toBeDefined();
    expect(screen.getByText(/Multi-participant collaboration is planned/i)).toBeDefined();
    expect(screen.getByText(/does not start meetings, invite participants, call models/i)).toBeDefined();
    expect(screen.getByRole("heading", { name: "Model Seat Preview" })).toBeDefined();
    expect(screen.getByText("Using local Model Seat status fallback.")).toBeDefined();
    expect(screen.getByText(/Model seats show the future multi-model workspace direction/i)).toBeDefined();
    expect(screen.getAllByText("Model routing").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Provider credentials")).toBeDefined();
    expect(screen.getByText("Seat persistence")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Default Assistant Seat" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Research Seat" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Builder Seat" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Reviewer Seat" })).toBeDefined();
    expect(screen.getByText(/does not assign models, route requests, collect credentials/i)).toBeDefined();
    expect(screen.getByRole("heading", { name: "Task Lane Preview" })).toBeDefined();
    expect(screen.getByText("Using local Task Lane status fallback.")).toBeDefined();
    expect(screen.getByText(/Task lanes show future workflow organization/i)).toBeDefined();
    expect(screen.getByText("Task runtime")).toBeDefined();
    expect(screen.getByText("Task persistence")).toBeDefined();
    expect(screen.getByText("Scheduler")).toBeDefined();
    expect(screen.getByText("Background jobs")).toBeDefined();
    expect(screen.getByText("Notifications")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Inbox Lane" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Planned Lane" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Active Lane" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Review Lane" })).toBeDefined();
    expect(screen.getByText(/does not create tasks, store tasks, run a scheduler/i)).toBeDefined();
    expect(screen.getAllByText("Preview").length).toBeGreaterThanOrEqual(6);
    expect(screen.getByRole("heading", { name: "Provider Setup" })).toBeDefined();
    expect(screen.getAllByRole("heading", { name: "Local Ollama" }).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByRole("heading", { name: "OpenAI API" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Anthropic API" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Google Gemini API" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "OpenRouter" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "OpenRouter Free Model Smoke" })).toBeDefined();
    expect(screen.getByRole("button", { name: "Run OpenRouter smoke" })).toHaveProperty("disabled", true);
    expect(screen.getAllByText(/SPARKBOT_PROVIDER_CALLS_ENABLED=true/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByRole("heading", { name: "OpenAI Codex Subscription" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Claude Subscription" })).toBeDefined();
    expect(screen.getByText(/Provider onboarding is env-driven/i)).toBeDefined();
    expect(screen.getByText("Using local provider status fallback.")).toBeDefined();
    expect(screen.getAllByText("Credential storage").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Provider calls")).toBeDefined();
    expect(screen.getAllByText("Model routing").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("not implemented").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/no API key fields, no password or token fields/i)).toBeDefined();
    expect(screen.getByRole("heading", { name: "Connector Status Preview" })).toBeDefined();
    expect(screen.getByText("Using local connector status fallback.")).toBeDefined();
    expect(screen.getByText("Connectors enabled")).toBeDefined();
    expect(screen.getAllByText("disabled").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Outbound actions")).toBeDefined();
    expect(screen.getAllByText("Audit trail").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByRole("heading", { name: "Messaging connectors" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Calendar connectors" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Email connectors" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "File connectors" })).toBeDefined();
    expect(screen.getByText(/no credential fields, no token fields/i)).toBeDefined();
    expect(screen.getByRole("heading", { name: "Provider Setup shell" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Guardian Controls shell" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Guardian Controls Preview" })).toBeDefined();
    expect(screen.getByText("Using local Guardian status fallback.")).toBeDefined();
    expect(screen.getByText("Runtime enforcement")).toBeDefined();
    expect(screen.getByText("Approval tokens")).toBeDefined();
    expect(screen.getByText("Policy decisions")).toBeDefined();
    expect(screen.getByText("Default posture")).toBeDefined();
    expect(screen.getByText("deny sensitive actions")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Local actions" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Provider access" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Files and workspace" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "External connections" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Approval checkpoints" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Audit trail" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "External sends" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Connector calls" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Credential use" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Model provider calls" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "File writes" })).toBeDefined();
    expect(screen.getAllByRole("heading", { name: "Tool execution" }).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/Guardian-gated controls are planned for later slices/i)).toBeDefined();
    expect(screen.getByText(/no approval buttons, no execution controls, no save actions/i)).toBeDefined();
    expect(screen.getByRole("heading", { name: "Backend Health" })).toBeDefined();
    await waitFor(() => expect(fetch).toHaveBeenCalledWith(expect.stringContaining("/capabilities"), expect.any(Object)));
  }, 10000);

  it("renders backend capability statuses when the capabilities API responds", async () => {
    vi.stubGlobal("fetch", mockBackendStatusFetch());

    render(<App />);

    await waitFor(() => expect(screen.getAllByText("Using backend capabilities status.").length).toBeGreaterThanOrEqual(2));
    expect(screen.getByRole("heading", { name: "Backend health endpoint" })).toBeDefined();
    expect(screen.getByText("Read-only local health check.")).toBeDefined();
    expect(screen.getByText("No connector calls or external sends.")).toBeDefined();
    expect(screen.getAllByText(/Only explicit OpenRouter prompt calls are available/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("No credential entry or storage path.")).toBeDefined();
    expect(screen.getByText("No terminal, tool, or automation execution.")).toBeDefined();
    expect(screen.getByText("Future local action")).toBeDefined();
    expect(screen.getByText("23 public capability entries loaded.")).toBeDefined();
    expect(screen.getAllByText("Disabled by default").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Guarded future").length).toBeGreaterThanOrEqual(8);
  });

  it("renders backend Chat status when the Chat status API responds", async () => {
    vi.stubGlobal("fetch", mockBackendStatusFetch());

    render(<App />);

    expect(await screen.findByText("Using backend Chat status.")).toBeDefined();
    expect(screen.getByText("Chat runtime")).toBeDefined();
    expect(screen.getByText("Message persistence")).toBeDefined();
    expect(screen.getAllByText("Model calls").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Streaming")).toBeDefined();
    expect(screen.getByText("Provider routing")).toBeDefined();
    expect(screen.getAllByText("not implemented").length).toBeGreaterThanOrEqual(5);
    expect(screen.getAllByRole("heading", { name: "Chat shell" }).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Static chat shell preview. No messages are sent.")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Message input" })).toBeDefined();
    expect(screen.getByText("Input remains disabled until chat runtime and safety gates exist.")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Model response" })).toBeDefined();
    expect(screen.getByText("No model calls are implemented.")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Message history" })).toBeDefined();
    expect(screen.getByText("No message persistence is implemented.")).toBeDefined();
    expect(screen.getAllByText("Disabled by default").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Guarded future").length).toBeGreaterThanOrEqual(6);
  });

  it("renders backend Round Table status when the Round Table status API responds", async () => {
    vi.stubGlobal("fetch", mockBackendStatusFetch());

    render(<App />);

    expect(await screen.findByText("Using backend Round Table status.")).toBeDefined();
    expect(screen.getByText("Meeting engine")).toBeDefined();
    expect(screen.getByText("Agent orchestration")).toBeDefined();
    expect(screen.getAllByText("Model calls").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Turn persistence")).toBeDefined();
    expect(screen.getAllByText("not implemented").length).toBeGreaterThanOrEqual(7);
    expect(screen.getByRole("heading", { name: "Operator" })).toBeDefined();
    expect(screen.getByText("Human operator role shown as part of the shell preview.")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Assistant seat" })).toBeDefined();
    expect(screen.getByText("Assistant role preview only. No model calls are made.")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Research seat" })).toBeDefined();
    expect(screen.getByText("Research role is planned. No agent runtime is implemented.")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Builder seat" })).toBeDefined();
    expect(screen.getByText("Builder role is planned. No tool execution is implemented.")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Reviewer seat" })).toBeDefined();
    expect(screen.getByText("Reviewer role is planned. No review workflow runtime is implemented.")).toBeDefined();
    expect(screen.getAllByText("Preview").length).toBeGreaterThanOrEqual(7);
    expect(screen.getAllByText("Planned").length).toBeGreaterThanOrEqual(3);
  });

  it("renders backend Model Seat status when the status API responds", async () => {
    vi.stubGlobal("fetch", mockBackendStatusFetch());

    render(<App />);

    expect(await screen.findByText("Using backend Model Seat status.")).toBeDefined();
    expect(screen.getAllByText("Model calls").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Model routing").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Provider credentials")).toBeDefined();
    expect(screen.getByText("Seat persistence")).toBeDefined();
    expect(screen.getAllByText("not implemented").length).toBeGreaterThanOrEqual(4);
    expect(screen.getByRole("heading", { name: "Default Assistant Seat" })).toBeDefined();
    expect(screen.getByText("Read-only seat preview. No model is assigned or called.")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Research Seat" })).toBeDefined();
    expect(screen.getByText("Future seat for research workflows. No runtime behavior is implemented.")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Builder Seat" })).toBeDefined();
    expect(screen.getByText("Future seat for implementation workflows. No tool execution is implemented.")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Reviewer Seat" })).toBeDefined();
    expect(screen.getByText("Future seat for review workflows. No model routing is implemented.")).toBeDefined();
    expect(screen.getAllByText("Preview").length).toBeGreaterThanOrEqual(8);
    expect(screen.getAllByText("Planned").length).toBeGreaterThanOrEqual(4);
  });

  it("renders backend Task Lane status when the status API responds", async () => {
    vi.stubGlobal("fetch", mockBackendStatusFetch());

    render(<App />);

    expect(await screen.findByText("Using backend Task Lane status.")).toBeDefined();
    expect(screen.getByText("Task runtime")).toBeDefined();
    expect(screen.getByText("Task persistence")).toBeDefined();
    expect(screen.getByText("Scheduler")).toBeDefined();
    expect(screen.getByText("Background jobs")).toBeDefined();
    expect(screen.getByText("Notifications")).toBeDefined();
    expect(screen.getAllByText("not implemented").length).toBeGreaterThanOrEqual(5);
    expect(screen.getByRole("heading", { name: "Inbox Lane" })).toBeDefined();
    expect(screen.getByText("Read-only lane preview. No tasks are stored or executed.")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Planned Lane" })).toBeDefined();
    expect(screen.getByText("Future planning lane. No scheduler is implemented.")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Active Lane" })).toBeDefined();
    expect(screen.getByText("Future active work lane. No task runtime is implemented.")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Review Lane" })).toBeDefined();
    expect(screen.getByText("Future review lane. No workflow runtime is implemented.")).toBeDefined();
    expect(screen.getAllByText("Preview").length).toBeGreaterThanOrEqual(9);
    expect(screen.getAllByText("Planned").length).toBeGreaterThanOrEqual(7);
  });

  it("renders backend provider configuration status when the status API responds", async () => {
    vi.stubGlobal("fetch", mockBackendStatusFetch());

    render(<App />);

    expect(await screen.findByText("Using backend provider configuration status.")).toBeDefined();
    expect(screen.getAllByText("Credential storage").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Provider calls")).toBeDefined();
    expect(screen.getAllByText("Model routing").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("not implemented").length).toBeGreaterThanOrEqual(3);
    expect(screen.getAllByRole("heading", { name: "Local Ollama" }).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/Active localhost-only adapter/i)).toBeDefined();
    expect(screen.getByRole("heading", { name: "OpenAI API" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Anthropic API" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Google Gemini API" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "OpenRouter" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "OpenRouter Free Model Smoke" })).toBeDefined();
    expect(screen.getByRole("button", { name: "Run OpenRouter smoke" })).toHaveProperty("disabled", true);
    expect(screen.getAllByText(/SPARKBOT_PROVIDER_CALLS_ENABLED=true/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByRole("heading", { name: "OpenAI Codex Subscription" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Claude Subscription" })).toBeDefined();
    expect(screen.getAllByText("lima guardian required").length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText(/Install the Codex CLI/i)).toBeDefined();
    expect(screen.getAllByText(/Install Claude Code/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Planned").length).toBeGreaterThanOrEqual(6);
  });

  it("runs the enabled OpenRouter smoke prompt from Provider Setup", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = input.toString();
      if (url.includes("/provider-config/openrouter/prompt")) {
        return mockJsonResponse(openRouterPromptResponsePayload);
      }
      if (url.includes("/provider-config/status")) {
        return mockJsonResponse(enabledOpenRouterProviderConfigStatusPayload());
      }
      return mockBackendStatusFetch()(input, init);
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);

    expect(await screen.findByText("Using backend provider configuration status.")).toBeDefined();
    const smokeForm = screen.getByRole("form", { name: "OpenRouter free model smoke test" });
    expect(within(smokeForm).getByText("Available")).toBeDefined();
    fireEvent.change(within(smokeForm).getByLabelText("OpenRouter smoke prompt"), { target: { value: "Say OK from UI." } });
    fireEvent.change(within(smokeForm).getByLabelText("OpenRouter smoke model"), {
      target: { value: "mistralai/mistral-7b-instruct:free" }
    });
    fireEvent.click(within(smokeForm).getByRole("button", { name: "Run OpenRouter smoke" }));

    expect(await screen.findByText("OK from OpenRouter")).toBeDefined();
    const promptCall = fetchMock.mock.calls.find(([input]) => input.toString().includes("/provider-config/openrouter/prompt"));
    expect(promptCall).toBeDefined();
    expect(promptCall?.[1]).toEqual(
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ prompt: "Say OK from UI.", model: "mistralai/mistral-7b-instruct:free" })
      })
    );
    expect(JSON.stringify(promptCall?.[1])).not.toContain("OPENROUTER_API_KEY");
  });

  it("renders backend connector status when the connector status API responds", async () => {
    vi.stubGlobal("fetch", mockBackendStatusFetch());

    render(<App />);

    expect(await screen.findByText("Using backend connector status.")).toBeDefined();
    expect(screen.getByText("Connectors enabled")).toBeDefined();
    expect(screen.getAllByText("disabled").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Outbound actions")).toBeDefined();
    expect(screen.getAllByText("Credential storage").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Audit trail").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("not implemented").length).toBeGreaterThanOrEqual(5);
    expect(screen.getByRole("heading", { name: "Messaging connectors" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Calendar connectors" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Email connectors" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "File connectors" })).toBeDefined();
    expect(screen.getAllByText("Guarded future").length).toBeGreaterThanOrEqual(8);
    expect(screen.getByText(/No outbound sends are implemented/i)).toBeDefined();
    expect(screen.getAllByText(/No external sends are implemented/i).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/No file mutation is implemented/i)).toBeDefined();
  });

  it("renders backend Guardian status when the Guardian status API responds", async () => {
    vi.stubGlobal("fetch", mockBackendStatusFetch());

    render(<App />);

    expect(await screen.findByText("Using backend Guardian status.")).toBeDefined();
    expect(screen.getByText("Runtime enforcement")).toBeDefined();
    expect(screen.getByText("Approval tokens")).toBeDefined();
    expect(screen.getByText("Policy decisions")).toBeDefined();
    expect(screen.getByText("Default posture")).toBeDefined();
    expect(screen.getByText("deny sensitive actions")).toBeDefined();
    expect(screen.getByRole("heading", { name: "LIMA Guardian provider runtime boundary" })).toBeDefined();
    expect(screen.getAllByText("lima guardian required").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("fail closed")).toBeDefined();
    expect(screen.getByText(/capability-check, operator-approval, audit-log/i)).toBeDefined();
    expect(screen.getByText(/Codex and Claude subscription CLI dispatch requires/i)).toBeDefined();
    expect(screen.getAllByText("not implemented").length).toBeGreaterThanOrEqual(8);
    expect(screen.getByRole("heading", { name: "External sends" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Connector calls" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Credential use" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Model provider calls" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "File writes" })).toBeDefined();
    expect(screen.getAllByRole("heading", { name: "Tool execution" }).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Guarded future").length).toBeGreaterThanOrEqual(14);
    expect(screen.getByText("No connector calls are implemented.")).toBeDefined();
    expect(screen.getByText("No model provider calls are implemented.")).toBeDefined();
    expect(screen.getByText("No terminal or tool execution is implemented.")).toBeDefined();
  });

  it("renders local Workstation runtime data from backend", async () => {
    vi.stubGlobal("fetch", mockBackendStatusFetch());

    render(<App />);

    expect((await screen.findAllByText("Seeded local chat")).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("1 local messages")).toBeDefined();
    expect((await screen.findAllByText("Seeded memory")).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Stored local note.")).toBeDefined();
    expect(await screen.findByText("Seeded card")).toBeDefined();
    expect(screen.getByText("Stored local card.")).toBeDefined();
    expect(screen.getByText("Linked chat: Seeded local chat")).toBeDefined();
    expect(screen.getAllByRole("button", { name: "Edit" }).length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByRole("button", { name: "Delete" }).length).toBeGreaterThanOrEqual(2);
  });

  it("creates a local chat session and stores a local message", async () => {
    const fetchMock = mockBackendStatusFetch();
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);

    fireEvent.change(screen.getByLabelText("Session title"), { target: { value: "New local chat" } });
    fireEvent.click(screen.getAllByRole("button", { name: "Save locally" })[0]);

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/local/chat/sessions"), expect.objectContaining({ method: "POST" }))
    );

    const localMessage = await screen.findByLabelText("Local message");
    fireEvent.change(localMessage, { target: { value: "Store this operator message locally." } });
    fireEvent.click(screen.getAllByRole("button", { name: "Save locally" })[1]);

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/local/chat/sessions/session-1/messages"),
        expect.objectContaining({ method: "POST" })
      )
    );
  });

  it("creates local memory notes and work lane cards through local endpoints", async () => {
    const fetchMock = mockBackendStatusFetch();
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);

    fireEvent.change(screen.getByLabelText("Note title"), { target: { value: "New local note" } });
    fireEvent.change(screen.getByLabelText("Note body"), { target: { value: "Only local storage." } });
    fireEvent.click(screen.getByRole("button", { name: "Add local note" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/local/memory-notes"), expect.objectContaining({ method: "POST" }))
    );

    fireEvent.change(screen.getByLabelText("Card title"), { target: { value: "New local card" } });
    fireEvent.change(screen.getByLabelText("Card body"), { target: { value: "Plan this locally." } });
    fireEvent.change(screen.getByLabelText("Linked local chat session"), { target: { value: "session-1" } });
    fireEvent.click(screen.getByRole("button", { name: "Add card" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/local/work-lane-cards"), expect.objectContaining({ method: "POST" }))
    );
    const cardCall = fetchMock.mock.calls.find(([input, init]) =>
      input.toString().includes("/local/work-lane-cards") && init?.method === "POST"
    );
    expect(JSON.parse((cardCall?.[1]?.body as string) ?? "{}")).toMatchObject({ chat_session_id: "session-1" });
  });


  it("renders local runtime settings from the backend without save controls", async () => {
    const fetchMock = mockBackendStatusFetch();
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);

    expect(await screen.findByText("Using backend local runtime settings.")).toBeDefined();
    const settingsPanel = screen.getByRole("region", { name: "Local Runtime Settings" });
    expect(within(settingsPanel).getByRole("heading", { name: "Local Runtime Settings" })).toBeDefined();
    expect(within(settingsPanel).getByText("SPARKBOT_DATA_DIR")).toBeDefined();
    expect(within(settingsPanel).getByText("sparkbot_public.sqlite3")).toBeDefined();
    expect(within(settingsPanel).getByText("~/.local/share/sparkbot-public")).toBeDefined();
    expect(within(settingsPanel).getByText("http://127.0.0.1:11434")).toBeDefined();
    expect(within(settingsPanel).getByText("localhost-only")).toBeDefined();
    expect(within(settingsPanel).getByText(/No credential fields, secret save buttons/i)).toBeDefined();
    expect(within(settingsPanel).queryByRole("button", { name: /save|secret|credential/i })).toBeNull();
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/local/runtime/settings"), expect.objectContaining({ cache: "no-store" }));
  });


  it("exports local Workstation data as a browser JSON download", async () => {
    const fetchMock = mockBackendStatusFetch();
    vi.stubGlobal("fetch", fetchMock);
    const createObjectUrl = vi.fn(() => "blob:local-export");
    const revokeObjectUrl = vi.fn();
    const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    Object.defineProperty(URL, "createObjectURL", { configurable: true, value: createObjectUrl });
    Object.defineProperty(URL, "revokeObjectURL", { configurable: true, value: revokeObjectUrl });

    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: "Export JSON" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/local/export"), expect.objectContaining({ cache: "no-store" }))
    );
    expect(clickSpy).toHaveBeenCalledTimes(1);
    expect(createObjectUrl).toHaveBeenCalledTimes(1);
    expect(revokeObjectUrl).toHaveBeenCalledWith("blob:local-export");
    expect(await screen.findByText(/Exported local Workstation JSON/i)).toBeDefined();
  });


  it("renders local model status as disabled by default", async () => {
    vi.stubGlobal("fetch", mockBackendStatusFetch());

    render(<App />);

    expect(await screen.findByText("Using backend local model status.")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Local Ollama Adapter" })).toBeDefined();
    expect(screen.getByText(/Status: disabled by default/i)).toBeDefined();
    expect(screen.getAllByText("disabled").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("localhost only")).toBeDefined();
    expect(screen.getAllByText("not supported").length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText(/Local prompt calls are disabled until the backend is explicitly enabled/i)).toBeDefined();
    expect((screen.getByRole("button", { name: "Run local prompt" }) as HTMLButtonElement).disabled).toBe(true);
    expect(screen.queryByLabelText(/api key|password|token/i)).toBeNull();
  });

  it("shows local model offline state when Ollama is enabled but unavailable", async () => {
    const fallbackFetch = mockBackendStatusFetch();
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = input.toString();
      if (url.includes("/local-models/status")) {
        return mockJsonResponse({
          ...localModelEnabledStatusPayload,
          status: "unavailable",
          ollama_reachable: false
        });
      }
      return fallbackFetch(input, init);
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);

    expect(await screen.findByText(/Status: unavailable/i)).toBeDefined();
    expect(screen.getByText(/Ollama is offline or unavailable on localhost/i)).toBeDefined();
    expect((screen.getByRole("button", { name: "Run local prompt" }) as HTMLButtonElement).disabled).toBe(true);
  });

  it("runs a local-only prompt when backend reports local models enabled", async () => {
    const fallbackFetch = mockBackendStatusFetch();
    const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = input.toString();
      if (url.includes("/local-models/status")) {
        return mockJsonResponse(localModelEnabledStatusPayload);
      }
      if (url.includes("/local-models/ollama/prompt")) {
        return mockJsonResponse(localPromptResponsePayload);
      }
      return fallbackFetch(input, init);
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);

    expect(await screen.findByText(/Status: available local only/i)).toBeDefined();
    expect((screen.getByRole("button", { name: "Run local prompt" }) as HTMLButtonElement).disabled).toBe(false);
    expect(screen.getByLabelText("Local chat session")).toBeDefined();
    expect(screen.getByRole("checkbox", { name: "Seeded memory" })).toBeDefined();
    fireEvent.click(screen.getByRole("checkbox", { name: "Seeded memory" }));
    fireEvent.change(screen.getByLabelText("Local prompt"), { target: { value: "Use only localhost." } });
    fireEvent.click(screen.getByRole("button", { name: "Run local prompt" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/local-models/ollama/prompt"), expect.objectContaining({ method: "POST" }))
    );
    expect(await screen.findByText("Local-only Ollama response.")).toBeDefined();
    expect(screen.getByText(/assistant response was saved to the selected session/i)).toBeDefined();
    expect(screen.getByText(/1 selected memory note\(s\) were included/i)).toBeDefined();
    const promptCall = fetchMock.mock.calls.find(([input]) => input.toString().includes("/local-models/ollama/prompt"));
    expect(JSON.parse((promptCall?.[1]?.body as string) ?? "{}")).toMatchObject({
      prompt: "Use only localhost.",
      model: "llama3.2",
      session_id: "session-1",
      selected_memory_note_ids: ["note-1"]
    });
  });

  it("keeps fallback statuses on the public capability contract vocabulary", () => {
    render(<App />);

    expect(screen.getAllByText("Available").length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText("Preview").length).toBeGreaterThanOrEqual(6);
    expect(screen.getAllByText("Planned").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Disabled by default").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Planned").length).toBeGreaterThanOrEqual(6);
  });

  it("keeps provider, connector, chat, Round Table, Task Lane, and guardian surfaces inert", () => {
    render(<App />);

    expect(screen.queryByPlaceholderText(/api key|password|token/i)).toBeNull();
    expect(screen.queryByLabelText(/api key|password|token/i)).toBeNull();
    expect(screen.queryByRole("textbox", { name: /api key|password|token/i })).toBeNull();
    expect(document.querySelectorAll('input[type="password"]').length).toBe(0);
    expect(document.querySelectorAll('textarea').length).toBeGreaterThanOrEqual(1);
    expect(document.querySelectorAll('input[type="password"]').length).toBe(0);
    expect(screen.queryByRole("button", { name: /test connection|\bconnect\b|\bcomplete\b|\bschedule\b|\bremind\b/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /approve|execute|enforce|allow|deny|assign/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /policy decision|runtime enforcement|approval token/i })).toBeNull();
    for (const button of screen.queryAllByRole("button", { name: /start|join|send|run|invite/i })) {
      expect((button as HTMLButtonElement).disabled).toBe(true);
    }
    expect(screen.queryByRole("button", { name: /send|execute|test provider/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /connector call|outbound action|external send/i })).toBeNull();
  });
});
