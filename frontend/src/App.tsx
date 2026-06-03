import { useEffect, useState } from "react";

import { API_BASE_URL, fetchBackendHealth, type HealthPayload } from "./api";
import ChatWorkstation from "./components/ChatWorkstation";
import CommandCenter from "./components/CommandCenter";
import ControlsSurface from "./components/ControlsSurface";
import RoundTableRoom from "./components/RoundTableRoom";
import SpineSurface from "./components/SpineSurface";
import WorkstationFloor from "./components/WorkstationFloor";

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
  const allowedPaths = new Set(["/workstation", "/chat", "/roundtable", "/command-center", "/spine", "/controls"]);
  if (pathname === "/" || pathname === "") return "/workstation";
  return allowedPaths.has(pathname) ? pathname : "/workstation";
}

function surfaceForPath(path: string) {
  if (path === "/chat") return <ChatWorkstation />;
  if (path === "/roundtable") return <RoundTableRoom />;
  if (path === "/command-center") return <CommandCenter />;
  if (path === "/spine") return <SpineSurface />;
  if (path === "/controls") return <ControlsSurface />;
  return <WorkstationFloor />;
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
          <p className="intro">Local-first AI Workstation for operator chat, rooms, seats, Round Table sessions, shared memory, event history, and guarded setup.</p>
        </div>
        <nav className="top-nav" aria-label="Primary navigation">
          <button type="button" aria-current={path === "/workstation" ? "page" : undefined} onClick={() => navigate("/workstation")}>
            Workstation
          </button>
          <button type="button" aria-current={path === "/chat" ? "page" : undefined} onClick={() => navigate("/chat")}>
            Chat
          </button>
          <button type="button" aria-current={path === "/roundtable" ? "page" : undefined} onClick={() => navigate("/roundtable")}>
            Round Table
          </button>
          <button type="button" aria-current={path === "/command-center" ? "page" : undefined} onClick={() => navigate("/command-center")}>
            Command Center
          </button>
          <button type="button" aria-current={path === "/spine" ? "page" : undefined} onClick={() => navigate("/spine")}>
            Spine
          </button>
          <button type="button" aria-current={path === "/controls" ? "page" : undefined} onClick={() => navigate("/controls")}>
            Controls
          </button>
        </nav>
      </header>

      {surfaceForPath(path)}

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
