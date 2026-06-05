export type RoundTableSeatStatus = "preview" | "planned" | "active";

export type RoundTableSeat = {
  label: string;
  role: string;
  status: RoundTableSeatStatus;
  description: string;
};

export const roundTableSeats: RoundTableSeat[] = [
  {
    label: "Operator",
    role: "Human direction",
    status: "active",
    description: "Represents the person guiding the backend-backed Round Table session."
  },
  {
    label: "Assistant seat",
    role: "General support",
    status: "active",
    description: "Participates through configured provider routes when available, with deterministic fallback."
  },
  {
    label: "Research seat",
    role: "Information review",
    status: "planned",
    description: "Reserved for research support through configured seat routing when available."
  },
  {
    label: "Builder seat",
    role: "Implementation planning",
    status: "planned",
    description: "Reserved for build-oriented planning. It does not run tools or actions."
  },
  {
    label: "Reviewer seat",
    role: "Quality review",
    status: "planned",
    description: "Reserved for review support after validation gates are established."
  }
];

export const roundTablePreviewSummary =
  "Round Table sessions are backend-backed and can use configured provider routes for text turns while external/tool execution remains unavailable.";
