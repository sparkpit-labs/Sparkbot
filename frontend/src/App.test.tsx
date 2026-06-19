import { render, screen, waitFor } from "@testing-library/react";
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
      status: "preview",
      notes: "No credential storage or provider calls."
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
      label: "Model calls",
      status: "guarded-future",
      notes: "No provider runtime or model routing."
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


const providerConfigStatusPayload = {
  service: "sparkbot-server",
  mode: "local",
  status: "preview",
  credential_storage: "not-implemented",
  provider_calls: "not-implemented",
  model_routing: "not-implemented",
  providers: [
    {
      id: "local",
      label: "Local provider",
      status: "planned",
      notes: "Local provider configuration is planned. No runtime provider calls are made."
    },
    {
      id: "openai-compatible",
      label: "OpenAI-compatible provider",
      status: "guarded-future",
      notes: "Cloud provider configuration will require explicit setup and safety gates."
    },
    {
      id: "anthropic-compatible",
      label: "Anthropic-compatible provider",
      status: "guarded-future",
      notes: "Cloud provider configuration will require explicit setup and safety gates."
    },
    {
      id: "google-compatible",
      label: "Google-compatible provider",
      status: "guarded-future",
      notes: "Cloud provider configuration will require explicit setup and safety gates."
    },
    {
      id: "custom-endpoint",
      label: "Custom endpoint",
      status: "guarded-future",
      notes: "Custom endpoints are planned for future guarded configuration."
    }
  ]
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

function mockJsonResponse(payload: unknown) {
  return Promise.resolve(
    new Response(JSON.stringify(payload), {
      status: 200,
      headers: { "Content-Type": "application/json" }
    })
  );
}

function mockBackendStatusFetch() {
  return vi.fn((input: RequestInfo | URL) => {
    const url = input.toString();

    if (url.includes("/connector-status")) {
      return mockJsonResponse(connectorStatusPayload);
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
    vi.unstubAllGlobals();
  });

  it("renders workstation navigation, preview-only shell sections, fallback statuses, and read-only health panel", async () => {
    render(<App />);

    expect(screen.getByRole("heading", { level: 1, name: "Sparkbot" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Workstation Shell" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Shell Sections" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Workstation Overview" })).toBeDefined();
    expect(screen.getByText("Using local fallback status list.")).toBeDefined();
    expect(screen.getByRole("button", { name: /Workstation.*Preview/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /Chat.*Preview/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /Round Table.*Preview/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /Provider Setup.*Preview/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /Guardian Controls.*Preview/i })).toBeDefined();
    expect(screen.getAllByText("Available").length).toBeGreaterThanOrEqual(2);
    expect(screen.getByRole("heading", { name: "Backend health endpoint" })).toBeDefined();
    expect(screen.getByText("Read-only local health check.")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Connectors" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Model calls" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Credential storage" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Tool execution" })).toBeDefined();
    expect(screen.getAllByText("Guarded future").length).toBeGreaterThanOrEqual(4);
    expect(screen.getByText("No connector calls or external sends.")).toBeDefined();
    expect(screen.getByText("No provider runtime or model routing.")).toBeDefined();
    expect(screen.getByText("No credential entry or storage path.")).toBeDefined();
    expect(screen.getByText("No terminal, tool, or automation execution.")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Chat shell" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Chat Shell Preview" })).toBeDefined();
    expect(screen.getByText(/chat runtime is planned for later slices/i)).toBeDefined();
    expect(screen.getByText(/Empty state: chat history will appear here/i)).toBeDefined();
    expect(screen.getByText(/no enabled send action, no chat endpoint/i)).toBeDefined();
    const plannedComposer = screen.getByLabelText("Chat message composer planned") as HTMLTextAreaElement;
    expect(plannedComposer.disabled).toBe(true);
    expect(plannedComposer.readOnly).toBe(true);
    expect(screen.getByRole("heading", { name: "Round Table" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Round Table Preview" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Operator" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Assistant seat" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Research seat" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Builder seat" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Reviewer seat" })).toBeDefined();
    expect(screen.getByText(/multi-agent collaboration is planned/i)).toBeDefined();
    expect(screen.getByText(/does not start meetings, call models, run a turn engine/i)).toBeDefined();
    expect(screen.getAllByText("Preview").length).toBeGreaterThanOrEqual(5);
    expect(screen.getByRole("heading", { name: "Provider Setup Preview" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Local provider" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "OpenAI-compatible provider" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Anthropic-compatible provider" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Google-compatible provider" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Custom endpoint" })).toBeDefined();
    expect(screen.getByText(/provider configuration status is read-only/i)).toBeDefined();
    expect(screen.getByText("Using local provider status fallback.")).toBeDefined();
    expect(screen.getAllByText("Credential storage").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Provider calls")).toBeDefined();
    expect(screen.getByText("Model routing")).toBeDefined();
    expect(screen.getAllByText("not implemented").length).toBeGreaterThanOrEqual(3);
    expect(screen.getByText(/no API key fields, no password or token fields/i)).toBeDefined();
    expect(screen.getByRole("heading", { name: "Connector Status Preview" })).toBeDefined();
    expect(screen.getByText("Using local connector status fallback.")).toBeDefined();
    expect(screen.getByText("Connectors enabled")).toBeDefined();
    expect(screen.getByText("disabled")).toBeDefined();
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
    expect(screen.getByRole("heading", { name: "Local actions" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Provider access" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Files and workspace" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "External connections" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Approval checkpoints" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Audit trail" })).toBeDefined();
    expect(screen.getByText(/Guardian-gated controls are planned for later slices/i)).toBeDefined();
    expect(screen.getByText(/no approval buttons, no execution controls, no save actions/i)).toBeDefined();
    expect(screen.getByRole("heading", { name: "Backend Health" })).toBeDefined();
    await waitFor(() => expect(fetch).toHaveBeenCalledWith(expect.stringContaining("/capabilities"), expect.any(Object)));
  });

  it("renders backend capability statuses when the capabilities API responds", async () => {
    vi.stubGlobal("fetch", mockBackendStatusFetch());

    render(<App />);

    expect(await screen.findByText("Using backend capabilities status.")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Backend health endpoint" })).toBeDefined();
    expect(screen.getByText("Read-only local health check.")).toBeDefined();
    expect(screen.getByText("No connector calls or external sends.")).toBeDefined();
    expect(screen.getByText("No provider runtime or model routing.")).toBeDefined();
    expect(screen.getByText("No credential entry or storage path.")).toBeDefined();
    expect(screen.getByText("No terminal, tool, or automation execution.")).toBeDefined();
    expect(screen.getByText("Future local action")).toBeDefined();
    expect(screen.getAllByText("Disabled by default").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Guarded future").length).toBeGreaterThanOrEqual(8);
  });

  it("renders backend provider configuration status when the status API responds", async () => {
    vi.stubGlobal("fetch", mockBackendStatusFetch());

    render(<App />);

    expect(await screen.findByText("Using backend provider configuration status.")).toBeDefined();
    expect(screen.getAllByText("Credential storage").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Provider calls")).toBeDefined();
    expect(screen.getByText("Model routing")).toBeDefined();
    expect(screen.getAllByText("not implemented").length).toBeGreaterThanOrEqual(3);
    expect(screen.getByRole("heading", { name: "Local provider" })).toBeDefined();
    expect(screen.getByText("Local provider configuration is planned. No runtime provider calls are made.")).toBeDefined();
    expect(screen.getByRole("heading", { name: "OpenAI-compatible provider" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Anthropic-compatible provider" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Google-compatible provider" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Custom endpoint" })).toBeDefined();
    expect(screen.getAllByText("Guarded future").length).toBeGreaterThanOrEqual(4);
  });

  it("renders backend connector status when the connector status API responds", async () => {
    vi.stubGlobal("fetch", mockBackendStatusFetch());

    render(<App />);

    expect(await screen.findByText("Using backend connector status.")).toBeDefined();
    expect(screen.getByText("Connectors enabled")).toBeDefined();
    expect(screen.getByText("disabled")).toBeDefined();
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
    expect(screen.getByText(/No external sends are implemented/i)).toBeDefined();
    expect(screen.getByText(/No file mutation is implemented/i)).toBeDefined();
  });

  it("keeps fallback statuses on the public capability contract vocabulary", () => {
    render(<App />);

    expect(screen.getAllByText("Available").length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText("Preview").length).toBeGreaterThanOrEqual(5);
    expect(screen.getAllByText("Planned").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Disabled by default").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Guarded future").length).toBeGreaterThanOrEqual(4);
  });

  it("keeps provider, connector, chat, and guardian surfaces inert", () => {
    render(<App />);

    expect(screen.queryByPlaceholderText(/api key|password|token/i)).toBeNull();
    expect(screen.queryByLabelText(/api key|password|token/i)).toBeNull();
    expect(screen.queryByRole("textbox", { name: /api key|password|token/i })).toBeNull();
    expect(document.querySelectorAll('input').length).toBe(0);
    expect(document.querySelectorAll('textarea').length).toBe(1);
    expect(document.querySelectorAll('input[type="password"]').length).toBe(0);
    expect(screen.queryByRole("button", { name: /save|test connection|connect/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /approve|execute|enforce|allow|deny/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /start|join|send|run/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /send|execute|save|test/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /connector call|outbound action|external send/i })).toBeNull();
  });
});
