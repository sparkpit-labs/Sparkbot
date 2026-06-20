import { FormEvent, useEffect, useState } from "react";

import {
  fallbackLocalModelStatus,
  fetchLocalModelStatus,
  formatLocalModelStatus,
  localModelStatusToCapabilityStatus,
  runLocalPrompt,
  type LocalModelStatusPayload
} from "../localModels/localModelStatus";
import StatusPill from "./StatusPill";

export default function LocalModelPanel() {
  const [status, setStatus] = useState<LocalModelStatusPayload>(fallbackLocalModelStatus);
  const [statusSource, setStatusSource] = useState("Using local model fallback status.");
  const [prompt, setPrompt] = useState("Summarize this local Sparkbot note in one sentence.");
  const [model, setModel] = useState("");
  const [responseText, setResponseText] = useState("");
  const [runMessage, setRunMessage] = useState("Local prompt calls are disabled until the backend is explicitly enabled.");

  const refreshStatus = async () => {
    try {
      const nextStatus = await fetchLocalModelStatus();
      setStatus(nextStatus);
      setStatusSource("Using backend local model status.");
      setRunMessage(nextStatus.local_models_enabled ? "Local prompt calls are enabled for localhost Ollama only." : "Local prompt calls are disabled until the backend is explicitly enabled.");
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
  }, []);

  const promptEnabled = status.local_models_enabled && status.prompt_calls === "enabled-local-only";

  const submitPrompt = async (event: FormEvent) => {
    event.preventDefault();
    if (!promptEnabled) return;
    try {
      const result = await runLocalPrompt(prompt, model);
      setResponseText(result.response);
      setRunMessage("Local prompt completed through localhost Ollama. No external provider was called.");
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
          Local Ollama model
          <input value={model} onChange={(event) => setModel(event.target.value)} placeholder="llama3.2" disabled={!promptEnabled} />
        </label>
        <label>
          Local prompt
          <textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} disabled={!promptEnabled} />
        </label>
        <div className="local-action-row">
          <button type="submit" disabled={!promptEnabled}>Run local prompt</button>
          <button type="button" onClick={refreshStatus}>Refresh</button>
        </div>
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
