import { FormEvent, useEffect, useState } from "react";

import {
  createLocalWorkLaneCard,
  deleteLocalWorkLaneCard,
  listLocalWorkLaneCards,
  updateLocalWorkLaneCard,
  workLaneCardStatuses,
  workLaneNames,
  type LocalWorkLaneCard,
  type WorkLaneCardStatus,
  type WorkLaneName
} from "../localWorkstation/localWorkLaneCards";

const emptyForm = { lane: "inbox" as WorkLaneName, title: "", body: "", status: "open" as WorkLaneCardStatus };

export default function LocalWorkLaneCardsPanel() {
  const [cards, setCards] = useState<LocalWorkLaneCard[]>([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState("Local work lane cards have not been loaded yet.");

  const refreshCards = async () => {
    try {
      setCards(await listLocalWorkLaneCards());
      setStatusMessage("Loaded local work lane cards.");
    } catch {
      setStatusMessage("Local work lane cards are unavailable. Start the local backend and retry.");
    }
  };

  useEffect(() => {
    void refreshCards();
  }, []);

  const saveCard = async (event: FormEvent) => {
    event.preventDefault();
    try {
      if (editingId) {
        await updateLocalWorkLaneCard(editingId, form);
        setStatusMessage("Updated local work lane card.");
      } else {
        await createLocalWorkLaneCard(form.lane, form.title, form.body, form.status);
        setStatusMessage("Added local work lane card.");
      }
      setForm(emptyForm);
      setEditingId(null);
      await refreshCards();
    } catch {
      setStatusMessage("Could not save local work lane card.");
    }
  };

  const editCard = (card: LocalWorkLaneCard) => {
    setEditingId(card.id);
    setForm({ lane: card.lane, title: card.title, body: card.body, status: card.status });
    setStatusMessage("Editing local work lane card.");
  };

  const deleteCard = async (cardId: string) => {
    try {
      await deleteLocalWorkLaneCard(cardId);
      if (editingId === cardId) {
        setEditingId(null);
        setForm(emptyForm);
      }
      await refreshCards();
      setStatusMessage("Deleted local work lane card.");
    } catch {
      setStatusMessage("Could not delete local work lane card.");
    }
  };

  return (
    <section className="local-runtime-panel" id="local-work-lane-cards" aria-labelledby="local-work-lane-cards-heading">
      <div className="local-runtime-heading">
        <p className="eyebrow">Available locally</p>
        <h2 id="local-work-lane-cards-heading">Local Work Lane Cards</h2>
        <p>Plan work with local cards. Cards are stored locally and do not run, schedule, remind, notify, or execute tasks.</p>
        <p className="capabilities-source">{statusMessage}</p>
      </div>

      <form className="local-runtime-form" onSubmit={saveCard}>
        <label>
          Card title
          <input value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} />
        </label>
        <label>
          Lane
          <select value={form.lane} onChange={(event) => setForm({ ...form, lane: event.target.value as WorkLaneName })}>
            {workLaneNames.map((lane) => (
              <option value={lane} key={lane}>{lane}</option>
            ))}
          </select>
        </label>
        <label>
          Card status
          <select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value as WorkLaneCardStatus })}>
            {workLaneCardStatuses.map((status) => (
              <option value={status} key={status}>{status}</option>
            ))}
          </select>
        </label>
        <label>
          Card body
          <textarea value={form.body} onChange={(event) => setForm({ ...form, body: event.target.value })} />
        </label>
        <div className="local-action-row">
          <button type="submit">{editingId ? "Update" : "Add card"}</button>
          <button type="button" onClick={refreshCards}>Refresh</button>
        </div>
      </form>

      <div className="local-card-grid" aria-label="Local work lane card list">
        {cards.length === 0 ? <p>No local work lane cards saved yet.</p> : null}
        {cards.map((card) => (
          <article className="local-runtime-card" key={card.id}>
            <h3>{card.title}</h3>
            <p>{card.body}</p>
            <small>Lane: {card.lane} | Status: {card.status}</small>
            <div className="local-action-row">
              <button type="button" onClick={() => editCard(card)}>Edit</button>
              <button type="button" onClick={() => void deleteCard(card.id)}>Delete</button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
