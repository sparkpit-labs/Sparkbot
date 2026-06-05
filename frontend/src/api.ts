export type HealthPayload = {
  status: string;
  service: string;
  mode: string;
};

export type ProviderStatus = {
  id: string;
  label: string;
  configured: boolean;
  auth_modes: string[];
  models: string[];
  models_available: boolean;
  available_models: string[];
  reachable?: boolean;
  base_url?: string;
};

export type AgentInviteRoute = {
  route: string;
  model: string;
  auth_mode: string;
  credential_configured: boolean;
};

export type AgentInfo = {
  name: string;
  label: string;
  description: string;
  system_prompt?: string;
  invite_route?: AgentInviteRoute;
};

export type LocalModelStatus = {
  base_url: string;
  reachable: boolean;
  models_available: boolean;
  models: string[];
  model_ids: string[];
  error: string | null;
};

export type ControlsConfig = {
  active_model: string;
  default_selection: {
    provider: string;
    model: string;
    label?: string;
  };
  stack: {
    primary: string;
    backup_1: string;
    backup_2: string;
    heavy_hitter: string;
  };
  local_runtime: {
    base_url: string;
    default_local_model: string;
  };
  routing_policy: {
    cross_provider_fallback: boolean;
  };
  agent_overrides: Record<string, { route: string; model: string }>;
  available_agents: AgentInfo[];
  model_labels: Record<string, string>;
  providers: ProviderStatus[];
  ollama_status: LocalModelStatus;
  token_guardian_mode: "off" | "shadow" | "live";
  security_guardrails_enabled: boolean;
  custom_guardrails: string;
  pin_configured: boolean;
  notices: string[];
};

export type OpenRouterModel = {
  id: string;
  raw_id: string;
  label: string;
  context_length?: number;
  is_free: boolean;
};

export type GuardianStatus = {
  available: boolean;
  security_guardrails_enabled: boolean;
  pin_configured: boolean;
  task_guardian_enabled: boolean;
  memory_guardian_enabled: boolean;
  token_guardian_mode: string;
  breakglass: { active: boolean };
  vault: { configured: boolean; mode: string };
};

export type SecurityStatus = {
  operator: {
    mode: string;
    pin_configured: boolean;
    breakglass_active: boolean;
    usernames: string[];
  };
  passphrase: {
    label: string;
    configured: boolean;
  };
  security_guardrails_enabled: boolean;
  custom_guardrails: string;
  provider_storage: string;
  operator_guidance: Array<{ area: string; operator_action: string }>;
};

export type DashboardSummary = {
  summary: {
    rooms_count: number;
    open_tasks: number;
    pending_reminders: number;
    pending_approvals: number;
    guardian_jobs: number;
    guardian_jobs_enabled: number;
    task_guardian_enabled: boolean;
    token_guardian_mode: string;
    security_guardrails_enabled: boolean;
    tasks_count?: number;
    paused_tasks_count?: number;
    done_tasks_count?: number;
    canceled_tasks_count?: number;
    blocked_tasks_count?: number;
    task_execution_enabled?: boolean;
  };
  today: {
    meeting_artifacts: unknown[];
    inbox: { summary_text: string };
  };
};

export type SpineOverview = {
  open_queue: unknown[];
  blocked_queue: unknown[];
  approval_waiting_queue: unknown[];
  stale_queue: unknown[];
  orphan_queue: unknown[];
  missing_source_queue: unknown[];
  missing_project_queue: unknown[];
  recently_resurfaced_queue: unknown[];
  assignment_ready_queue: unknown[];
  executive_directives_queue: unknown[];
  completed_queue?: unknown[];
  status: string;
  note: string;
  workstation_counts?: Record<string, number | boolean>;
  task_execution_enabled?: boolean;
};

const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";

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

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const endpoint = new URL(path, API_BASE_URL).toString();
  const response = await fetch(endpoint, {
    ...init,
    headers: {
      Accept: "application/json",
      ...(init?.body ? { "Content-Type": "application/json" } : {}),
      ...init?.headers
    },
    cache: "no-store"
  });

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const payload = (await response.json()) as { detail?: string };
      if (payload.detail) detail = payload.detail;
    } catch {
      // Keep the generic status message.
    }
    throw new Error(detail);
  }

  return (await response.json()) as T;
}

export function fetchControlsConfig(): Promise<ControlsConfig> {
  return fetchJson<ControlsConfig>("/api/v1/chat/models/config");
}

export function saveControlsConfig(payload: unknown): Promise<ControlsConfig> {
  return fetchJson<ControlsConfig>("/api/v1/chat/models/config", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function fetchOpenRouterModels(): Promise<{ models: OpenRouterModel[] }> {
  return fetchJson<{ models: OpenRouterModel[] }>("/api/v1/chat/openrouter/models");
}

export function fetchLocalModelStatus(): Promise<LocalModelStatus> {
  return fetchJson<LocalModelStatus>("/api/v1/chat/ollama/status");
}

export function fetchGuardianStatus(): Promise<GuardianStatus> {
  return fetchJson<GuardianStatus>("/api/v1/chat/guardian/status");
}

export function fetchSecurityStatus(): Promise<SecurityStatus> {
  return fetchJson<SecurityStatus>("/api/v1/chat/security/status");
}

export function fetchDashboardSummary(): Promise<DashboardSummary> {
  return fetchJson<DashboardSummary>("/api/v1/chat/dashboard/summary");
}

export function fetchSpineOverview(): Promise<SpineOverview> {
  return fetchJson<SpineOverview>("/api/v1/chat/spine/operator/overview");
}

export function saveOperatorPin(payload: { current_pin?: string; pin: string }): Promise<{ ok: boolean }> {
  return fetchJson<{ ok: boolean }>("/api/v1/chat/security/operator-pin", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function createAgent(payload: { name: string; description: string; system_prompt: string }): Promise<AgentInfo> {
  return fetchJson<AgentInfo>("/api/v1/chat/agents", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function updateAgent(agentName: string, payload: { description?: string; system_prompt?: string }): Promise<AgentInfo> {
  return fetchJson<AgentInfo>(`/api/v1/chat/agents/${encodeURIComponent(agentName)}`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
}

export function saveAgentInviteRoute(
  agentName: string,
  payload: { model?: string; api_key?: string; auth_mode?: string }
): Promise<{ name: string; configured: boolean; invite_route: AgentInviteRoute | null }> {
  return fetchJson<{ name: string; configured: boolean; invite_route: AgentInviteRoute | null }>(
    `/api/v1/chat/agents/${encodeURIComponent(agentName)}/invite-route`,
    {
      method: "POST",
      body: JSON.stringify(payload)
    }
  );
}

export function clearAgentInviteRoute(agentName: string): Promise<{ name: string; configured: boolean; invite_route: null }> {
  return fetchJson<{ name: string; configured: boolean; invite_route: null }>(`/api/v1/chat/agents/${encodeURIComponent(agentName)}/invite-route`, {
    method: "DELETE"
  });
}

export type WorkstationSeat = {
  seat_index: number;
  label: string;
  agent: string;
  provider: string;
  model: string;
  updated_at: string;
};

export type WorkstationRoom = {
  id: string;
  title: string;
  status: string;
  phase: string;
  goal: string;
  summary: string;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  participants?: unknown[];
  notes?: WorkstationNote[];
};

export type WorkstationNote = {
  id: string;
  title: string;
  body: string;
  surface: string;
  source_id: string;
  actor: string;
  tags: string[];
  created_at: string;
  updated_at: string;
};

export type WorkstationMemory = {
  id: string;
  content: string;
  memory_type: string;
  source_surface: string;
  source_id: string;
  actor: string;
  tags: string[];
  created_at: string;
  updated_at: string;
};

export type WorkstationEvent = {
  id: string;
  event_type: string;
  surface: string;
  source_id: string;
  actor: string;
  summary: string;
  payload: Record<string, unknown>;
  created_at: string;
};

export type EventProducer = {
  subsystem: string;
  description: string;
  event_types: string[];
  event_count: number;
  last_event_at: string | null;
};

export type TaskHistoryEntry = {
  id: string;
  task_id: string;
  event_type: string;
  status_from: string;
  status_to: string;
  note: string;
  actor: string;
  metadata: Record<string, unknown>;
  created_at: string;
};

export type WorkstationTask = {
  id: string;
  title: string;
  status: "open" | "paused" | "done" | "canceled" | "blocked" | string;
  notes: string;
  surface: string;
  source_id: string;
  actor: string;
  tags: string[];
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  execution_enabled: boolean;
  history?: TaskHistoryEntry[];
};

export type GuardianConfirmation = {
  id: string;
  action_type: string;
  status: string;
  risk_level: string;
  prompt: string;
  surface: string;
  source_id: string;
  created_at: string;
  expires_at: string;
  resolved_at: string | null;
  used_at: string | null;
};

export type ChatMessage = {
  id: string;
  session_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  actor: string;
  provider: string;
  model: string;
  metadata: Record<string, unknown>;
  created_at: string;
};

export type ChatSession = {
  id: string;
  title: string;
  status: string;
  active_room_id: string;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  messages?: ChatMessage[];
  notes?: WorkstationNote[];
  last_message?: ChatMessage | null;
  message_count?: number;
};

export type ChatTurnResult = {
  session: ChatSession;
  user_message: ChatMessage;
  assistant_message: ChatMessage;
  route: { provider: string; model: string; label: string; seat_index: number; seat_label: string; agent: string };
  context: { memories: WorkstationMemory[]; notes: WorkstationNote[] };
  saved_memory: WorkstationMemory | null;
  guardian_confirmation: GuardianConfirmation | null;
  blocked_action: string | null;
  model_execution: {
    status: string;
    provider: string;
    model: string;
    event_id: string;
    error: string;
  };
  workstation: WorkstationState;
};

export type RoundTableParticipant = {
  seat_index: number;
  label: string;
  agent: string;
  provider: string;
  model: string;
  role: string;
};

export type RoundTableTurn = {
  id: string;
  session_id: string;
  room_id: string;
  turn_index: number;
  phase: string;
  seat_index: number | null;
  agent: string;
  role: string;
  content: string;
  assignment_id: string;
  provider: string;
  model: string;
  metadata: Record<string, unknown>;
  created_at: string;
};

export type RoundTableAssignment = {
  id: string;
  session_id: string;
  room_id: string;
  seat_index: number | null;
  agent: string;
  title: string;
  instruction: string;
  status: string;
  response_turn_id: string;
  created_at: string;
  updated_at: string;
};

export type RoundTableSummary = {
  id: string;
  session_id: string;
  room_id: string;
  phase: string;
  content: string;
  note_id: string;
  created_at: string;
};

export type RoundTableSession = {
  id: string;
  room_id: string;
  title: string;
  status: string;
  phase: string;
  goal: string;
  context_query: string;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  room?: WorkstationRoom | null;
  participants?: RoundTableParticipant[];
  turns?: RoundTableTurn[];
  assignments?: RoundTableAssignment[];
  summaries?: RoundTableSummary[];
  notes?: WorkstationNote[];
  turn_count?: number;
  assignment_count?: number;
  blocked_action?: string;
};

export type WorkstationState = {
  controls: ControlsConfig;
  seats: WorkstationSeat[];
  rooms: WorkstationRoom[];
  notes: WorkstationNote[];
  memory: { items: WorkstationMemory[]; count: number };
  events: WorkstationEvent[];
  producers: EventProducer[];
  tasks: {
    items: WorkstationTask[];
    count: number;
    open_count: number;
    paused_count: number;
    done_count: number;
    canceled_count: number;
    blocked_count: number;
    history: TaskHistoryEntry[];
    execution_enabled: boolean;
  };
  guardian: {
    pending_confirmations: GuardianConfirmation[];
    recent_confirmations: GuardianConfirmation[];
  };
  chat: {
    sessions: ChatSession[];
    sessions_count: number;
    messages_count: number;
  };
  roundtable: {
    sessions: RoundTableSession[];
    sessions_count: number;
    turns_count: number;
    assignments_count: number;
    summaries_count: number;
  };
  dashboard: {
    rooms_count: number;
    notes_count: number;
    memory_count: number;
    events_count: number;
    seat_count: number;
    chat_sessions_count: number;
    chat_messages_count: number;
    roundtable_sessions_count: number;
    roundtable_turns_count: number;
    roundtable_assignments_count: number;
    roundtable_summaries_count: number;
    pending_confirmations: number;
    tasks_count: number;
    open_tasks_count: number;
    paused_tasks_count: number;
    done_tasks_count: number;
    canceled_tasks_count: number;
    blocked_tasks_count: number;
    task_history_count: number;
    task_execution_enabled: boolean;
  };
  storage: { type: string; path: string };
};

export type WorkstationHistory = WorkstationState;

export function fetchWorkstationState(): Promise<WorkstationState> {
  return fetchJson<WorkstationState>("/api/workstation/state");
}

export function fetchWorkstationHistory(limit = 25): Promise<WorkstationHistory> {
  return fetchJson<WorkstationHistory>(`/api/workstation/history?limit=${limit}`);
}

export function updateSeat(
  seatIndex: number,
  payload: { label?: string; agent?: string; provider?: string; model?: string }
): Promise<WorkstationSeat> {
  return fetchJson<WorkstationSeat>(`/api/seats/${seatIndex}`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
}

export function createNote(payload: {
  title: string;
  body: string;
  surface?: string;
  source_id?: string;
  tags?: string[];
}): Promise<WorkstationNote> {
  return fetchJson<WorkstationNote>("/api/notes", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function fetchNote(noteId: string): Promise<WorkstationNote> {
  return fetchJson<WorkstationNote>(`/api/notes/${encodeURIComponent(noteId)}`);
}

export function updateNote(noteId: string, payload: {
  title?: string;
  body?: string;
  surface?: string;
  source_id?: string;
  tags?: string[];
}): Promise<WorkstationNote> {
  return fetchJson<WorkstationNote>(`/api/notes/${encodeURIComponent(noteId)}`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
}

export function fetchTasks(params: { limit?: number; status?: string } = {}): Promise<{ tasks: WorkstationTask[]; count: number; execution_enabled: boolean }> {
  const search = new URLSearchParams();
  if (params.limit) search.set("limit", String(params.limit));
  if (params.status) search.set("status", params.status);
  const query = search.toString();
  return fetchJson<{ tasks: WorkstationTask[]; count: number; execution_enabled: boolean }>(`/api/tasks${query ? `?${query}` : ""}`);
}

export function createTask(payload: {
  title: string;
  notes?: string;
  status?: string;
  surface?: string;
  source_id?: string;
  tags?: string[];
  metadata?: Record<string, unknown>;
}): Promise<WorkstationTask> {
  return fetchJson<WorkstationTask>("/api/tasks", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function updateTask(taskId: string, payload: {
  title?: string;
  notes?: string;
  status?: string;
  surface?: string;
  source_id?: string;
  tags?: string[];
  metadata?: Record<string, unknown>;
}): Promise<WorkstationTask> {
  return fetchJson<WorkstationTask>(`/api/tasks/${encodeURIComponent(taskId)}`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
}

export function transitionTask(taskId: string, operation: "pause" | "resume" | "done" | "cancel"): Promise<WorkstationTask> {
  return fetchJson<WorkstationTask>(`/api/tasks/${encodeURIComponent(taskId)}/${operation}`, {
    method: "POST",
    body: JSON.stringify({})
  });
}

export function fetchEvents(params: {
  limit?: number;
  event_type?: string;
  surface?: string;
  source_id?: string;
} = {}): Promise<{ events: WorkstationEvent[]; count: number }> {
  const search = new URLSearchParams();
  if (params.limit) search.set("limit", String(params.limit));
  if (params.event_type) search.set("event_type", params.event_type);
  if (params.surface) search.set("surface", params.surface);
  if (params.source_id) search.set("source_id", params.source_id);
  const query = search.toString();
  return fetchJson<{ events: WorkstationEvent[]; count: number }>(`/api/events${query ? `?${query}` : ""}`);
}

export function fetchEventProducers(): Promise<{ producers: EventProducer[]; count: number }> {
  return fetchJson<{ producers: EventProducer[]; count: number }>("/api/events/producers");
}

export function createMemory(payload: {
  content: string;
  memory_type?: string;
  source_surface?: string;
  source_id?: string;
  tags?: string[];
}): Promise<WorkstationMemory> {
  return fetchJson<WorkstationMemory>("/api/memory", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function updateMemory(memoryId: string, payload: {
  content?: string;
  memory_type?: string;
  source_surface?: string;
  source_id?: string;
  tags?: string[];
}): Promise<WorkstationMemory> {
  return fetchJson<WorkstationMemory>(`/api/memory/${encodeURIComponent(memoryId)}`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
}

export function createGuardianConfirmation(payload: {
  action_type: string;
  risk_level?: string;
  prompt?: string;
  surface?: string;
  source_id?: string;
  actor?: string;
}): Promise<GuardianConfirmation> {
  return fetchJson<GuardianConfirmation>("/api/guardian/actions/confirmations", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function decideGuardianConfirmation(confirmationId: string, decision: "approved" | "denied"): Promise<GuardianConfirmation> {
  return fetchJson<GuardianConfirmation>(`/api/guardian/actions/confirmations/${encodeURIComponent(confirmationId)}/decision`, {
    method: "POST",
    body: JSON.stringify({ decision })
  });
}

export function deleteMemory(memoryId: string, confirmationId: string): Promise<{ deleted: string }> {
  const params = new URLSearchParams({ confirmation_id: confirmationId });
  return fetchJson<{ deleted: string }>(`/api/memory/${encodeURIComponent(memoryId)}?${params.toString()}`, {
    method: "DELETE"
  });
}

export function createRoom(payload: {
  title: string;
  status?: string;
  phase?: string;
  goal?: string;
  summary?: string;
  metadata?: Record<string, unknown>;
}): Promise<WorkstationRoom> {
  return fetchJson<WorkstationRoom>("/api/rooms", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function fetchChatSessions(limit = 50): Promise<{ sessions: ChatSession[]; count: number }> {
  return fetchJson<{ sessions: ChatSession[]; count: number }>(`/api/chat/sessions?limit=${limit}`);
}

export function createChatSession(payload: {
  title?: string;
  active_room_id?: string;
  metadata?: Record<string, unknown>;
} = {}): Promise<ChatSession> {
  return fetchJson<ChatSession>("/api/chat/sessions", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function fetchChatSession(sessionId: string): Promise<ChatSession> {
  return fetchJson<ChatSession>(`/api/chat/sessions/${sessionId}`);
}

export function sendChatMessage(payload: {
  session_id?: string;
  content: string;
  save_to_memory?: boolean;
  metadata?: Record<string, unknown>;
}): Promise<ChatTurnResult> {
  return fetchJson<ChatTurnResult>("/api/chat/messages", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function fetchRoundTableSessions(limit = 50): Promise<{ sessions: RoundTableSession[]; count: number }> {
  return fetchJson<{ sessions: RoundTableSession[]; count: number }>(`/api/roundtable/sessions?limit=${limit}`);
}

export function createRoundTableSession(payload: {
  room_id?: string;
  title?: string;
  goal?: string;
  context_query?: string;
  metadata?: Record<string, unknown>;
}): Promise<RoundTableSession> {
  return fetchJson<RoundTableSession>("/api/roundtable/sessions", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function fetchRoundTableSession(sessionId: string): Promise<RoundTableSession> {
  return fetchJson<RoundTableSession>(`/api/roundtable/sessions/${sessionId}`);
}

export function runRoundTableSession(sessionId: string): Promise<RoundTableSession> {
  return fetchJson<RoundTableSession>(`/api/roundtable/sessions/${sessionId}/run`, {
    method: "POST",
    body: JSON.stringify({})
  });
}
