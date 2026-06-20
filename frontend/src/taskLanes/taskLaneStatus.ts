import type { TaskLaneStatusItem, TaskLanesStatusPayload } from "../api";
import type { ShellSectionStatus } from "../workstation/shellSections";

export type TaskLaneStatus = Extract<ShellSectionStatus, "preview" | "planned">;

export type TaskLane = TaskLaneStatusItem & {
  role: string;
};

export const taskLaneItems: TaskLane[] = [
  {
    id: "inbox",
    label: "Inbox Lane",
    role: "Future work intake preview",
    status: "preview",
    notes: "Read-only lane preview. No tasks are stored or executed."
  },
  {
    id: "planned",
    label: "Planned Lane",
    role: "Planning workflow placeholder",
    status: "planned",
    notes: "Future planning lane. No scheduler is implemented."
  },
  {
    id: "active",
    label: "Active Lane",
    role: "Active work placeholder",
    status: "planned",
    notes: "Future active work lane. No task runtime is implemented."
  },
  {
    id: "review",
    label: "Review Lane",
    role: "Review workflow placeholder",
    status: "planned",
    notes: "Future review lane. No workflow runtime is implemented."
  }
];

export const fallbackTaskLanesStatus: TaskLanesStatusPayload = {
  service: "sparkbot-server",
  mode: "local",
  status: "preview",
  task_runtime: "not-implemented",
  task_persistence: "not-implemented",
  scheduler: "not-implemented",
  background_jobs: "not-implemented",
  notifications: "not-implemented",
  lanes: taskLaneItems.map(({ id, label, status, notes }) => ({ id, label, status, notes }))
};

export const taskLaneRoles = new Map(taskLaneItems.map((lane) => [lane.id, lane.role]));

export const taskLanePreviewSummary =
  "Task lanes show future workflow organization, but this public surface is read-only and does not create, store, schedule, notify, or execute tasks.";
