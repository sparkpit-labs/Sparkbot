import { guardianControlItems, guardianControlsSummary } from "../guardian/guardianControlsStatus";

function formatStatus(status: "skeleton" | "planned") {
  return status === "skeleton" ? "Skeleton" : "Planned";
}

export default function GuardianControlsPreview() {
  return (
    <section className="guardian-controls-preview" aria-labelledby="guardian-controls-heading">
      <div className="guardian-controls-copy">
        <p className="eyebrow">Planned surface</p>
        <h2 id="guardian-controls-heading">Guardian Controls Preview</h2>
        <p>{guardianControlsSummary}</p>
      </div>

      <div className="guardian-layout" aria-label="Read-only Guardian controls preview">
        {guardianControlItems.map((control) => (
          <article className="guardian-card" key={control.name}>
            <div className="guardian-card-top">
              <h3>{control.name}</h3>
              <span className={`status-badge status-${control.status}`}>{formatStatus(control.status)}</span>
            </div>
            <p>{control.summary}</p>
          </article>
        ))}
      </div>

      <p className="guardian-note">
        This preview includes no approval buttons, no execution controls, no save actions, and no policy enforcement.
      </p>
    </section>
  );
}
