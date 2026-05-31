export type ChatPreviewStatus = "skeleton" | "planned";

export type ChatPreviewMessage = {
  speaker: string;
  status: ChatPreviewStatus;
  summary: string;
};

export const chatPreviewMessages: ChatPreviewMessage[] = [
  {
    speaker: "Draft prompt",
    status: "skeleton",
    summary: "A future local chat prompt starts here. This preview does not accept or send messages."
  },
  {
    speaker: "Assistant preview",
    status: "planned",
    summary: "A future response area will appear here after chat contracts, providers, and validation gates exist."
  }
];

export const chatShellSummary =
  "Chat runtime is planned for later slices. This preview is read-only and does not call models, store messages, or send anything.";
