import { useState } from "react";

import ChatRuntime from "./ChatRuntime";
import GuardianControlsPreview from "./GuardianControlsPreview";
import RoadmapCard from "./RoadmapCard";
import RoundTablePreview from "./RoundTablePreview";
import ShellNavigation from "./ShellNavigation";
import StatusCard from "./StatusCard";
import { workstationRoadmapItems, workstationStatusItems } from "../workstation/workstationStatus";

export default function WorkstationShell() {
  const [activeSectionId, setActiveSectionId] = useState("workstation-overview");

  return (
    <section className="workstation-shell" aria-label="Sparkbot workstation">
      <div className="workstation-shell-header">
        <h2>Workstation</h2>
        <p>
          A local-first workstation for chat and provider routing. Round Table and Guardian controls remain gated for
          later runtime slices.
        </p>
      </div>

      <div className="workstation-layout">
        <ShellNavigation activeSectionId={activeSectionId} onSelectSection={setActiveSectionId} />

        <div className="workstation-content">
          <section className="section-panel" id="workstation-overview" aria-labelledby="workstation-overview-heading">
            <div className="section-panel-heading">
              <p className="eyebrow">Works Today</p>
              <h2 id="workstation-overview-heading">Workstation Overview</h2>
              <p>Current public runtime status across the visible surfaces.</p>
            </div>

            <div className="status-grid">
              {workstationStatusItems.map((item) => (
                <StatusCard key={item.name} name={item.name} status={item.status} summary={item.summary} />
              ))}
            </div>
          </section>

          <ChatRuntime />
          <RoundTablePreview />
          <GuardianControlsPreview />

          <div className="roadmap-grid">
            <RoadmapCard title="Planned Follow-up Work" items={workstationRoadmapItems} />
          </div>
        </div>
      </div>
    </section>
  );
}
