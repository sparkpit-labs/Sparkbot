import { localJsonRequest } from "./localRequests";

export type LocalDataExportPayload = {
  service: string;
  mode: "local";
  export_type: "local-workstation-data";
  schema_version: number;
  exported_at: string;
  import_supported: false;
  cloud_sync: "not-supported";
  external_upload: "not-supported";
  data: {
    chat_sessions: unknown[];
    memory_notes: unknown[];
    work_lane_cards: unknown[];
  };
};

export async function fetchLocalDataExport(): Promise<LocalDataExportPayload> {
  return localJsonRequest<LocalDataExportPayload>("/local/export");
}

export function buildLocalExportFilename(exportedAt: string): string {
  const safeTimestamp = exportedAt.replace(/[^0-9A-Za-z-]/g, "-");
  return `sparkbot-local-export-${safeTimestamp}.json`;
}
