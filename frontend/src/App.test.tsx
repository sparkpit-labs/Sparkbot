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
      status: "available",
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
      label: "Provider Setup",
      status: "preview",
      notes: "No credential storage or provider calls."
    },
    {
      id: "guardian-controls",
      label: "Guardian Controls",
      status: "preview",
      notes: "No policy enforcement runtime."
    },
    {
      id: "desktop-packaging",
      label: "Desktop packaging",
      status: "planned",
      notes: "No installer or desktop binary yet."
    }
  ]
};

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
    expect(screen.getByRole("button", { name: /Workstation.*Works Today/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /Chat.*Preview/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /Round Table.*Preview/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /Provider Setup.*Planned/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /Guardian Controls.*Planned/i })).toBeDefined();
    expect(screen.getByText("Not Implemented")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Server baseline" })).toBeDefined();
    expect(screen.getByText(/section selector, and status model exist as a read-only baseline/i)).toBeDefined();
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
    expect(screen.getAllByText("Preview").length).toBeGreaterThanOrEqual(3);
    expect(screen.getByRole("heading", { name: "Provider Setup Preview" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Local model provider" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "OpenAI-compatible provider" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Anthropic-compatible provider" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Google-compatible provider" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Custom endpoint" })).toBeDefined();
    expect(screen.getByText(/provider configuration is planned for later slices/i)).toBeDefined();
    expect(screen.getByText(/no API key fields, no save actions, and no test-connection actions/i)).toBeDefined();
    expect(screen.getByRole("heading", { name: "Provider setup" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Guardian-gated controls" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Guardian Controls Preview" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Local actions" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Provider access" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Files and workspace" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "External connections" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Approval checkpoints" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Audit trail" })).toBeDefined();
    expect(screen.getByText(/Guardian-gated controls are planned for later slices/i)).toBeDefined();
    expect(screen.getByText(/no approval buttons, no execution controls, no save actions/i)).toBeDefined();
    expect(screen.getAllByText("Works Today").length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText("Planned").length).toBeGreaterThanOrEqual(3);
    expect(screen.getByRole("heading", { name: "Backend Health" })).toBeDefined();
    await waitFor(() => expect(fetch).toHaveBeenCalledWith(expect.stringContaining("/capabilities"), expect.any(Object)));
  });

  it("renders backend capability statuses when the capabilities API responds", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify(capabilitiesPayload), {
          status: 200,
          headers: { "Content-Type": "application/json" }
        })
      )
    );

    render(<App />);

    expect(await screen.findByText("Using backend capabilities status.")).toBeDefined();
    expect(screen.getByRole("heading", { name: "Backend health endpoint" })).toBeDefined();
    expect(screen.getByText("Read-only local health check.")).toBeDefined();
    expect(screen.getByText("No credential storage or provider calls.")).toBeDefined();
    expect(screen.getByText("No policy enforcement runtime.")).toBeDefined();
    expect(screen.getByText("No installer or desktop binary yet.")).toBeDefined();
  });

  it("keeps provider, chat, and guardian surfaces inert", () => {
    render(<App />);

    expect(screen.queryByPlaceholderText(/api key/i)).toBeNull();
    expect(screen.queryByRole("button", { name: /save|test connection|connect/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /approve|execute|enforce|allow|deny/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /start|join|send|run/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /send|execute|save|test/i })).toBeNull();
  });
});
