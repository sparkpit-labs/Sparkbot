import { localJsonRequest } from "./localRequests";

export type LocalRuntimeSettingsPayload = {
  service: "sparkbot-server";
  mode: "local";
  status: "available";
  configuration: "env-driven";
  settings_writes: "not-supported";
  credentials: "not-supported";
  data_directory: {
    configured_by: "SPARKBOT_DATA_DIR" | "default-user-data-dir";
    display_path: string;
  };
  sqlite_database: {
    filename: string;
    display_path: string;
  };
  local_models: {
    enabled: boolean;
    status: string;
    adapter: "ollama";
    base_url: string | null;
    base_url_policy: "localhost-only";
    configured_model: string | null;
    prompt_calls: string;
    credentials: "not-supported";
    configuration_error?: string | null;
  };
};

export async function fetchLocalRuntimeSettings(): Promise<LocalRuntimeSettingsPayload> {
  return localJsonRequest<LocalRuntimeSettingsPayload>("/local/runtime/settings");
}
