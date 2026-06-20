import { useEffect, useState } from "react";

import { fetchTaskLanesStatus, type TaskLanesStatusPayload } from "../api";
import { fallbackTaskLanesStatus, taskLanePreviewSummary, taskLaneRoles } from "../taskLanes/taskLaneStatus";
import { formatShellStatus } from "./ShellNavigation";

type TaskLaneStatusState = {
  payload: TaskLanesStatusPayload;
  sourceLabel: string;
};

const fallbackTaskLanesStatusState: TaskLaneStatusState = {
  payload: fallbackTaskLanesStatus,
  sourceLabel: "Using local Task Lane status fallback."
};

function formatImplementationStatus(status: string) {
  return status.replace(/-/g, " ");
}

export default function TaskLanePreview() {
  const [taskLanesStatusState, setTaskLanesStatusState] = useState<TaskLaneStatusState>(
    fallbackTaskLanesStatusState
  );

  useEffect(() => {
    const controller = new AbortController();

    fetchTaskLanesStatus(controller.signal)
      .then((payload) => {
        setTaskLanesStatusState({
          payload,
          sourceLabel: "Using backend Task Lane status."
        });
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }
        setTaskLanesStatusState(fallbackTaskLanesStatusState);
      });

    return () => controller.abort();
  }, []);

  const { payload } = taskLanesStatusState;

  return (
    <section className="work-lane-preview section-panel" id="work-lanes" aria-labelledby="work-lanes-heading">
      <div className="work-lane-copy">
        <p className="eyebrow">{formatShellStatus(payload.status)}</p>
        <h2 id="work-lanes-heading">Task Lane Preview</h2>
        <p>{taskLanePreviewSummary}</p>
        <p className="capabilities-source">{taskLanesStatusState.sourceLabel}</p>
      </div>

      <dl className="work-lane-status-grid" aria-label="Task Lane implementation status">
        <div>
          <dt>Task runtime</dt>
          <dd>{formatImplementationStatus(payload.task_runtime)}</dd>
        </div>
        <div>
          <dt>Task persistence</dt>
          <dd>{formatImplementationStatus(payload.task_persistence)}</dd>
        </div>
        <div>
          <dt>Scheduler</dt>
          <dd>{formatImplementationStatus(payload.scheduler)}</dd>
        </div>
        <div>
          <dt>Background jobs</dt>
          <dd>{formatImplementationStatus(payload.background_jobs)}</dd>
        </div>
        <div>
          <dt>Notifications</dt>
          <dd>{formatImplementationStatus(payload.notifications)}</dd>
        </div>
      </dl>

      <div className="work-lane-layout" aria-label="Read-only Task Lane preview">
        {payload.lanes.map((lane) => (
          <article className="work-lane-card" key={lane.id}>
            <div className="work-lane-card-top">
              <h3>{lane.label}</h3>
              <span className={`status-badge status-${lane.status}`}>{formatShellStatus(lane.status)}</span>
            </div>
            <p className="work-lane-role">{taskLaneRoles.get(lane.id) ?? "Planned lane"}</p>
            <p>{lane.notes}</p>
          </article>
        ))}
      </div>

      <p className="work-lane-note">
        The preview is read-only. It does not create tasks, store tasks, run a scheduler, start background jobs, send
        notifications, execute workflows, save lane state, or mutate files.
      </p>
    </section>
  );
}
