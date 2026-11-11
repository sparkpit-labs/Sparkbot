import { FormEvent, KeyboardEvent, useCallback, useEffect, useRef, useState } from "react";
import { desktopConnectorCommand } from "../desktop";

import {
  agentCommands,
  createRoom,
  createSeat,
  deleteSeat,
  formatTime,
  getRoom,
  listMessages,
  listRooms,
  postMessage,
  setPaused,
  suggestSlug,
  type AgentKind,
  type NewRoundtableSeat,
  type RoundtableMessage,
  type RoundtableRoom,
  type RoundtableSeat
} from "../roundtable/roundtableApi";

const POLL_MS = 3000;

type Invite = { seat: NewRoundtableSeat; agent: AgentKind };

const agentLabels: Record<AgentKind, string> = {
  claude: "Claude Code",
  codex: "Codex",
  other: "Other (MCP)"
};

const presenceLabels: Record<RoundtableSeat["presence"], string> = {
  online: "Listening",
  working: "Working",
  offline: "Not running"
};

export default function RoundTableRoom() {
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);
  const [rooms, setRooms] = useState<RoundtableRoom[]>([]);
  const [roomId, setRoomId] = useState<string | null>(null);
  const [room, setRoom] = useState<RoundtableRoom | null>(null);
  const [seats, setSeats] = useState<RoundtableSeat[]>([]);
  const [messages, setMessages] = useState<RoundtableMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [newRoomName, setNewRoomName] = useState("");
  const [agentName, setAgentName] = useState("");
  const [agentKind, setAgentKind] = useState<AgentKind>("claude");
  const [invite, setInvite] = useState<Invite | null>(null);
  const [notice, setNotice] = useState("");
  const [connectorCommand, setConnectorCommand] = useState<string>();
  const lastSeq = useRef(0);
  const listRef = useRef<HTMLOListElement>(null);

  const loadRooms = useCallback(async () => {
    try {
      const next = await listRooms();
      setRooms(next);
      setBackendOnline(true);
      setRoomId((current) => (current && next.some((r) => r.id === current) ? current : (next[0]?.id ?? null)));
    } catch {
      setBackendOnline(false);
    }
  }, []);

  useEffect(() => {
    void loadRooms();
    void desktopConnectorCommand().then(setConnectorCommand).catch(() => setNotice("Could not locate the installed agent connector. Restart Sparkbot and try again."));
  }, [loadRooms]);

  const refresh = useCallback(async () => {
    if (!roomId) return;
    try {
      const [detail, fresh] = await Promise.all([getRoom(roomId), listMessages(roomId, lastSeq.current)]);
      setRoom(detail);
      setSeats(detail.seats);
      if (fresh.length) {
        lastSeq.current = fresh[fresh.length - 1].seq;
        setMessages((current) => [...current, ...fresh.filter((m) => !current.some((c) => c.id === m.id))]);
      }
      setBackendOnline(true);
    } catch {
      setBackendOnline(false);
    }
  }, [roomId]);

  useEffect(() => {
    lastSeq.current = 0;
    setMessages([]);
    setInvite(null);
    void refresh();
    if (!roomId) return undefined;
    const timer = window.setInterval(() => void refresh(), POLL_MS);
    return () => window.clearInterval(timer);
  }, [roomId, refresh]);

  useEffect(() => {
    const list = listRef.current;
    if (list) list.scrollTop = list.scrollHeight;
  }, [messages.length]);

  const addRoom = async (event: FormEvent) => {
    event.preventDefault();
    const name = newRoomName.trim() || "Roundtable";
    try {
      const created = await createRoom(name);
      setNewRoomName("");
      await loadRooms();
      setRoomId(created.id);
    } catch {
      setNotice("Could not create the room.");
    }
  };

  const send = async () => {
    const content = draft.trim();
    if (!roomId || !content) return;
    try {
      await postMessage(roomId, content);
      setDraft("");
      await refresh();
    } catch {
      setNotice("Message not sent. Is the backend running?");
    }
  };

  const onComposerKey = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void send();
    }
  };

  const addAgent = async (event: FormEvent) => {
    event.preventDefault();
    if (!roomId) return;
    const name = agentName.trim() || agentLabels[agentKind].split(" ")[0];
    const base = suggestSlug(name);
    const taken = new Set(seats.map((s) => s.slug));
    let slug = base;
    for (let n = 2; taken.has(slug); n += 1) slug = `${base.slice(0, 28)}-${n}`;
    try {
      const seat = await createSeat(roomId, name, slug);
      setInvite({ seat, agent: agentKind });
      setAgentName("");
      await refresh();
    } catch {
      setNotice("Could not add the agent.");
    }
  };

  const removeSeat = async (seat: RoundtableSeat) => {
    if (!roomId) return;
    try {
      await deleteSeat(roomId, seat.id);
      if (invite?.seat.id === seat.id) setInvite(null);
      await refresh();
    } catch {
      setNotice("Could not remove the agent.");
    }
  };

  const togglePause = async () => {
    if (!roomId || !room) return;
    try {
      setRoom(await setPaused(roomId, !room.paused));
      await refresh();
    } catch {
      setNotice("Could not change the pause state.");
    }
  };

  const copy = (text: string) => {
    void navigator.clipboard?.writeText(text).then(
      () => setNotice("Copied."),
      () => setNotice("Copy failed; select the text and copy it.")
    );
  };

  return (
    <section className="round-table-room section-panel" id="round-table" aria-labelledby="round-table-heading">
      <div className="round-table-copy">
        <p className="eyebrow">Local rooms</p>
        <h2 id="round-table-heading">Round Table Rooms</h2>
        <p>
          A room where you and AI agents on this computer work together. Add an agent, start its runner, then ask it
          something with <code>@name</code> (or <code>@all</code>). Sparkbot makes no model calls: each agent answers
          with its own CLI and sign-in, on this computer, with no tools.
        </p>
      </div>

      {backendOnline === false ? (
        <p className="round-table-note" role="status">
          Round Table needs the local backend. Start it and this panel will load.
        </p>
      ) : null}

      <div className="round-table-rooms" aria-label="Rooms">
        {rooms.map((r) => (
          <button
            type="button"
            key={r.id}
            className={r.id === roomId ? "room-chip active" : "room-chip"}
            aria-pressed={r.id === roomId}
            onClick={() => setRoomId(r.id)}
          >
            {r.name}
          </button>
        ))}
        <form className="inline-form" onSubmit={addRoom}>
          <label className="visually-hidden" htmlFor="new-room-name">
            New room name
          </label>
          <input
            id="new-room-name"
            value={newRoomName}
            maxLength={120}
            placeholder="New room name"
            onChange={(e) => setNewRoomName(e.target.value)}
          />
          <button type="submit" disabled={backendOnline === false}>
            New room
          </button>
        </form>
      </div>

      {roomId && room ? (
        <div className="round-table-workspace">
          <div className="round-table-conversation">
            {room.paused ? (
              <p className="round-table-paused" role="status">
                Paused. Agents get no new work until you resume.
              </p>
            ) : null}
            <ol className="round-table-messages" aria-label="Room messages" ref={listRef}>
              {messages.length === 0 ? <li className="round-table-empty">No messages yet.</li> : null}
              {messages.map((m) => (
                <li key={m.id} className={`round-table-message from-${m.sender_kind}`}>
                  <div className="round-table-message-meta">
                    <strong>{m.sender_name}</strong>
                    {m.sender_kind !== "owner" ? <span>{m.sender_kind === "agent" ? "agent" : "notice"}</span> : null}
                    <time dateTime={m.created_at}>{formatTime(m.created_at)}</time>
                  </div>
                  <p>{m.content}</p>
                </li>
              ))}
            </ol>
            {(room.jobs || []).some((job) => job.status !== "done") ? (
              <section aria-label="Agent activity" aria-live="polite">
                <h3>Agent activity</h3>
                {(room.jobs || []).filter((job) => job.status !== "done").map((job) => (
                  <p key={job.id}><strong>{job.display_name}: {job.status === "claimed" ? "working" : job.status}</strong>{job.reason ? ` â€” ${job.reason}` : ""}</p>
                ))}
              </section>
            ) : null}
            <div className="round-table-composer">
              <label htmlFor="round-table-draft">Message the room</label>
              <textarea
                id="round-table-draft"
                rows={3}
                maxLength={8000}
                value={draft}
                placeholder="@claude what should we build next?  (Enter sends, Shift+Enter for a new line)"
                onChange={(e) => setDraft(e.target.value)}
                onKeyDown={onComposerKey}
              />
              <button type="button" onClick={() => void send()} disabled={!draft.trim()}>
                Send
              </button>
            </div>
          </div>

          <aside className="round-table-people" aria-label="People in this room">
            <div className="round-table-people-head">
              <h3>People</h3>
              <button type="button" onClick={() => void togglePause()}>
                {room.paused ? "Resume" : "Pause"}
              </button>
            </div>
            <ul>
              <li className="round-table-person">
                <span className="presence presence-online" aria-hidden="true" />
                <span>You (owner)</span>
              </li>
              {seats.map((seat) => (
                <li key={seat.id} className="round-table-person">
                  <span className={`presence presence-${seat.presence}`} aria-hidden="true" />
                  <span>
                    {seat.display_name} <code>@{seat.slug}</code>
                    <small>
                      {presenceLabels[seat.presence]}
                      {seat.working_note ? `: ${seat.working_note}` : ""}
                    </small>
                  </span>
                  <button
                    type="button"
                    className="link-button"
                    aria-label={`Remove ${seat.display_name}`}
                    onClick={() => void removeSeat(seat)}
                  >
                    Remove
                  </button>
                </li>
              ))}
            </ul>

            <form className="round-table-add" onSubmit={addAgent}>
              <h3>Add an AI agent</h3>
              <label htmlFor="agent-kind">Agent</label>
              <select id="agent-kind" value={agentKind} onChange={(e) => setAgentKind(e.target.value as AgentKind)}>
                {(Object.keys(agentLabels) as AgentKind[]).map((kind) => (
                  <option key={kind} value={kind}>
                    {agentLabels[kind]}
                  </option>
                ))}
              </select>
              <label htmlFor="agent-name">Name in the room</label>
              <input
                id="agent-name"
                value={agentName}
                maxLength={60}
                placeholder={agentLabels[agentKind].split(" ")[0]}
                onChange={(e) => setAgentName(e.target.value)}
              />
              <button type="submit">Add agent</button>
            </form>

            {invite ? (
              <div className="round-table-invite" role="status">
                <h3>Start {invite.seat.display_name}</h3>
                <p>
                  This seat key is shown once. {connectorCommand ? "Run these in PowerShell" : "Run these from the Sparkbot folder in a terminal"}; paste the key when the first one asks for it.
                </p>
                <div className="copy-row">
                  <code className="seat-key">{invite.seat.key}</code>
                  <button type="button" onClick={() => copy(invite.seat.key)}>
                    Copy key
                  </button>
                </div>
                {(import.meta.env.VITE_SPARKBOT_DESKTOP === "true" && !connectorCommand ? [] : agentCommands(invite.seat.slug, invite.agent, connectorCommand)).map((command) => (
                  <div className="copy-row" key={command}>
                    <code>{command}</code>
                    <button type="button" onClick={() => copy(command)}>
                      Copy
                    </button>
                  </div>
                ))}
                {invite.agent === "other" ? (
                  <p>Add the second command to your agent as an MCP server so it can read and post in this room.</p>
                ) : (
                  <p>
                    Leave the second command running. Ask with <code>@{invite.seat.slug}</code>; Ctrl+C stops it.
                  </p>
                )}
                <button type="button" className="link-button" onClick={() => setInvite(null)}>
                  Done, hide the key
                </button>
              </div>
            ) : null}
          </aside>
        </div>
      ) : backendOnline ? (
        <p className="round-table-note">Create a room to start.</p>
      ) : null}

      {notice ? (
        <p className="round-table-note" role="status">
          {notice}
        </p>
      ) : null}
    </section>
  );
}
