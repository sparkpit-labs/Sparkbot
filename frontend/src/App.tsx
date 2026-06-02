import { useState } from "react";

import { API_BASE_URL, fetchBackendHealth, type HealthPayload } from "./api";
import WorkstationShell from "./components/WorkstationShell";

type HealthState =
  | { phase: "idle"; message: string; payload: null }
  | { phase: "loading"; message: string; payload: null }
  | { phase: "online"; message: string; payload: HealthPayload }
  | { phase: "offline"; message: string; payload: null };

const initialHealthState: HealthState = {
  phase: "idle",
  message: "Backend health has not been checked yet.",
  payload: null
};

export default function App() {
  const [healthState, setHealthState] = useState<HealthState>(initialHealthState);

  const runHealthCheck = async () => {
    setHealthState({
      phase: "loading",
      message: "Checking backend health...",
      payload: null
    });

    try {
      const payload = await fetchBackendHealth();
      setHealthState({
        phase: "online",
        message: "Backend health check succeeded.",
        payload
      });
    } catch {
      setHealthState({
        phase: "offline",
        message: "Backend is offline or unreachable. Start the local backend and retry.",
        payload: null
      });
    }
  };

  return (
    <main className="app-shell">
      <header className="shell-header">
        <h1>Sparkbot</h1>
        <p className="intro">Sparkbot is an early local-first AI workstation from Spark Pit Labs.</p>
      </header>

      <WorkstationShell />

      <section className="health-panel">
        <div className="health-header">
          <h2>Backend Health</h2>
          <button type="button" onClick={runHealthCheck} disabled={healthState.phase === "loading"}>
            {healthState.phase === "loading" ? "Checking..." : "Check health"}
          </button>
        </div>

        <p className="health-base-url">API base URL: {API_BASE_URL}</p>
        <p className="health-message">{healthState.message}</p>

        {healthState.phase === "online" ? (
          <dl className="health-grid">
            <div>
              <dt>Status</dt>
              <dd>{healthState.payload.status}</dd>
            </div>
            <div>
              <dt>Service</dt>
              <dd>{healthState.payload.service}</dd>
            </div>
            <div>
              <dt>Mode</dt>
              <dd>{healthState.payload.mode}</dd>
            </div>
          </dl>
        ) : null}
      </section>
    </main>
  );
}
