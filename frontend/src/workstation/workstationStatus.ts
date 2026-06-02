import type { ShellSectionStatus } from "./shellSections";

export type WorkstreamStatus = ShellSectionStatus;

export type WorkstationStatusItem = {
  name: string;
  status: WorkstreamStatus;
  summary: string;
};

export const workstationStatusItems: WorkstationStatusItem[] = [
  {
    name: "Server runtime",
    status: "worksToday",
    summary: "FastAPI health, provider status, and chat endpoints are present."
  },
  {
    name: "Frontend shell",
    status: "worksToday",
    summary: "Public React and TypeScript workstation builds and tests successfully."
  },
  {
    name: "Workstation",
    status: "worksToday",
    summary: "Local workstation layout, section selector, health check, and runtime chat surface are active."
  },
  {
    name: "Chat runtime",
    status: "worksToday",
    summary: "Chat sends messages through the backend provider router and displays provider responses."
  },
  {
    name: "Provider runtime",
    status: "worksToday",
    summary: "OpenAI, OpenAI-compatible, and Ollama paths are selected through backend configuration."
  },
  {
    name: "Round Table",
    status: "preview",
    summary: "Round Table remains a future runtime slice without meeting or model behavior."
  },
  {
    name: "Guardian-gated controls",
    status: "planned",
    summary: "Guardian controls remain inactive until the basic action confirmation slice."
  }
];

export const workstationRoadmapItems: string[] = [
  "Persist provider settings in a safe local backend store.",
  "Restore the Round Table runtime with sequential seats and Meeting Manager flow.",
  "Add durable memory and meeting notes after the real chat loop is stable.",
  "Add basic Guardian confirmations before any tool or connector action support."
];
