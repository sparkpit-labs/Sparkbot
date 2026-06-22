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

export type ProviderImplementationStatus = "not-implemented" | "env-driven" | "disabled-by-default" | "guarded-manual";
export type ChatImplementationStatus = "not-implemented";
export type RoundTableImplementationStatus = "not-implemented";
export type ModelSeatImplementationStatus = "not-implemented";
export type TaskLaneImplementationStatus = "not-implemented";
export type ConnectorImplementationStatus = "not-implemented";
export type ConnectorAuditTrailStatus = "planned";
export type GuardianImplementationStatus = "not-implemented";
export type GuardianAuditTrailStatus = "planned";
export type GuardianDefaultPosture = "deny-sensitive-actions";

export type ChatSurfaceStatusItem = {
  id: string;
  label: string;
  status: PublicCapabilityStatus;
  notes: string;
};

export type ChatStatusPayload = {
  service: string;
  mode: string;
  status: PublicCapabilityStatus;
  chat_runtime: ChatImplementationStatus;
  message_persistence: ChatImplementationStatus;
  model_calls: ChatImplementationStatus;
  streaming: ChatImplementationStatus;
  provider_routing: ChatImplementationStatus;
  supported_surfaces: ChatSurfaceStatusItem[];
};

export type RoundTableSeatStatusItem = {
  id: string;
  label: string;
  status: PublicCapabilityStatus;
  notes: string;
};

export type RoundTableStatusPayload = {
  service: string;
  mode: string;
  status: PublicCapabilityStatus;
  meeting_engine: RoundTableImplementationStatus;
  agent_orchestration: RoundTableImplementationStatus;
  model_calls: RoundTableImplementationStatus;
  turn_persistence: RoundTableImplementationStatus;
  seats: RoundTableSeatStatusItem[];
};

export type ModelSeatStatusItem = {
  id: string;
  label: string;
  status: PublicCapabilityStatus;
  notes: string;
};

export type ModelSeatsStatusPayload = {
  service: string;
  mode: string;
  status: PublicCapabilityStatus;
  model_calls: ModelSeatImplementationStatus;
  model_routing: ModelSeatImplementationStatus;
  provider_credentials: ModelSeatImplementationStatus;
  seat_persistence: ModelSeatImplementationStatus;
  seats: ModelSeatStatusItem[];
};

export type TaskLaneStatusItem = {
  id: string;
  label: string;
  status: PublicCapabilityStatus;
  notes: string;
};

export type TaskLanesStatusPayload = {
  service: string;
  mode: string;
  status: PublicCapabilityStatus;
  task_runtime: TaskLaneImplementationStatus;
  task_persistence: TaskLaneImplementationStatus;
  scheduler: TaskLaneImplementationStatus;
  background_jobs: TaskLaneImplementationStatus;
  notifications: TaskLaneImplementationStatus;
  lanes: TaskLaneStatusItem[];
};

export type ProviderStatusItem = {
  id: string;
  label: string;
  status: PublicCapabilityStatus;
  configured: boolean;
  auth_mode: string;
  configuration: string;
  credential_source: string;
  default_model: string | null;
  model_examples: string[];
  runtime: string;
  notes: string;
  cli_available?: boolean;
  sign_in_detected?: boolean;
  runtime_gate?: string;
  operator_action?: string;
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
const providerImplementationStatuses = new Set(["not-implemented", "env-driven", "disabled-by-default", "guarded-manual"]);

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

export async function fetchChatStatus(signal?: AbortSignal): Promise<ChatStatusPayload> {
  const endpoint = new URL("/chat/status", API_BASE_URL).toString();
  const response = await fetch(endpoint, {
    method: "GET",
    headers: {
      Accept: "application/json"
    },
    cache: "no-store",
    signal
  });

  if (!response.ok) {
    throw new Error(`Chat status request failed with status ${response.status}`);
  }

  const payload = (await response.json()) as Partial<ChatStatusPayload>;
  if (
    !payload.service ||
    !payload.mode ||
    !payload.status ||
    payload.chat_runtime !== "not-implemented" ||
    payload.message_persistence !== "not-implemented" ||
    payload.model_calls !== "not-implemented" ||
    payload.streaming !== "not-implemented" ||
    payload.provider_routing !== "not-implemented" ||
    !Array.isArray(payload.supported_surfaces) ||
    !publicCapabilityStatuses.has(payload.status)
  ) {
    throw new Error("Chat status response is missing required fields");
  }

  const supportedSurfaces = payload.supported_surfaces.map((surface) => {
    if (
      !surface ||
      !surface.id ||
      !surface.label ||
      !surface.notes ||
      !publicCapabilityStatuses.has(surface.status ?? "")
    ) {
      throw new Error("Chat status response includes an invalid surface item");
    }

    return {
      id: surface.id,
      label: surface.label,
      status: surface.status,
      notes: surface.notes
    };
  });

  return {
    service: payload.service,
    mode: payload.mode,
    status: payload.status,
    chat_runtime: payload.chat_runtime,
    message_persistence: payload.message_persistence,
    model_calls: payload.model_calls,
    streaming: payload.streaming,
    provider_routing: payload.provider_routing,
    supported_surfaces: supportedSurfaces
  };
}

export async function fetchRoundTableStatus(signal?: AbortSignal): Promise<RoundTableStatusPayload> {
  const endpoint = new URL("/round-table/status", API_BASE_URL).toString();
  const response = await fetch(endpoint, {
    method: "GET",
    headers: {
      Accept: "application/json"
    },
    cache: "no-store",
    signal
  });

  if (!response.ok) {
    throw new Error(`Round Table status request failed with status ${response.status}`);
  }

  const payload = (await response.json()) as Partial<RoundTableStatusPayload>;
  if (
    !payload.service ||
    !payload.mode ||
    !payload.status ||
    payload.meeting_engine !== "not-implemented" ||
    payload.agent_orchestration !== "not-implemented" ||
    payload.model_calls !== "not-implemented" ||
    payload.turn_persistence !== "not-implemented" ||
    !Array.isArray(payload.seats) ||
    !publicCapabilityStatuses.has(payload.status)
  ) {
    throw new Error("Round Table status response is missing required fields");
  }

  const seats = payload.seats.map((seat) => {
    if (!seat || !seat.id || !seat.label || !seat.notes || !publicCapabilityStatuses.has(seat.status ?? "")) {
      throw new Error("Round Table status response includes an invalid seat item");
    }

    return {
      id: seat.id,
      label: seat.label,
      status: seat.status,
      notes: seat.notes
    };
  });

  return {
    service: payload.service,
    mode: payload.mode,
    status: payload.status,
    meeting_engine: payload.meeting_engine,
    agent_orchestration: payload.agent_orchestration,
    model_calls: payload.model_calls,
    turn_persistence: payload.turn_persistence,
    seats
  };
}

export async function fetchModelSeatsStatus(signal?: AbortSignal): Promise<ModelSeatsStatusPayload> {
  const endpoint = new URL("/model-seats/status", API_BASE_URL).toString();
  const response = await fetch(endpoint, {
    method: "GET",
    headers: {
      Accept: "application/json"
    },
    cache: "no-store",
    signal
  });

  if (!response.ok) {
    throw new Error(`Model Seat status request failed with status ${response.status}`);
  }

  const payload = (await response.json()) as Partial<ModelSeatsStatusPayload>;
  if (
    !payload.service ||
    !payload.mode ||
    !payload.status ||
    payload.model_calls !== "not-implemented" ||
    payload.model_routing !== "not-implemented" ||
    payload.provider_credentials !== "not-implemented" ||
    payload.seat_persistence !== "not-implemented" ||
    !Array.isArray(payload.seats) ||
    !publicCapabilityStatuses.has(payload.status)
  ) {
    throw new Error("Model Seat status response is missing required fields");
  }

  const seats = payload.seats.map((seat) => {
    if (!seat || !seat.id || !seat.label || !seat.notes || !publicCapabilityStatuses.has(seat.status ?? "")) {
      throw new Error("Model Seat status response includes an invalid seat item");
    }

    return {
      id: seat.id,
      label: seat.label,
      status: seat.status,
      notes: seat.notes
    };
  });

  return {
    service: payload.service,
    mode: payload.mode,
    status: payload.status,
    model_calls: payload.model_calls,
    model_routing: payload.model_routing,
    provider_credentials: payload.provider_credentials,
    seat_persistence: payload.seat_persistence,
    seats
  };
}

export async function fetchTaskLanesStatus(signal?: AbortSignal): Promise<TaskLanesStatusPayload> {
  const endpoint = new URL("/work-lanes/status", API_BASE_URL).toString();
  const response = await fetch(endpoint, {
    method: "GET",
    headers: {
      Accept: "application/json"
    },
    cache: "no-store",
    signal
  });

  if (!response.ok) {
    throw new Error(`Task Lane status request failed with status ${response.status}`);
  }

  const payload = (await response.json()) as Partial<TaskLanesStatusPayload>;
  if (
    !payload.service ||
    !payload.mode ||
    !payload.status ||
    payload.task_runtime !== "not-implemented" ||
    payload.task_persistence !== "not-implemented" ||
    payload.scheduler !== "not-implemented" ||
    payload.background_jobs !== "not-implemented" ||
    payload.notifications !== "not-implemented" ||
    !Array.isArray(payload.lanes) ||
    !publicCapabilityStatuses.has(payload.status)
  ) {
    throw new Error("Task Lane status response is missing required fields");
  }

  const lanes = payload.lanes.map((lane) => {
    if (!lane || !lane.id || !lane.label || !lane.notes || !publicCapabilityStatuses.has(lane.status ?? "")) {
      throw new Error("Task Lane status response includes an invalid lane item");
    }

    return {
      id: lane.id,
      label: lane.label,
      status: lane.status,
      notes: lane.notes
    };
  });

  return {
    service: payload.service,
    mode: payload.mode,
    status: payload.status,
    task_runtime: payload.task_runtime,
    task_persistence: payload.task_persistence,
    scheduler: payload.scheduler,
    background_jobs: payload.background_jobs,
    notifications: payload.notifications,
    lanes
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
    !providerImplementationStatuses.has(payload.credential_storage ?? "") ||
    !providerImplementationStatuses.has(payload.provider_calls ?? "") ||
    !providerImplementationStatuses.has(payload.model_routing ?? "") ||
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
      typeof provider.configured !== "boolean" ||
      !provider.auth_mode ||
      !provider.configuration ||
      !provider.credential_source ||
      !Array.isArray(provider.model_examples) ||
      !provider.runtime ||
      !publicCapabilityStatuses.has(provider.status ?? "")
    ) {
      throw new Error("Provider config status response includes an invalid provider item");
    }

    return {
      id: provider.id,
      label: provider.label,
      status: provider.status,
      configured: provider.configured,
      auth_mode: provider.auth_mode,
      configuration: provider.configuration,
      credential_source: provider.credential_source,
      default_model: provider.default_model ?? null,
      model_examples: provider.model_examples,
      runtime: provider.runtime,
      notes: provider.notes,
      cli_available: typeof provider.cli_available === "boolean" ? provider.cli_available : undefined,
      sign_in_detected: typeof provider.sign_in_detected === "boolean" ? provider.sign_in_detected : undefined,
      runtime_gate: provider.runtime_gate,
      operator_action: provider.operator_action
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
