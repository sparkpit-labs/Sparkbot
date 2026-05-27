export type GuardianControlStatus = "skeleton" | "planned";

export type GuardianControlItem = {
  name: string;
  status: GuardianControlStatus;
  summary: string;
};

export const guardianControlItems: GuardianControlItem[] = [
  {
    name: "Local actions",
    status: "skeleton",
    summary: "Planned review surface for local actions. No approval or execution behavior is active."
  },
  {
    name: "Provider access",
    status: "planned",
    summary: "Planned control category for provider usage. No model routing or provider calls are active."
  },
  {
    name: "Files and workspace",
    status: "planned",
    summary: "Planned control category for workspace access. No file mutation controls are active."
  },
  {
    name: "External connections",
    status: "planned",
    summary: "Planned control category for outbound connections. No connector calls or external sends are active."
  },
  {
    name: "Approval checkpoints",
    status: "planned",
    summary: "Planned checkpoint surface. No approval token or policy enforcement engine is active."
  },
  {
    name: "Audit trail",
    status: "planned",
    summary: "Planned activity review surface. No runtime audit capture or sensitive action logging is active."
  }
];

export const guardianControlsSummary =
  "Guardian-gated controls are planned for later slices. This preview is read-only and does not enforce policy, approve actions, or run sensitive workflows.";
