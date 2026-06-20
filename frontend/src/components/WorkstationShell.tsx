import { useState } from "react";

import ChatShellPreview from "./ChatShellPreview";
import ConnectorStatusPreview from "./ConnectorStatusPreview";
import GuardianControlsPreview from "./GuardianControlsPreview";
import ModelSeatPreview from "./ModelSeatPreview";
import ProviderSetupPreview from "./ProviderSetupPreview";
import RoadmapCard from "./RoadmapCard";
import RoundTablePreview from "./RoundTablePreview";
import ShellNavigation from "./ShellNavigation";
import StatusCard from "./StatusCard";
import TaskLanePreview from "./TaskLanePreview";
import { workstationRoadmapItems, workstationStatusItems, type WorkstationStatusItem } from "../workstation/workstationStatus";

type WorkstationShellProps = {
  statusItems?: WorkstationStatusItem[];
  statusSourceLabel?: string;
};

export default function WorkstationShell({
  statusItems = workstationStatusItems,
  statusSourceLabel = "Using local fallback status list."
}: WorkstationShellProps) {
  const [activeSectionId, setActiveSectionId] = useState("workstation-overview");

  return (
    <section className="workstation-shell" aria-label="Workstation shell status">
      <div className="workstation-shell-header">
        <h2>Workstation Shell</h2>
        <p>
          A read-only operating floor for the public shell. It keeps available checks, preview rooms, setup surfaces,
          and guarded future work visible without enabling orchestration, chat runtime, model execution, or tool actions.
        </p>
      </div>

      <div className="workstation-layout">
        <ShellNavigation activeSectionId={activeSectionId} onSelectSection={setActiveSectionId} />

        <div className="workstation-content">
          <section className="section-panel" id="workstation-overview" aria-labelledby="workstation-overview-heading">
            <div className="section-panel-heading">
              <p className="eyebrow">Capability status</p>
              <h2 id="workstation-overview-heading">Workstation Overview</h2>
              <p>Current public shell status across the visible surfaces, grouped for quick review.</p>
              <p className="capabilities-source">{statusSourceLabel}</p>
            </div>

            <div className="workstation-lane-grid" aria-label="Workstation capability lanes">
              <article className="workstation-lane">
                <h3>Available today</h3>
                <p>Read-only public surfaces that are implemented and validated.</p>
                <div className="status-grid">
                  {statusItems
                    .filter((item) => item.status === "available")
                    .map((item) => (
                      <StatusCard key={item.id} name={item.name} status={item.status} summary={item.summary} />
                    ))}
                </div>
              </article>

              <article className="workstation-lane">
                <h3>Preview workspace</h3>
                <p>Visible product rooms and setup surfaces with runtime behavior intentionally inactive.</p>
                <div className="status-grid">
                  {statusItems
                    .filter((item) => item.status === "preview")
                    .map((item) => (
                      <StatusCard key={item.id} name={item.name} status={item.status} summary={item.summary} />
                    ))}
                </div>
              </article>

              <article className="workstation-lane">
                <h3>Planned and guarded</h3>
                <p>Future work remains planned, disabled by default, or guarded until public contracts are satisfied.</p>
                <div className="status-grid">
                  {statusItems
                    .filter((item) => item.status !== "available" && item.status !== "preview")
                    .map((item) => (
                      <StatusCard key={item.id} name={item.name} status={item.status} summary={item.summary} />
                    ))}
                </div>
              </article>
            </div>
          </section>

          <ChatShellPreview />
          <RoundTablePreview />
          <ModelSeatPreview />
          <TaskLanePreview />
          <ProviderSetupPreview />
          <ConnectorStatusPreview />
          <GuardianControlsPreview />

          <div className="roadmap-grid">
            <RoadmapCard title="Planned Follow-up Work" items={workstationRoadmapItems} />
          </div>
        </div>
      </div>
    </section>
  );
}
