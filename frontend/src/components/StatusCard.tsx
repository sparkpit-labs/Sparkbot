import type { WorkstreamStatus } from "../workstation/workstationStatus";
import { formatShellStatus } from "./ShellNavigation";

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
        <span className={`status-badge status-${status}`}>{formatShellStatus(status)}</span>
      </div>
      <p>{summary}</p>
    </article>
  );
}
