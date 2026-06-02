import { shellSections, shellStatusLabels, type ShellSectionStatus } from "../workstation/shellSections";

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
        <h3>Workstation Sections</h3>
        <p>Select a section to inspect the active local surfaces.</p>
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
            <span className={`status-badge status-${section.status}`}>{formatShellStatus(section.status)}</span>
            <span className="shell-navigation-summary">{section.summary}</span>
          </button>
        ))}
      </div>

      <dl className="status-legend" aria-label="Status label meanings">
        <div>
          <dt>Works Today</dt>
          <dd>Visible local runtime or utility exists now.</dd>
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
          <dt>Not Implemented</dt>
          <dd>No public runtime capability is active in this slice.</dd>
        </div>
      </dl>
    </aside>
  );
}
