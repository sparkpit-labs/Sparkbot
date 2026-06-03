import { render, screen } from "@testing-library/react";

import App from "./App";

describe("App", () => {
  it("renders the restored Workstation Command Center instead of preview-only shell sections", () => {
    render(<App />);

    expect(screen.getByRole("heading", { level: 1, name: "Sparkbot" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Workstation Command Center" })).toBeDefined();
    expect(screen.getByRole("navigation", { name: "Primary navigation" })).toBeDefined();
    expect(screen.getByRole("navigation", { name: "Command Center sections" })).toBeDefined();

    expect(screen.getByRole("heading", { name: "AI Setup" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Ollama status" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Four-model stack" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Security" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Operator PIN" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Connectors" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Agent routing and Specialty Wing controls" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "System Health" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Token Guardian" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Scheduled work" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Spine and Guardian operations" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Model seats and Specialty Wing" })).toBeDefined();

    expect(screen.getByRole("button", { name: "Refresh OpenRouter models" })).toBeDefined();
    expect(screen.getByRole("button", { name: "Check local" })).toBeDefined();
    expect(screen.getByRole("button", { name: "Save default model" })).toBeDefined();
    expect(screen.getByRole("button", { name: "Save credential" })).toBeDefined();
    expect(screen.getByRole("button", { name: "Save overrides" })).toBeDefined();
    expect(screen.getByRole("button", { name: "Save seat routes" })).toBeDefined();

    expect(screen.queryByRole("heading", { name: "Workstation Shell" })).toBeNull();
    expect(screen.queryByText(/read-only map/i)).toBeNull();
    expect(screen.queryByText(/Provider Setup Preview/i)).toBeNull();
    expect(screen.queryByText(/Guardian Controls Preview/i)).toBeNull();
    expect(screen.queryByText(/no enabled send action/i)).toBeNull();
    expect(screen.getByRole("heading", { name: "Backend Health" })).toBeDefined();
  });
});
