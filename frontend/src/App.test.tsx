import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { vi } from "vitest";

import App from "./App";
import ChatWorkstation from "./components/ChatWorkstation";

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
    expect(screen.getByRole("button", { name: "Run Round Table meeting" })).toBeDefined();
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

  it("does not persist Agents Wing or seat state in browser storage", async () => {
    window.history.pushState({}, "", "/command-center");
    const storageSpy = vi.spyOn(Storage.prototype, "setItem");

    try {
      render(<App />);
      await Promise.resolve();

      expect(storageSpy).not.toHaveBeenCalled();
    } finally {
      storageSpy.mockRestore();
    }
  });

  it("renders and deletes memory through server confirmations", async () => {
    const storageSpy = vi.spyOn(Storage.prototype, "setItem");
    let memoryDeleted = false;
    const workstationState = () => ({
      controls: { default_selection: { provider: "openrouter", model: "openrouter/openai/gpt-4o-mini", label: "OpenRouter" } },
      seats: [{ seat_index: 1, label: "Seat 1", agent: "meetings_manager", provider: "default", model: "", updated_at: "2026-01-01T00:00:00Z" }],
      rooms: [],
      notes: [],
      memory: {
        items: memoryDeleted ? [] : [{
          id: "mem-1",
          content: "Visible shared memory. api_key=[redacted]",
          memory_type: "preference",
          source_surface: "chat",
          source_id: "chat-1",
          actor: "operator",
          tags: ["chat"],
          created_at: "2026-01-01T00:00:00Z",
          updated_at: "2026-01-01T00:00:00Z"
        }],
        count: memoryDeleted ? 0 : 1
      },
      events: [],
      guardian: { pending_confirmations: [], recent_confirmations: [] },
      chat: { sessions: [], sessions_count: 0, messages_count: 0 },
      roundtable: { sessions: [], sessions_count: 0, turns_count: 0, assignments_count: 0, summaries_count: 0 },
      dashboard: {
        rooms_count: 0,
        notes_count: 0,
        memory_count: memoryDeleted ? 0 : 1,
        events_count: 0,
        seat_count: 1,
        chat_sessions_count: 0,
        chat_messages_count: 0,
        roundtable_sessions_count: 0,
        roundtable_turns_count: 0,
        roundtable_assignments_count: 0,
        roundtable_summaries_count: 0,
        pending_confirmations: 0
      },
      storage: { type: "sqlite", path: "local-workstation-store" }
    });

    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/api/workstation/state")) {
        return new Response(JSON.stringify(workstationState()), { status: 200, headers: { "Content-Type": "application/json" } });
      }
      if (url.includes("/api/chat/sessions")) {
        return new Response(JSON.stringify({ sessions: [], count: 0 }), { status: 200, headers: { "Content-Type": "application/json" } });
      }
      if (url.includes("/api/guardian/actions/confirmations/conf-1/decision")) {
        return new Response(JSON.stringify({ id: "conf-1", action_type: "memory.delete", status: "approved" }), { status: 200, headers: { "Content-Type": "application/json" } });
      }
      if (url.includes("/api/guardian/actions/confirmations")) {
        return new Response(JSON.stringify({ id: "conf-1", action_type: "memory.delete", status: "pending" }), { status: 201, headers: { "Content-Type": "application/json" } });
      }
      if (url.includes("/api/memory/mem-1")) {
        memoryDeleted = true;
        return new Response(JSON.stringify({ deleted: "mem-1" }), { status: 200, headers: { "Content-Type": "application/json" } });
      }
      return new Response(JSON.stringify({ detail: "unexpected request" }), { status: 500, headers: { "Content-Type": "application/json" } });
    });
    vi.stubGlobal("fetch", fetchMock);

    try {
      render(<ChatWorkstation />);

      expect(await screen.findByText(/Visible shared memory/)).toBeDefined();
      expect(screen.queryByText(/raw-ui-secret/)).toBeNull();

      fireEvent.click(screen.getByRole("button", { name: "Delete" }));
      fireEvent.click(await screen.findByRole("button", { name: "Confirm delete" }));

      await waitFor(() => expect(screen.queryByText(/Visible shared memory/)).toBeNull());
      expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/api/guardian/actions/confirmations"), expect.objectContaining({ method: "POST" }));
      expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/api/guardian/actions/confirmations/conf-1/decision"), expect.objectContaining({ method: "POST" }));
      expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/api/memory/mem-1?confirmation_id=conf-1"), expect.objectContaining({ method: "DELETE" }));
      expect(storageSpy).not.toHaveBeenCalled();
    } finally {
      storageSpy.mockRestore();
      vi.unstubAllGlobals();
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
    expect(screen.getAllByRole("button", { name: "Save invite" }).length).toBeGreaterThan(0);
    expect(screen.getAllByRole("button", { name: "Assign invited agent" }).length).toBeGreaterThan(0);
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
