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
    summary: "Product shell layout, section selector, and status model exist as a read-only baseline."
  },
  {
    name: "Chat shell",
    status: "preview",
    summary: "Read-only Chat Shell preview is visible without message handling, storage, or model behavior."
  },
  {
    name: "Round Table",
    status: "preview",
    summary: "Read-only Round Table preview surface is present without meeting or model behavior."
  },
  {
    name: "Provider setup",
    status: "planned",
    summary: "Read-only Provider Setup preview surface is present without credential handling or provider calls."
  },
  {
    name: "Guardian-gated controls",
    status: "planned",
    summary: "Read-only Guardian Controls preview surface is present without approvals, enforcement, or sensitive actions."
  }
];

export const workstationRoadmapItems: string[] = [
  "Define workstation view structure with stable public contracts.",
  "Document chat interaction contracts before enabling message handling or model behavior.",
  "Expand Round Table preview surfaces only after public interaction contracts are documented.",
  "Document provider setup contracts before enabling credential or network behavior.",
  "Document Guardian control contracts before enabling approval or enforcement behavior.",
  "Prepare provider and guardrail integration points without runtime activation."
];
