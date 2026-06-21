import { useEffect, useState } from "react";

import { fetchLocalRuntimeSettings, type LocalRuntimeSettingsPayload } from "../localWorkstation/localRuntimeSettings";

function displayValue(value: string | null | undefined) {
  return value && value.trim() ? value : "Not configured";
}

export default function LocalRuntimeSettingsPanel() {
  const [settings, setSettings] = useState<LocalRuntimeSettingsPayload | null>(null);
  const [statusMessage, setStatusMessage] = useState("Loading local runtime settings.");

  useEffect(() => {
    let mounted = true;
    fetchLocalRuntimeSettings()
      .then((payload) => {
        if (!mounted) return;
        setSettings(payload);
        setStatusMessage("Using backend local runtime settings.");
      })
      .catch(() => {
        if (!mounted) return;
        setStatusMessage("Local runtime settings are unavailable until the local backend is running.");
      });
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <section className="local-runtime-panel" id="local-runtime-settings" aria-labelledby="local-runtime-settings-heading">
      <div className="local-runtime-heading">
        <p className="eyebrow">Available locally</p>
        <h2 id="local-runtime-settings-heading">Local Runtime Settings</h2>
        <p>Read-only status for the local data path and env-driven Ollama configuration.</p>
        <p className="capabilities-source">{statusMessage}</p>
      </div>

      <div className="local-model-status-grid">
        <article className="local-runtime-card">
          <h3>Data directory</h3>
          <dl className="runtime-definition-list">
            <div>
              <dt>Configured by</dt>
              <dd>{settings?.data_directory.configured_by ?? "Unknown"}</dd>
            </div>
            <div>
              <dt>Path</dt>
              <dd><code>{settings?.data_directory.display_path ?? "Unavailable"}</code></dd>
            </div>
          </dl>
        </article>

        <article className="local-runtime-card">
          <h3>SQLite file</h3>
          <dl className="runtime-definition-list">
            <div>
              <dt>Filename</dt>
              <dd>{settings?.sqlite_database.filename ?? "Unavailable"}</dd>
            </div>
            <div>
              <dt>Path</dt>
              <dd><code>{settings?.sqlite_database.display_path ?? "Unavailable"}</code></dd>
            </div>
          </dl>
        </article>

        <article className="local-runtime-card">
          <h3>Local models</h3>
          <dl className="runtime-definition-list">
            <div>
              <dt>Enabled</dt>
              <dd>{settings ? (settings.local_models.enabled ? "true" : "false") : "Unknown"}</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>{settings?.local_models.status ?? "Unknown"}</dd>
            </div>
            <div>
              <dt>Adapter</dt>
              <dd>{settings?.local_models.adapter ?? "Unknown"}</dd>
            </div>
          </dl>
        </article>

        <article className="local-runtime-card">
          <h3>Ollama config</h3>
          <dl className="runtime-definition-list">
            <div>
              <dt>Base URL</dt>
              <dd><code>{displayValue(settings?.local_models.base_url)}</code></dd>
            </div>
            <div>
              <dt>Model</dt>
              <dd>{displayValue(settings?.local_models.configured_model)}</dd>
            </div>
            <div>
              <dt>Policy</dt>
              <dd>{settings?.local_models.base_url_policy ?? "localhost-only"}</dd>
            </div>
          </dl>
        </article>
      </div>

      <div className="local-runtime-card">
        <h3>Settings boundary</h3>
        <p>Configuration remains environment-driven and read-only in this panel.</p>
        <p>No credential fields, secret save buttons, cloud sync, external upload, or provider test call is implemented.</p>
      </div>
    </section>
  );
}
