import type { ChatStatusPayload } from "../api";

export const fallbackChatStatus: ChatStatusPayload = {
  service: "sparkbot-server",
  mode: "local",
  status: "preview",
  chat_runtime: "not-implemented",
  message_persistence: "not-implemented",
  model_calls: "not-implemented",
  streaming: "not-implemented",
  provider_routing: "not-implemented",
  supported_surfaces: [
    {
      id: "chat-shell",
      label: "Chat shell",
      status: "preview",
      notes: "Static chat shell preview. No messages are sent."
    },
    {
      id: "message-input",
      label: "Message input",
      status: "disabled-by-default",
      notes: "Input remains disabled until chat runtime and safety gates exist."
    },
    {
      id: "model-response",
      label: "Model response",
      status: "guarded-future",
      notes: "No model calls are implemented."
    },
    {
      id: "message-history",
      label: "Message history",
      status: "guarded-future",
      notes: "No message persistence is implemented."
    }
  ]
};

export const chatShellSummary =
  "Chat status is read-only. The public shell shows the planned conversation area without accepting messages, storing messages, streaming, routing providers, calling models, or sending anything.";
