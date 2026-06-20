import { FormEvent, useEffect, useState } from "react";

import {
  addLocalChatMessage,
  createLocalChatSession,
  deleteLocalChatSession,
  getLocalChatSession,
  listLocalChatSessions,
  updateLocalChatSession,
  type LocalChatMessage,
  type LocalChatSession,
  type LocalChatSessionSummary
} from "../localWorkstation/localChat";

export default function LocalChatPanel() {
  const [sessions, setSessions] = useState<LocalChatSessionSummary[]>([]);
  const [activeSession, setActiveSession] = useState<LocalChatSession | null>(null);
  const [title, setTitle] = useState("Local planning chat");
  const [messageRole, setMessageRole] = useState<LocalChatMessage["role"]>("operator");
  const [messageContent, setMessageContent] = useState("");
  const [statusMessage, setStatusMessage] = useState("Local chat sessions have not been loaded yet.");

  const refreshSessions = async () => {
    try {
      const nextSessions = await listLocalChatSessions();
      setSessions(nextSessions);
      setStatusMessage("Loaded local chat sessions.");
      if (activeSession) {
        const stillExists = nextSessions.some((session) => session.id === activeSession.id);
        if (stillExists) {
          setActiveSession(await getLocalChatSession(activeSession.id));
        } else {
          setActiveSession(null);
        }
      }
    } catch {
      setStatusMessage("Local chat store is unavailable. Start the local backend and retry.");
    }
  };

  useEffect(() => {
    void refreshSessions();
  }, []);

  const createSession = async (event: FormEvent) => {
    event.preventDefault();
    try {
      const created = await createLocalChatSession(title);
      setActiveSession(created);
      setTitle(created.title);
      await refreshSessions();
      setStatusMessage("Saved local chat session.");
    } catch {
      setStatusMessage("Could not save local chat session.");
    }
  };

  const selectSession = async (sessionId: string) => {
    try {
      setActiveSession(await getLocalChatSession(sessionId));
      setStatusMessage("Loaded local chat session.");
    } catch {
      setStatusMessage("Could not load local chat session.");
    }
  };

  const updateSession = async () => {
    if (!activeSession) return;
    try {
      const updated = await updateLocalChatSession(activeSession.id, title);
      setActiveSession(updated);
      await refreshSessions();
      setStatusMessage("Updated local chat session.");
    } catch {
      setStatusMessage("Could not update local chat session.");
    }
  };

  const deleteSession = async () => {
    if (!activeSession) return;
    try {
      await deleteLocalChatSession(activeSession.id);
      setActiveSession(null);
      setMessageContent("");
      await refreshSessions();
      setStatusMessage("Deleted local chat session.");
    } catch {
      setStatusMessage("Could not delete local chat session.");
    }
  };

  const saveMessage = async (event: FormEvent) => {
    event.preventDefault();
    if (!activeSession) return;
    try {
      await addLocalChatMessage(activeSession.id, messageRole, messageContent);
      setMessageContent("");
      setActiveSession(await getLocalChatSession(activeSession.id));
      await refreshSessions();
      setStatusMessage("Saved local message. No model response was generated.");
    } catch {
      setStatusMessage("Could not save local message.");
    }
  };

  return (
    <section className="local-runtime-panel local-chat-panel" id="local-chat" aria-labelledby="local-chat-heading">
      <div className="local-runtime-heading">
        <p className="eyebrow">Available locally</p>
        <h2 id="local-chat-heading">Local Chat Drafts</h2>
        <p>Store operator notes and draft chat sessions in the local SQLite Workstation store. Local assistant responses are saved only through the manual Local Ollama Adapter flow.</p>
        <p className="capabilities-source">{statusMessage}</p>
      </div>

      <div className="local-runtime-grid">
        <form className="local-runtime-form" onSubmit={createSession}>
          <label>
            Session title
            <input value={title} onChange={(event) => setTitle(event.target.value)} />
          </label>
          <div className="local-action-row">
            <button type="submit">Save locally</button>
            <button type="button" onClick={updateSession} disabled={!activeSession}>Update</button>
            <button type="button" onClick={deleteSession} disabled={!activeSession}>Delete</button>
            <button type="button" onClick={refreshSessions}>Refresh</button>
          </div>
        </form>

        <div className="local-runtime-list" aria-label="Local chat sessions">
          {sessions.length === 0 ? <p>No local chat sessions saved yet.</p> : null}
          {sessions.map((session) => (
            <button className="local-list-button" type="button" key={session.id} onClick={() => void selectSession(session.id)}>
              <strong>{session.title}</strong>
              <span>{session.message_count} local messages</span>
            </button>
          ))}
        </div>
      </div>

      {activeSession ? (
        <form className="local-runtime-form" onSubmit={saveMessage}>
          <h3>{activeSession.title}</h3>
          <label>
            Local message role
            <select value={messageRole} onChange={(event) => setMessageRole(event.target.value as LocalChatMessage["role"])}>
              <option value="operator">Operator</option>
              <option value="note">Note</option>
            </select>
          </label>
          <label>
            Local message
            <textarea value={messageContent} onChange={(event) => setMessageContent(event.target.value)} />
          </label>
          <button type="submit">Save locally</button>
          <div className="local-message-list" aria-label="Local chat messages">
            {activeSession.messages.length === 0 ? <p>No local messages saved yet.</p> : null}
            {activeSession.messages.map((message) => (
              <article className="local-runtime-card" key={message.id}>
                <h4>{message.role}</h4>
                <p>{message.content}</p>
                <small>{message.created_at}</small>
              </article>
            ))}
          </div>
        </form>
      ) : null}
    </section>
  );
}
