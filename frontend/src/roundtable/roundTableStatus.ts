export type RoundTableSeatStatus = "preview" | "planned";

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
    status: "preview",
    description: "Represents the person guiding a future collaborative session."
  },
  {
    label: "Assistant seat",
    role: "General support",
    status: "planned",
    description: "Reserved for a future assistant participant. No chat or model behavior is active."
  },
  {
    label: "Research seat",
    role: "Information review",
    status: "planned",
    description: "Reserved for future research support after public contracts are defined."
  },
  {
    label: "Builder seat",
    role: "Implementation planning",
    status: "planned",
    description: "Reserved for future build-oriented collaboration. It does not run tools or actions."
  },
  {
    label: "Reviewer seat",
    role: "Quality review",
    status: "planned",
    description: "Reserved for future review support after validation gates are established."
  }
];

export const roundTablePreviewSummary =
  "Multi-agent collaboration is planned for Sparkbot, but this branch only provides an inert Round Table shell preview.";
