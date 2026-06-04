import { FormEvent, useEffect, useState } from "react";

import RoundTableRoom from "./RoundTableRoom";

import {
  createNote,
  createRoom,
  fetchWorkstationState,
  type WorkstationState
} from "../api";

type LoadState = "loading" | "ready" | "error";

function routeText(provider: string, model: string): string {
  const cleanProvider = provider && provider !== "default" ? provider : "default stack";
  return model ? `${cleanProvider} / ${model}` : cleanProvider;
}

export default function WorkstationFloor() {
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [workstation, setWorkstation] = useState<WorkstationState | null>(null);
  const [roomDraft, setRoomDraft] = useState({ title: "Planning Room", goal: "" });
  const [noteDraft, setNoteDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("Loading Workstation floor from shared state...");
  const [error, setError] = useState<string | null>(null);

  async function loadData() {
    setLoadState("loading");
    setError(null);
    try {
      const state = await fetchWorkstationState();
      setWorkstation(state);
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

      <section className="command-grid" aria-label="Shared context and activity">
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
            {(workstation?.memory.items || []).slice(0, 4).map((memory) => (
              <p key={memory.id}><strong>{memory.memory_type}</strong> {memory.content}</p>
            ))}
            {(workstation?.notes || []).slice(0, 4).map((note) => (
              <p key={note.id}><strong>{note.title}</strong> {note.body}</p>
            ))}
          </div>
        </article>

        <article className="command-panel">
          <div className="command-panel-heading">
            <p className="eyebrow">Activity</p>
            <h3>Events and Guardian</h3>
            <p>Recent Spine entries and pending confirmations stay visible before any action-capable feature is added.</p>
          </div>
          <div className="context-list">
            {(workstation?.guardian.pending_confirmations || []).slice(0, 4).map((confirmation) => (
              <p key={confirmation.id}><strong>{confirmation.action_type}</strong> {confirmation.status}: {confirmation.prompt}</p>
            ))}
            {(workstation?.events || []).slice(0, 6).map((event) => (
              <p key={event.id}><strong>{event.event_type}</strong> {event.summary}</p>
            ))}
            {workstation?.events.length || workstation?.guardian.pending_confirmations.length ? null : <p>No recent activity yet.</p>}
          </div>
        </article>
      </section>
    </section>
  );
}
