import { shellSections, shellStatusLabels, type ShellSectionStatus } from "../workstation/shellSections";
import StatusPill from "./StatusPill";

type ShellNavigationProps = {
  activeSectionId: string;
  onSelectSection: (sectionId: string) => void;
};

export function formatShellStatus(status: ShellSectionStatus) {
  return shellStatusLabels[status];
}

export default function ShellNavigation({ activeSectionId, onSelectSection }: ShellNavigationProps) {
  return (
    <aside className="shell-navigation" aria-label="Workstation sections">
      <div className="shell-navigation-header">
        <h3>Shell Sections</h3>
        <p>Use this read-only selector to scan the current public surfaces.</p>
      </div>

      <div className="shell-navigation-list" role="list">
        {shellSections.map((section) => (
          <button
            aria-current={activeSectionId === section.id ? "true" : undefined}
            className="shell-navigation-item"
            key={section.id}
            onClick={() => onSelectSection(section.id)}
            type="button"
          >
            <span className="shell-navigation-label">{section.label}</span>
            <StatusPill status={section.status} />
            <span className="shell-navigation-summary">{section.summary}</span>
          </button>
        ))}
      </div>

      <dl className="status-legend" aria-label="Status label meanings">
        <div>
          <dt>Available</dt>
          <dd>Implemented in the public repo, validated, documented, and safe by default.</dd>
        </div>
        <div>
          <dt>Preview</dt>
          <dd>Shape is visible, but runtime behavior is intentionally inactive.</dd>
        </div>
        <div>
          <dt>Planned</dt>
          <dd>Public direction is shown without input handling or integrations.</dd>
        </div>
        <div>
          <dt>Disabled by default</dt>
          <dd>Future active behavior must stay off until explicitly enabled and tested.</dd>
        </div>
        <div>
          <dt>Guarded future</dt>
          <dd>Not implemented; future runtime work requires contract gates and review.</dd>
        </div>
      </dl>
    </aside>
  );
}
