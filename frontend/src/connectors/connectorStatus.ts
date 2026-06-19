import type { ConnectorStatusPayload, ConnectorStatusItem } from "../api";

export type ConnectorPreviewItem = ConnectorStatusItem;

export const connectorPreviewItems: ConnectorPreviewItem[] = [
  {
    id: "messaging",
    label: "Messaging connectors",
    status: "guarded-future",
    notes: "Messaging connectors are planned for future guarded configuration. No outbound sends are implemented."
  },
  {
    id: "calendar",
    label: "Calendar connectors",
    status: "guarded-future",
    notes: "Calendar connectors are planned for future guarded configuration."
  },
  {
    id: "email",
    label: "Email connectors",
    status: "guarded-future",
    notes: "Email connectors are planned for future guarded configuration. No external sends are implemented."
  },
  {
    id: "files",
    label: "File connectors",
    status: "guarded-future",
    notes: "File connectors are planned for future guarded configuration. No file mutation is implemented."
  }
];

export const fallbackConnectorStatus: ConnectorStatusPayload = {
  service: "sparkbot-server",
  mode: "local",
  status: "guarded-future",
  connectors_enabled: false,
  outbound_actions: "not-implemented",
  credential_storage: "not-implemented",
  audit_trail: "planned",
  connectors: connectorPreviewItems
};

export const connectorPreviewSummary =
  "Connector status is read-only. Connectors are disabled, outbound actions are not implemented, and credentials are not handled.";
