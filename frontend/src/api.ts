export type HealthPayload = {
  status: string;
  service: string;
  mode: string;
};

export type ProviderId = "openai" | "openai_compatible" | "ollama";

export type ProviderStatus = {
  id: ProviderId;
  label: string;
  configured: boolean;
  model: string | null;
  base_url_configured: boolean;
  message: string;
};

export type ProviderStatusPayload = {
  selected_provider: ProviderId;
  selected_model: string | null;
  configured: boolean;
  message: string;
  providers: ProviderStatus[];
};

export type ChatPayload = {
  message: string;
  provider?: ProviderId;
  model?: string;
};

export type ChatResponse = {
  provider: ProviderId;
  model: string;
  content: string;
};

const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";

export const API_BASE_URL =
  import.meta.env.VITE_SPARKBOT_API_BASE_URL?.trim() || DEFAULT_API_BASE_URL;

export async function fetchBackendHealth(signal?: AbortSignal): Promise<HealthPayload> {
  const payload = await requestJson<Partial<HealthPayload>>("/health", {
    method: "GET",
    headers: {
      Accept: "application/json"
    },
    cache: "no-store",
    signal
  });

  if (!payload.status || !payload.service || !payload.mode) {
    throw new Error("Health response is missing required fields");
  }

  return {
    status: payload.status,
    service: payload.service,
    mode: payload.mode
  };
}

export async function fetchProviderStatus(signal?: AbortSignal): Promise<ProviderStatusPayload> {
  return requestJson<ProviderStatusPayload>("/api/providers/status", {
    method: "GET",
    headers: {
      Accept: "application/json"
    },
    cache: "no-store",
    signal
  });
}

export async function sendChatMessage(payload: ChatPayload, signal?: AbortSignal): Promise<ChatResponse> {
  return requestJson<ChatResponse>("/api/chat", {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload),
    signal
  });
}

async function requestJson<T>(path: string, init: RequestInit): Promise<T> {
  const endpoint = new URL(path, API_BASE_URL).toString();
  const response = await fetch(endpoint, init);
  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const detail = typeof payload?.detail === "string" ? payload.detail : null;
    throw new Error(detail || `Request failed with status ${response.status}`);
  }

  return payload as T;
}
