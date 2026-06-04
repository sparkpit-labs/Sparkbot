import type { ShellSectionStatus } from "./shellSections";

export type WorkstreamStatus = ShellSectionStatus;

export type WorkstationStatusItem = {
  name: string;
  status: WorkstreamStatus;
  summary: string;
};

export const workstationStatusItems: WorkstationStatusItem[] = [
  {
    name: "Server baseline",
    status: "worksToday",
    summary: "FastAPI health endpoint and backend validation path are present."
  },
  {
    name: "Frontend shell",
    status: "worksToday",
    summary: "Public React and TypeScript shell with build and test workflows is present."
  },
  {
    name: "Workstation shell",
    status: "worksToday",
    summary: "Product shell layout, section selector, and backend-backed status model are present."
  },
  {
    name: "Chat shell",
    status: "worksToday",
    summary: "Backend-backed Chat sessions, shared context, and configured-provider execution are active."
  },
  {
    name: "Round Table",
    status: "worksToday",
    summary: "Backend-backed Round Table sessions, shared context, assignments, summaries, and configured-provider turns are active when available."
  },
  {
    name: "Provider setup",
    status: "worksToday",
    summary: "Command Center stores provider credentials server-side and reports provider readiness."
  },
  {
    name: "Guardian-gated controls",
    status: "worksToday",
    summary: "Guardian confirmations and fail-closed protected-action blocks are active for current guarded paths."
  }
];

export const workstationRoadmapItems: string[] = [
  "Define workstation view structure with stable public contracts.",
  "Keep chat provider execution narrow, logged, and server-side.",
  "Keep Round Table provider execution text-only with deterministic fallback.",
  "Keep provider setup server-side and redacted in browser-visible state.",
  "Expand Guardian enforcement only through action-bound confirmations.",
  "Do not add connector, scheduler, file/process, terminal, or device execution without new Guardian gates."
];
