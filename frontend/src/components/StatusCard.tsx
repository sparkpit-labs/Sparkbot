import type { WorkstreamStatus } from "../workstation/workstationStatus";
import StatusPill from "./StatusPill";

type StatusCardProps = {
  name: string;
  status: WorkstreamStatus;
  summary: string;
};

export default function StatusCard({ name, status, summary }: StatusCardProps) {
  return (
    <article className="status-card">
      <div className="status-card-top">
        <h3>{name}</h3>
        <StatusPill status={status} />
      </div>
      <p>{summary}</p>
    </article>
  );
}
