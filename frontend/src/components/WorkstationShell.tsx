import GuardianControlsPreview from "./GuardianControlsPreview";
import ProviderSetupPreview from "./ProviderSetupPreview";
import RoadmapCard from "./RoadmapCard";
import RoundTablePreview from "./RoundTablePreview";
import StatusCard from "./StatusCard";
import { workstationRoadmapItems, workstationStatusItems } from "../workstation/workstationStatus";

export default function WorkstationShell() {
  return (
    <section className="workstation-shell" aria-label="Workstation shell status">
      <div className="workstation-shell-header">
        <h2>Workstation Shell</h2>
        <p>
          This product slice establishes a local workstation shell structure and status model without enabling
          orchestration, chat, model execution, or tool runtime actions.
        </p>
      </div>

      <div className="status-grid">
        {workstationStatusItems.map((item) => (
          <StatusCard key={item.name} name={item.name} status={item.status} summary={item.summary} />
        ))}
      </div>

      <RoundTablePreview />
      <ProviderSetupPreview />
      <GuardianControlsPreview />

      <div className="roadmap-grid">
        <RoadmapCard title="Planned Follow-up Work" items={workstationRoadmapItems} />
      </div>
    </section>
  );
}
