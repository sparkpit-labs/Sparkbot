import { FormEvent, useEffect, useState } from "react";

import {
  createLocalMemoryNote,
  deleteLocalMemoryNote,
  listLocalMemoryNotes,
  updateLocalMemoryNote,
  type LocalMemoryNote
} from "../localWorkstation/localMemoryNotes";

const emptyForm = { title: "", body: "", source: "operator" };

export default function LocalMemoryNotesPanel() {
  const [notes, setNotes] = useState<LocalMemoryNote[]>([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState("Local memory notes have not been loaded yet.");

  const refreshNotes = async () => {
    try {
      setNotes(await listLocalMemoryNotes());
      setStatusMessage("Loaded local memory notes.");
    } catch {
      setStatusMessage("Local memory notes are unavailable. Start the local backend and retry.");
    }
  };

  useEffect(() => {
    void refreshNotes();
  }, []);

  const saveNote = async (event: FormEvent) => {
    event.preventDefault();
    try {
      if (editingId) {
        await updateLocalMemoryNote(editingId, form);
        setStatusMessage("Updated local memory note.");
      } else {
        await createLocalMemoryNote(form.title, form.body, form.source);
        setStatusMessage("Added local note.");
      }
      setForm(emptyForm);
      setEditingId(null);
      await refreshNotes();
    } catch {
      setStatusMessage("Could not save local memory note.");
    }
  };

  const editNote = (note: LocalMemoryNote) => {
    setEditingId(note.id);
    setForm({ title: note.title, body: note.body, source: note.source });
    setStatusMessage("Editing local memory note.");
  };

  const deleteNote = async (noteId: string) => {
    try {
      await deleteLocalMemoryNote(noteId);
      if (editingId === noteId) {
        setEditingId(null);
        setForm(emptyForm);
      }
      await refreshNotes();
      setStatusMessage("Deleted local memory note.");
    } catch {
      setStatusMessage("Could not delete local memory note.");
    }
  };

  return (
    <section className="local-runtime-panel" id="local-memory-notes" aria-labelledby="local-memory-notes-heading">
      <div className="local-runtime-heading">
        <p className="eyebrow">Available locally</p>
        <h2 id="local-memory-notes-heading">Local Memory Notes</h2>
        <p>Save notes to the local Workstation store. These are not model memory and are not synced to a cloud service.</p>
        <p className="capabilities-source">{statusMessage}</p>
      </div>

      <form className="local-runtime-form" onSubmit={saveNote}>
        <label>
          Note title
          <input value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} />
        </label>
        <label>
          Source label
          <input value={form.source} onChange={(event) => setForm({ ...form, source: event.target.value })} />
        </label>
        <label>
          Note body
          <textarea value={form.body} onChange={(event) => setForm({ ...form, body: event.target.value })} />
        </label>
        <div className="local-action-row">
          <button type="submit">{editingId ? "Update" : "Add local note"}</button>
          <button type="button" onClick={refreshNotes}>Refresh</button>
        </div>
      </form>

      <div className="local-card-grid" aria-label="Local memory note list">
        {notes.length === 0 ? <p>No local memory notes saved yet.</p> : null}
        {notes.map((note) => (
          <article className="local-runtime-card" key={note.id}>
            <h3>{note.title}</h3>
            <p>{note.body}</p>
            <small>Source: {note.source}</small>
            <div className="local-action-row">
              <button type="button" onClick={() => editNote(note)}>Edit</button>
              <button type="button" onClick={() => void deleteNote(note.id)}>Delete</button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
