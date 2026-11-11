import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { agentCommands, suggestSlug } from "../roundtable/roundtableApi";
import RoundTableRoom from "./RoundTableRoom";

type Call = { url: string; method: string; body: unknown; headers: Record<string, string> };

function fakeBackend(jobs: Record<string, unknown>[] = []) {
  const calls: Call[] = [];
  const room = { id: "r1", name: "Planning", paused: false, seat_count: 0, created_at: "", updated_at: "" };
  const seats: Record<string, unknown>[] = [];
  const messages: Record<string, unknown>[] = [];
  const json = (data: unknown, status = 200) =>
    new Response(JSON.stringify(data), { status, headers: { "Content-Type": "application/json" } });

  const fetchMock = vi.fn(async (input: string, init: RequestInit = {}) => {
    const url = new URL(String(input));
    const method = init.method ?? "GET";
    const body = init.body ? JSON.parse(String(init.body)) : undefined;
    calls.push({ url: url.pathname + url.search, method, body, headers: (init.headers ?? {}) as Record<string, string> });
    const path = url.pathname;
    if (path === "/roundtable/rooms" && method === "GET") return json({ rooms: [room] });
    if (path === "/roundtable/rooms/r1" && method === "GET") return json({ ...room, seats, jobs });
    if (path === "/roundtable/rooms/r1/messages" && method === "GET") {
      const after = Number(url.searchParams.get("after") ?? 0);
      return json({ messages: messages.filter((m) => Number(m.seq) > after) });
    }
    if (path === "/roundtable/rooms/r1/messages" && method === "POST") {
      const message = {
        seq: messages.length + 1,
        id: `m${messages.length + 1}`,
        room_id: "r1",
        sender_kind: "owner",
        seat_id: null,
        sender_name: "You",
        content: (body as { content: string }).content,
        reply_to_id: null,
        created_at: "2026-11-09T15:04:00Z"
      };
      messages.push(message);
      return json(message, 201);
    }
    if (path === "/roundtable/rooms/r1/seats" && method === "POST") {
      const { display_name, slug } = body as { display_name: string; slug: string };
      const seat = { id: "s1", room_id: "r1", slug, display_name, created_at: "", last_seen_at: null, pending_jobs: 0, working_note: null, presence: "offline" };
      seats.push(seat);
      return json({ ...seat, key: "rts_s1_onetimekey" }, 201);
    }
    return json({ detail: "not found" }, 404);
  });
  vi.stubGlobal("fetch", fetchMock);
  return { calls, messages };
}

describe("RoundTableRoom", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("sends owner messages with the local owner header", async () => {
    const backend = fakeBackend();
    render(<RoundTableRoom />);

    const composer = (await screen.findByLabelText("Message the room")) as HTMLTextAreaElement;
    fireEvent.change(composer, { target: { value: "@claude what's next?" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));

    expect(await screen.findByText("@claude what's next?")).toBeDefined();
    const post = backend.calls.find((c) => c.method === "POST" && c.url.endsWith("/messages"));
    expect(post?.body).toEqual({ content: "@claude what's next?", sender_name: "You" });
    expect(backend.calls.every((c) => c.headers["X-Sparkbot-Local"] === "1")).toBe(true);
  });

  it("adds an agent and shows its one-time key with copy-paste commands", async () => {
    fakeBackend();
    render(<RoundTableRoom />);

    fireEvent.change(await screen.findByLabelText("Name in the room"), { target: { value: "Claude" } });
    fireEvent.click(screen.getByRole("button", { name: "Add agent" }));

    expect(await screen.findByText("rts_s1_onetimekey")).toBeDefined();
    expect(screen.getByText("python tools/sparkbot-roundtable.py login --profile claude")).toBeDefined();
    expect(screen.getByText("python tools/sparkbot-roundtable.py run --profile claude --agent claude")).toBeDefined();
    await waitFor(() => expect(screen.getByRole("button", { name: "Remove Claude" })).toBeDefined());

    fireEvent.click(screen.getByRole("button", { name: "Done, hide the key" }));
    expect(screen.queryByText("rts_s1_onetimekey")).toBeNull();
  });

  it("explains what to do when the backend is not running", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
    render(<RoundTableRoom />);
    expect(await screen.findByText(/Round Table needs the local backend/i)).toBeDefined();
  });
});

describe("roundtable helpers", () => {
  it("makes valid handles and commands", () => {
    expect(suggestSlug("Claude Code")).toBe("claude-code");
    expect(suggestSlug("!")).toBe("agent");
    expect(agentCommands("codex", "codex")[1]).toBe("python tools/sparkbot-roundtable.py run --profile codex --agent codex");
    expect(agentCommands("helper", "other")[1]).toBe("python tools/sparkbot-roundtable.py mcp --profile helper");
  });
});

it("shows failed job status and recovery instructions independently of messages", async () => {
  fakeBackend([{id: "j1", trigger_message_id: "m1", status: "failed", display_name: "Claude", reason: "Agent CLI not found. Install it and restart the runner."}]);
  render(<RoundTableRoom />);
  await screen.findByText("Claude: failed");
  expect(screen.getByText(/Agent CLI not found/)).toBeTruthy();
});
