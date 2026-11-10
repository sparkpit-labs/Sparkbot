import { localJsonRequest } from "../localWorkstation/localRequests";

// Owner requests carry this header. A browser only sends it from an allowed
// origin after a CORS check, so other web pages cannot drive the room.
const OWNER_HEADERS = { "X-Sparkbot-Local": "1" };

export type RoundtableRoom = {
  id: string;
  name: string;
  paused: boolean;
  seat_count: number;
  created_at: string;
  updated_at: string;
};

export type RoundtablePresence = "online" | "working" | "offline";

export type RoundtableSeat = {
  id: string;
  room_id: string;
  slug: string;
  display_name: string;
  created_at: string;
  last_seen_at: string | null;
  pending_jobs: number;
  working_note: string | null;
  presence: RoundtablePresence;
};

export type NewRoundtableSeat = RoundtableSeat & { key: string };

export type RoundtableMessage = {
  seq: number;
  id: string;
  room_id: string;
  sender_kind: "owner" | "agent" | "system";
  seat_id: string | null;
  sender_name: string;
  content: string;
  reply_to_id: string | null;
  created_at: string;
};

function owner<T>(path: string, options: RequestInit = {}): Promise<T> {
  return localJsonRequest<T>(path, { ...options, headers: { ...OWNER_HEADERS, ...options.headers } });
}

export async function listRooms(): Promise<RoundtableRoom[]> {
  const payload = await owner<{ rooms?: unknown }>("/roundtable/rooms");
  if (!Array.isArray(payload?.rooms)) {
    throw new Error("Round Table rooms response is invalid");
  }
  return payload.rooms as RoundtableRoom[];
}

export function createRoom(name: string): Promise<RoundtableRoom> {
  return owner<RoundtableRoom>("/roundtable/rooms", { method: "POST", body: JSON.stringify({ name }) });
}

export async function deleteRoom(roomId: string): Promise<void> {
  await owner<void>(`/roundtable/rooms/${roomId}`, { method: "DELETE" });
}

export async function getRoom(roomId: string): Promise<RoundtableRoom & { seats: RoundtableSeat[] }> {
  const room = await owner<RoundtableRoom & { seats?: unknown }>(`/roundtable/rooms/${roomId}`);
  if (!Array.isArray(room?.seats)) {
    throw new Error("Round Table room response is invalid");
  }
  return room as RoundtableRoom & { seats: RoundtableSeat[] };
}

export async function listMessages(roomId: string, after = 0): Promise<RoundtableMessage[]> {
  const query = after > 0 ? `?after=${after}` : "";
  const payload = await owner<{ messages?: unknown }>(`/roundtable/rooms/${roomId}/messages${query}`);
  if (!Array.isArray(payload?.messages)) {
    throw new Error("Round Table messages response is invalid");
  }
  return payload.messages as RoundtableMessage[];
}

export function postMessage(roomId: string, content: string): Promise<RoundtableMessage> {
  return owner<RoundtableMessage>(`/roundtable/rooms/${roomId}/messages`, {
    method: "POST",
    body: JSON.stringify({ content, sender_name: "You" })
  });
}

export function setPaused(roomId: string, paused: boolean): Promise<RoundtableRoom> {
  return owner<RoundtableRoom>(`/roundtable/rooms/${roomId}/pause`, { method: "POST", body: JSON.stringify({ paused }) });
}

export function createSeat(roomId: string, displayName: string, slug: string): Promise<NewRoundtableSeat> {
  return owner<NewRoundtableSeat>(`/roundtable/rooms/${roomId}/seats`, {
    method: "POST",
    body: JSON.stringify({ display_name: displayName, slug })
  });
}

export function rotateSeatKey(roomId: string, seatId: string): Promise<NewRoundtableSeat> {
  return owner<NewRoundtableSeat>(`/roundtable/rooms/${roomId}/seats/${seatId}/rotate`, { method: "POST" });
}

export async function deleteSeat(roomId: string, seatId: string): Promise<void> {
  await owner<void>(`/roundtable/rooms/${roomId}/seats/${seatId}`, { method: "DELETE" });
}

export function suggestSlug(name: string): string {
  const slug = name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 31);
  return slug.length >= 2 ? slug : "agent";
}

export type AgentKind = "claude" | "codex" | "other";

export function agentCommands(slug: string, agent: AgentKind, desktopCommand?: string): string[] {
  const script = desktopCommand || "python tools/sparkbot-roundtable.py";
  const url = desktopCommand ? " --url http://127.0.0.1:18765" : "";
  const login = `${script} login --profile ${slug}${url}`;
  if (agent === "other") {
    return [login, `${script} mcp --profile ${slug}`];
  }
  return [login, `${script} run --profile ${slug} --agent ${agent}`];
}

export function formatTime(iso: string): string {
  const when = new Date(iso);
  if (Number.isNaN(when.getTime())) {
    return "";
  }
  // Stored in UTC; shown in the viewer's own time zone.
  return when.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
}
