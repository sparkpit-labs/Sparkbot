import { describe, expect, it } from "vitest";
import { agentCommands } from "./roundtable/roundtableApi";

describe("desktop connector instructions", () => {
  it("uses the installed executable and desktop port, persisting the URL at login", () => {
    const command = "& 'C:\\Apps\\Sparkbot Roundtable\\sparkbot-roundtable.exe'";
    expect(agentCommands("helper", "claude", command)).toEqual([
      `${command} login --profile helper --url http://127.0.0.1:18765`,
      `${command} run --profile helper --agent claude`
    ]);
    expect(agentCommands("helper", "other", command)[1]).toBe(`${command} mcp --profile helper`);
  });
  it("keeps source checkout instructions available", () => {
    expect(agentCommands("helper", "codex")[0]).toBe("python tools/sparkbot-roundtable.py login --profile helper");
  });
});
