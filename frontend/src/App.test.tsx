import { render, screen } from "@testing-library/react";

import App from "./App";

describe("App", () => {
  it("renders workstation shell status, Round Table preview, and health panel", () => {
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
    expect(screen.getByRole("heading", { name: "Provider setup" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Guardian-gated controls" })).toBeDefined();
    expect(screen.getAllByText("Planned").length).toBeGreaterThanOrEqual(3);
    expect(screen.getByRole("heading", { name: "Backend Health" })).toBeDefined();
    expect(screen.queryByRole("button", { name: /start|join|send|run/i })).toBeNull();
  });
});
