export type WorkstreamStatus = "implemented" | "skeleton" | "planned";

export type WorkstationStatusItem = {
  name: string;
  status: WorkstreamStatus;
  summary: string;
};

export const workstationStatusItems: WorkstationStatusItem[] = [
  {
    name: "Server baseline",
    status: "implemented",
    summary: "FastAPI health endpoint and backend validation path are present."
  },
  {
    name: "Frontend shell",
    status: "implemented",
    summary: "Public React and TypeScript shell with build and test workflows is present."
  },
  {
    name: "Workstation shell",
    status: "skeleton",
    summary: "Product shell layout exists as a read-only baseline in this branch."
  },
  {
    name: "Chat shell",
    status: "skeleton",
    summary: "Read-only Chat Shell preview surface is present without message handling or model behavior."
  },
  {
    name: "Round Table",
    status: "skeleton",
    summary: "Read-only Round Table preview surface is present without meeting or model behavior."
  },
  {
    name: "Provider setup",
    status: "skeleton",
    summary: "Read-only Provider Setup preview surface is present without credential handling or provider calls."
  },
  {
    name: "Guardian-gated controls",
    status: "skeleton",
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
