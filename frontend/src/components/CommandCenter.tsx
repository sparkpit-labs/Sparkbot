import { useEffect, useMemo, useState } from "react";

import {
  API_BASE_URL,
  createAgent,
  fetchWorkstationState,
  fetchDashboardSummary,
  fetchGuardianStatus,
  fetchLocalModelStatus,
  fetchOpenRouterModels,
  fetchSecurityStatus,
  fetchSpineOverview,
  saveControlsConfig,
  saveOperatorPin,
  updateSeat as persistSeat,
  type AgentInfo,
  type ControlsConfig,
  type DashboardSummary,
  type GuardianStatus,
  type LocalModelStatus,
  type OpenRouterModel,
  type SecurityStatus,
  type SpineOverview,
  type WorkstationState,
  type WorkstationSeat
} from "../api";

type LoadState = "loading" | "ready" | "error";

type SeatState = WorkstationSeat;

const fallbackConfig: ControlsConfig = {
  active_model: "openrouter/openai/gpt-4o-mini",
  default_selection: {
    provider: "openrouter",
    model: "openrouter/openai/gpt-4o-mini",
    label: "OpenRouter - GPT-4o Mini"
  },
  stack: {
    primary: "openrouter/openai/gpt-4o-mini",
    backup_1: "gpt-4o-mini",
    backup_2: "claude-3-5-sonnet-latest",
    heavy_hitter: "gpt-4o"
  },
  local_runtime: {
    base_url: "http://127.0.0.1:11434",
    default_local_model: "ollama/phi4-mini"
  },
  routing_policy: { cross_provider_fallback: false },
  agent_overrides: {},
  available_agents: [
    { name: "meetings_manager", label: "Meetings Manager", description: "Runs agendas, assignments, summaries, and follow-up plans." },
    { name: "researcher", label: "Researcher", description: "Investigates facts and context." },
    { name: "analyst", label: "Analyst", description: "Structures tradeoffs and data." },
    { name: "writer", label: "Writer", description: "Drafts notes, summaries, and messaging." },
    { name: "builder", label: "Builder", description: "Turns decisions into implementation steps." }
  ],
  model_labels: {
    "openrouter/openai/gpt-4o-mini": "OpenRouter - GPT-4o Mini",
    "gpt-4o-mini": "OpenAI - GPT-4o Mini",
    "claude-3-5-sonnet-latest": "Anthropic - Claude 3.5 Sonnet",
    "ollama/phi4-mini": "Phi-4 Mini - default local"
  },
  providers: [],
  ollama_status: {
    base_url: "http://127.0.0.1:11434",
    reachable: false,
    models_available: false,
    models: [],
    model_ids: [],
    error: null
  },
  token_guardian_mode: "shadow",
  security_guardrails_enabled: false,
  custom_guardrails: "",
  pin_configured: false,
  notices: []
};

const providerSecretFields: Record<string, string> = {
  openrouter: "openrouter_api_key",
  openai: "openai_api_key",
  anthropic: "anthropic_api_key",
  google: "google_api_key",
  groq: "groq_api_key",
  minimax: "minimax_api_key",
  xai: "xai_api_key"
};

const stackFields: Array<[keyof ControlsConfig["stack"], string]> = [
  ["primary", "Primary"],
  ["backup_1", "Backup 1"],
  ["backup_2", "Backup 2"],
  ["heavy_hitter", "Heavy Hitter"]
];

const queueLabels: Array<[keyof SpineOverview, string]> = [
  ["open_queue", "Open"],
  ["blocked_queue", "Blocked"],
  ["approval_waiting_queue", "Approval waiting"],
  ["stale_queue", "Stale"],
  ["orphan_queue", "Orphaned"],
  ["assignment_ready_queue", "Ready"],
  ["executive_directives_queue", "Directives"]
];

function getFallbackSeats(agents: AgentInfo[]): SeatState[] {
  return Array.from({ length: 8 }, (_, index) => {
    const agent = agents[index % Math.max(agents.length, 1)]?.name || "";
    return {
      seat_index: index + 1,
      label: `Seat ${index + 1}`,
      agent,
      provider: "default",
      model: "",
      updated_at: ""
    };
  });
}

function statusLabel(value: boolean): string {
  return value ? "Ready" : "Needs setup";
}

function modelLabel(config: ControlsConfig, modelId: string): string {
  return config.model_labels[modelId] || modelId || "No model selected";
}

function providerForModel(modelId: string): string {
  if (modelId.startsWith("openrouter/")) return "openrouter";
  if (modelId.startsWith("ollama/")) return "ollama";
  if (modelId.startsWith("gpt-")) return "openai";
  if (modelId.startsWith("claude-")) return "anthropic";
  if (modelId.startsWith("gemini/")) return "google";
  if (modelId.startsWith("groq/")) return "groq";
  if (modelId.startsWith("minimax/")) return "minimax";
  if (modelId.startsWith("xai/")) return "xai";
  if (modelId.startsWith("openai-codex/")) return "openai_codex";
  if (modelId.startsWith("claude-sub/")) return "claude_sub";
  return "default";
}

function allModelOptions(config: ControlsConfig, openRouterModels: OpenRouterModel[]): string[] {
  const models = new Set<string>();
  config.providers.forEach((provider) => {
    provider.models.forEach((model) => models.add(model));
    provider.available_models.forEach((model) => models.add(model));
  });
  openRouterModels.forEach((model) => models.add(model.id));
  Object.keys(config.model_labels).forEach((model) => models.add(model));
  Object.values(config.stack).forEach((model) => models.add(model));
  if (config.local_runtime.default_local_model) models.add(config.local_runtime.default_local_model);
  return Array.from(models).filter(Boolean).sort();
}

export default function CommandCenter() {
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [config, setConfig] = useState<ControlsConfig>(fallbackConfig);
  const [guardian, setGuardian] = useState<GuardianStatus | null>(null);
  const [security, setSecurity] = useState<SecurityStatus | null>(null);
  const [dashboard, setDashboard] = useState<DashboardSummary | null>(null);
  const [spine, setSpine] = useState<SpineOverview | null>(null);
  const [openRouterModels, setOpenRouterModels] = useState<OpenRouterModel[]>([]);
  const [selectedProvider, setSelectedProvider] = useState(fallbackConfig.default_selection.provider);
  const [selectedModel, setSelectedModel] = useState(fallbackConfig.default_selection.model);
  const [stackDraft, setStackDraft] = useState(fallbackConfig.stack);
  const [localBaseUrl, setLocalBaseUrl] = useState(fallbackConfig.local_runtime.base_url);
  const [localModel, setLocalModel] = useState(fallbackConfig.local_runtime.default_local_model);
  const [localStatus, setLocalStatus] = useState<LocalModelStatus>(fallbackConfig.ollama_status);
  const [providerDrafts, setProviderDrafts] = useState<Record<string, string>>({});
  const [agentOverrides, setAgentOverrides] = useState(fallbackConfig.agent_overrides);
  const [customGuardrails, setCustomGuardrails] = useState("");
  const [pinDraft, setPinDraft] = useState({ current: "", next: "", confirm: "" });
  const [tokenMode, setTokenMode] = useState<"off" | "shadow" | "live">("shadow");
  const [message, setMessage] = useState("Loading Command Center...");
  const [error, setError] = useState<string | null>(null);
  const [refreshingModels, setRefreshingModels] = useState(false);
  const [checkingLocal, setCheckingLocal] = useState(false);
  const [seats, setSeats] = useState<SeatState[]>(() => getFallbackSeats(fallbackConfig.available_agents));
  const [workstation, setWorkstation] = useState<WorkstationState | null>(null);
  const [newAgent, setNewAgent] = useState({ name: "", description: "", prompt: "" });

  const models = useMemo(() => allModelOptions(config, openRouterModels), [config, openRouterModels]);
  const provider = config.providers.find((item) => item.id === selectedProvider);
  const defaultProvider = config.providers.find((item) => item.id === config.default_selection.provider);

  async function refreshAll() {
    setLoadState("loading");
    setError(null);
    try {
      const [workstationResult, guardianResult, securityResult, dashboardResult, spineResult] = await Promise.allSettled([
        fetchWorkstationState(),
        fetchGuardianStatus(),
        fetchSecurityStatus(),
        fetchDashboardSummary(),
        fetchSpineOverview()
      ]);

      if (workstationResult.status === "fulfilled") {
        setWorkstation(workstationResult.value);
        applyConfig(workstationResult.value.controls);
        setSeats(workstationResult.value.seats.length ? workstationResult.value.seats : getFallbackSeats(workstationResult.value.controls.available_agents));
      } else {
        throw workstationResult.reason;
      }
      if (guardianResult.status === "fulfilled") setGuardian(guardianResult.value);
      if (securityResult.status === "fulfilled") setSecurity(securityResult.value);
      if (dashboardResult.status === "fulfilled") setDashboard(dashboardResult.value);
      if (spineResult.status === "fulfilled") setSpine(spineResult.value);
      setLoadState("ready");
      setMessage("Command Center synced with the local backend.");
    } catch (caught) {
      setLoadState("error");
      setError(caught instanceof Error ? caught.message : "Command Center backend is unavailable.");
      setMessage("Command Center is showing the local fallback layout until the backend is reachable.");
    }
  }

  function applyConfig(nextConfig: ControlsConfig) {
    setConfig(nextConfig);
    setSelectedProvider(nextConfig.default_selection.provider);
    setSelectedModel(nextConfig.default_selection.model);
    setStackDraft(nextConfig.stack);
    setLocalBaseUrl(nextConfig.local_runtime.base_url);
    setLocalModel(nextConfig.local_runtime.default_local_model);
    setLocalStatus(nextConfig.ollama_status);
    setAgentOverrides(nextConfig.agent_overrides || {});
    setCustomGuardrails(nextConfig.custom_guardrails || "");
    setTokenMode(nextConfig.token_guardian_mode);
    setSeats((current) => current.length ? current : getFallbackSeats(nextConfig.available_agents));
  }

  useEffect(() => {
    void refreshAll();
  }, []);

  async function saveDefaultModel() {
    setError(null);
    try {
      const next = await saveControlsConfig({
        default_selection: { provider: selectedProvider, model: selectedModel }
      });
      applyConfig(next);
      setMessage(next.notices[0] || "Default model saved.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Default model could not be saved.");
    }
  }

  async function saveProviderCredential() {
    setError(null);
    const field = providerSecretFields[selectedProvider];
    if (!field) {
      setError("This provider does not use a browser-entered credential in the public Command Center.");
      return;
    }
    const value = providerDrafts[selectedProvider]?.trim();
    if (!value) {
      setError("Paste a replacement credential before saving.");
      return;
    }
    try {
      const next = await saveControlsConfig({ providers: { [field]: value } });
      setProviderDrafts((drafts) => ({ ...drafts, [selectedProvider]: "" }));
      applyConfig(next);
      setMessage("Credential saved server-side. The browser did not retain the value.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Credential could not be saved.");
    }
  }

  async function refreshOpenRouter() {
    setRefreshingModels(true);
    setError(null);
    try {
      const result = await fetchOpenRouterModels();
      setOpenRouterModels(result.models);
      setMessage(`OpenRouter model list refreshed: ${result.models.length} models available.`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "OpenRouter models could not be refreshed.");
    } finally {
      setRefreshingModels(false);
    }
  }

  async function checkLocalModels() {
    setCheckingLocal(true);
    setError(null);
    try {
      const next = await saveControlsConfig({ local_runtime: { base_url: localBaseUrl } });
      applyConfig(next);
      const status = await fetchLocalModelStatus();
      setLocalStatus(status);
      setMessage(status.reachable ? "Local model endpoint is reachable." : "Local model endpoint is not reachable.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Local model status could not be checked.");
    } finally {
      setCheckingLocal(false);
    }
  }

  async function saveLocalModel() {
    setError(null);
    try {
      const next = await saveControlsConfig({
        local_runtime: { base_url: localBaseUrl, default_local_model: localModel },
        default_selection: selectedProvider === "ollama" ? { provider: "ollama", model: localModel } : undefined
      });
      applyConfig(next);
      setMessage("Local model route saved.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Local model route could not be saved.");
    }
  }

  async function saveStack() {
    setError(null);
    try {
      const next = await saveControlsConfig({ stack: stackDraft });
      applyConfig(next);
      setMessage("Four-model stack saved.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Model stack could not be saved.");
    }
  }

  async function saveAgentOverrides() {
    setError(null);
    try {
      const next = await saveControlsConfig({ agent_overrides: agentOverrides });
      applyConfig(next);
      setMessage("Agent model overrides saved.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Agent overrides could not be saved.");
    }
  }

  async function saveSecurity(enabled: boolean) {
    setError(null);
    try {
      const next = await saveControlsConfig({ security_guardrails_enabled: enabled });
      applyConfig(next);
      setMessage(enabled ? "Security profile enabled." : "Security profile disabled for owner-local work.");
      void refreshAll();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Security profile could not be saved.");
    }
  }

  async function saveGuardrails() {
    setError(null);
    try {
      const next = await saveControlsConfig({ custom_guardrails: customGuardrails });
      applyConfig(next);
      setMessage("Custom guardrails saved.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Guardrails could not be saved.");
    }
  }

  async function saveTokenMode() {
    setError(null);
    try {
      const next = await saveControlsConfig({ token_guardian_mode: tokenMode });
      applyConfig(next);
      setMessage("Model routing monitor mode saved.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Routing monitor mode could not be saved.");
    }
  }

  async function savePin() {
    setError(null);
    if (pinDraft.next !== pinDraft.confirm) {
      setError("PIN confirmation does not match.");
      return;
    }
    try {
      await saveOperatorPin({ current_pin: pinDraft.current || undefined, pin: pinDraft.next });
      setPinDraft({ current: "", next: "", confirm: "" });
      setMessage("Operator PIN saved.");
      void refreshAll();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "PIN could not be saved.");
    }
  }

  async function spawnAgent() {
    setError(null);
    try {
      await createAgent({ name: newAgent.name, description: newAgent.description, system_prompt: newAgent.prompt });
      setNewAgent({ name: "", description: "", prompt: "" });
      setMessage("Agent created and added to Command Center routing.");
      void refreshAll();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Agent could not be created.");
    }
  }

  async function updateSeat(index: number, patch: Partial<SeatState>) {
    setError(null);
    const current = seats[index];
    if (!current) return;
    const nextModel = patch.model ?? current.model;
    const nextAgent = patch.agent ?? current.agent;
    const nextProvider = patch.provider ?? (patch.model !== undefined ? providerForModel(nextModel) : current.provider);
    try {
      const saved = await persistSeat(current.seat_index || index + 1, {
        label: patch.label ?? current.label,
        agent: nextAgent,
        provider: nextProvider,
        model: nextModel
      });
      setSeats((items) => items.map((seat, seatIndex) => (seatIndex === index ? saved : seat)));
      if (nextAgent) {
        setAgentOverrides((overrides) => ({
          ...overrides,
          [nextAgent]: {
            route: nextModel ? providerForModel(nextModel) : nextProvider || overrides[nextAgent]?.route || "default",
            model: nextModel || overrides[nextAgent]?.model || ""
          }
        }));
      }
      setMessage((saved.label || "Seat") + " saved to Workstation state.");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Seat assignment could not be saved.");
    }
  }

  return (
    <section className="command-center" aria-label="Workstation Command Center">
      <header className="command-header">
        <div>
          <p className="eyebrow">Sparkbot operations</p>
          <h2>Workstation Command Center</h2>
          <p>
            Configuration and security surface for AI setup, model routing, local models, agents, Guardian settings,
            dashboard status, and Spine inspection.
          </p>
        </div>
        <div className="command-header-actions">
          <span className={`status-badge ${loadState === "ready" ? "status-worksToday" : loadState === "loading" ? "status-preview" : "status-notImplemented"}`}>
            {loadState === "ready" ? "Backend synced" : loadState === "loading" ? "Syncing" : "Backend needed"}
          </span>
          <button type="button" onClick={refreshAll}>Refresh</button>
        </div>
      </header>

      <nav className="command-tabs" aria-label="Command Center sections">
        {[
          ["ai-setup", "AI Setup"],
          ["security", "Security"],
          ["connectors", "Comms"],
          ["agents", "Agents"],
          ["operations", "Operations"],
          ["spine", "Spine"],
          ["seats", "Seats"]
        ].map(([id, label]) => (
          <a key={id} href={`#${id}`}>{label}</a>
        ))}
      </nav>

      <div className="command-message" role="status">
        <span>{message}</span>
        <span>API base URL: {API_BASE_URL}</span>
      </div>
      {error ? <div className="command-error" role="alert">{error}</div> : null}

      <section className="command-grid command-grid-setup" id="ai-setup" aria-labelledby="ai-setup-heading">
        <article className="command-panel command-panel-wide">
          <div className="command-panel-heading">
            <p className="eyebrow">Provider selection</p>
            <h3 id="ai-setup-heading">AI Setup</h3>
            <p>Default provider, model picker, OpenRouter refresh, local model route, and four-model stack.</p>
          </div>

          <div className="provider-button-grid" role="list" aria-label="Provider options">
            {config.providers.map((item) => (
              <button
                key={item.id}
                type="button"
                className={item.id === selectedProvider ? "provider-button provider-button-active" : "provider-button"}
                onClick={() => {
                  setSelectedProvider(item.id);
                  const firstModel = item.id === "openrouter" && openRouterModels[0]
                    ? openRouterModels[0].id
                    : item.models[0] || item.available_models[0] || selectedModel;
                  setSelectedModel(firstModel);
                }}
              >
                <span>{item.label}</span>
                <strong>{statusLabel(item.configured || item.models_available)}</strong>
              </button>
            ))}
          </div>

          <div className="field-grid two-columns">
            <label>
              <span>Selected provider</span>
              <input value={provider?.label || selectedProvider} readOnly />
            </label>
            <label>
              <span>Selected model</span>
              <select value={selectedModel} onChange={(event) => setSelectedModel(event.target.value)}>
                <option value="">Choose a model</option>
                {(selectedProvider === "openrouter" && openRouterModels.length > 0
                  ? openRouterModels.map((model) => model.id)
                  : provider?.models.length ? provider.models : models
                ).map((model) => (
                  <option key={model} value={model}>{modelLabel(config, model)}</option>
                ))}
              </select>
            </label>
          </div>

          <div className="command-actions">
            <button type="button" onClick={saveDefaultModel}>Save default model</button>
            <button type="button" onClick={refreshOpenRouter} disabled={refreshingModels}>
              {refreshingModels ? "Refreshing models..." : "Refresh OpenRouter models"}
            </button>
          </div>

          {providerSecretFields[selectedProvider] ? (
            <div className="field-grid two-columns credential-row">
              <label>
                <span>{provider?.label || selectedProvider} credential</span>
                <input
                  type="password"
                  value={providerDrafts[selectedProvider] || ""}
                  onChange={(event) => setProviderDrafts((drafts) => ({ ...drafts, [selectedProvider]: event.target.value }))}
                  placeholder={provider?.configured ? "Saved server-side. Paste replacement only." : "Paste credential for server-side storage"}
                />
              </label>
              <div className="field-help">
                <strong>Server-side only</strong>
                <span>The browser never receives saved credential values back from the backend.</span>
              </div>
              <button type="button" onClick={saveProviderCredential}>Save credential</button>
            </div>
          ) : null}
        </article>

        <article className="command-panel">
          <div className="command-panel-heading">
            <p className="eyebrow">Local AI</p>
            <h3>Ollama status</h3>
            <p>Checks the configured local model endpoint without calling chat models.</p>
          </div>
          <label>
            <span>Local endpoint</span>
            <input value={localBaseUrl} onChange={(event) => setLocalBaseUrl(event.target.value)} />
          </label>
          <label>
            <span>Preferred local model</span>
            <select value={localModel} onChange={(event) => setLocalModel(event.target.value)}>
              {Array.from(new Set([...localStatus.model_ids, ...config.providers.find((item) => item.id === "ollama")?.models || []])).map((model) => (
                <option key={model} value={model}>{modelLabel(config, model)}</option>
              ))}
            </select>
          </label>
          <div className="status-list">
            <span>Endpoint: {localStatus.reachable ? "reachable" : "not reachable"}</span>
            <span>Models: {localStatus.model_ids.length}</span>
            {localStatus.error ? <span>{localStatus.error}</span> : null}
          </div>
          <div className="command-actions">
            <button type="button" onClick={checkLocalModels} disabled={checkingLocal}>{checkingLocal ? "Checking..." : "Check local"}</button>
            <button type="button" onClick={saveLocalModel}>Save local route</button>
          </div>
        </article>

        <article className="command-panel command-panel-wide">
          <div className="command-panel-heading">
            <p className="eyebrow">Routing stack</p>
            <h3>Four-model stack</h3>
            <p>Primary, backups, and heavy hitter define the local routing stack used by Chat and seats.</p>
          </div>
          <div className="field-grid four-columns">
            {stackFields.map(([field, label]) => (
              <label key={field}>
                <span>{label}</span>
                <select value={stackDraft[field]} onChange={(event) => setStackDraft((draft) => ({ ...draft, [field]: event.target.value }))}>
                  {models.map((model) => <option key={`${field}-${model}`} value={model}>{modelLabel(config, model)}</option>)}
                </select>
              </label>
            ))}
          </div>
          <button type="button" onClick={saveStack}>Save stack</button>
        </article>
      </section>

      <section className="command-grid" id="security" aria-labelledby="security-heading">
        <article className="command-panel">
          <div className="command-panel-heading">
            <p className="eyebrow">Operator profile</p>
            <h3 id="security-heading">Security</h3>
            <p>Owner-controlled security profile for local guardrails and operator setup.</p>
          </div>
          <div className="switch-row">
            <span>Security profile {config.security_guardrails_enabled ? "on" : "off"}</span>
            <button type="button" onClick={() => saveSecurity(!config.security_guardrails_enabled)}>
              {config.security_guardrails_enabled ? "Turn off" : "Turn on"}
            </button>
          </div>
          <label>
            <span>Custom guardrails</span>
            <textarea value={customGuardrails} onChange={(event) => setCustomGuardrails(event.target.value)} rows={5} />
          </label>
          <button type="button" onClick={saveGuardrails}>Save guardrails</button>
          <dl className="mini-metrics">
            <div><dt>PIN</dt><dd>{security?.operator.pin_configured || config.pin_configured ? "configured" : "not configured"}</dd></div>
            <div><dt>Provider storage</dt><dd>{security?.provider_storage || "server-side only"}</dd></div>
          </dl>
        </article>

        <article className="command-panel">
          <div className="command-panel-heading">
            <p className="eyebrow">PIN</p>
            <h3>Operator PIN</h3>
            <p>Used by public-safe action gates as they are added.</p>
          </div>
          {config.pin_configured ? (
            <label>
              <span>Current PIN</span>
              <input type="password" inputMode="numeric" value={pinDraft.current} onChange={(event) => setPinDraft((draft) => ({ ...draft, current: event.target.value }))} />
            </label>
          ) : null}
          <label>
            <span>New 6 digit PIN</span>
            <input type="password" inputMode="numeric" value={pinDraft.next} onChange={(event) => setPinDraft((draft) => ({ ...draft, next: event.target.value }))} />
          </label>
          <label>
            <span>Confirm PIN</span>
            <input type="password" inputMode="numeric" value={pinDraft.confirm} onChange={(event) => setPinDraft((draft) => ({ ...draft, confirm: event.target.value }))} />
          </label>
          <button type="button" onClick={savePin}>{config.pin_configured ? "Change PIN" : "Save PIN"}</button>
        </article>
      </section>

      <section className="command-grid" id="connectors" aria-labelledby="connectors-heading">
        <article className="command-panel command-panel-wide">
          <div className="command-panel-heading">
            <p className="eyebrow">Comms setup</p>
            <h3 id="connectors-heading">Connectors</h3>
            <p>Connector cards remain visible as setup placeholders, but write-capable bridges are disabled until public backend gates exist.</p>
          </div>
          <div className="connector-grid">
            {["Source control", "Email", "Calendar", "Drive", "Team chat", "Webhook bridge"].map((item) => (
              <div className="connector-card" key={item}>
                <strong>{item}</strong>
                <span>Disabled pending public-safe backend gate.</span>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="command-grid" id="agents" aria-labelledby="agents-heading">
        <article className="command-panel command-panel-wide">
          <div className="command-panel-heading">
            <p className="eyebrow">Agents</p>
            <h3 id="agents-heading">Agent routing and Specialty Wing controls</h3>
            <p>Packaged and custom agents share the same model override path used by Workstation seats.</p>
          </div>
          <div className="agent-list">
            {config.available_agents.map((agent) => {
              const override = agentOverrides[agent.name] || { route: "default", model: "" };
              return (
                <div className="agent-row" key={agent.name}>
                  <div>
                    <strong>{agent.label}</strong>
                    <span>{agent.description}</span>
                  </div>
                  <select
                    value={override.route}
                    onChange={(event) => setAgentOverrides((draft) => ({ ...draft, [agent.name]: { ...override, route: event.target.value } }))}
                  >
                    <option value="default">Default stack</option>
                    {config.providers.map((item) => <option key={item.id} value={item.id}>{item.label}</option>)}
                  </select>
                  <select
                    value={override.model}
                    onChange={(event) => setAgentOverrides((draft) => ({ ...draft, [agent.name]: { ...override, model: event.target.value } }))}
                  >
                    <option value="">Use route default</option>
                    {models.map((model) => <option key={`${agent.name}-${model}`} value={model}>{modelLabel(config, model)}</option>)}
                  </select>
                </div>
              );
            })}
          </div>
          <button type="button" onClick={saveAgentOverrides}>Save overrides</button>
        </article>

        <article className="command-panel">
          <div className="command-panel-heading">
            <p className="eyebrow">Spawn Agent</p>
            <h3>Create agent</h3>
            <p>Persists to the local backend Command Center config.</p>
          </div>
          <label><span>Name</span><input value={newAgent.name} onChange={(event) => setNewAgent((draft) => ({ ...draft, name: event.target.value }))} /></label>
          <label><span>Description</span><input value={newAgent.description} onChange={(event) => setNewAgent((draft) => ({ ...draft, description: event.target.value }))} /></label>
          <label><span>System prompt</span><textarea rows={4} value={newAgent.prompt} onChange={(event) => setNewAgent((draft) => ({ ...draft, prompt: event.target.value }))} /></label>
          <button type="button" onClick={spawnAgent} disabled={!newAgent.name.trim()}>Create agent</button>
        </article>
      </section>

      <section className="command-grid" id="operations" aria-labelledby="operations-heading">
        <article className="command-panel">
          <div className="command-panel-heading">
            <p className="eyebrow">Operations</p>
            <h3 id="operations-heading">System Health</h3>
            <p>Command Center status routes for local backend checks.</p>
          </div>
          <dl className="mini-metrics">
            <div><dt>Backend</dt><dd>{loadState === "ready" ? "online" : "needs check"}</dd></div>
            <div><dt>Default provider</dt><dd>{defaultProvider?.label || config.default_selection.provider}</dd></div>
            <div><dt>Default model</dt><dd>{modelLabel(config, config.default_selection.model)}</dd></div>
            <div><dt>Pending approvals</dt><dd>{dashboard?.summary.pending_approvals ?? workstation?.dashboard.pending_confirmations ?? 0}</dd></div>
            <div><dt>Rooms</dt><dd>{workstation?.dashboard.rooms_count ?? 0}</dd></div>
            <div><dt>Notes</dt><dd>{workstation?.dashboard.notes_count ?? 0}</dd></div>
            <div><dt>Memory</dt><dd>{workstation?.dashboard.memory_count ?? 0}</dd></div>
            <div><dt>Events</dt><dd>{workstation?.dashboard.events_count ?? 0}</dd></div>
          </dl>
        </article>

        <article className="command-panel">
          <div className="command-panel-heading">
            <p className="eyebrow">Model routing monitor</p>
            <h3>Token Guardian</h3>
            <p>Routing monitor mode is stored locally; it does not enable external execution.</p>
          </div>
          <select value={tokenMode} onChange={(event) => setTokenMode(event.target.value as "off" | "shadow" | "live")}>
            <option value="off">Off</option>
            <option value="shadow">Shadow</option>
            <option value="live">Live monitor label (no execution)</option>
          </select>
          <button type="button" onClick={saveTokenMode}>Save mode</button>
        </article>

        <article className="command-panel">
          <div className="command-panel-heading">
            <p className="eyebrow">Task Guardian</p>
            <h3>Scheduled work</h3>
            <p>Route status is visible; scheduler and job mutation remain blocked until a public backend gate exists.</p>
          </div>
          <dl className="mini-metrics">
            <div><dt>Jobs</dt><dd>{dashboard?.summary.guardian_jobs ?? 0}</dd></div>
            <div><dt>Enabled</dt><dd>{dashboard?.summary.guardian_jobs_enabled ?? 0}</dd></div>
            <div><dt>Status</dt><dd>{guardian?.task_guardian_enabled ? "enabled" : "blocked in this branch"}</dd></div>
          </dl>
          <button type="button" disabled title="Task scheduler backend is deferred.">Run now</button>
        </article>
      </section>

      <section className="command-grid" id="spine" aria-labelledby="spine-heading">
        <article className="command-panel command-panel-wide">
          <div className="command-panel-heading">
            <p className="eyebrow">Spine inspector</p>
            <h3 id="spine-heading">Spine and Guardian operations</h3>
            <p>{spine?.note || "Spine route is available when the backend is running."}</p>
          </div>
          <div className="spine-stats">
            {queueLabels.map(([key, label]) => (
              <div className="spine-stat" key={String(key)}>
                <span>{label}</span>
                <strong>{Array.isArray(spine?.[key]) ? (spine?.[key] as unknown[]).length : 0}</strong>
              </div>
            ))}
          </div>
          <div className="connector-grid">
            {["Overview", "Queues", "Projects", "Events", "Producers", "Security", "Vault", "Task Guardian", "Improvement"].map((tab) => (
              <div className="connector-card" key={tab}>
                <strong>{tab}</strong>
                <span>{tab === "Overview" ? "Active empty-state route" : "Route path documented for follow-up parity"}</span>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="command-grid" id="seats" aria-labelledby="seats-heading">
        <article className="command-panel command-panel-wide">
          <div className="command-panel-heading">
            <p className="eyebrow">Round Table</p>
            <h3 id="seats-heading">Model seats and Specialty Wing</h3>
            <p>Seat assignment and model routing controls are active; Chat uses the selected configured provider route, while Round Table still runs deterministic provider-safe sessions.</p>
          </div>
          <div className="seat-grid">
            {seats.map((seat, index) => (
              <div className="seat-card" key={`seat-${index + 1}`}>
                <strong>Seat {index + 1}</strong>
                <label>
                  <span>Agent</span>
                  <select value={seat.agent} onChange={(event) => updateSeat(index, { agent: event.target.value })}>
                    {config.available_agents.map((agent) => <option key={agent.name} value={agent.name}>{agent.label}</option>)}
                  </select>
                </label>
                <label>
                  <span>Model</span>
                  <select value={seat.model} onChange={(event) => updateSeat(index, { model: event.target.value })}>
                    <option value="">Use agent default</option>
                    {models.map((model) => <option key={`seat-${index}-${model}`} value={model}>{modelLabel(config, model)}</option>)}
                  </select>
                </label>
              </div>
            ))}
          </div>
          <div className="command-actions">
            <button type="button" onClick={saveAgentOverrides}>Save seat routes</button>
            <button type="button" disabled title="Start deterministic provider-safe Round Table sessions from Workstation. Live provider-seat execution remains deferred.">Configured in Workstation</button>
          </div>
        </article>
      </section>
    </section>
  );
}
