import { render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";

describe("App", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = input.toString();
        if (url.endsWith("/api/providers/status")) {
          return new Response(
            JSON.stringify({
              selected_provider: "openai",
              selected_model: "gpt-4o-mini",
              configured: true,
              message: "Configured",
              providers: [
                {
                  id: "openai",
                  label: "OpenAI",
                  configured: true,
                  model: "gpt-4o-mini",
                  base_url_configured: true,
                  message: "Configured"
                },
                {
                  id: "openai_compatible",
                  label: "OpenAI-compatible",
                  configured: false,
                  model: null,
                  base_url_configured: false,
                  message: "OpenAI-compatible base URL is not configured on the backend."
                },
                {
                  id: "ollama",
                  label: "Ollama",
                  configured: false,
                  model: null,
                  base_url_configured: true,
                  message: "Ollama model is not configured."
                }
              ]
            }),
            { status: 200, headers: { "Content-Type": "application/json" } }
          );
        }

        return new Response(
          JSON.stringify({ status: "ok", service: "sparkbot-server", mode: "local" }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        );
      })
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders workstation runtime chat and backend-configured provider status", async () => {
    render(<App />);

    expect(screen.getByRole("heading", { level: 1, name: "Sparkbot" })).toBeDefined();
    expect(screen.getByRole("heading", { level: 2, name: "Workstation" })).toBeDefined();
    expect(await screen.findByRole("heading", { name: "Workstation Sections" })).toBeDefined();
    expect(screen.getByRole("button", { name: /Chat.*Works Today/i })).toBeDefined();
    expect(screen.getByRole("button", { name: /Provider.*Works Today/i })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Sparkbot Runtime Chat" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Provider Runtime" })).toBeDefined();
    expect(screen.getByLabelText("Message Sparkbot")).toBeDefined();
    expect(screen.getByRole("button", { name: "Send" })).toBeDefined();
    expect((await screen.findAllByText("Configured")).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByDisplayValue("gpt-4o-mini")).toBeDefined();
    expect(screen.queryByPlaceholderText(/api key/i)).toBeNull();
    expect(screen.getByRole("heading", { name: "Backend Health" })).toBeDefined();
  });
});
