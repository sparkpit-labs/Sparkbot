import { FormEvent, useEffect, useMemo, useState } from "react";

import {
  createChatSession,
  createNote,
  fetchChatSession,
  fetchChatSessions,
  fetchWorkstationState,
  sendChatMessage,
  type ChatSession,
  type WorkstationState
} from "../api";

type LoadState = "loading" | "ready" | "error";

function shortId(value: string): string {
  return value ? value.slice(0, 8) : "";
}

function selectedRoute(state: WorkstationState | null): string {
  const seatOne = state?.seats?.[0];
  const fallback = state?.controls?.default_selection;
  const provider = seatOne?.provider && seatOne.provider !== "default" ? seatOne.provider : fallback?.provider;
  const model = seatOne?.model || fallback?.model;
  return `${provider || "local"} / ${model || "local-workstation"}`;
}

export default function ChatWorkstation() {
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [workstation, setWorkstation] = useState<WorkstationState | null>(null);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSession, setActiveSession] = useState<ChatSession | null>(null);
  const [draft, setDraft] = useState("");
  const [noteDraft, setNoteDraft] = useState("");
  const [saveToMemory, setSaveToMemory] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("Loading shared Workstation state...");
  const [error, setError] = useState<string | null>(null);

  const routeLabel = useMemo(() => selectedRoute(workstation), [workstation]);
  const messages = activeSession?.messages || [];

  async function loadData(preferredSessionId?: string) {
    setLoadState("loading");
    setError(null);
    try {
      const [state, sessionList] = await Promise.all([fetchWorkstationState(), fetchChatSessions()]);
      setWorkstation(state);
      setSessions(sessionList.sessions);
      const targetId = preferredSessionId || activeSession?.id || sessionList.sessions[0]?.id;
      if (targetId) {
        setActiveSession(await fetchChatSession(targetId));
      } else {
        setActiveSession(null);
      }
      setLoadState("ready");
      setMessage("Chat is synced with the shared Workstation store.");
    } catch (caught) {
      setLoadState("error");
      setError(caught instanceof Error ? caught.message : "Workstation backend is unavailable.");
      setMessage("Start the local backend to use backend-backed chat.");
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  async function startSession() {
    setBusy(true);
    setError(null);
    try {
      const session = await createChatSession({ title: "Sparkbot chat", metadata: { surface: "chat" } });
      await loadData(session.id);
      setMessage("New chat session created in shared Workstation state.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Chat session could not be created.");
    } finally {
      setBusy(false);
    }
  }

  async function selectSession(sessionId: string) {
    setBusy(true);
    setError(null);
    try {
      setActiveSession(await fetchChatSession(sessionId));
      setMessage("Chat session loaded from shared Workstation state.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Chat session could not be loaded.");
    } finally {
      setBusy(false);
    }
  }

  async function submitMessage(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const content = draft.trim();
    if (!content) return;
    setBusy(true);
    setError(null);
    try {
      const result = await sendChatMessage({
        session_id: activeSession?.id,
        content,
        save_to_memory: saveToMemory,
        metadata: { surface: "workstation" }
      });
      setDraft("");
      setActiveSession(result.session);
      setWorkstation(result.workstation);
      const sessionList = await fetchChatSessions();
      setSessions(sessionList.sessions);
      if (result.guardian_confirmation) {
        setMessage("Guardian confirmation created. No privileged action was executed.");
      } else if (result.blocked_action) {
        setMessage("Privileged request blocked. No external or destructive action was executed.");
      } else {
        setMessage("Chat turn saved to shared Workstation state.");
      }
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Chat message could not be saved.");
    } finally {
      setBusy(false);
    }
  }

  async function saveNote() {
    const body = noteDraft.trim();
    if (!body || !activeSession) return;
    setBusy(true);
    setError(null);
    try {
      await createNote({
        title: `Chat note ${shortId(activeSession.id)}`,
        body,
        surface: "chat",
        source_id: activeSession.id,
        tags: ["chat"]
      });
      setNoteDraft("");
      await loadData(activeSession.id);
      setMessage("Note saved to shared Workstation state.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Note could not be saved.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="chat-workstation" aria-label="Sparkbot Workstation chat">
      <header className="command-header chat-workstation-header">
        <div>
          <p className="eyebrow">Shared Workstation</p>
          <h2>Sparkbot Workstation</h2>
          <p>Chat sessions, memory, notes, rooms, events, model seats, and Guardian confirmations use the shared local backend store.</p>
        </div>
        <div className="command-header-actions">
          <span className={`status-badge ${loadState === "ready" ? "status-worksToday" : loadState === "loading" ? "status-preview" : "status-notImplemented"}`}>
            {loadState === "ready" ? "Backend synced" : loadState === "loading" ? "Syncing" : "Backend needed"}
          </span>
          <button type="button" onClick={() => loadData()} disabled={busy}>Refresh</button>
        </div>
      </header>

      <div className="command-message" role="status">
        <span>{message}</span>
        <span>Selected route: {routeLabel}</span>
      </div>
      {error ? <div className="command-error" role="alert">{error}</div> : null}

      <section className="chat-workstation-grid">
        <aside className="command-panel chat-session-list" aria-label="Chat sessions">
          <div className="command-panel-heading">
            <p className="eyebrow">Sessions</p>
            <h3>Shared Chat</h3>
            <p>{sessions.length} session(s) stored locally.</p>
          </div>
          <button type="button" onClick={startSession} disabled={busy}>New chat</button>
          <div className="chat-session-buttons">
            {sessions.map((session) => (
              <button
                key={session.id}
                type="button"
                className={activeSession?.id === session.id ? "chat-session-button chat-session-button-active" : "chat-session-button"}
                onClick={() => selectSession(session.id)}
                disabled={busy}
              >
                <span>{session.title}</span>
                <strong>{session.message_count || 0} message(s)</strong>
              </button>
            ))}
          </div>
        </aside>

        <article className="command-panel chat-thread-panel">
          <div className="command-panel-heading">
            <p className="eyebrow">Conversation</p>
            <h3>{activeSession?.title || "No chat session selected"}</h3>
            <p>Provider calls are deferred here; this branch proves shared persistence, context recall, notes, events, and Guardian boundaries.</p>
          </div>

          <div className="chat-thread" aria-live="polite">
            {messages.length ? messages.map((item) => (
              <article key={item.id} className={`chat-message chat-message-${item.role}`}>
                <div className="chat-message-top">
                  <strong>{item.role === "assistant" ? "Sparkbot" : item.actor || "Operator"}</strong>
                  <span>{item.provider} / {item.model}</span>
                </div>
                <p>{item.content}</p>
              </article>
            )) : (
              <div className="empty-state">No messages yet. Send a chat turn to create backend-backed history.</div>
            )}
          </div>

          <form className="chat-composer" onSubmit={submitMessage}>
            <label>
              <span>Message</span>
              <textarea value={draft} onChange={(event) => setDraft(event.target.value)} rows={4} placeholder="Ask Sparkbot to use shared Workstation context." />
            </label>
            <label className="inline-check">
              <input type="checkbox" checked={saveToMemory} onChange={(event) => setSaveToMemory(event.target.checked)} />
              <span>Save this user message to Workstation memory</span>
            </label>
            <button type="submit" disabled={busy || !draft.trim()}>{busy ? "Saving..." : "Send"}</button>
          </form>
        </article>

        <aside className="command-panel chat-context-panel" aria-label="Shared Workstation context">
          <div className="command-panel-heading">
            <p className="eyebrow">Context</p>
            <h3>Memory, notes, and Spine</h3>
          </div>
          <dl className="mini-metrics">
            <div><dt>Memory</dt><dd>{workstation?.dashboard.memory_count ?? 0}</dd></div>
            <div><dt>Notes</dt><dd>{workstation?.dashboard.notes_count ?? 0}</dd></div>
            <div><dt>Events</dt><dd>{workstation?.dashboard.events_count ?? 0}</dd></div>
            <div><dt>Rooms</dt><dd>{workstation?.dashboard.rooms_count ?? 0}</dd></div>
            <div><dt>Pending</dt><dd>{workstation?.dashboard.pending_confirmations ?? 0}</dd></div>
            <div><dt>Chat turns</dt><dd>{workstation?.dashboard.chat_messages_count ?? 0}</dd></div>
          </dl>

          <div className="context-list">
            <h4>Recent memory</h4>
            {(workstation?.memory.items || []).slice(0, 4).map((memory) => (
              <p key={memory.id}><strong>{memory.memory_type}</strong> {memory.content}</p>
            ))}
          </div>

          <div className="context-list">
            <h4>Recent notes</h4>
            {(workstation?.notes || []).slice(0, 4).map((note) => (
              <p key={note.id}><strong>{note.title}</strong> {note.body}</p>
            ))}
          </div>

          <label>
            <span>Save note on this chat</span>
            <textarea value={noteDraft} onChange={(event) => setNoteDraft(event.target.value)} rows={3} disabled={!activeSession} />
          </label>
          <button type="button" onClick={saveNote} disabled={busy || !activeSession || !noteDraft.trim()}>Save note</button>
        </aside>
      </section>
    </section>
  );
}
