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
    name: "Round Table",
    status: "skeleton",
    summary: "Read-only Round Table preview surface is present without meeting or model behavior."
  },
  {
    name: "Provider setup",
    status: "planned",
    summary: "Provider configuration and runtime wiring are planned for later phases."
  },
  {
    name: "Guardian-gated controls",
    status: "planned",
    summary: "Guarded control surfaces are planned and are not active in this branch."
  }
];

export const workstationRoadmapItems: string[] = [
  "Define workstation view structure with stable public contracts.",
  "Expand Round Table preview surfaces only after public interaction contracts are documented.",
  "Prepare provider and guardrail integration points without runtime activation."
];
