import { useEffect, useState } from "react";

import {
  API_BASE_URL,
  fetchBackendHealth,
  fetchWorkstationState,
  type HealthPayload,
  type WorkstationState
} from "../api";

type LoadState = "loading" | "ready" | "error";

export default function ControlsSurface() {
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [workstation, setWorkstation] = useState<WorkstationState | null>(null);
  const [health, setHealth] = useState<HealthPayload | null>(null);
  const [message, setMessage] = useState("Loading setup controls...");
  const [error, setError] = useState<string | null>(null);

  async function loadData() {
    setLoadState("loading");
    setError(null);
    try {
      const [state, backendHealth] = await Promise.all([fetchWorkstationState(), fetchBackendHealth()]);
      setWorkstation(state);
      setHealth(backendHealth);
      setLoadState("ready");
      setMessage("Controls setup view synced with local backend configuration.");
    } catch (caught) {
      setLoadState("error");
      setError(caught instanceof Error ? caught.message : "Controls backend is unavailable.");
      setMessage("Start the local backend to inspect setup and capability state.");
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  const controls = workstation?.controls;
  const configuredProviders = controls?.providers.filter((provider) => provider.configured).length ?? 0;

  return (
    <section className="controls-surface" aria-label="Sparkbot Controls">
      <header className="command-header">
        <div>
          <p className="eyebrow">Controls</p>
          <h2>Controls Setup</h2>
          <p>Local setup, backend reachability, provider readiness, and public capability limits. Configuration edits live in Command Center.</p>
        </div>
        <div className="command-header-actions">
          <span className={`status-badge ${loadState === "ready" ? "status-worksToday" : loadState === "loading" ? "status-preview" : "status-notImplemented"}`}>
            {loadState === "ready" ? "Backend synced" : loadState === "loading" ? "Syncing" : "Backend needed"}
          </span>
          <button type="button" onClick={loadData}>Refresh</button>
        </div>
      </header>

      <div className="command-message" role="status">
        <span>{message}</span>
        <span>API base URL: {API_BASE_URL}</span>
      </div>
      {error ? <div className="command-error" role="alert">{error}</div> : null}

      <section className="command-grid" aria-label="Setup status">
        <article className="command-panel command-panel-wide">
          <div className="command-panel-heading">
            <p className="eyebrow">Setup</p>
            <h3>Local readiness</h3>
            <p>Controls reports what is configured. It does not call models, send connector messages, run files, or start background work.</p>
          </div>
          <dl className="mini-metrics">
            <div><dt>Backend</dt><dd>{health?.status || (loadState === "ready" ? "online" : "needs check")}</dd></div>
            <div><dt>Service</dt><dd>{health?.service || "local backend"}</dd></div>
            <div><dt>Mode</dt><dd>{health?.mode || "local"}</dd></div>
            <div><dt>Providers ready</dt><dd>{configuredProviders}</dd></div>
            <div><dt>PIN</dt><dd>{controls?.pin_configured ? "configured" : "not configured"}</dd></div>
            <div><dt>Storage</dt><dd>{workstation?.storage.type || "sqlite"}</dd></div>
          </dl>
        </article>
      </section>

      <section className="command-grid" aria-label="Capability limits">
        <article className="command-panel">
          <div className="command-panel-heading">
            <p className="eyebrow">Provider setup</p>
            <h3>Routes and credentials</h3>
            <p>Provider credentials stay server-side. Chat uses local acknowledgements and Round Table uses provider-safe local turns until real provider execution is added.</p>
          </div>
          <div className="context-list">
            {(controls?.providers || []).map((provider) => (
              <p key={provider.id}>
                <strong>{provider.label}</strong> {provider.configured || provider.models_available ? "ready for configuration" : "needs setup"}
              </p>
            ))}
          </div>
        </article>

        <article className="command-panel">
          <div className="command-panel-heading">
            <p className="eyebrow">Guarded capabilities</p>
            <h3>Deferred action paths</h3>
            <p>Anything destructive, external, privileged, scheduled, or action-capable must use the shared Guardian confirmation boundary first.</p>
          </div>
          <div className="connector-grid">
            {["Real provider execution", "Connector sends", "File/process execution", "Scheduler jobs", "Physical device control"].map((item) => (
              <div className="connector-card" key={item}>
                <strong>{item}</strong>
                <span>Deferred. No public runtime action is active in this branch.</span>
              </div>
            ))}
          </div>
        </article>
      </section>
    </section>
  );
}
