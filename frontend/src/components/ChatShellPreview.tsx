import { chatPreviewMessages, chatShellSummary } from "../chat/chatShellStatus";

function formatStatus(status: "skeleton" | "planned") {
  return status === "skeleton" ? "Skeleton" : "Planned";
}

export default function ChatShellPreview() {
  return (
    <section className="chat-shell-preview" aria-labelledby="chat-shell-heading">
      <div className="chat-shell-copy">
        <p className="eyebrow">Skeleton surface</p>
        <h2 id="chat-shell-heading">Chat Shell Preview</h2>
        <p>{chatShellSummary}</p>
      </div>

      <div className="chat-preview-window" aria-label="Read-only chat shell preview">
        {chatPreviewMessages.map((message) => (
          <article className="chat-preview-message" key={message.speaker}>
            <div className="chat-preview-message-top">
              <h3>{message.speaker}</h3>
              <span className={`status-badge status-${message.status}`}>{formatStatus(message.status)}</span>
            </div>
            <p>{message.summary}</p>
          </article>
        ))}
      </div>

      <label className="chat-planned-composer" htmlFor="chat-planned-composer">
        <span>Planned composer</span>
        <textarea
          id="chat-planned-composer"
          aria-label="Chat message composer planned"
          disabled
          readOnly
          value="Chat input is planned for a later branch."
        />
      </label>

      <p className="chat-shell-note">
        This preview includes no enabled send action, no chat endpoint, no message persistence, and no model calls.
      </p>
    </section>
  );
}
