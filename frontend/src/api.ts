export type HealthPayload = {
  status: string;
  service: string;
  mode: string;
};

export type PublicCapabilityStatus = "available" | "preview" | "planned";

export type PublicCapability = {
  id: string;
  label: string;
  status: PublicCapabilityStatus;
  notes: string;
};

export type CapabilitiesPayload = {
  service: string;
  mode: string;
  capabilities: PublicCapability[];
};

const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";
const publicCapabilityStatuses = new Set(["available", "preview", "planned"]);

export const API_BASE_URL =
  import.meta.env.VITE_SPARKBOT_API_BASE_URL?.trim() || DEFAULT_API_BASE_URL;

export async function fetchBackendHealth(signal?: AbortSignal): Promise<HealthPayload> {
  const endpoint = new URL("/health", API_BASE_URL).toString();
  const response = await fetch(endpoint, {
    method: "GET",
    headers: {
      Accept: "application/json"
    },
    cache: "no-store",
    signal
  });

  if (!response.ok) {
    throw new Error(`Health request failed with status ${response.status}`);
  }

  const payload = (await response.json()) as Partial<HealthPayload>;
  if (!payload.status || !payload.service || !payload.mode) {
    throw new Error("Health response is missing required fields");
  }

  return {
    status: payload.status,
    service: payload.service,
    mode: payload.mode
  };
}

export async function fetchPublicCapabilities(signal?: AbortSignal): Promise<CapabilitiesPayload> {
  const endpoint = new URL("/capabilities", API_BASE_URL).toString();
  const response = await fetch(endpoint, {
    method: "GET",
    headers: {
      Accept: "application/json"
    },
    cache: "no-store",
    signal
  });

  if (!response.ok) {
    throw new Error(`Capabilities request failed with status ${response.status}`);
  }

  const payload = (await response.json()) as Partial<CapabilitiesPayload>;
  if (!payload.service || !payload.mode || !Array.isArray(payload.capabilities)) {
    throw new Error("Capabilities response is missing required fields");
  }

  const capabilities = payload.capabilities.map((item) => {
    if (!item || !item.id || !item.label || !item.notes || !publicCapabilityStatuses.has(item.status ?? "")) {
      throw new Error("Capabilities response includes an invalid capability item");
    }

    return {
      id: item.id,
      label: item.label,
      status: item.status,
      notes: item.notes
    };
  });

  return {
    service: payload.service,
    mode: payload.mode,
    capabilities
  };
}
