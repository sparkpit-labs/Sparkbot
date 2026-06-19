import type { RoundTableSeatStatusItem, RoundTableStatusPayload } from "../api";
import type { ShellSectionStatus } from "../workstation/shellSections";

export type RoundTableSeatStatus = Extract<ShellSectionStatus, "preview" | "planned">;

export type RoundTableSeat = RoundTableSeatStatusItem & {
  role: string;
};

export const roundTableSeats: RoundTableSeat[] = [
  {
    id: "operator",
    label: "Operator",
    role: "Human direction",
    status: "preview",
    notes: "Human operator role shown as part of the shell preview."
  },
  {
    id: "assistant",
    label: "Assistant seat",
    role: "General support",
    status: "preview",
    notes: "Assistant role preview only. No model calls are made."
  },
  {
    id: "research",
    label: "Research seat",
    role: "Information review",
    status: "planned",
    notes: "Research role is planned. No agent runtime is implemented."
  },
  {
    id: "builder",
    label: "Builder seat",
    role: "Implementation planning",
    status: "planned",
    notes: "Builder role is planned. No tool execution is implemented."
  },
  {
    id: "reviewer",
    label: "Reviewer seat",
    role: "Quality review",
    status: "planned",
    notes: "Reviewer role is planned. No review workflow runtime is implemented."
  }
];

export const fallbackRoundTableStatus: RoundTableStatusPayload = {
  service: "sparkbot-server",
  mode: "local",
  status: "preview",
  meeting_engine: "not-implemented",
  agent_orchestration: "not-implemented",
  model_calls: "not-implemented",
  turn_persistence: "not-implemented",
  seats: roundTableSeats.map(({ id, label, status, notes }) => ({ id, label, status, notes }))
};

export const roundTableSeatRoles = new Map(roundTableSeats.map((seat) => [seat.id, seat.role]));

export const roundTablePreviewSummary =
  "Multi-participant collaboration is planned for Sparkbot, but this public surface is a read-only Round Table status preview.";
