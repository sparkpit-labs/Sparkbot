import { localJsonRequest } from "../localWorkstation/localRequests";
import type { PublicCapabilityStatus } from "../api";

export type LocalModelStatus = "disabled-by-default" | "unavailable" | "available-local-only";

export type LocalModelStatusPayload = {
  service: string;
  mode: string;
  status: LocalModelStatus;
  local_models_enabled: boolean;
  adapter: "ollama";
  base_url: string | null;
  base_url_policy: "localhost-only";
  configured_model: string | null;
  prompt_calls: "disabled" | "enabled-local-only" | "unavailable";
  credentials: "not-supported";
  external_network: "not-supported";
  ollama_reachable?: boolean;
  configuration_error?: string;
};

export type LocalPromptResponse = {
  adapter: "ollama";
  base_url_policy: "localhost-only";
  model: string;
  response: string;
  done: boolean;
  stored_message: unknown | null;
};

export const fallbackLocalModelStatus: LocalModelStatusPayload = {
  service: "sparkbot-server",
  mode: "local",
  status: "disabled-by-default",
  local_models_enabled: false,
  adapter: "ollama",
  base_url: "http://127.0.0.1:11434",
  base_url_policy: "localhost-only",
  configured_model: null,
  prompt_calls: "disabled",
  credentials: "not-supported",
  external_network: "not-supported"
};

export function localModelStatusToCapabilityStatus(status: LocalModelStatus): PublicCapabilityStatus {
  if (status === "disabled-by-default") return "disabled-by-default";
  if (status === "available-local-only") return "available";
  return "preview";
}

export function formatLocalModelStatus(status: LocalModelStatus) {
  if (status === "available-local-only") return "available local only";
  return status.replaceAll("-", " ");
}

export async function fetchLocalModelStatus(): Promise<LocalModelStatusPayload> {
  return localJsonRequest<LocalModelStatusPayload>("/local-models/status");
}

export async function runLocalPrompt(
  prompt: string,
  model?: string,
  sessionId?: string
): Promise<LocalPromptResponse> {
  return localJsonRequest<LocalPromptResponse>("/local-models/ollama/prompt", {
    method: "POST",
    body: JSON.stringify({ prompt, model: model?.trim() || undefined, session_id: sessionId || undefined })
  });
}
