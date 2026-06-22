import type { PublicCapability } from "../api";
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
    name: "Backend health endpoint",
    status: "available",
    summary: "Read-only local health check."
  },
  {
    id: "frontend-shell",
    name: "Frontend shell",
    status: "available",
    summary: "Public shell interface."
  },
  {
    id: "local-workstation-store",
    name: "Local Workstation store",
    status: "available",
    summary: "Local SQLite storage for Workstation data."
  },
  {
    id: "local-chat-drafts",
    name: "Local chat drafts",
    status: "available",
    summary: "Stores operator and note messages locally without model calls."
  },
  {
    id: "local-memory-notes",
    name: "Local memory notes",
    status: "available",
    summary: "Stores local notes and supports explicit per-prompt selection without automatic retrieval or model memory."
  },
  {
    id: "local-work-lane-cards",
    name: "Local work lane cards",
    status: "available",
    summary: "Stores local planning cards and optional local chat-session links without scheduler or task execution."
  },
  {
    id: "local-data-export",
    name: "Local data export",
    status: "available",
    summary: "Downloads a read-only JSON backup of local Workstation data without import, sync, or upload."
  },
  {
    id: "local-runtime-settings",
    name: "Local runtime settings",
    status: "available",
    summary: "Shows env-driven local runtime paths and Ollama settings without credential fields or save actions."
  },
  {
    id: "local-model-adapter",
    name: "Local model adapter",
    status: "disabled-by-default",
    summary: "Localhost-only Ollama adapter; prompt calls require explicit operator enablement."
  },
  {
    id: "local-ollama",
    name: "Local Ollama",
    status: "disabled-by-default",
    summary: "Uses only localhost or 127.0.0.1 and no credentials or cloud providers."
  },
  {
    id: "workstation",
    name: "Workstation shell",
    status: "preview",
    summary: "Navigation and product shell preview."
  },
  {
    id: "chat",
    name: "Chat shell",
    status: "preview",
    summary: "No model calls or message persistence."
  },
  {
    id: "round-table",
    name: "Round Table",
    status: "preview",
    summary: "No meeting engine or agent orchestration."
  },
  {
    id: "provider-setup",
    name: "Provider Setup shell",
    status: "available",
    summary: "Env-driven provider onboarding and CLI sign-in status without browser credential storage."
  },
  {
    id: "model-seats",
    name: "Model Seat preview",
    status: "preview",
    summary: "No model assignment, routing, calls, credentials, or seat persistence."
  },
  {
    id: "work-lanes",
    name: "Task Lane preview",
    status: "preview",
    summary: "No scheduler, background jobs, task execution, notifications, or task persistence."
  },
  {
    id: "guardian-controls",
    name: "Guardian Controls shell",
    status: "preview",
    summary: "No policy enforcement runtime."
  },
  {
    id: "desktop-packaging",
    name: "Desktop packaging",
    status: "planned",
    summary: "No installer or desktop binary yet."
  },
  {
    id: "connectors",
    name: "Connectors",
    status: "guarded-future",
    summary: "No connector calls or external sends."
  },
  {
    id: "model-calls",
    name: "Cloud model calls",
    status: "disabled-by-default",
    summary: "Only explicit OpenRouter prompt calls are available when SPARKBOT_PROVIDER_CALLS_ENABLED=true and an env key is configured."
  },
  {
    id: "credential-storage",
    name: "Credential storage",
    status: "guarded-future",
    summary: "No credential entry or storage path."
  },
  {
    id: "tool-execution",
    name: "Tool execution",
    status: "guarded-future",
    summary: "No terminal, tool, or automation execution."
  }
];

export function capabilityToStatusItem(capability: PublicCapability): WorkstationStatusItem {
  return {
    id: capability.id,
    name: capability.label,
    status: capability.status,
    summary: capability.notes
  };
}

export const workstationRoadmapItems: string[] = [
  "Define workstation view structure with stable public contracts.",
  "Document chat interaction contracts before enabling message handling or model behavior.",
  "Expand Round Table preview surfaces only after public interaction contracts are documented.",
  "Document provider setup contracts before enabling credential or network behavior.",
  "Document Guardian control contracts before enabling approval or enforcement behavior.",
  "Prepare model seat, task lane, provider, and guardrail integration points without runtime activation."
];
