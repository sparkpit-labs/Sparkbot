export type ProviderPreviewStatus = "skeleton" | "planned";

export type ProviderPreviewItem = {
  name: string;
  status: ProviderPreviewStatus;
  summary: string;
};

export const providerPreviewItems: ProviderPreviewItem[] = [
  {
    name: "Local model provider",
    status: "skeleton",
    summary: "Planned local model configuration surface. Runtime configuration is not active in this branch."
  },
  {
    name: "OpenAI-compatible provider",
    status: "planned",
    summary: "Planned compatibility surface for OpenAI-style APIs. No credential or network behavior is active."
  },
  {
    name: "Anthropic-compatible provider",
    status: "planned",
    summary: "Planned compatibility surface for Anthropic-style APIs. No credential or network behavior is active."
  },
  {
    name: "Google-compatible provider",
    status: "planned",
    summary: "Planned compatibility surface for Google-style APIs. No credential or network behavior is active."
  },
  {
    name: "Custom endpoint",
    status: "planned",
    summary: "Planned custom endpoint profile. No endpoint input, save, or connection testing is active."
  }
];

export const providerPreviewSummary =
  "Provider configuration is planned for later slices. This preview is read-only and does not accept, store, or transmit credentials.";
