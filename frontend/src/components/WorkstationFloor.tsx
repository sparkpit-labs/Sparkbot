import { FormEvent, useEffect, useState } from "react";

import RoundTableRoom from "./RoundTableRoom";

import {
  createNote,
  createRoom,
  fetchWorkstationHistory,
  fetchWorkstationState,
  updateNote,
  type WorkstationHistory,
  type WorkstationNote,
  type WorkstationState
} from "../api";

type LoadState = "loading" | "ready" | "error";

type NoteEditDraft = {
  id: string;
  title: string;
  body: string;
};

function routeText(provider: string, model: string): string {
  const cleanProvider = provider && provider !== "default" ? provider : "default stack";
  return model ? `${cleanProvider} / ${model}` : cleanProvider;
}

function shortId(value: string): string {
  return value ? value.slice(0, 8) : "shared";
}

function sourceLabel(note: WorkstationNote): string {
  if (note.surface === "roundtable") return `Round Table ${shortId(note.source_id)}`;
  if (note.surface === "chat") return `Chat ${shortId(note.source_id)}`;
  if (note.surface === "room") return `Room ${shortId(note.source_id)}`;
  return note.surface || "workstation";
}

export default function WorkstationFloor() {
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [workstation, setWorkstation] = useState<WorkstationState | null>(null);
  const [history, setHistory] = useState<WorkstationHistory | null>(null);
  const [roomDraft, setRoomDraft] = useState({ title: "Planning Room", goal: "" });
  const [noteDraft, setNoteDraft] = useState("");
  const [noteEdit, setNoteEdit] = useState<NoteEditDraft | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("Loading Workstation floor from shared state...");
  const [error, setError] = useState<string | null>(null);

  async function loadData() {
    setLoadState("loading");
    setError(null);
    try {
      const [state, historyState] = await Promise.all([fetchWorkstationState(), fetchWorkstationHistory(25)]);
      setWorkstation(state);
      setHistory(historyState);
      setLoadState("ready");
      setMessage("Workstation floor synced with the shared backend store.");
    } catch (caught) {
      setLoadState("error");
      setError(caught instanceof Error ? caught.message : "Workstation backend is unavailable.");
      setMessage("Start the local backend to inspect rooms, seats, memory, notes, events, and Guardian state.");
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  async function createRoomFoundation(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const title = roomDraft.title.trim() || "Planning Room";
    setBusy(true);
    setError(null);
    try {
      await createRoom({
        title,
        goal: roomDraft.goal.trim(),
        phase: "setup",
        status: "open",
        metadata: { source: "workstation" }
      });
      setRoomDraft({ title: "Planning Room", goal: "" });
      await loadData();
      setMessage("Room foundation created. No meeting engine or model turn loop was started.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Room could not be created.");
    } finally {
      setBusy(false);
    }
  }

  async function saveFloorNote() {
    const body = noteDraft.trim();
    if (!body) return;
    setBusy(true);
    setError(null);
    try {
      await createNote({
        title: "Workstation floor note",
        body,
        surface: "workstation",
        tags: ["workstation"]
      });
      setNoteDraft("");
      await loadData();
      setMessage("Workstation note saved to shared backend state.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Workstation note could not be saved.");
    } finally {
      setBusy(false);
    }
  }

  async function saveNoteEdit() {
    if (!noteEdit) return;
    const title = noteEdit.title.trim() || "Workstation note";
    const body = noteEdit.body.trim();
    if (!body) return;
    setBusy(true);
    setError(null);
    try {
      await updateNote(noteEdit.id, { title, body });
      setNoteEdit(null);
      await loadData();
      setMessage("Note updated in shared backend state.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Workstation note could not be updated.");
    } finally {
      setBusy(false);
    }
  }

  const notes = history?.notes || workstation?.notes || [];
  const roundtableSessions = history?.roundtable.sessions || workstation?.roundtable.sessions || [];
  const chatSessions = history?.chat.sessions || workstation?.chat.sessions || [];
  const recentEvents = history?.events || workstation?.events || [];

  return (
    <section className="workstation-floor" aria-label="Sparkbot Workstation floor">
      <header className="command-header">
        <div>
          <p className="eyebrow">Work floor</p>
          <h2>Workstation Floor</h2>
          <p>Company-style operating view for rooms, model seats, shared memory, notes, recent activity, and Guardian confirmation state.</p>
        </div>
        <div className="command-header-actions">
          <span className={`status-badge ${loadState === "ready" ? "status-worksToday" : loadState === "loading" ? "status-preview" : "status-notImplemented"}`}>
            {loadState === "ready" ? "Backend synced" : loadState === "loading" ? "Syncing" : "Backend needed"}
          </span>
          <button type="button" onClick={loadData} disabled={busy}>Refresh</button>
        </div>
      </header>

      <div className="command-message" role="status">
        <span>{message}</span>
        <span>Source of truth: shared local backend store</span>
      </div>
      {error ? <div className="command-error" role="alert">{error}</div> : null}

      <section className="command-grid" aria-label="Workstation counters">
        <article className="command-panel command-panel-wide">
          <div className="command-panel-heading">
            <p className="eyebrow">Floor state</p>
            <h3>Shared counters</h3>
            <p>These counters come from the same store used by Chat, Command Center, Spine, Controls, and Guardian confirmations.</p>
          </div>
          <dl className="mini-metrics">
            <div><dt>Rooms</dt><dd>{workstation?.dashboard.rooms_count ?? 0}</dd></div>
            <div><dt>Seats</dt><dd>{workstation?.dashboard.seat_count ?? 0}</dd></div>
            <div><dt>Memory</dt><dd>{workstation?.dashboard.memory_count ?? 0}</dd></div>
            <div><dt>Notes</dt><dd>{workstation?.dashboard.notes_count ?? 0}</dd></div>
            <div><dt>Events</dt><dd>{workstation?.dashboard.events_count ?? 0}</dd></div>
            <div><dt>Chat turns</dt><dd>{workstation?.dashboard.chat_messages_count ?? 0}</dd></div>
            <div><dt>Round Table</dt><dd>{workstation?.dashboard.roundtable_sessions_count ?? 0}</dd></div>
            <div><dt>Pending confirmations</dt><dd>{workstation?.dashboard.pending_confirmations ?? 0}</dd></div>
          </dl>
        </article>
      </section>

      <RoundTableRoom embedded />

      <section className="command-grid" aria-label="Rooms and seats">
        <article className="command-panel">
          <div className="command-panel-heading">
            <p className="eyebrow">Rooms</p>
            <h3>Room foundation</h3>
            <p>Rooms persist with participants and setup metadata. Round Table sessions now run from the shared Workstation store.</p>
          </div>
          <form className="field-grid" onSubmit={createRoomFoundation}>
            <label>
              <span>Room title</span>
              <input value={roomDraft.title} onChange={(event) => setRoomDraft((draft) => ({ ...draft, title: event.target.value }))} />
            </label>
            <label>
              <span>Goal</span>
              <textarea rows={3} value={roomDraft.goal} onChange={(event) => setRoomDraft((draft) => ({ ...draft, goal: event.target.value }))} />
            </label>
            <button type="submit" disabled={busy}>Create room foundation</button>
          </form>
          <div className="context-list">
            {(workstation?.rooms || []).slice(0, 5).map((room) => (
              <p key={room.id}><strong>{room.title}</strong> {room.phase} / {room.status}</p>
            ))}
            {workstation?.rooms.length ? null : <p>No rooms yet.</p>}
          </div>
        </article>

        <article className="command-panel">
          <div className="command-panel-heading">
            <p className="eyebrow">Seats</p>
            <h3>Model seats</h3>
            <p>Seat assignments are shared with Command Center and used by the Round Table flow.</p>
          </div>
          <div className="seat-grid">
            {(workstation?.seats || []).map((seat) => (
              <div className="seat-card" key={seat.seat_index}>
                <strong>{seat.label}</strong>
                <span>{seat.agent}</span>
                <span>{routeText(seat.provider, seat.model)}</span>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="command-grid" aria-label="Shared context and history">
        <article className="command-panel">
          <div className="command-panel-heading">
            <p className="eyebrow">Shared context</p>
            <h3>Memory and notes</h3>
            <p>Workstation notes and memory are persisted centrally, not in browser storage.</p>
          </div>
          <label>
            <span>Save Workstation note</span>
            <textarea rows={4} value={noteDraft} onChange={(event) => setNoteDraft(event.target.value)} />
          </label>
          <button type="button" onClick={saveFloorNote} disabled={busy || !noteDraft.trim()}>Save note</button>
          <div className="context-list">
            <h4>Recent memory</h4>
            {(workstation?.memory.items || []).slice(0, 4).map((memory) => (
              <p key={memory.id}><strong>{memory.memory_type}</strong> {memory.content}</p>
            ))}
            {workstation?.memory.items.length ? null : <p>No shared memory saved yet.</p>}
          </div>
          <div className="context-list">
            <h4>Notes and artifacts</h4>
            {notes.slice(0, 6).map((note) => {
              const editing = noteEdit?.id === note.id;
              return (
                <div className="note-list-item" key={note.id}>
                  {editing ? (
                    <div className="field-grid">
                      <label>
                        <span>Title</span>
                        <input value={noteEdit.title} onChange={(event) => setNoteEdit((draft) => draft ? { ...draft, title: event.target.value } : draft)} />
                      </label>
                      <label>
                        <span>Body</span>
                        <textarea rows={5} value={noteEdit.body} onChange={(event) => setNoteEdit((draft) => draft ? { ...draft, body: event.target.value } : draft)} />
                      </label>
                      <div className="note-edit-actions">
                        <button type="button" onClick={saveNoteEdit} disabled={busy || !noteEdit.body.trim()}>Save edit</button>
                        <button type="button" onClick={() => setNoteEdit(null)} disabled={busy}>Cancel</button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="note-list-top">
                        <strong>{note.title}</strong>
                        <span>{sourceLabel(note)}</span>
                      </div>
                      <p>{note.body}</p>
                      <div className="metadata-row">
                        <span>{note.tags.join(", ") || "untagged"}</span>
                        <span>Updated {new Date(note.updated_at).toLocaleString()}</span>
                      </div>
                      <button type="button" onClick={() => setNoteEdit({ id: note.id, title: note.title, body: note.body })} disabled={busy}>Edit note</button>
                    </>
                  )}
                </div>
              );
            })}
            {notes.length ? null : <p>No notes yet.</p>}
          </div>
        </article>

        <article className="command-panel">
          <div className="command-panel-heading">
            <p className="eyebrow">History</p>
            <h3>Session history</h3>
            <p>Chat and Round Table records reopen from the same backend store used by their dedicated pages.</p>
          </div>
          <div className="history-list">
            <h4>Round Table sessions</h4>
            {roundtableSessions.slice(0, 5).map((session) => (
              <div className="history-list-item" key={session.id}>
                <strong>{session.title}</strong>
                <span>{session.status} / {session.phase}</span>
                <span>{session.turn_count || session.turns?.length || 0} turn(s), {session.assignment_count || session.assignments?.length || 0} assignment(s)</span>
                {session.summaries?.[0]?.note_id ? <span>Wrap-up note {shortId(session.summaries[0].note_id)}</span> : <span>No wrap-up note yet</span>}
                <a href="/roundtable">Open Round Table</a>
              </div>
            ))}
            {roundtableSessions.length ? null : <p>No Round Table history yet.</p>}
          </div>
          <div className="history-list">
            <h4>Chat sessions</h4>
            {chatSessions.slice(0, 5).map((session) => (
              <div className="history-list-item" key={session.id}>
                <strong>{session.title}</strong>
                <span>{session.message_count || 0} message(s)</span>
                <span>{session.last_message ? `${session.last_message.role}: ${session.last_message.content}` : "No messages yet"}</span>
                <a href="/chat">Open Chat</a>
              </div>
            ))}
            {chatSessions.length ? null : <p>No Chat history yet.</p>}
          </div>
        </article>
      </section>

      <section className="command-grid" aria-label="Activity and Guardian">
        <article className="command-panel command-panel-wide">
          <div className="command-panel-heading">
            <p className="eyebrow">Activity</p>
            <h3>Spine events and Guardian</h3>
            <p>Recent events show safe metadata from provider/model calls, memory, notes, rooms, sessions, and Guardian blocks. Prompts, model outputs, headers, credentials, and secrets are not displayed.</p>
          </div>
          <div className="event-list-grid">
            {(workstation?.guardian.pending_confirmations || []).slice(0, 4).map((confirmation) => (
              <div className="event-list-item" key={confirmation.id}>
                <strong>{confirmation.action_type}</strong>
                <span>{confirmation.status}: {confirmation.prompt}</span>
                <span>{confirmation.surface}:{shortId(confirmation.source_id)}</span>
              </div>
            ))}
            {recentEvents.slice(0, 10).map((event) => (
              <div className="event-list-item" key={event.id}>
                <strong>{event.event_type}</strong>
                <span>{event.summary}</span>
                <span>{event.surface}:{shortId(event.source_id)}</span>
              </div>
            ))}
            {recentEvents.length || workstation?.guardian.pending_confirmations.length ? null : <p>No recent activity yet.</p>}
          </div>
        </article>
      </section>
    </section>
  );
}
