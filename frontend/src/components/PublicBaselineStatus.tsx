import type { ShellSectionStatus } from "../workstation/shellSections";
import type { WorkstationStatusItem } from "../workstation/workstationStatus";
import StatusPill from "./StatusPill";

type PublicBaselineStatusProps = {
  apiBaseUrl: string;
  capabilityItems: WorkstationStatusItem[];
  capabilitySourceLabel: string;
  healthPhase: "idle" | "loading" | "online" | "offline";
  healthMessage: string;
};

type SurfaceStatus = {
  id: string;
  label: string;
  endpoint: string;
  status: ShellSectionStatus;
  summary: string;
};

const surfaceStatuses: SurfaceStatus[] = [
  {
    id: "health",
    label: "Health",
    endpoint: "GET /health",
    status: "available",
    summary: "Read-only backend health check."
  },
  {
    id: "capabilities",
    label: "Capabilities",
    endpoint: "GET /capabilities",
    status: "available",
    summary: "Public capability status contract."
  },
  {
    id: "local-chat",
    label: "Local Chat",
    endpoint: "GET /local/chat/sessions",
    status: "available",
    summary: "Local chat drafts and operator notes stored in SQLite."
  },
  {
    id: "local-memory-notes",
    label: "Local Memory",
    endpoint: "GET /local/memory-notes",
    status: "available",
    summary: "Local notes stored without model calls or cloud sync."
  },
  {
    id: "local-work-cards",
    label: "Local Work Cards",
    endpoint: "GET /local/work-lane-cards",
    status: "available",
    summary: "Local planning cards with no scheduler or execution path."
  },
  {
    id: "local-data-export",
    label: "Local Export",
    endpoint: "GET /local/export",
    status: "available",
    summary: "Read-only JSON export for local Workstation backup and testing."
  },
  {
    id: "local-models",
    label: "Local Models",
    endpoint: "GET /local-models/status",
    status: "disabled-by-default",
    summary: "Localhost-only Ollama adapter; prompt endpoint is disabled unless explicitly enabled."
  },
  {
    id: "chat",
    label: "Chat",
    endpoint: "GET /chat/status",
    status: "preview",
    summary: "No chat runtime, persistence, streaming, provider routing, or send action."
  },
  {
    id: "round-table",
    label: "Round Table",
    endpoint: "GET /round-table/status",
    status: "preview",
    summary: "No meeting engine, agent orchestration, model calls, or turn persistence."
  },
  {
    id: "model-seats",
    label: "Model Seats",
    endpoint: "GET /model-seats/status",
    status: "preview",
    summary: "No model assignment, routing, calls, credentials, or seat persistence."
  },
  {
    id: "work-lanes",
    label: "Task Lanes",
    endpoint: "GET /work-lanes/status",
    status: "preview",
    summary: "No scheduler, background jobs, notifications, task execution, or persistence."
  },
  {
    id: "provider-config",
    label: "Provider Config",
    endpoint: "GET /provider-config/status",
    status: "preview",
    summary: "No credential handling, provider calls, or model routing."
  },
  {
    id: "connector-status",
    label: "Connector Status",
    endpoint: "GET /connector-status",
    status: "guarded-future",
    summary: "Connectors disabled; no outbound actions or credential storage."
  },
  {
    id: "guardian-status",
    label: "Guardian Status",
    endpoint: "GET /guardian/status",
    status: "preview",
    summary: "No runtime enforcement, approvals, or policy decisions."
  }
];

const orderedStatuses: ShellSectionStatus[] = ["available", "preview", "planned", "disabled-by-default", "guarded-future"];

function countStatuses(items: WorkstationStatusItem[]) {
  return orderedStatuses.map((status) => ({
    status,
    count: items.filter((item) => item.status === status).length
  }));
}

function healthLabel(phase: PublicBaselineStatusProps["healthPhase"]) {
  if (phase === "online") return "Online";
  if (phase === "offline") return "Offline";
  if (phase === "loading") return "Checking";
  return "Not checked";
}

export default function PublicBaselineStatus({
  apiBaseUrl,
  capabilityItems,
  capabilitySourceLabel,
  healthPhase,
  healthMessage
}: PublicBaselineStatusProps) {
  return (
    <section className="public-baseline-panel" aria-labelledby="public-baseline-heading">
      <div className="public-baseline-heading">
        <p className="eyebrow">Public baseline</p>
        <h2 id="public-baseline-heading">System Status</h2>
        <p>Read-only dashboard for the current local shell. It summarizes what is available and what remains preview, planned, or guarded.</p>
      </div>

      <div className="baseline-overview-grid">
        <article className="baseline-primary-card">
          <span className={`health-dot health-${healthPhase}`} aria-hidden="true" />
          <div>
            <h3>Backend health</h3>
            <p>{healthLabel(healthPhase)}</p>
            <small>{healthMessage}</small>
          </div>
        </article>

        <article className="baseline-primary-card">
          <span className="health-dot health-online" aria-hidden="true" />
          <div>
            <h3>API base</h3>
            <p>{apiBaseUrl}</p>
            <small>Local read-only status requests only.</small>
          </div>
        </article>

        <article className="baseline-primary-card">
          <span className="health-dot health-idle" aria-hidden="true" />
          <div>
            <h3>Capability source</h3>
            <p>{capabilitySourceLabel}</p>
            <small>{capabilityItems.length} public capability entries loaded.</small>
          </div>
        </article>
      </div>

      <div className="baseline-count-grid" aria-label="Capability status counts">
        {countStatuses(capabilityItems).map(({ status, count }) => (
          <div className="baseline-count-card" key={status}>
            <StatusPill status={status} />
            <strong>{count}</strong>
          </div>
        ))}
      </div>

      <div className="baseline-surface-grid" aria-label="Read-only status surfaces">
        {surfaceStatuses.map((surface) => (
          <article className="baseline-surface-card" key={surface.id}>
            <div className="baseline-surface-top">
              <h3>{surface.label}</h3>
              <StatusPill status={surface.status} />
            </div>
            <p className="baseline-endpoint">{surface.endpoint}</p>
            <p>{surface.summary}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
