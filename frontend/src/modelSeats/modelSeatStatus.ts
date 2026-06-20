import type { ModelSeatStatusItem, ModelSeatsStatusPayload } from "../api";
import type { ShellSectionStatus } from "../workstation/shellSections";

export type ModelSeatStatus = Extract<ShellSectionStatus, "preview" | "planned">;

export type ModelSeat = ModelSeatStatusItem & {
  role: string;
};

export const modelSeatItems: ModelSeat[] = [
  {
    id: "default-assistant",
    label: "Default Assistant Seat",
    role: "General assistance preview",
    status: "preview",
    notes: "Read-only seat preview. No model is assigned or called."
  },
  {
    id: "research-seat",
    label: "Research Seat",
    role: "Research workflow planning",
    status: "planned",
    notes: "Future seat for research workflows. No runtime behavior is implemented."
  },
  {
    id: "builder-seat",
    label: "Builder Seat",
    role: "Implementation workflow planning",
    status: "planned",
    notes: "Future seat for implementation workflows. No tool execution is implemented."
  },
  {
    id: "reviewer-seat",
    label: "Reviewer Seat",
    role: "Review workflow planning",
    status: "planned",
    notes: "Future seat for review workflows. No model routing is implemented."
  }
];

export const fallbackModelSeatsStatus: ModelSeatsStatusPayload = {
  service: "sparkbot-server",
  mode: "local",
  status: "preview",
  model_calls: "not-implemented",
  model_routing: "not-implemented",
  provider_credentials: "not-implemented",
  seat_persistence: "not-implemented",
  seats: modelSeatItems.map(({ id, label, status, notes }) => ({ id, label, status, notes }))
};

export const modelSeatRoles = new Map(modelSeatItems.map((seat) => [seat.id, seat.role]));

export const modelSeatPreviewSummary =
  "Model seats show the future multi-model workspace direction, but this public surface is read-only and does not assign, route, call, or persist models.";
