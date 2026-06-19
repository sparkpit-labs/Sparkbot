import { shellStatusLabels, type ShellSectionStatus } from "../workstation/shellSections";

type StatusPillProps = {
  status: ShellSectionStatus;
};

export default function StatusPill({ status }: StatusPillProps) {
  return <span className={`status-badge status-${status}`}>{shellStatusLabels[status]}</span>;
}
