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
    summary: "Local workstation frame, status cards, and backend health surface."
  },
  {
    id: "chat-shell",
    label: "Chat",
    status: "worksToday",
    summary: "Runtime chat surface connected to the backend provider router."
  },
  {
    id: "round-table",
    label: "Round Table",
    status: "preview",
    summary: "Static seat layout for future multi-participant work."
  },
  {
    id: "provider-setup",
    label: "Provider",
    status: "worksToday",
    summary: "Backend-configured provider and model status for chat requests."
  },
  {
    id: "guardian-controls",
    label: "Guardian Controls",
    status: "planned",
    summary: "Read-only control categories remain inactive in this preview."
  }
];
