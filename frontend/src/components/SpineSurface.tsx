import { useEffect, useState } from "react";

import {
  fetchSpineOverview,
  fetchWorkstationHistory,
  type SpineOverview,
  type WorkstationHistory
} from "../api";

type LoadState = "loading" | "ready" | "error";

const queueLabels: Array<[keyof SpineOverview, string]> = [
  ["open_queue", "Open"],
  ["blocked_queue", "Blocked"],
  ["approval_waiting_queue", "Approval waiting"],
  ["stale_queue", "Stale"],
  ["orphan_queue", "Orphaned"],
  ["assignment_ready_queue", "Assignment ready"],
  ["executive_directives_queue", "Directives"],
  ["completed_queue", "Completed"]
];

function shortId(value: string): string {
  return value ? value.slice(0, 8) : "shared";
}

function eventGroup(eventType: string): string {
  if (eventType.startsWith("model.call")) return "Provider/model";
  if (eventType.startsWith("memory.")) return "Memory";
  if (eventType.startsWith("note.")) return "Notes";
  if (eventType.startsWith("roundtable.")) return "Round Table";
  if (eventType.startsWith("task.")) return "Tasks";
  if (eventType.startsWith("chat.")) return "Chat";
  if (eventType.startsWith("guardian.")) return "Guardian";
  if (eventType.startsWith("room.")) return "Rooms";
  return "Workstation";
}

export default function SpineSurface() {
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [history, setHistory] = useState<WorkstationHistory | null>(null);
  const [spine, setSpine] = useState<SpineOverview | null>(null);
  const [message, setMessage] = useState("Loading Spine events and counters...");
  const [error, setError] = useState<string | null>(null);

  async function loadData() {
    setLoadState("loading");
    setError(null);
    try {
      const [historyState, overview] = await Promise.all([fetchWorkstationHistory(50), fetchSpineOverview()]);
      setHistory(historyState);
      setSpine(overview);
      setLoadState("ready");
      setMessage("Spine view synced with shared event history.");
    } catch (caught) {
      setLoadState("error");
      setError(caught instanceof Error ? caught.message : "Spine backend is unavailable.");
      setMessage("Start the local backend to inspect Spine events and counters.");
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  return (
    <section className="spine-surface" aria-label="Sparkbot Spine">
      <header className="command-header">
        <div>
          <p className="eyebrow">Spine</p>
          <h2>Spine Event Log</h2>
          <p>Event history, dashboard counters, notes, artifacts, and room/session history from the shared Workstation store.</p>
        </div>
        <div className="command-header-actions">
          <span className={`status-badge ${loadState === "ready" ? "status-worksToday" : loadState === "loading" ? "status-preview" : "status-notImplemented"}`}>
            {loadState === "ready" ? "Backend synced" : loadState === "loading" ? "Syncing" : "Backend needed"}
          </span>
          <button type="button" onClick={loadData}>Refresh</button>
        </div>
      </header>

      <div className="command-message" role="status">
        <span>{message}</span>
        <span>Spine writes are backend event-log entries only.</span>
      </div>
      {error ? <div className="command-error" role="alert">{error}</div> : null}

      <section className="command-grid" aria-label="Spine counters">
        <article className="command-panel command-panel-wide">
          <div className="command-panel-heading">
            <p className="eyebrow">Counters</p>
            <h3>Shared event state</h3>
            <p>{spine?.note || "Task and project queues remain empty-state views until the next backend slice."}</p>
          </div>
          <dl className="mini-metrics">
            <div><dt>Events</dt><dd>{history?.dashboard.events_count ?? 0}</dd></div>
            <div><dt>Rooms</dt><dd>{history?.dashboard.rooms_count ?? 0}</dd></div>
            <div><dt>Memory</dt><dd>{history?.dashboard.memory_count ?? 0}</dd></div>
            <div><dt>Notes</dt><dd>{history?.dashboard.notes_count ?? 0}</dd></div>
            <div><dt>Tasks</dt><dd>{history?.dashboard.tasks_count ?? 0}</dd></div>
            <div><dt>Open tasks</dt><dd>{history?.dashboard.open_tasks_count ?? 0}</dd></div>
            <div><dt>Chat turns</dt><dd>{history?.dashboard.chat_messages_count ?? 0}</dd></div>
            <div><dt>Round Table</dt><dd>{history?.dashboard.roundtable_sessions_count ?? 0}</dd></div>
            <div><dt>Pending confirmations</dt><dd>{history?.dashboard.pending_confirmations ?? 0}</dd></div>
          </dl>
        </article>
      </section>

      <section className="command-grid" aria-label="Spine history and events">
        <article className="command-panel">
          <div className="command-panel-heading">
            <p className="eyebrow">History</p>
            <h3>Notes and artifacts</h3>
            <p>Workstation, Chat, room, and Round Table wrap-up notes are visible here with their backend source labels.</p>
          </div>
          <div className="history-list">
            {(history?.notes || []).slice(0, 8).map((note) => (
              <div className="history-list-item" key={note.id}>
                <strong>{note.title}</strong>
                <span>{note.surface}:{shortId(note.source_id)}</span>
                <span>{note.tags.join(", ") || "untagged"}</span>
                <p>{note.body}</p>
              </div>
            ))}
            {history?.notes.length ? null : <p>No notes or artifacts yet.</p>}
          </div>
        </article>

        <article className="command-panel">
          <div className="command-panel-heading">
            <p className="eyebrow">History</p>
            <h3>Room and session history</h3>
            <p>Chat and Round Table records are backend-backed and reopen from their dedicated surfaces.</p>
          </div>
          <div className="history-list">
            {(history?.roundtable.sessions || []).slice(0, 6).map((session) => (
              <div className="history-list-item" key={session.id}>
                <strong>{session.title}</strong>
                <span>Round Table {session.status} / {session.phase}</span>
                <span>{session.turns?.length || session.turn_count || 0} turn(s), {session.assignments?.length || session.assignment_count || 0} assignment(s)</span>
                {session.summaries?.[0]?.note_id ? <span>Wrap-up note {shortId(session.summaries[0].note_id)}</span> : <span>No wrap-up note yet</span>}
              </div>
            ))}
            {(history?.chat.sessions || []).slice(0, 6).map((session) => (
              <div className="history-list-item" key={session.id}>
                <strong>{session.title}</strong>
                <span>Chat {session.status}</span>
                <span>{session.message_count || 0} message(s)</span>
                <span>{session.last_message ? `${session.last_message.role}: ${session.last_message.content}` : "No messages yet"}</span>
              </div>
            ))}
            {history?.roundtable.sessions.length || history?.chat.sessions.length ? null : <p>No room or session history yet.</p>}
          </div>
        </article>
      </section>

      <section className="command-grid" aria-label="Spine queues and events">
        <article className="command-panel">
          <div className="command-panel-heading">
            <p className="eyebrow">Queues</p>
            <h3>Task queues</h3>
            <p>Queues reflect local task records and Guardian confirmations only. They do not schedule or execute work.</p>
          </div>
          <div className="spine-stats">
            {queueLabels.map(([key, label]) => (
              <div className="spine-stat" key={String(key)}>
                <span>{label}</span>
                <strong>{Array.isArray(spine?.[key]) ? (spine?.[key] as unknown[]).length : 0}</strong>
              </div>
            ))}
          </div>
          <div className="work-item-list compact">
            {(history?.tasks.items || []).slice(0, 6).map((task) => (
              <div className="work-item-row" key={task.id}>
                <div className="work-item-top">
                  <strong>{task.title}</strong>
                  <span>{task.status}</span>
                </div>
                <p>{task.notes || "No notes saved."}</p>
                <span>{task.surface}:{shortId(task.source_id)}</span>
              </div>
            ))}
            {history?.tasks.items.length ? null : <p>No task records yet.</p>}
          </div>
        </article>

        <article className="command-panel">
          <div className="command-panel-heading">
            <p className="eyebrow">Events</p>
            <h3>Recent events</h3>
            <p>Provider/model, memory, notes, rooms, Chat, Round Table, and Guardian events show safe metadata only.</p>
          </div>
          <div className="event-list-grid">
            {(history?.events || []).slice(0, 16).map((event) => (
              <div className="event-list-item" key={event.id}>
                <strong>{event.event_type}</strong>
                <span>{eventGroup(event.event_type)}</span>
                <span>{event.summary}</span>
                <span>{event.surface}:{shortId(event.source_id)}</span>
              </div>
            ))}
            {history?.events.length ? null : <p>No events yet.</p>}
          </div>
        </article>
      </section>

      <section className="command-grid" aria-label="Spine producers">
        <article className="command-panel command-panel-wide">
          <div className="command-panel-heading">
            <p className="eyebrow">Producers</p>
            <h3>Event producers</h3>
            <p>Producer metadata shows safe subsystem names, event types, counts, and last event timestamps.</p>
          </div>
          <div className="producer-grid">
            {(history?.producers || []).map((producer) => (
              <div className="producer-item" key={producer.subsystem}>
                <strong>{producer.subsystem}</strong>
                <span>{producer.description}</span>
                <span>{producer.event_count} event(s)</span>
                <span>{producer.event_types.slice(0, 5).join(", ") || "No events yet"}</span>
              </div>
            ))}
            {history?.producers.length ? null : <p>No producer metadata yet.</p>}
          </div>
        </article>
      </section>
    </section>
  );
}
