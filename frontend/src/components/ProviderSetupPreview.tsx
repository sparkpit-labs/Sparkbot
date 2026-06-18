import { useEffect, useState } from "react";

import { fetchProviderConfigStatus, type ProviderConfigStatusPayload } from "../api";
import { fallbackProviderConfigStatus, providerPreviewSummary } from "../providers/providerSetupStatus";
import { formatShellStatus } from "./ShellNavigation";

type ProviderStatusState = {
  payload: ProviderConfigStatusPayload;
  sourceLabel: string;
};

const fallbackProviderStatusState: ProviderStatusState = {
  payload: fallbackProviderConfigStatus,
  sourceLabel: "Using local provider status fallback."
};

function formatImplementationStatus(status: string) {
  return status.replace(/-/g, " ");
}

export default function ProviderSetupPreview() {
  const [providerStatusState, setProviderStatusState] = useState<ProviderStatusState>(fallbackProviderStatusState);

  useEffect(() => {
    const controller = new AbortController();

    fetchProviderConfigStatus(controller.signal)
      .then((payload) => {
        setProviderStatusState({
          payload,
          sourceLabel: "Using backend provider configuration status."
        });
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }
        setProviderStatusState(fallbackProviderStatusState);
      });

    return () => controller.abort();
  }, []);

  const { payload } = providerStatusState;

  return (
    <section className="provider-setup-preview section-panel" id="provider-setup" aria-labelledby="provider-setup-heading">
      <div className="provider-setup-copy">
        <p className="eyebrow">{formatShellStatus(payload.status)}</p>
        <h2 id="provider-setup-heading">Provider Setup Preview</h2>
        <p>{providerPreviewSummary}</p>
        <p className="capabilities-source">{providerStatusState.sourceLabel}</p>
      </div>

      <dl className="provider-status-grid" aria-label="Provider configuration implementation status">
        <div>
          <dt>Credential storage</dt>
          <dd>{formatImplementationStatus(payload.credential_storage)}</dd>
        </div>
        <div>
          <dt>Provider calls</dt>
          <dd>{formatImplementationStatus(payload.provider_calls)}</dd>
        </div>
        <div>
          <dt>Model routing</dt>
          <dd>{formatImplementationStatus(payload.model_routing)}</dd>
        </div>
      </dl>

      <div className="provider-layout" aria-label="Read-only provider setup preview">
        {payload.providers.map((provider) => (
          <article className="provider-card" key={provider.id}>
            <div className="provider-card-top">
              <h3>{provider.label}</h3>
              <span className={`status-badge status-${provider.status}`}>{formatShellStatus(provider.status)}</span>
            </div>
            <p>{provider.notes}</p>
          </article>
        ))}
      </div>

      <p className="provider-note">
        This preview includes no API key fields, no password or token fields, no save actions, no test-connection
        actions, and no provider calls.
      </p>
    </section>
  );
}
