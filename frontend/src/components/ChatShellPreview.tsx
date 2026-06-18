import { chatPreviewMessages, chatShellSummary } from "../chat/chatShellStatus";
import { formatShellStatus } from "./ShellNavigation";

export default function ChatShellPreview() {
  return (
    <section className="chat-shell-preview section-panel" id="chat-shell" aria-labelledby="chat-shell-heading">
      <div className="chat-shell-copy">
        <p className="eyebrow">Preview</p>
        <h2 id="chat-shell-heading">Chat Shell Preview</h2>
        <p>{chatShellSummary}</p>
      </div>

      <div className="chat-preview-window" aria-label="Read-only chat shell preview">
        {chatPreviewMessages.map((message) => (
          <article className="chat-preview-message" key={message.speaker}>
            <div className="chat-preview-message-top">
              <h3>{message.speaker}</h3>
              <span className={`status-badge status-${message.status}`}>{formatShellStatus(message.status)}</span>
            </div>
            <p>{message.summary}</p>
          </article>
        ))}
      </div>

      <label className="chat-planned-composer" htmlFor="chat-planned-composer">
        <span>Preview composer</span>
        <textarea
          id="chat-planned-composer"
          aria-label="Chat message composer planned"
          disabled
          readOnly
          value="Message input is intentionally disabled in this public preview."
        />
      </label>

      <p className="chat-shell-note">
        Empty state: chat history will appear here in a later runtime branch. This preview includes no enabled send
        action, no chat endpoint, no message persistence, and no model calls.
      </p>
    </section>
  );
}
