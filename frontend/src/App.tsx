import { useEffect, useState } from "react";

import { API_BASE_URL, fetchBackendHealth, type HealthPayload } from "./api";
import CommandCenter from "./components/CommandCenter";

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

function normalizeCommandPath(pathname: string): string {
  if (pathname === "/controls" || pathname === "/command-center") return "/spine";
  if (pathname === "/" || pathname === "") return "/spine";
  return pathname;
}

export default function App() {
  const [healthState, setHealthState] = useState<HealthState>(initialHealthState);
  const [path, setPath] = useState(() => normalizeCommandPath(window.location.pathname));

  useEffect(() => {
    const normalized = normalizeCommandPath(window.location.pathname);
    if (normalized !== window.location.pathname) {
      window.history.replaceState({}, "", normalized);
      setPath(normalized);
    }

    const onPopState = () => setPath(normalizeCommandPath(window.location.pathname));
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  const navigate = (nextPath: string) => {
    window.history.pushState({}, "", nextPath);
    setPath(nextPath);
  };

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
      <header className="shell-header app-topbar">
        <div>
          <h1>Sparkbot</h1>
          <p className="intro">Local-first AI Workstation with a restored Command Center.</p>
        </div>
        <nav className="top-nav" aria-label="Primary navigation">
          <button type="button" aria-current={path === "/spine" ? "page" : undefined} onClick={() => navigate("/spine")}>
            Command Center
          </button>
          <button type="button" aria-current={path === "/workstation" ? "page" : undefined} onClick={() => navigate("/workstation")}>
            Workstation
          </button>
        </nav>
      </header>

      {path === "/spine" || path === "/workstation" ? <CommandCenter /> : <CommandCenter />}

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
