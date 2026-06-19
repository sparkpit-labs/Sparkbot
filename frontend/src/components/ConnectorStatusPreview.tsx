import { useEffect, useState } from "react";

import { fetchConnectorStatus, type ConnectorStatusPayload } from "../api";
import { connectorPreviewSummary, fallbackConnectorStatus } from "../connectors/connectorStatus";
import { formatShellStatus } from "./ShellNavigation";

type ConnectorStatusState = {
  payload: ConnectorStatusPayload;
  sourceLabel: string;
};

const fallbackConnectorStatusState: ConnectorStatusState = {
  payload: fallbackConnectorStatus,
  sourceLabel: "Using local connector status fallback."
};

function formatImplementationStatus(status: string) {
  return status.replace(/-/g, " ");
}

function formatEnabledStatus(enabled: boolean) {
  return enabled ? "enabled" : "disabled";
}

export default function ConnectorStatusPreview() {
  const [connectorStatusState, setConnectorStatusState] = useState<ConnectorStatusState>(fallbackConnectorStatusState);

  useEffect(() => {
    const controller = new AbortController();

    fetchConnectorStatus(controller.signal)
      .then((payload) => {
        setConnectorStatusState({
          payload,
          sourceLabel: "Using backend connector status."
        });
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }
        setConnectorStatusState(fallbackConnectorStatusState);
      });

    return () => controller.abort();
  }, []);

  const { payload } = connectorStatusState;

  return (
    <section className="connector-status-preview section-panel" id="connector-status" aria-labelledby="connector-status-heading">
      <div className="connector-status-copy">
        <p className="eyebrow">{formatShellStatus(payload.status)}</p>
        <h2 id="connector-status-heading">Connector Status Preview</h2>
        <p>{connectorPreviewSummary}</p>
        <p className="capabilities-source">{connectorStatusState.sourceLabel}</p>
      </div>

      <dl className="connector-status-grid" aria-label="Connector implementation status">
        <div>
          <dt>Connectors enabled</dt>
          <dd>{formatEnabledStatus(payload.connectors_enabled)}</dd>
        </div>
        <div>
          <dt>Outbound actions</dt>
          <dd>{formatImplementationStatus(payload.outbound_actions)}</dd>
        </div>
        <div>
          <dt>Credential storage</dt>
          <dd>{formatImplementationStatus(payload.credential_storage)}</dd>
        </div>
        <div>
          <dt>Audit trail</dt>
          <dd>{formatImplementationStatus(payload.audit_trail)}</dd>
        </div>
      </dl>

      <div className="connector-layout" aria-label="Read-only connector status preview">
        {payload.connectors.map((connector) => (
          <article className="connector-card" key={connector.id}>
            <div className="connector-card-top">
              <h3>{connector.label}</h3>
              <span className={`status-badge status-${connector.status}`}>{formatShellStatus(connector.status)}</span>
            </div>
            <p>{connector.notes}</p>
          </article>
        ))}
      </div>

      <p className="connector-note">
        This preview includes no credential fields, no token fields, no save actions, no test actions, no connector calls,
        no messaging sends, and no external sends.
      </p>
    </section>
  );
}
