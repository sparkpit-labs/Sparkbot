import { render, screen } from "@testing-library/react";

import App from "./App";

describe("App", () => {
  it("renders workstation shell status, Round Table preview, provider setup preview, Guardian Controls preview, and health panel", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: "Sparkbot" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Workstation Shell" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Server baseline" })).toBeDefined();
    expect(screen.getByText(/product shell layout exists as a read-only baseline/i)).toBeDefined();
    expect(screen.getByRole("heading", { name: "Round Table" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Round Table Preview" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Operator" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Assistant seat" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Research seat" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Builder seat" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Reviewer seat" })).toBeDefined();
    expect(screen.getByText(/multi-agent collaboration is planned/i)).toBeDefined();
    expect(screen.getByText(/does not start meetings, call models, run a turn engine/i)).toBeDefined();
    expect(screen.getAllByText("Preview").length).toBeGreaterThanOrEqual(1);
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
    expect(screen.getAllByText("Skeleton").length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText("Planned").length).toBeGreaterThanOrEqual(3);
    expect(screen.getByRole("heading", { name: "Backend Health" })).toBeDefined();
    expect(screen.queryByPlaceholderText(/api key/i)).toBeNull();
    expect(screen.queryByRole("button", { name: /save|test connection|connect/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /approve|execute|enforce|allow|deny/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /start|join|send|run/i })).toBeNull();
  });
});
