import { render, screen } from "@testing-library/react";

import App from "./App";

describe("App", () => {
  it("renders workstation shell status and health panel", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: "Sparkbot" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Workstation Shell" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Server baseline" })).toBeDefined();
    expect(screen.getByText(/product shell layout exists as a read-only baseline/i)).toBeDefined();
    expect(screen.getByRole("heading", { name: "Round Table" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Provider setup" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Guardian-gated controls" })).toBeDefined();
    expect(screen.getAllByText("Planned").length).toBeGreaterThanOrEqual(3);
    expect(screen.getByRole("heading", { name: "Backend Health" })).toBeDefined();
  });
});
