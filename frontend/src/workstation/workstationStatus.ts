import type { PublicCapability, PublicCapabilityStatus } from "../api";
import type { ShellSectionStatus } from "./shellSections";

export type WorkstreamStatus = ShellSectionStatus;

export type WorkstationStatusItem = {
  id: string;
  name: string;
  status: WorkstreamStatus;
  summary: string;
};

export const workstationStatusItems: WorkstationStatusItem[] = [
  {
    id: "backend-health",
    name: "Server baseline",
    status: "worksToday",
    summary: "FastAPI health endpoint and backend validation path are present."
  },
  {
    id: "frontend-shell",
    name: "Frontend shell",
    status: "worksToday",
    summary: "Public React and TypeScript shell with build and test workflows is present."
  },
  {
    id: "workstation",
    name: "Workstation shell",
    status: "worksToday",
    summary: "Product shell layout, section selector, and status model exist as a read-only baseline."
  },
  {
    id: "chat",
    name: "Chat shell",
    status: "preview",
    summary: "Read-only Chat Shell preview is visible without message handling, storage, or model behavior."
  },
  {
    id: "round-table",
    name: "Round Table",
    status: "preview",
    summary: "Read-only Round Table preview surface is present without meeting or model behavior."
  },
  {
    id: "provider-setup",
    name: "Provider setup",
    status: "planned",
    summary: "Read-only Provider Setup preview surface is present without credential handling or provider calls."
  },
  {
    id: "guardian-controls",
    name: "Guardian-gated controls",
    status: "planned",
    summary: "Read-only Guardian Controls preview surface is present without approvals, enforcement, or sensitive actions."
  },
  {
    id: "desktop-packaging",
    name: "Desktop packaging",
    status: "planned",
    summary: "Planning notes are present. No installer or desktop binary exists yet."
  }
];

const capabilityStatusMap: Record<PublicCapabilityStatus, WorkstreamStatus> = {
  available: "worksToday",
  preview: "preview",
  planned: "planned"
};

export function capabilityToStatusItem(capability: PublicCapability): WorkstationStatusItem {
  return {
    id: capability.id,
    name: capability.label,
    status: capabilityStatusMap[capability.status],
    summary: capability.notes
  };
}

export const workstationRoadmapItems: string[] = [
  "Define workstation view structure with stable public contracts.",
  "Document chat interaction contracts before enabling message handling or model behavior.",
  "Expand Round Table preview surfaces only after public interaction contracts are documented.",
  "Document provider setup contracts before enabling credential or network behavior.",
  "Document Guardian control contracts before enabling approval or enforcement behavior.",
  "Prepare provider and guardrail integration points without runtime activation."
];
