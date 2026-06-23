import { useEffect, useState } from "react";

import { fetchGuardianStatus, type GuardianStatusPayload } from "../api";
import { fallbackGuardianStatus, guardianControlItems, guardianControlsSummary } from "../guardian/guardianControlsStatus";
import { formatShellStatus } from "./ShellNavigation";

type GuardianStatusState = {
  payload: GuardianStatusPayload;
  sourceLabel: string;
};

const fallbackGuardianStatusState: GuardianStatusState = {
  payload: fallbackGuardianStatus,
  sourceLabel: "Using local Guardian status fallback."
};

function formatImplementationStatus(status: string) {
  return status.replace(/-/g, " ");
}

export default function GuardianControlsPreview() {
  const [guardianStatusState, setGuardianStatusState] = useState<GuardianStatusState>(fallbackGuardianStatusState);

  useEffect(() => {
    const controller = new AbortController();

    fetchGuardianStatus(controller.signal)
      .then((payload) => {
        setGuardianStatusState({
          payload,
          sourceLabel: "Using backend Guardian status."
        });
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }
        setGuardianStatusState(fallbackGuardianStatusState);
      });

    return () => controller.abort();
  }, []);

  const { payload } = guardianStatusState;

  return (
    <section
      className="guardian-controls-preview section-panel"
      id="guardian-controls"
      aria-labelledby="guardian-controls-heading"
    >
      <div className="guardian-controls-copy">
        <p className="eyebrow">{formatShellStatus(payload.status)}</p>
        <h2 id="guardian-controls-heading">Guardian Controls Preview</h2>
        <p>{guardianControlsSummary}</p>
        <p className="capabilities-source">{guardianStatusState.sourceLabel}</p>
      </div>

      <dl className="guardian-status-grid" aria-label="Guardian policy implementation status">
        <div>
          <dt>Runtime enforcement</dt>
          <dd>{formatImplementationStatus(payload.runtime_enforcement)}</dd>
        </div>
        <div>
          <dt>Approval tokens</dt>
          <dd>{formatImplementationStatus(payload.approval_tokens)}</dd>
        </div>
        <div>
          <dt>Policy decisions</dt>
          <dd>{formatImplementationStatus(payload.policy_decisions)}</dd>
        </div>
        <div>
          <dt>Audit trail</dt>
          <dd>{formatImplementationStatus(payload.audit_trail)}</dd>
        </div>
        <div>
          <dt>Default posture</dt>
          <dd>{formatImplementationStatus(payload.default_posture)}</dd>
        </div>
      </dl>

      <div className="guardian-layout" aria-label="Read-only Guardian controls preview">
        {guardianControlItems.map((control) => (
          <article className="guardian-card" key={control.name}>
            <div className="guardian-card-top">
              <h3>{control.name}</h3>
              <span className={`status-badge status-${control.status}`}>{formatShellStatus(control.status)}</span>
            </div>
            <p>{control.summary}</p>
          </article>
        ))}
      </div>

      <article className="guardian-boundary-card" aria-label="Provider execution boundary">
        <div className="guardian-card-top">
          <h3>{payload.provider_execution_boundary.label}</h3>
          <span className={`status-badge status-${payload.provider_execution_boundary.status}`}>
            {formatShellStatus(payload.provider_execution_boundary.status)}
          </span>
        </div>
        <dl className="guardian-boundary-grid">
          <div>
            <dt>Runtime gate</dt>
            <dd>{formatImplementationStatus(payload.provider_execution_boundary.runtime_gate)}</dd>
          </div>
          <div>
            <dt>Dispatch</dt>
            <dd>{formatImplementationStatus(payload.provider_execution_boundary.dispatch)}</dd>
          </div>
          <div>
            <dt>Required controls</dt>
            <dd>{payload.provider_execution_boundary.required_controls.join(", ")}</dd>
          </div>
          <div>
            <dt>Blocked until</dt>
            <dd>{payload.provider_execution_boundary.blocked_until}</dd>
          </div>
        </dl>
        <p>{payload.provider_execution_boundary.notes}</p>
      </article>


      <article className="guardian-boundary-card" aria-label="Provider adapter contract">
        <div className="guardian-card-top">
          <h3>{payload.provider_adapter_contract.label}</h3>
          <span className={`status-badge status-${payload.provider_adapter_contract.status}`}>
            {formatShellStatus(payload.provider_adapter_contract.status)}
          </span>
        </div>
        <dl className="guardian-boundary-grid">
          <div>
            <dt>Contract version</dt>
            <dd>{payload.provider_adapter_contract.contract_version}</dd>
          </div>
          <div>
            <dt>Dispatch</dt>
            <dd>{formatImplementationStatus(payload.provider_adapter_contract.dispatch)}</dd>
          </div>
          <div>
            <dt>Provider IDs</dt>
            <dd>{payload.provider_adapter_contract.provider_ids.join(", ")}</dd>
          </div>
          <div>
            <dt>Required request fields</dt>
            <dd>{payload.provider_adapter_contract.required_request_fields.join(", ")}</dd>
          </div>
          <div>
            <dt>Response statuses</dt>
            <dd>{payload.provider_adapter_contract.allowed_response_statuses.join(", ")}</dd>
          </div>
          <div>
            <dt>Audit</dt>
            <dd>{formatImplementationStatus(payload.provider_adapter_contract.audit)}</dd>
          </div>
        </dl>
        <p>{payload.provider_adapter_contract.notes}</p>
      </article>

      <div className="guardian-sensitive-layout" aria-label="Read-only sensitive action category status">
        {payload.sensitive_action_categories.map((category) => (
          <article className="guardian-card" key={category.id}>
            <div className="guardian-card-top">
              <h3>{category.label}</h3>
              <span className={`status-badge status-${category.status}`}>{formatShellStatus(category.status)}</span>
            </div>
            <p>{category.notes}</p>
          </article>
        ))}
      </div>

      <p className="guardian-note">
        This preview includes no approval buttons, no execution controls, no save actions, no policy decisions, and no
        runtime enforcement.
      </p>
    </section>
  );
}
