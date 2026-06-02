import { FormEvent, useEffect, useMemo, useState } from "react";

import {
  fetchProviderStatus,
  sendChatMessage,
  type ChatResponse,
  type ProviderId,
  type ProviderStatusPayload
} from "../api";

type RuntimeMessage = {
  id: number;
  role: "user" | "assistant" | "system";
  content: string;
  provider?: ProviderId;
  model?: string;
};

type ProviderPhase = "loading" | "ready" | "offline";

const fallbackProviders: Array<{ id: ProviderId; label: string }> = [
  { id: "openai", label: "OpenAI" },
  { id: "openai_compatible", label: "OpenAI-compatible" },
  { id: "ollama", label: "Ollama" }
];

export default function ChatRuntime() {
  const [providerStatus, setProviderStatus] = useState<ProviderStatusPayload | null>(null);
  const [providerPhase, setProviderPhase] = useState<ProviderPhase>("loading");
  const [providerMessage, setProviderMessage] = useState("Loading provider status...");
  const [selectedProvider, setSelectedProvider] = useState<ProviderId>("openai");
  const [selectedModel, setSelectedModel] = useState("gpt-4o-mini");
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState<RuntimeMessage[]>([]);
  const [isSending, setIsSending] = useState(false);

  const providerOptions = useMemo(() => {
    return providerStatus?.providers.length
      ? providerStatus.providers.map((provider) => ({ id: provider.id, label: provider.label }))
      : fallbackProviders;
  }, [providerStatus]);

  const refreshProviderStatus = async () => {
    setProviderPhase("loading");
    setProviderMessage("Loading provider status...");
    try {
      const status = await fetchProviderStatus();
      setProviderStatus(status);
      setSelectedProvider(status.selected_provider);
      setSelectedModel(status.selected_model || "");
      setProviderPhase("ready");
      setProviderMessage(status.message);
    } catch (error) {
      setProviderPhase("offline");
      setProviderMessage(error instanceof Error ? error.message : "Provider status is unavailable.");
    }
  };

  useEffect(() => {
    void refreshProviderStatus();
  }, []);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const message = draft.trim();
    if (!message || isSending) {
      return;
    }

    const userMessage: RuntimeMessage = { id: Date.now(), role: "user", content: message };
    setMessages((current) => [...current, userMessage]);
    setDraft("");
    setIsSending(true);

    try {
      const response: ChatResponse = await sendChatMessage({
        message,
        provider: selectedProvider,
        model: selectedModel.trim() || undefined
      });
      setSelectedProvider(response.provider);
      setSelectedModel(response.model);
      setMessages((current) => [
        ...current,
        {
          id: Date.now() + 1,
          role: "assistant",
          content: response.content,
          provider: response.provider,
          model: response.model
        }
      ]);
      void refreshProviderStatus();
    } catch (error) {
      setMessages((current) => [
        ...current,
        {
          id: Date.now() + 1,
          role: "system",
          content: error instanceof Error ? error.message : "Chat request failed."
        }
      ]);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <section className="chat-runtime section-panel" id="chat-shell" aria-labelledby="chat-runtime-heading">
      <div className="chat-runtime-copy">
        <p className="eyebrow">Works Today</p>
        <h2 id="chat-runtime-heading">Sparkbot Runtime Chat</h2>
        <p>Send a real message through the backend provider router. Provider credentials stay server-side.</p>
      </div>

      <div className="runtime-config" id="provider-setup" aria-labelledby="provider-runtime-heading">
        <div>
          <p className="eyebrow">Backend-configured provider</p>
          <h2 id="provider-runtime-heading">Provider Runtime</h2>
          <p className="provider-safe-note">Configure provider values in backend environment settings. API keys are never stored in the browser.</p>
        </div>

        <div className="runtime-config-grid">
          <label>
            <span>Provider</span>
            <select value={selectedProvider} onChange={(event) => setSelectedProvider(event.target.value as ProviderId)}>
              {providerOptions.map((provider) => (
                <option value={provider.id} key={provider.id}>
                  {provider.label}
                </option>
              ))}
            </select>
          </label>

          <label>
            <span>Model</span>
            <input
              value={selectedModel}
              onChange={(event) => setSelectedModel(event.target.value)}
              placeholder="Backend default model"
            />
          </label>

          <button type="button" onClick={refreshProviderStatus} disabled={providerPhase === "loading"}>
            {providerPhase === "loading" ? "Refreshing..." : "Refresh status"}
          </button>
        </div>

        <div className={`provider-runtime-status provider-runtime-${providerPhase}`}>
          <strong>{providerPhase === "ready" ? "Provider status" : "Status"}</strong>
          <span>{providerMessage}</span>
        </div>

        {providerStatus ? (
          <div className="provider-status-list" aria-label="Provider configuration status">
            {providerStatus.providers.map((provider) => (
              <article className="provider-status-item" key={provider.id}>
                <div>
                  <h3>{provider.label}</h3>
                  <p>{provider.model ? `Model: ${provider.model}` : "Model not configured"}</p>
                </div>
                <span className={`status-badge ${provider.configured ? "status-worksToday" : "status-planned"}`}>
                  {provider.configured ? "Configured" : "Needs env"}
                </span>
              </article>
            ))}
          </div>
        ) : null}
      </div>

      <div className="chat-runtime-window" aria-label="Sparkbot chat messages">
        {messages.length ? (
          messages.map((message) => (
            <article className={`chat-runtime-message chat-runtime-message-${message.role}`} key={message.id}>
              <div className="chat-runtime-message-top">
                <h3>{message.role === "assistant" ? "Sparkbot" : message.role === "system" ? "System" : "You"}</h3>
                {message.provider && message.model ? <span>{message.provider} / {message.model}</span> : null}
              </div>
              <p>{message.content}</p>
            </article>
          ))
        ) : (
          <p className="chat-runtime-empty">No messages yet. Send a prompt to call the configured backend provider.</p>
        )}
      </div>

      <form className="chat-runtime-composer" onSubmit={handleSubmit}>
        <label htmlFor="chat-runtime-input">Message Sparkbot</label>
        <textarea
          id="chat-runtime-input"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Ask Sparkbot a question..."
          rows={4}
        />
        <button type="submit" disabled={isSending || !draft.trim()}>
          {isSending ? "Sending..." : "Send"}
        </button>
      </form>
    </section>
  );
}
