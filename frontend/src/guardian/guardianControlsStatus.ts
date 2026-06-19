import type { GuardianStatusPayload, SensitiveActionCategory } from "../api";
import type { ShellSectionStatus } from "../workstation/shellSections";

export type GuardianControlStatus = Extract<ShellSectionStatus, "preview" | "planned">;

export type GuardianControlItem = {
  name: string;
  status: GuardianControlStatus;
  summary: string;
};

export const guardianControlItems: GuardianControlItem[] = [
  {
    name: "Local actions",
    status: "planned",
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

export type GuardianSensitiveActionPreview = SensitiveActionCategory;

export const guardianSensitiveActionCategories: GuardianSensitiveActionPreview[] = [
  {
    id: "external-sends",
    label: "External sends",
    status: "guarded-future",
    notes: "No external sends are implemented."
  },
  {
    id: "connector-calls",
    label: "Connector calls",
    status: "guarded-future",
    notes: "No connector calls are implemented."
  },
  {
    id: "credential-use",
    label: "Credential use",
    status: "guarded-future",
    notes: "No credential use or storage is implemented."
  },
  {
    id: "model-provider-calls",
    label: "Model provider calls",
    status: "guarded-future",
    notes: "No model provider calls are implemented."
  },
  {
    id: "file-writes",
    label: "File writes",
    status: "guarded-future",
    notes: "No file mutation workflow is implemented."
  },
  {
    id: "tool-execution",
    label: "Tool execution",
    status: "guarded-future",
    notes: "No terminal or tool execution is implemented."
  }
];

export const fallbackGuardianStatus: GuardianStatusPayload = {
  service: "sparkbot-server",
  mode: "local",
  status: "preview",
  runtime_enforcement: "not-implemented",
  approval_tokens: "not-implemented",
  policy_decisions: "not-implemented",
  audit_trail: "planned",
  default_posture: "deny-sensitive-actions",
  sensitive_action_categories: guardianSensitiveActionCategories
};

export const guardianControlsSummary =
  "Guardian-gated controls are planned for later slices. This preview is read-only and does not enforce policy, approve actions, or run sensitive workflows.";
