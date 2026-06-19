import { useEffect, useState } from "react";

import { fetchRoundTableStatus, type RoundTableStatusPayload } from "../api";
import { fallbackRoundTableStatus, roundTablePreviewSummary, roundTableSeatRoles } from "../roundtable/roundTableStatus";
import { formatShellStatus } from "./ShellNavigation";

type RoundTableStatusState = {
  payload: RoundTableStatusPayload;
  sourceLabel: string;
};

const fallbackRoundTableStatusState: RoundTableStatusState = {
  payload: fallbackRoundTableStatus,
  sourceLabel: "Using local Round Table status fallback."
};

function formatImplementationStatus(status: string) {
  return status.replace(/-/g, " ");
}

export default function RoundTablePreview() {
  const [roundTableStatusState, setRoundTableStatusState] = useState<RoundTableStatusState>(
    fallbackRoundTableStatusState
  );

  useEffect(() => {
    const controller = new AbortController();

    fetchRoundTableStatus(controller.signal)
      .then((payload) => {
        setRoundTableStatusState({
          payload,
          sourceLabel: "Using backend Round Table status."
        });
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }
        setRoundTableStatusState(fallbackRoundTableStatusState);
      });

    return () => controller.abort();
  }, []);

  const { payload } = roundTableStatusState;

  return (
    <section className="round-table-preview section-panel" id="round-table" aria-labelledby="round-table-heading">
      <div className="round-table-copy">
        <p className="eyebrow">{formatShellStatus(payload.status)}</p>
        <h2 id="round-table-heading">Round Table Preview</h2>
        <p>{roundTablePreviewSummary}</p>
        <p className="capabilities-source">{roundTableStatusState.sourceLabel}</p>
      </div>

      <dl className="round-table-status-grid" aria-label="Round Table implementation status">
        <div>
          <dt>Meeting engine</dt>
          <dd>{formatImplementationStatus(payload.meeting_engine)}</dd>
        </div>
        <div>
          <dt>Agent orchestration</dt>
          <dd>{formatImplementationStatus(payload.agent_orchestration)}</dd>
        </div>
        <div>
          <dt>Model calls</dt>
          <dd>{formatImplementationStatus(payload.model_calls)}</dd>
        </div>
        <div>
          <dt>Turn persistence</dt>
          <dd>{formatImplementationStatus(payload.turn_persistence)}</dd>
        </div>
      </dl>

      <div className="round-table-layout" aria-label="Read-only Round Table seat preview">
        {payload.seats.map((seat) => (
          <article className="round-table-seat" key={seat.id}>
            <div className="round-table-seat-top">
              <h3>{seat.label}</h3>
              <span className={`status-badge status-${seat.status}`}>{formatShellStatus(seat.status)}</span>
            </div>
            <p className="round-table-role">{roundTableSeatRoles.get(seat.id) ?? "Planned role"}</p>
            <p>{seat.notes}</p>
          </article>
        ))}
      </div>

      <p className="round-table-note">
        The preview is read-only. It does not start meetings, invite participants, call models, run a turn engine,
        orchestrate agents, invoke tools, persist sessions, assign work, or send messages.
      </p>
    </section>
  );
}
