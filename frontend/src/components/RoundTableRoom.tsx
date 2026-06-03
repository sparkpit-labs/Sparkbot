
import { FormEvent, useEffect, useMemo, useState } from "react";

import {
  createRoundTableSession,
  fetchRoundTableSession,
  fetchWorkstationState,
  runRoundTableSession,
  type RoundTableSession,
  type RoundTableTurn,
  type WorkstationState
} from "../api";

type LoadState = "loading" | "ready" | "error";

type Props = {
  embedded?: boolean;
};

const phaseLabels: Record<string, string> = {
  first_pass: "First pass",
  manager_assessment: "Manager assessment",
  second_pass: "Second pass",
  manager_summary: "Manager summary"
};

function turnsFor(session: RoundTableSession | null, phase: string): RoundTableTurn[] {
  return (session?.turns || []).filter((turn) => turn.phase === phase);
}

function seatLabel(seatIndex: number | null | undefined): string {
  return seatIndex ? `Seat ${seatIndex}` : "Seat";
}

function statusCopy(session: RoundTableSession | null): string {
  if (!session) return "Create or select a session to begin.";
  if (session.status === "blocked") return "Blocked by Guardian boundary";
  if (session.status === "complete") return "Provider-safe meeting complete";
  if (session.status === "running") return "Provider-safe meeting running";
  return "Ready for provider-safe meeting flow";
}

export default function RoundTableRoom({ embedded = false }: Props) {
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [workstation, setWorkstation] = useState<WorkstationState | null>(null);
  const [activeSession, setActiveSession] = useState<RoundTableSession | null>(null);
  const [draft, setDraft] = useState({ title: "Round Table Planning Room", goal: "" });
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("Loading Round Table room from shared Workstation state...");
  const [error, setError] = useState<string | null>(null);

  const manager = useMemo(
    () => (activeSession?.participants || workstation?.seats || []).find((seat) => seat.seat_index === 1),
    [activeSession, workstation]
  );

  async function loadData(sessionId?: string) {
    setLoadState("loading");
    setError(null);
    try {
      const state = await fetchWorkstationState();
      setWorkstation(state);
      const nextSessionId = sessionId || activeSession?.id || state.roundtable.sessions[0]?.id || "";
      const nextSession = nextSessionId ? await fetchRoundTableSession(nextSessionId) : null;
      setActiveSession(nextSession);
      setLoadState("ready");
      setMessage("Round Table room synced with shared backend state.");
    } catch (caught) {
      setLoadState("error");
      setError(caught instanceof Error ? caught.message : "Round Table backend state is unavailable.");
      setMessage("Start the local backend to inspect provider-safe Round Table sessions.");
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  async function createSession(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const title = draft.title.trim() || "Round Table Planning Room";
    const goal = draft.goal.trim();
    setBusy(true);
    setError(null);
    try {
      const session = await createRoundTableSession({
        title,
        goal,
        context_query: goal || title,
        metadata: { surface: "workstation_roundtable", mode: "provider_safe" }
      });
      setDraft({ title: "Round Table Planning Room", goal: "" });
      setActiveSession(session);
      await loadData(session.id);
      setMessage("Round Table session created in the shared Workstation store.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Round Table session could not be created.");
    } finally {
      setBusy(false);
    }
  }

  async function selectSession(sessionId: string) {
    setBusy(true);
    setError(null);
    try {
      const session = await fetchRoundTableSession(sessionId);
      setActiveSession(session);
      setMessage("Round Table session loaded from shared backend state.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Round Table session could not be loaded.");
    } finally {
      setBusy(false);
    }
  }

  async function runSession() {
    if (!activeSession) return;
    setBusy(true);
    setError(null);
    try {
      const session = await runRoundTableSession(activeSession.id);
      setActiveSession(session);
      await loadData(session.id);
      setMessage(session.status === "blocked" ? "Round Table request was blocked by Guardian boundaries." : "Provider-safe Round Table flow completed and saved a manager summary note.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Round Table session could not be run.");
    } finally {
      setBusy(false);
    }
  }

  const firstPass = turnsFor(activeSession, "first_pass");
  const assessment = turnsFor(activeSession, "manager_assessment");
  const secondPass = turnsFor(activeSession, "second_pass");
  const managerSummary = turnsFor(activeSession, "manager_summary");
  const canRun = Boolean(activeSession && !busy && activeSession.status !== "complete" && activeSession.status !== "blocked");

  return (
    <section className={embedded ? "roundtable-room roundtable-room-embedded" : "roundtable-room"} aria-label="Sparkbot Round Table room">
      <header className="command-header">
        <div>
          <p className="eyebrow">Workstation room</p>
          <h2>Round Table Room</h2>
          <p>Backend-backed meeting room for seats, shared context, provider-safe turns, assignments, manager wrap-up, notes, and Spine events.</p>
        </div>
        <div className="command-header-actions">
          <span className={`status-badge ${loadState === "ready" ? "status-preview" : loadState === "loading" ? "status-preview" : "status-notImplemented"}`}>
            {loadState === "ready" ? "Provider-safe" : loadState === "loading" ? "Syncing" : "Backend needed"}
          </span>
          <button type="button" onClick={() => loadData()} disabled={busy}>Refresh</button>
        </div>
      </header>

      <div className="command-message" role="status">
        <span>{message}</span>
        <span>{statusCopy(activeSession)}</span>
      </div>
      {error ? <div className="command-error" role="alert">{error}</div> : null}
      {activeSession?.blocked_action ? <div className="command-error" role="alert">Guardian blocked action type: {activeSession.blocked_action}</div> : null}

      <section className="command-grid" aria-label="Round Table counters">
        <article className="command-panel command-panel-wide">
          <div className="command-panel-heading">
            <p className="eyebrow">Shared state</p>
            <h3>Round Table counters</h3>
            <p>Sessions, turns, assignments, summaries, and wrap-up notes are persisted in the same local store as Chat, Workstation, Guardian, and Spine.</p>
          </div>
          <dl className="mini-metrics">
            <div><dt>Sessions</dt><dd>{workstation?.roundtable.sessions_count ?? 0}</dd></div>
            <div><dt>Turns</dt><dd>{workstation?.roundtable.turns_count ?? 0}</dd></div>
            <div><dt>Assignments</dt><dd>{workstation?.roundtable.assignments_count ?? 0}</dd></div>
            <div><dt>Summaries</dt><dd>{workstation?.roundtable.summaries_count ?? 0}</dd></div>
            <div><dt>Memory</dt><dd>{workstation?.dashboard.memory_count ?? 0}</dd></div>
            <div><dt>Notes</dt><dd>{workstation?.dashboard.notes_count ?? 0}</dd></div>
          </dl>
        </article>
      </section>

      <section className="command-grid" aria-label="Round Table setup and seats">
        <article className="command-panel">
          <div className="command-panel-heading">
            <p className="eyebrow">Meeting setup</p>
            <h3>Create or select a session</h3>
            <p>Starting a session creates a shared room and participants from persisted Workstation seats. Running the flow uses deterministic local responses only.</p>
          </div>
          <form className="field-grid" onSubmit={createSession}>
            <label>
              <span>Session title</span>
              <input value={draft.title} onChange={(event) => setDraft((current) => ({ ...current, title: event.target.value }))} />
            </label>
            <label>
              <span>Problem or task</span>
              <textarea rows={4} value={draft.goal} onChange={(event) => setDraft((current) => ({ ...current, goal: event.target.value }))} />
            </label>
            <button type="submit" disabled={busy}>Create Round Table session</button>
          </form>
          <div className="chat-session-buttons roundtable-session-buttons" aria-label="Round Table sessions">
            {(workstation?.roundtable.sessions || []).slice(0, 6).map((session) => (
              <button
                type="button"
                className={`chat-session-button ${activeSession?.id === session.id ? "chat-session-button-active" : ""}`}
                key={session.id}
                onClick={() => selectSession(session.id)}
                disabled={busy}
              >
                <strong>{session.title}</strong>
                <span>{session.status} / {session.phase}</span>
              </button>
            ))}
            {workstation?.roundtable.sessions.length ? null : <p>No Round Table sessions yet.</p>}
          </div>
        </article>

        <article className="command-panel">
          <div className="command-panel-heading">
            <p className="eyebrow">Seats</p>
            <h3>Seat 1 Meeting Manager</h3>
            <p>Seat 1 manages the provider-safe flow. Other persisted seats contribute first-pass ideas and answer assigned second-pass work.</p>
          </div>
          <div className="seat-grid roundtable-seat-grid">
            {(activeSession?.participants || workstation?.seats || []).slice(0, 8).map((seat) => (
              <div className="seat-card" key={`${seat.seat_index}-${seat.agent}`}>
                <strong>{seat.seat_index === 1 ? "Seat 1 Meeting Manager" : seatLabel(seat.seat_index)}</strong>
                <span>{seat.agent}</span>
                <span>{seat.seat_index === 1 ? "manager" : "participant"}</span>
              </div>
            ))}
          </div>
          <button type="button" onClick={runSession} disabled={!canRun}>Run provider-safe meeting</button>
          <p className="helper-text">No provider calls, connector sends, scheduled jobs, files, processes, terminal commands, or device actions are executed in this branch.</p>
        </article>
      </section>

      <section className="command-grid" aria-label="Round Table meeting flow">
        <article className="command-panel command-panel-wide">
          <div className="command-panel-heading">
            <p className="eyebrow">Meeting flow</p>
            <h3>First pass, assignments, second pass, wrap-up</h3>
            <p>The flow is saved as turns, assignments, one manager summary, one wrap-up note, and shared Spine events.</p>
          </div>
          <div className="roundtable-flow-grid">
            <div className="context-list">
              <h4>{phaseLabels.first_pass}</h4>
              {firstPass.map((turn) => <p key={turn.id}><strong>{seatLabel(turn.seat_index)}</strong> {turn.content}</p>)}
              {firstPass.length ? null : <p>No first-pass turns yet.</p>}
            </div>
            <div className="context-list">
              <h4>{phaseLabels.manager_assessment}</h4>
              {assessment.map((turn) => <p key={turn.id}><strong>{manager?.label || "Seat 1"}</strong> {turn.content}</p>)}
              {assessment.length ? null : <p>No manager assessment yet.</p>}
            </div>
            <div className="context-list">
              <h4>Assignments</h4>
              {(activeSession?.assignments || []).map((assignment) => (
                <p key={assignment.id}><strong>{seatLabel(assignment.seat_index)}</strong> {assignment.status}: {assignment.instruction}</p>
              ))}
              {activeSession?.assignments?.length ? null : <p>No assignments yet.</p>}
            </div>
            <div className="context-list">
              <h4>{phaseLabels.second_pass}</h4>
              {secondPass.map((turn) => <p key={turn.id}><strong>{seatLabel(turn.seat_index)}</strong> {turn.content}</p>)}
              {secondPass.length ? null : <p>No second-pass turns yet.</p>}
            </div>
            <div className="context-list">
              <h4>{phaseLabels.manager_summary}</h4>
              {managerSummary.map((turn) => <p key={turn.id}><strong>{manager?.label || "Seat 1"}</strong> {turn.content}</p>)}
              {(activeSession?.summaries || []).map((summary) => <p key={summary.id}><strong>Saved summary</strong> Note {summary.note_id}</p>)}
              {managerSummary.length || activeSession?.summaries?.length ? null : <p>No manager summary yet.</p>}
            </div>
          </div>
        </article>
      </section>

      <section className="command-grid" aria-label="Round Table context and activity">
        <article className="command-panel">
          <div className="command-panel-heading">
            <p className="eyebrow">Shared context</p>
            <h3>Memory and notes available</h3>
            <p>Round Table recalls shared memory and Workstation or room notes before writing its provider-safe turns.</p>
          </div>
          <div className="context-list">
            {(workstation?.memory.items || []).slice(0, 4).map((memory) => (
              <p key={memory.id}><strong>{memory.memory_type}</strong> {memory.content}</p>
            ))}
            {(workstation?.notes || []).slice(0, 4).map((note) => (
              <p key={note.id}><strong>{note.title}</strong> {note.body}</p>
            ))}
            {workstation?.memory.items.length || workstation?.notes.length ? null : <p>No shared context saved yet.</p>}
          </div>
        </article>

        <article className="command-panel">
          <div className="command-panel-heading">
            <p className="eyebrow">Wrap-up notes and Spine</p>
            <h3>Checkpoint artifacts</h3>
            <p>Notes are saved at manager wrap-up only. Turn-by-turn notes are intentionally not generated.</p>
          </div>
          <div className="context-list">
            {(activeSession?.notes || []).map((note) => (
              <p key={note.id}><strong>{note.title}</strong> {note.body}</p>
            ))}
            {(workstation?.events || []).filter((event) => event.surface === "roundtable").slice(0, 6).map((event) => (
              <p key={event.id}><strong>{event.event_type}</strong> {event.summary}</p>
            ))}
            {activeSession?.notes?.length || workstation?.events.some((event) => event.surface === "roundtable") ? null : <p>No Round Table artifacts yet.</p>}
          </div>
        </article>
      </section>
    </section>
  );
}
