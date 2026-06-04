import { cleanup, render, screen } from "@testing-library/react";
import { vi } from "vitest";

import App from "./App";

describe("App", () => {
  beforeEach(() => {
    window.history.pushState({}, "", "/");
  });

  afterEach(() => {
    cleanup();
  });

  it("routes root to the Workstation floor", () => {
    render(<App />);

    expect(screen.getByRole("heading", { level: 1, name: "Sparkbot" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Workstation Floor" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Room foundation" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Model seats" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Round Table Room" })).toBeDefined();
    expect(screen.queryByRole("heading", { name: "Sparkbot Chat" })).toBeNull();
    expect(screen.queryByRole("heading", { name: "Workstation Command Center" })).toBeNull();
  });

  it("routes Round Table to the backend-backed room surface", () => {
    window.history.pushState({}, "", "/roundtable");

    render(<App />);

    expect(screen.getByRole("heading", { name: "Round Table Room" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Round Table counters" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Seat 1 Meeting Manager" })).toBeDefined();
    expect(screen.getByRole("button", { name: "Run provider-safe meeting" })).toBeDefined();
    expect(screen.queryByRole("heading", { name: "Workstation Floor" })).toBeNull();
    expect(screen.queryByRole("heading", { name: "Sparkbot Chat" })).toBeNull();
  });

  it("does not persist Round Table meeting state in browser storage", async () => {
    window.history.pushState({}, "", "/roundtable");
    const storageSpy = vi.spyOn(Storage.prototype, "setItem");

    try {
      render(<App />);
      await Promise.resolve();

      expect(storageSpy).not.toHaveBeenCalled();
    } finally {
      storageSpy.mockRestore();
    }
  });

  it("keeps Chat as the operator conversation surface", () => {
    window.history.pushState({}, "", "/chat");

    render(<App />);

    expect(screen.getByRole("heading", { name: "Sparkbot Chat" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Shared Chat" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Memory, notes, and Spine" })).toBeDefined();
    expect(screen.getByRole("button", { name: "Send" })).toBeDefined();
    expect(screen.getByText(/Selected route:/)).toBeDefined();
    expect(screen.queryByText("unit-test-credential-value")).toBeNull();
    expect(screen.queryByRole("heading", { name: "Workstation Floor" })).toBeNull();
  });

  it("keeps Command Center focused on configuration and security", () => {
    window.history.pushState({}, "", "/command-center");

    render(<App />);

    expect(screen.getByRole("heading", { name: "Workstation Command Center" })).toBeDefined();
    expect(screen.getByRole("navigation", { name: "Command Center sections" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "AI Setup" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Security" })).toBeDefined();
    expect(screen.queryByRole("heading", { name: "Workstation Floor" })).toBeNull();
    expect(screen.queryByRole("heading", { name: "Spine Event Log" })).toBeNull();
  });

  it("keeps Spine focused on event history and counters", () => {
    window.history.pushState({}, "", "/spine");

    render(<App />);

    expect(screen.getByRole("heading", { name: "Spine Event Log" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Shared event state" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Recent events" })).toBeDefined();
    expect(screen.queryByRole("heading", { name: "Workstation Command Center" })).toBeNull();
  });

  it("keeps Controls focused on setup and capability limits", () => {
    window.history.pushState({}, "", "/controls");

    render(<App />);

    expect(screen.getByRole("heading", { name: "Controls Setup" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Local readiness" })).toBeDefined();
    expect(screen.getByRole("heading", { name: "Deferred action paths" })).toBeDefined();
    expect(screen.queryByRole("heading", { name: "Sparkbot Chat" })).toBeNull();
  });
});
