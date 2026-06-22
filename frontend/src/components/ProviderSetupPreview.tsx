import { FormEvent, useEffect, useState } from "react";

import { fetchProviderConfigStatus, runOpenRouterPrompt, type OpenRouterPromptResponse, type ProviderConfigStatusPayload } from "../api";
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

const DEFAULT_OPENROUTER_SMOKE_MODEL = "meta-llama/llama-3.2-3b-instruct:free";

function formatImplementationStatus(status: string) {
  return status.replace(/-/g, " ");
}

function formatBool(value: boolean) {
  return value ? "configured" : "not configured";
}

export default function ProviderSetupPreview() {
  const [providerStatusState, setProviderStatusState] = useState<ProviderStatusState>(fallbackProviderStatusState);
  const [openRouterPrompt, setOpenRouterPrompt] = useState("Say OK.");
  const [openRouterModel, setOpenRouterModel] = useState(DEFAULT_OPENROUTER_SMOKE_MODEL);
  const [openRouterResult, setOpenRouterResult] = useState<OpenRouterPromptResponse | null>(null);
  const [openRouterError, setOpenRouterError] = useState<string | null>(null);
  const [openRouterSubmitting, setOpenRouterSubmitting] = useState(false);

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
  const openRouterProvider = payload.providers.find((provider) => provider.id === "openrouter");
  const openRouterReady = openRouterProvider?.status === "available" && payload.provider_calls === "guarded-manual";
  const openRouterDefaultModel = openRouterProvider?.default_model || DEFAULT_OPENROUTER_SMOKE_MODEL;

  useEffect(() => {
    if (!openRouterModel.trim()) {
      setOpenRouterModel(openRouterDefaultModel);
    }
  }, [openRouterDefaultModel, openRouterModel]);

  async function handleOpenRouterSmoke(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setOpenRouterError(null);
    setOpenRouterResult(null);
    setOpenRouterSubmitting(true);

    try {
      const result = await runOpenRouterPrompt(openRouterPrompt, openRouterModel);
      setOpenRouterResult(result);
    } catch (error: unknown) {
      setOpenRouterError(error instanceof Error ? error.message : "OpenRouter prompt request failed.");
    } finally {
      setOpenRouterSubmitting(false);
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

      <form className="provider-smoke-panel" aria-label="OpenRouter free model smoke test" onSubmit={handleOpenRouterSmoke}>
        <div className="provider-card-top">
          <h3>OpenRouter Free Model Smoke</h3>
          <span className={`status-badge status-${openRouterReady ? "available" : "disabled-by-default"}`}>
            {openRouterReady ? "Available" : "Disabled by default"}
          </span>
        </div>
        <div className="provider-smoke-fields">
          <label>
            <span>OpenRouter smoke model</span>
            <input
              value={openRouterModel}
              onChange={(event) => setOpenRouterModel(event.target.value)}
              placeholder={openRouterDefaultModel}
              autoComplete="off"
            />
          </label>
          <label>
            <span>OpenRouter smoke prompt</span>
            <textarea
              value={openRouterPrompt}
              onChange={(event) => setOpenRouterPrompt(event.target.value)}
              rows={3}
            />
          </label>
        </div>
        <button
          type="submit"
          disabled={!openRouterReady || openRouterSubmitting || !openRouterPrompt.trim() || !openRouterModel.trim()}
        >
          {openRouterSubmitting ? "Running..." : "Run OpenRouter smoke"}
        </button>
        {!openRouterReady ? (
          <p className="provider-action">Next: set SPARKBOT_PROVIDER_CALLS_ENABLED=true and OPENROUTER_API_KEY in the backend environment.</p>
        ) : null}
        {openRouterError ? <p className="provider-error" role="alert">{openRouterError}</p> : null}
        {openRouterResult ? (
          <output className="provider-smoke-result" aria-live="polite">
            <strong>{openRouterResult.model}</strong>
            <span>{openRouterResult.response}</span>
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
        provider health checks. OpenRouter calls require explicit backend env enablement and an operator-submitted prompt.
      </p>
    </section>
  );
}
