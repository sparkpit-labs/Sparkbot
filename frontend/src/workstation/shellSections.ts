export type ShellSectionStatus = "available" | "preview" | "planned" | "disabled-by-default" | "guarded-future";

export type ShellSection = {
  id: string;
  label: string;
  status: ShellSectionStatus;
  summary: string;
};

export const shellStatusLabels: Record<ShellSectionStatus, string> = {
  available: "Available",
  preview: "Preview",
  planned: "Planned",
  "disabled-by-default": "Disabled by default",
  "guarded-future": "Guarded future"
};

export const shellSections: ShellSection[] = [
  {
    id: "workstation-overview",
    label: "Workstation",
    status: "preview",
    summary: "Read-only shell map, status cards, and local health check surface."
  },
  {
    id: "local-chat",
    label: "Local Chat",
    status: "available",
    summary: "Local operator and note messages stored in SQLite."
  },
  {
    id: "local-memory-notes",
    label: "Memory Notes",
    status: "available",
    summary: "Local notes stored without cloud sync or model memory."
  },
  {
    id: "local-work-lane-cards",
    label: "Work Cards",
    status: "available",
    summary: "Local planning cards with no scheduler or execution path."
  },
  {
    id: "chat-shell",
    label: "Chat",
    status: "preview",
    summary: "Static chat preview with message actions inactive."
  },
  {
    id: "round-table",
    label: "Round Table",
    status: "preview",
    summary: "Static seat layout for future multi-participant work."
  },
  {
    id: "model-seats",
    label: "Model Seats",
    status: "preview",
    summary: "Read-only model seat plan with routing and calls inactive."
  },
  {
    id: "work-lanes",
    label: "Task Lanes",
    status: "preview",
    summary: "Read-only lane plan with scheduling and execution inactive."
  },
  {
    id: "provider-setup",
    label: "Provider Setup",
    status: "preview",
    summary: "Read-only provider planning cards with credentials inactive."
  },
  {
    id: "guardian-controls",
    label: "Guardian Controls",
    status: "preview",
    summary: "Read-only control categories remain inactive in this preview."
  }
];
