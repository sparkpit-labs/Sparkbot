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
    id: "provider-setup",
    label: "Provider Setup",
    status: "planned",
    summary: "Read-only provider planning cards with credentials inactive."
  },
  {
    id: "guardian-controls",
    label: "Guardian Controls",
    status: "planned",
    summary: "Read-only control categories remain inactive in this preview."
  }
];
