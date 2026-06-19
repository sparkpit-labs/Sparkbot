export type HealthPayload = {
  status: string;
  service: string;
  mode: string;
};

export type PublicCapabilityStatus = "available" | "preview" | "planned" | "disabled-by-default" | "guarded-future";

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

export type ProviderImplementationStatus = "not-implemented";
export type ConnectorImplementationStatus = "not-implemented";
export type ConnectorAuditTrailStatus = "planned";
export type GuardianImplementationStatus = "not-implemented";
export type GuardianAuditTrailStatus = "planned";
export type GuardianDefaultPosture = "deny-sensitive-actions";

export type ProviderStatusItem = {
  id: string;
  label: string;
  status: PublicCapabilityStatus;
  notes: string;
};

export type ProviderConfigStatusPayload = {
  service: string;
  mode: string;
  status: PublicCapabilityStatus;
  credential_storage: ProviderImplementationStatus;
  provider_calls: ProviderImplementationStatus;
  model_routing: ProviderImplementationStatus;
  providers: ProviderStatusItem[];
};

export type ConnectorStatusItem = {
  id: string;
  label: string;
  status: PublicCapabilityStatus;
  notes: string;
};

export type ConnectorStatusPayload = {
  service: string;
  mode: string;
  status: PublicCapabilityStatus;
  connectors_enabled: boolean;
  outbound_actions: ConnectorImplementationStatus;
  credential_storage: ConnectorImplementationStatus;
  audit_trail: ConnectorAuditTrailStatus;
  connectors: ConnectorStatusItem[];
};

export type SensitiveActionCategory = {
  id: string;
  label: string;
  status: PublicCapabilityStatus;
  notes: string;
};

export type GuardianStatusPayload = {
  service: string;
  mode: string;
  status: PublicCapabilityStatus;
  runtime_enforcement: GuardianImplementationStatus;
  approval_tokens: GuardianImplementationStatus;
  policy_decisions: GuardianImplementationStatus;
  audit_trail: GuardianAuditTrailStatus;
  default_posture: GuardianDefaultPosture;
  sensitive_action_categories: SensitiveActionCategory[];
};

const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";
const publicCapabilityStatuses = new Set(["available", "preview", "planned", "disabled-by-default", "guarded-future"]);

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

export async function fetchProviderConfigStatus(signal?: AbortSignal): Promise<ProviderConfigStatusPayload> {
  const endpoint = new URL("/provider-config/status", API_BASE_URL).toString();
  const response = await fetch(endpoint, {
    method: "GET",
    headers: {
      Accept: "application/json"
    },
    cache: "no-store",
    signal
  });

  if (!response.ok) {
    throw new Error(`Provider config status request failed with status ${response.status}`);
  }

  const payload = (await response.json()) as Partial<ProviderConfigStatusPayload>;
  if (
    !payload.service ||
    !payload.mode ||
    !payload.status ||
    payload.credential_storage !== "not-implemented" ||
    payload.provider_calls !== "not-implemented" ||
    payload.model_routing !== "not-implemented" ||
    !Array.isArray(payload.providers) ||
    !publicCapabilityStatuses.has(payload.status)
  ) {
    throw new Error("Provider config status response is missing required fields");
  }

  const providers = payload.providers.map((provider) => {
    if (
      !provider ||
      !provider.id ||
      !provider.label ||
      !provider.notes ||
      !publicCapabilityStatuses.has(provider.status ?? "")
    ) {
      throw new Error("Provider config status response includes an invalid provider item");
    }

    return {
      id: provider.id,
      label: provider.label,
      status: provider.status,
      notes: provider.notes
    };
  });

  return {
    service: payload.service,
    mode: payload.mode,
    status: payload.status,
    credential_storage: payload.credential_storage,
    provider_calls: payload.provider_calls,
    model_routing: payload.model_routing,
    providers
  };
}

export async function fetchConnectorStatus(signal?: AbortSignal): Promise<ConnectorStatusPayload> {
  const endpoint = new URL("/connector-status", API_BASE_URL).toString();
  const response = await fetch(endpoint, {
    method: "GET",
    headers: {
      Accept: "application/json"
    },
    cache: "no-store",
    signal
  });

  if (!response.ok) {
    throw new Error(`Connector status request failed with status ${response.status}`);
  }

  const payload = (await response.json()) as Partial<ConnectorStatusPayload>;
  if (
    !payload.service ||
    !payload.mode ||
    !payload.status ||
    payload.connectors_enabled !== false ||
    payload.outbound_actions !== "not-implemented" ||
    payload.credential_storage !== "not-implemented" ||
    payload.audit_trail !== "planned" ||
    !Array.isArray(payload.connectors) ||
    !publicCapabilityStatuses.has(payload.status)
  ) {
    throw new Error("Connector status response is missing required fields");
  }

  const connectors = payload.connectors.map((connector) => {
    if (
      !connector ||
      !connector.id ||
      !connector.label ||
      !connector.notes ||
      !publicCapabilityStatuses.has(connector.status ?? "")
    ) {
      throw new Error("Connector status response includes an invalid connector item");
    }

    return {
      id: connector.id,
      label: connector.label,
      status: connector.status,
      notes: connector.notes
    };
  });

  return {
    service: payload.service,
    mode: payload.mode,
    status: payload.status,
    connectors_enabled: payload.connectors_enabled,
    outbound_actions: payload.outbound_actions,
    credential_storage: payload.credential_storage,
    audit_trail: payload.audit_trail,
    connectors
  };
}

export async function fetchGuardianStatus(signal?: AbortSignal): Promise<GuardianStatusPayload> {
  const endpoint = new URL("/guardian/status", API_BASE_URL).toString();
  const response = await fetch(endpoint, {
    method: "GET",
    headers: {
      Accept: "application/json"
    },
    cache: "no-store",
    signal
  });

  if (!response.ok) {
    throw new Error(`Guardian status request failed with status ${response.status}`);
  }

  const payload = (await response.json()) as Partial<GuardianStatusPayload>;
  if (
    !payload.service ||
    !payload.mode ||
    !payload.status ||
    payload.runtime_enforcement !== "not-implemented" ||
    payload.approval_tokens !== "not-implemented" ||
    payload.policy_decisions !== "not-implemented" ||
    payload.audit_trail !== "planned" ||
    payload.default_posture !== "deny-sensitive-actions" ||
    !Array.isArray(payload.sensitive_action_categories) ||
    !publicCapabilityStatuses.has(payload.status)
  ) {
    throw new Error("Guardian status response is missing required fields");
  }

  const sensitiveActionCategories = payload.sensitive_action_categories.map((category) => {
    if (
      !category ||
      !category.id ||
      !category.label ||
      !category.notes ||
      !publicCapabilityStatuses.has(category.status ?? "")
    ) {
      throw new Error("Guardian status response includes an invalid sensitive action category");
    }

    return {
      id: category.id,
      label: category.label,
      status: category.status,
      notes: category.notes
    };
  });

  return {
    service: payload.service,
    mode: payload.mode,
    status: payload.status,
    runtime_enforcement: payload.runtime_enforcement,
    approval_tokens: payload.approval_tokens,
    policy_decisions: payload.policy_decisions,
    audit_trail: payload.audit_trail,
    default_posture: payload.default_posture,
    sensitive_action_categories: sensitiveActionCategories
  };
}
