import { FormEvent, useEffect, useState } from "react";

import { fetchProviderConfigStatus, runProviderPrompt, type ProviderConfigStatusPayload, type ProviderPromptResponse } from "../api";
import { fallbackProviderConfigStatus, providerPreviewSummary } from "../providers/providerSetupStatus";
import { formatShellStatus } from "./ShellNavigation";

type ProviderStatusState = {
  payload: ProviderConfigStatusPayload;
  sourceLabel: string;
};

const fallbackProviderStatusState: ProviderStatusState = {
  payload: fallbackProviderConfigStatus,
  sourceLabel: "Using local provider status fallback."
};

const DEFAULT_PROVIDER_SMOKE_MODEL = "meta-llama/llama-3.2-3b-instruct:free";

function formatImplementationStatus(status: string) {
  return status.replace(/-/g, " ");
}

function formatBool(value: boolean) {
  return value ? "configured" : "not configured";
}

function formatProviderLabel(label: string, aliases?: string[]) {
  return aliases?.length ? `${label} (${aliases.join(", ")})` : label;
}

export default function ProviderSetupPreview() {
  const [providerStatusState, setProviderStatusState] = useState<ProviderStatusState>(fallbackProviderStatusState);
  const [selectedPromptProviderId, setSelectedPromptProviderId] = useState("openrouter");
  const [providerPrompt, setProviderPrompt] = useState("Say OK.");
  const [providerModel, setProviderModel] = useState(DEFAULT_PROVIDER_SMOKE_MODEL);
  const [providerResult, setProviderResult] = useState<ProviderPromptResponse | null>(null);
  const [providerError, setProviderError] = useState<string | null>(null);
  const [providerSubmitting, setProviderSubmitting] = useState(false);

  useEffect(() => {
    const controller = new AbortController();

    fetchProviderConfigStatus(controller.signal)
      .then((payload) => {
        setProviderStatusState({
          payload,
          sourceLabel: "Using backend provider configuration status."
        });
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }
        setProviderStatusState(fallbackProviderStatusState);
      });

    return () => controller.abort();
  }, []);

  const { payload } = providerStatusState;
  const promptProviders = payload.providers.filter((provider) => provider.prompt_endpoint);
  const selectedPromptProvider =
    promptProviders.find((provider) => provider.id === selectedPromptProviderId) ||
    promptProviders.find((provider) => provider.id === "openrouter") ||
    promptProviders[0];
  const providerReady = selectedPromptProvider?.status === "available" && payload.provider_calls === "guarded-manual";
  const providerDefaultModel = selectedPromptProvider?.default_model || DEFAULT_PROVIDER_SMOKE_MODEL;
  const providerModelSuggestions = Array.from(
    new Set([providerDefaultModel, ...(selectedPromptProvider?.model_examples || [])].filter(Boolean))
  );
  const providerModelListId = selectedPromptProvider
    ? `provider-smoke-models-${selectedPromptProvider.id}`
    : "provider-smoke-models";
  const selectedProviderAction =
    selectedPromptProvider?.operator_action ||
    `Set SPARKBOT_PROVIDER_CALLS_ENABLED=true and ${selectedPromptProvider?.credential_source || "the provider environment"} in the backend environment.`;

  useEffect(() => {
    setProviderModel(providerDefaultModel);
    setProviderResult(null);
    setProviderError(null);
  }, [providerDefaultModel, selectedPromptProvider?.id]);

  async function handleProviderSmoke(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedPromptProvider) {
      return;
    }
    setProviderError(null);
    setProviderResult(null);
    setProviderSubmitting(true);

    try {
      const result = await runProviderPrompt(selectedPromptProvider.id, providerPrompt, providerModel);
      setProviderResult(result);
    } catch (error: unknown) {
      setProviderError(error instanceof Error ? error.message : "Provider prompt request failed.");
    } finally {
      setProviderSubmitting(false);
    }
  }

  return (
    <section className="provider-setup-preview section-panel" id="provider-setup" aria-labelledby="provider-setup-heading">
      <div className="provider-setup-copy">
        <p className="eyebrow">{formatShellStatus(payload.status)}</p>
        <h2 id="provider-setup-heading">Provider Setup</h2>
        <p>{providerPreviewSummary}</p>
        <p className="capabilities-source">{providerStatusState.sourceLabel}</p>
      </div>

      <dl className="provider-status-grid" aria-label="Provider configuration implementation status">
        <div>
          <dt>Credential storage</dt>
          <dd>{formatImplementationStatus(payload.credential_storage)}</dd>
        </div>
        <div>
          <dt>Provider calls</dt>
          <dd>{formatImplementationStatus(payload.provider_calls)}</dd>
        </div>
        <div>
          <dt>Model routing</dt>
          <dd>{formatImplementationStatus(payload.model_routing)}</dd>
        </div>
      </dl>

      <form className="provider-smoke-panel" aria-label="Provider prompt smoke test" onSubmit={handleProviderSmoke}>
        <div className="provider-card-top">
          <h3>Provider Prompt Smoke</h3>
          <span className={`status-badge status-${providerReady ? "available" : "disabled-by-default"}`}>
            {providerReady ? "Available" : "Disabled by default"}
          </span>
        </div>
        <div className="provider-smoke-fields">
          <label>
            <span>Smoke provider</span>
            <select
              value={selectedPromptProvider?.id || ""}
              onChange={(event) => setSelectedPromptProviderId(event.target.value)}
            >
              {promptProviders.map((provider) => (
                <option value={provider.id} key={provider.id}>
                  {formatProviderLabel(provider.label, provider.provider_aliases)}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>Smoke model</span>
            <input
              value={providerModel}
              onChange={(event) => setProviderModel(event.target.value)}
              placeholder={providerDefaultModel}
              list={providerModelSuggestions.length ? providerModelListId : undefined}
              autoComplete="off"
            />
            {providerModelSuggestions.length ? (
              <datalist id={providerModelListId}>
                {providerModelSuggestions.map((model) => (
                  <option value={model} key={model} />
                ))}
              </datalist>
            ) : null}
          </label>
          <label>
            <span>Smoke prompt</span>
            <textarea
              value={providerPrompt}
              onChange={(event) => setProviderPrompt(event.target.value)}
              rows={3}
            />
          </label>
        </div>
        <button
          type="submit"
          disabled={!selectedPromptProvider || !providerReady || providerSubmitting || !providerPrompt.trim() || !providerModel.trim()}
        >
          {providerSubmitting ? "Running..." : "Run provider smoke"}
        </button>
        {!providerReady && selectedPromptProvider ? (
          <p className="provider-action">Next: {selectedProviderAction}</p>
        ) : null}
        {providerError ? <p className="provider-error" role="alert">{providerError}</p> : null}
        {providerResult ? (
          <output className="provider-smoke-result" aria-live="polite">
            <strong>{selectedPromptProvider?.label}: {providerResult.model}</strong>
            <span>{providerResult.response}</span>
            {providerResult.audit_id ? <small>Audit: {providerResult.audit_id}</small> : null}
          </output>
        ) : null}
      </form>

      <div className="provider-layout" aria-label="Provider setup status">
        {payload.providers.map((provider) => (
          <article className="provider-card" key={provider.id}>
            <div className="provider-card-top">
              <h3>{provider.label}</h3>
              <span className={`status-badge status-${provider.status}`}>{formatShellStatus(provider.status)}</span>
            </div>
            <dl className="provider-card-meta" aria-label={`${provider.label} configuration`}>
              <div>
                <dt>State</dt>
                <dd>{formatBool(provider.configured)}</dd>
              </div>
              <div>
                <dt>Auth</dt>
                <dd>{formatImplementationStatus(provider.auth_mode)}</dd>
              </div>
              <div>
                <dt>Config</dt>
                <dd>{formatImplementationStatus(provider.configuration)}</dd>
              </div>
              <div>
                <dt>Source</dt>
                <dd>{provider.credential_source}</dd>
              </div>
              {provider.default_model ? (
                <div>
                  <dt>Default model</dt>
                  <dd>{provider.default_model}</dd>
                </div>
              ) : null}
              {typeof provider.cli_available === "boolean" ? (
                <div>
                  <dt>CLI</dt>
                  <dd>{provider.cli_available ? "available" : "missing"}</dd>
                </div>
              ) : null}
              {typeof provider.sign_in_detected === "boolean" ? (
                <div>
                  <dt>Sign-in</dt>
                  <dd>{provider.sign_in_detected ? "detected" : "needed"}</dd>
                </div>
              ) : null}
              {provider.runtime_gate ? (
                <div>
                  <dt>Runtime gate</dt>
                  <dd>{formatImplementationStatus(provider.runtime_gate)}</dd>
                </div>
              ) : null}
              {provider.provider_aliases?.length ? (
                <div>
                  <dt>Aliases</dt>
                  <dd>{provider.provider_aliases.join(", ")}</dd>
                </div>
              ) : null}
              {typeof provider.adapter_configured === "boolean" ? (
                <div>
                  <dt>Adapter</dt>
                  <dd>{formatBool(provider.adapter_configured)}</dd>
                </div>
              ) : null}
            </dl>
            <p>{provider.runtime}</p>
            <p>{provider.notes}</p>
            {provider.operator_action ? <p className="provider-action">Next: {provider.operator_action}</p> : null}
            {provider.model_examples.length ? (
              <p className="provider-model-list">Models: {provider.model_examples.join(", ")}</p>
            ) : null}
          </article>
        ))}
      </div>

      <p className="provider-note">
        This setup surface includes no API key fields, no password or token fields, no save actions, and no hidden
        provider health checks. Provider prompt calls require explicit backend env enablement and an operator-submitted prompt.
      </p>
    </section>
  );
}
