export async function desktopConnectorCommand(): Promise<string | undefined> {
  if (import.meta.env.VITE_SPARKBOT_DESKTOP !== "true") return undefined;
  const { invoke } = await import("@tauri-apps/api/core");
  return invoke<string>("desktop_connector_command");
}
