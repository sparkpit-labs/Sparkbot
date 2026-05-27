import { roundTablePreviewSummary, roundTableSeats } from "../roundtable/roundTableStatus";

function formatStatus(status: "preview" | "planned") {
  return status === "preview" ? "Preview" : "Planned";
}

export default function RoundTablePreview() {
  return (
    <section className="round-table-preview" aria-labelledby="round-table-heading">
      <div className="round-table-copy">
        <p className="eyebrow">Preview surface</p>
        <h2 id="round-table-heading">Round Table Preview</h2>
        <p>{roundTablePreviewSummary}</p>
      </div>

      <div className="round-table-layout" aria-label="Read-only Round Table seat preview">
        {roundTableSeats.map((seat) => (
          <article className="round-table-seat" key={seat.label}>
            <div className="round-table-seat-top">
              <h3>{seat.label}</h3>
              <span className={`status-badge status-${seat.status}`}>{formatStatus(seat.status)}</span>
            </div>
            <p className="round-table-role">{seat.role}</p>
            <p>{seat.description}</p>
          </article>
        ))}
      </div>

      <p className="round-table-note">
        The preview is read-only. It does not start meetings, call models, run a turn engine, invoke tools, or send
        messages.
      </p>
    </section>
  );
}
