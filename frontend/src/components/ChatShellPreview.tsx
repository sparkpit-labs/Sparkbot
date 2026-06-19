import { useEffect, useState } from "react";

import { fetchChatStatus, type ChatStatusPayload } from "../api";
import { chatShellSummary, fallbackChatStatus } from "../chat/chatShellStatus";
import { formatShellStatus } from "./ShellNavigation";

type ChatStatusState = {
  payload: ChatStatusPayload;
  sourceLabel: string;
};

const fallbackChatStatusState: ChatStatusState = {
  payload: fallbackChatStatus,
  sourceLabel: "Using local Chat status fallback."
};

function formatImplementationStatus(status: string) {
  return status.replace(/-/g, " ");
}

export default function ChatShellPreview() {
  const [chatStatusState, setChatStatusState] = useState<ChatStatusState>(fallbackChatStatusState);

  useEffect(() => {
    const controller = new AbortController();

    fetchChatStatus(controller.signal)
      .then((payload) => {
        setChatStatusState({
          payload,
          sourceLabel: "Using backend Chat status."
        });
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }
        setChatStatusState(fallbackChatStatusState);
      });

    return () => controller.abort();
  }, []);

  const { payload } = chatStatusState;

  return (
    <section className="chat-shell-preview section-panel" id="chat-shell" aria-labelledby="chat-shell-heading">
      <div className="chat-shell-copy">
        <p className="eyebrow">{formatShellStatus(payload.status)}</p>
        <h2 id="chat-shell-heading">Chat Shell Preview</h2>
        <p>{chatShellSummary}</p>
        <p className="capabilities-source">{chatStatusState.sourceLabel}</p>
      </div>

      <dl className="chat-status-grid" aria-label="Chat implementation status">
        <div>
          <dt>Chat runtime</dt>
          <dd>{formatImplementationStatus(payload.chat_runtime)}</dd>
        </div>
        <div>
          <dt>Message persistence</dt>
          <dd>{formatImplementationStatus(payload.message_persistence)}</dd>
        </div>
        <div>
          <dt>Model calls</dt>
          <dd>{formatImplementationStatus(payload.model_calls)}</dd>
        </div>
        <div>
          <dt>Streaming</dt>
          <dd>{formatImplementationStatus(payload.streaming)}</dd>
        </div>
        <div>
          <dt>Provider routing</dt>
          <dd>{formatImplementationStatus(payload.provider_routing)}</dd>
        </div>
      </dl>

      <div className="chat-preview-window" aria-label="Read-only chat shell preview">
        {payload.supported_surfaces.map((surface) => (
          <article className="chat-preview-message" key={surface.id}>
            <div className="chat-preview-message-top">
              <h3>{surface.label}</h3>
              <span className={`status-badge status-${surface.status}`}>{formatShellStatus(surface.status)}</span>
            </div>
            <p>{surface.notes}</p>
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
        Empty state: chat history will appear here in a later runtime branch. This preview has no enabled send action,
        no user-entered text handling, no chat endpoint that accepts text, no message persistence, no streaming, no
        provider routing, and no model calls.
      </p>
    </section>
  );
}
