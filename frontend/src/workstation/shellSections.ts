export type ShellSectionStatus = "worksToday" | "preview" | "planned" | "notImplemented";

export type ShellSection = {
  id: string;
  label: string;
  status: ShellSectionStatus;
  summary: string;
};

export const shellStatusLabels: Record<ShellSectionStatus, string> = {
  worksToday: "Works Today",
  preview: "Preview",
  planned: "Planned",
  notImplemented: "Not Implemented"
};

export const shellSections: ShellSection[] = [
  {
    id: "workstation-overview",
    label: "Workstation",
    status: "worksToday",
    summary: "Read-only shell map, status cards, and local health check surface."
  },
  {
    id: "chat-shell",
    label: "Chat",
    status: "worksToday",
    summary: "Backend-backed chat sessions with shared context and configured-provider execution."
  },
  {
    id: "round-table",
    label: "Round Table",
    status: "worksToday",
    summary: "Backend-backed meeting sessions with configured-provider turns when available."
  },
  {
    id: "provider-setup",
    label: "Provider Setup",
    status: "planned",
    summary: "Server-side provider configuration is active through Command Center."
  },
  {
    id: "guardian-controls",
    label: "Guardian Controls",
    status: "planned",
    summary: "Guardian confirmation state and protected-action block logging are active."
  }
];
