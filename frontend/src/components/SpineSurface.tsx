import { useEffect, useState } from "react";

import {
  fetchSpineOverview,
  fetchWorkstationState,
  type SpineOverview,
  type WorkstationState
} from "../api";

type LoadState = "loading" | "ready" | "error";

const queueLabels: Array<[keyof SpineOverview, string]> = [
  ["open_queue", "Open"],
  ["blocked_queue", "Blocked"],
  ["approval_waiting_queue", "Approval waiting"],
  ["stale_queue", "Stale"],
  ["orphan_queue", "Orphaned"],
  ["assignment_ready_queue", "Assignment ready"],
  ["executive_directives_queue", "Directives"]
];

export default function SpineSurface() {
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [workstation, setWorkstation] = useState<WorkstationState | null>(null);
  const [spine, setSpine] = useState<SpineOverview | null>(null);
  const [message, setMessage] = useState("Loading Spine events and counters...");
  const [error, setError] = useState<string | null>(null);

  async function loadData() {
    setLoadState("loading");
    setError(null);
    try {
      const [state, overview] = await Promise.all([fetchWorkstationState(), fetchSpineOverview()]);
      setWorkstation(state);
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
          <p>Event history, dashboard counters, and empty-state queues from the shared Workstation store.</p>
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
            <div><dt>Events</dt><dd>{workstation?.dashboard.events_count ?? 0}</dd></div>
            <div><dt>Rooms</dt><dd>{workstation?.dashboard.rooms_count ?? 0}</dd></div>
            <div><dt>Memory</dt><dd>{workstation?.dashboard.memory_count ?? 0}</dd></div>
            <div><dt>Notes</dt><dd>{workstation?.dashboard.notes_count ?? 0}</dd></div>
            <div><dt>Chat turns</dt><dd>{workstation?.dashboard.chat_messages_count ?? 0}</dd></div>
            <div><dt>Pending confirmations</dt><dd>{workstation?.dashboard.pending_confirmations ?? 0}</dd></div>
          </dl>
        </article>
      </section>

      <section className="command-grid" aria-label="Spine queues and events">
        <article className="command-panel">
          <div className="command-panel-heading">
            <p className="eyebrow">Queues</p>
            <h3>Task/project queues</h3>
            <p>Visible empty-state queues are honest placeholders. They do not schedule or execute work.</p>
          </div>
          <div className="spine-stats">
            {queueLabels.map(([key, label]) => (
              <div className="spine-stat" key={String(key)}>
                <span>{label}</span>
                <strong>{Array.isArray(spine?.[key]) ? (spine?.[key] as unknown[]).length : 0}</strong>
              </div>
            ))}
          </div>
        </article>

        <article className="command-panel">
          <div className="command-panel-heading">
            <p className="eyebrow">History</p>
            <h3>Recent events</h3>
            <p>Chat, rooms, notes, memory, seats, Command Center, and Guardian all write here.</p>
          </div>
          <div className="context-list">
            {(workstation?.events || []).slice(0, 12).map((event) => (
              <p key={event.id}><strong>{event.event_type}</strong> {event.summary}</p>
            ))}
            {workstation?.events.length ? null : <p>No events yet.</p>}
          </div>
        </article>
      </section>
    </section>
  );
}
