import type { ProviderConfigStatusPayload, ProviderStatusItem } from "../api";

export type ProviderPreviewItem = ProviderStatusItem;

export const providerPreviewItems: ProviderPreviewItem[] = [
  {
    id: "local",
    label: "Local provider",
    status: "planned",
    notes: "Local provider configuration is planned. No runtime provider calls are made."
  },
  {
    id: "openai-compatible",
    label: "OpenAI-compatible provider",
    status: "guarded-future",
    notes: "Cloud provider configuration will require explicit setup and safety gates."
  },
  {
    id: "anthropic-compatible",
    label: "Anthropic-compatible provider",
    status: "guarded-future",
    notes: "Cloud provider configuration will require explicit setup and safety gates."
  },
  {
    id: "google-compatible",
    label: "Google-compatible provider",
    status: "guarded-future",
    notes: "Cloud provider configuration will require explicit setup and safety gates."
  },
  {
    id: "custom-endpoint",
    label: "Custom endpoint",
    status: "guarded-future",
    notes: "Custom endpoints are planned for future guarded configuration."
  }
];

export const fallbackProviderConfigStatus: ProviderConfigStatusPayload = {
  service: "sparkbot-server",
  mode: "local",
  status: "preview",
  credential_storage: "not-implemented",
  provider_calls: "not-implemented",
  model_routing: "not-implemented",
  providers: providerPreviewItems
};

export const providerPreviewSummary =
  "Provider configuration status is read-only. Credentials are not handled, provider calls are not made, and model routing is not implemented.";
