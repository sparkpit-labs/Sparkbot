import { render, screen } from "@testing-library/react";

import App from "./App";

describe("App", () => {
  it("renders Sparkbot heading and implemented status", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: "Sparkbot" })).toBeDefined();
    expect(screen.getByText(/server baseline exists/i)).toBeDefined();
    expect(screen.getByRole("heading", { name: "Backend Health" })).toBeDefined();
  });
});
