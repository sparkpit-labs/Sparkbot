import { FormEvent, useEffect, useState } from "react";

import {
  fallbackLocalModelStatus,
  fetchLocalModelStatus,
  formatLocalModelStatus,
  localModelStatusToCapabilityStatus,
  runLocalPrompt,
  type LocalModelStatusPayload
} from "../localModels/localModelStatus";
import { listLocalChatSessions, type LocalChatSessionSummary } from "../localWorkstation/localChat";
import { listLocalMemoryNotes, type LocalMemoryNote } from "../localWorkstation/localMemoryNotes";
import StatusPill from "./StatusPill";

export default function LocalModelPanel() {
  const [status, setStatus] = useState<LocalModelStatusPayload>(fallbackLocalModelStatus);
  const [sessions, setSessions] = useState<LocalChatSessionSummary[]>([]);
  const [memoryNotes, setMemoryNotes] = useState<LocalMemoryNote[]>([]);
  const [selectedSessionId, setSelectedSessionId] = useState("");
  const [selectedMemoryNoteIds, setSelectedMemoryNoteIds] = useState<string[]>([]);
  const [sessionMessage, setSessionMessage] = useState("Local chat sessions have not been loaded yet.");
  const [memoryMessage, setMemoryMessage] = useState("Local memory notes have not been loaded yet.");
  const [statusSource, setStatusSource] = useState("Using local model fallback status.");
  const [prompt, setPrompt] = useState("Summarize this local Sparkbot note in one sentence.");
  const [model, setModel] = useState("");
  const [responseText, setResponseText] = useState("");
  const [runMessage, setRunMessage] = useState("Local prompt calls are disabled until the backend is explicitly enabled.");

  const refreshSessions = async () => {
    try {
      const nextSessions = await listLocalChatSessions();
      setSessions(nextSessions);
      setSessionMessage(nextSessions.length > 0 ? "Select an existing local chat session for the response." : "Create a local chat session before running a local prompt.");
      if (!selectedSessionId && nextSessions.length > 0) {
        setSelectedSessionId(nextSessions[0].id);
      }
      if (selectedSessionId && !nextSessions.some((session) => session.id === selectedSessionId)) {
        setSelectedSessionId(nextSessions[0]?.id ?? "");
      }
    } catch {
      setSessions([]);
      setSelectedSessionId("");
      setSessionMessage("Local chat sessions are unavailable. Start the local backend and retry.");
    }
  };

  const refreshMemoryNotes = async () => {
    try {
      const nextNotes = await listLocalMemoryNotes();
      setMemoryNotes(nextNotes);
      setSelectedMemoryNoteIds((currentIds) => currentIds.filter((noteId) => nextNotes.some((note) => note.id === noteId)));
      setMemoryMessage(nextNotes.length > 0 ? "Select local memory notes to include with the prompt." : "No local memory notes are available.");
    } catch {
      setMemoryNotes([]);
      setSelectedMemoryNoteIds([]);
      setMemoryMessage("Local memory notes are unavailable. Start the local backend and retry.");
    }
  };

  const refreshStatus = async () => {
    try {
      const nextStatus = await fetchLocalModelStatus();
      setStatus(nextStatus);
      setStatusSource("Using backend local model status.");
      if (!nextStatus.local_models_enabled) {
        setRunMessage("Local prompt calls are disabled until the backend is explicitly enabled.");
      } else if (nextStatus.status !== "available-local-only") {
        setRunMessage("Local prompt calls are enabled, but Ollama is offline or unavailable on localhost.");
      } else {
        setRunMessage("Local prompt calls are enabled for localhost Ollama only.");
      }
      if (nextStatus.configured_model && !model) {
        setModel(nextStatus.configured_model);
      }
    } catch {
      setStatus(fallbackLocalModelStatus);
      setStatusSource("Using local model fallback status.");
      setRunMessage("Local model status is unavailable. Prompt calls remain disabled in the UI.");
    }
  };

  useEffect(() => {
    void refreshStatus();
    void refreshSessions();
    void refreshMemoryNotes();
  }, []);

  const promptEnabled =
    status.local_models_enabled &&
    status.prompt_calls === "enabled-local-only" &&
    status.status === "available-local-only" &&
    Boolean(selectedSessionId);

  const toggleMemoryNote = (noteId: string) => {
    setSelectedMemoryNoteIds((currentIds) =>
      currentIds.includes(noteId) ? currentIds.filter((currentId) => currentId !== noteId) : [...currentIds, noteId]
    );
  };

  const submitPrompt = async (event: FormEvent) => {
    event.preventDefault();
    if (!promptEnabled) return;
    try {
      const result = await runLocalPrompt(prompt, model, selectedSessionId, selectedMemoryNoteIds);
      setResponseText(result.response);
      const memoryText =
        result.selected_memory_note_count > 0 ? ` ${result.selected_memory_note_count} selected memory note(s) were included.` : "";
      setRunMessage(
        result.stored_message
          ? `Local prompt completed through localhost Ollama and the assistant response was saved to the selected session.${memoryText}`
          : `Local prompt completed through localhost Ollama. No external provider was called.${memoryText}`
      );
    } catch {
      setRunMessage("Local prompt failed safely. Check that Ollama is running locally and a local model name is configured.");
    }
  };

  return (
    <section className="local-runtime-panel local-model-panel" id="local-models" aria-labelledby="local-models-heading">
      <div className="local-runtime-heading">
        <p className="eyebrow">Disabled by default</p>
        <h2 id="local-models-heading">Local Ollama Adapter</h2>
        <p>
          Local-only prompt adapter for Ollama on localhost. It uses no cloud provider SDKs, no credentials, no connector
          calls, and no external sends.
        </p>
        <p className="capabilities-source">{statusSource}</p>
      </div>

      <div className="local-model-status-grid">
        <article className="local-runtime-card">
          <h3>Adapter status</h3>
          <StatusPill status={localModelStatusToCapabilityStatus(status.status)} />
          <dl className="runtime-definition-list">
            <div>
              <dt>Adapter</dt>
              <dd>{status.adapter}</dd>
            </div>
            <div>
              <dt>Prompt calls</dt>
              <dd>{status.prompt_calls.replaceAll("-", " ")}</dd>
            </div>
            <div>
              <dt>Base URL policy</dt>
              <dd>{status.base_url_policy.replaceAll("-", " ")}</dd>
            </div>
            <div>
              <dt>Configured model</dt>
              <dd>{status.configured_model ?? "not set"}</dd>
            </div>
            <div>
              <dt>Credentials</dt>
              <dd>{status.credentials.replaceAll("-", " ")}</dd>
            </div>
            <div>
              <dt>External network</dt>
              <dd>{status.external_network.replaceAll("-", " ")}</dd>
            </div>
          </dl>
        </article>

        <article className="local-runtime-card">
          <h3>Local boundary</h3>
          <p>Status: {formatLocalModelStatus(status.status)}.</p>
          <p>Enable backend prompt calls with <code>SPARKBOT_LOCAL_MODELS_ENABLED=true</code>.</p>
          <p>Default endpoint: <code>{status.base_url ?? "localhost-only URL required"}</code>.</p>
          {status.configuration_error ? <p>{status.configuration_error}</p> : null}
        </article>
      </div>

      <form className="local-runtime-form" onSubmit={submitPrompt}>
        <label>
          Local chat session
          <select value={selectedSessionId} onChange={(event) => setSelectedSessionId(event.target.value)} disabled={!status.local_models_enabled || sessions.length === 0}>
            {sessions.length === 0 ? <option value="">No local chat sessions</option> : null}
            {sessions.map((session) => (
              <option value={session.id} key={session.id}>
                {session.title}
              </option>
            ))}
          </select>
        </label>
        <label>
          Local Ollama model
          <input value={model} onChange={(event) => setModel(event.target.value)} placeholder="llama3.2" disabled={!promptEnabled} />
        </label>
        <fieldset className="local-memory-context-list" disabled={!promptEnabled || memoryNotes.length === 0}>
          <legend>Local memory context</legend>
          {memoryNotes.length === 0 ? <p>No local memory notes</p> : null}
          {memoryNotes.map((note) => (
            <label className="local-checkbox-row" key={note.id}>
              <input
                type="checkbox"
                checked={selectedMemoryNoteIds.includes(note.id)}
                onChange={() => toggleMemoryNote(note.id)}
              />
              <span>{note.title}</span>
            </label>
          ))}
        </fieldset>
        <label>
          Local prompt
          <textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} disabled={!promptEnabled} />
        </label>
        <div className="local-action-row">
          <button type="submit" disabled={!promptEnabled}>Run local prompt</button>
          <button type="button" onClick={refreshStatus}>Refresh</button>
          <button type="button" onClick={refreshSessions}>Refresh sessions</button>
          <button type="button" onClick={refreshMemoryNotes}>Refresh notes</button>
        </div>
        <p className="capabilities-source">{sessionMessage}</p>
        <p className="capabilities-source">{memoryMessage}</p>
        <p className="capabilities-source">{runMessage}</p>
      </form>

      {responseText ? (
        <article className="local-runtime-card" aria-label="Local model response">
          <h3>Local response</h3>
          <p>{responseText}</p>
        </article>
      ) : null}
    </section>
  );
}
