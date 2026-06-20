import { useEffect, useState } from "react";

import { fetchModelSeatsStatus, type ModelSeatsStatusPayload } from "../api";
import { fallbackModelSeatsStatus, modelSeatPreviewSummary, modelSeatRoles } from "../modelSeats/modelSeatStatus";
import { formatShellStatus } from "./ShellNavigation";

type ModelSeatStatusState = {
  payload: ModelSeatsStatusPayload;
  sourceLabel: string;
};

const fallbackModelSeatsStatusState: ModelSeatStatusState = {
  payload: fallbackModelSeatsStatus,
  sourceLabel: "Using local Model Seat status fallback."
};

function formatImplementationStatus(status: string) {
  return status.replace(/-/g, " ");
}

export default function ModelSeatPreview() {
  const [modelSeatsStatusState, setModelSeatsStatusState] = useState<ModelSeatStatusState>(
    fallbackModelSeatsStatusState
  );

  useEffect(() => {
    const controller = new AbortController();

    fetchModelSeatsStatus(controller.signal)
      .then((payload) => {
        setModelSeatsStatusState({
          payload,
          sourceLabel: "Using backend Model Seat status."
        });
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }
        setModelSeatsStatusState(fallbackModelSeatsStatusState);
      });

    return () => controller.abort();
  }, []);

  const { payload } = modelSeatsStatusState;

  return (
    <section className="model-seat-preview section-panel" id="model-seats" aria-labelledby="model-seats-heading">
      <div className="model-seat-copy">
        <p className="eyebrow">{formatShellStatus(payload.status)}</p>
        <h2 id="model-seats-heading">Model Seat Preview</h2>
        <p>{modelSeatPreviewSummary}</p>
        <p className="capabilities-source">{modelSeatsStatusState.sourceLabel}</p>
      </div>

      <dl className="model-seat-status-grid" aria-label="Model Seat implementation status">
        <div>
          <dt>Model calls</dt>
          <dd>{formatImplementationStatus(payload.model_calls)}</dd>
        </div>
        <div>
          <dt>Model routing</dt>
          <dd>{formatImplementationStatus(payload.model_routing)}</dd>
        </div>
        <div>
          <dt>Provider credentials</dt>
          <dd>{formatImplementationStatus(payload.provider_credentials)}</dd>
        </div>
        <div>
          <dt>Seat persistence</dt>
          <dd>{formatImplementationStatus(payload.seat_persistence)}</dd>
        </div>
      </dl>

      <div className="model-seat-layout" aria-label="Read-only Model Seat preview">
        {payload.seats.map((seat) => (
          <article className="model-seat-card" key={seat.id}>
            <div className="model-seat-card-top">
              <h3>{seat.label}</h3>
              <span className={`status-badge status-${seat.status}`}>{formatShellStatus(seat.status)}</span>
            </div>
            <p className="model-seat-role">{modelSeatRoles.get(seat.id) ?? "Planned seat"}</p>
            <p>{seat.notes}</p>
          </article>
        ))}
      </div>

      <p className="model-seat-note">
        The preview is read-only. It does not assign models, route requests, collect credentials, persist seat choices,
        test providers, call models, execute agents, or save settings.
      </p>
    </section>
  );
}
