import { providerPreviewItems, providerPreviewSummary } from "../providers/providerSetupStatus";
import { formatShellStatus } from "./ShellNavigation";

export default function ProviderSetupPreview() {
  return (
    <section className="provider-setup-preview section-panel" id="provider-setup" aria-labelledby="provider-setup-heading">
      <div className="provider-setup-copy">
        <p className="eyebrow">Planned</p>
        <h2 id="provider-setup-heading">Provider Setup Preview</h2>
        <p>{providerPreviewSummary}</p>
      </div>

      <div className="provider-layout" aria-label="Read-only provider setup preview">
        {providerPreviewItems.map((provider) => (
          <article className="provider-card" key={provider.name}>
            <div className="provider-card-top">
              <h3>{provider.name}</h3>
              <span className={`status-badge status-${provider.status}`}>{formatShellStatus(provider.status)}</span>
            </div>
            <p>{provider.summary}</p>
          </article>
        ))}
      </div>

      <p className="provider-note">
        This preview includes no API key fields, no save actions, and no test-connection actions.
      </p>
    </section>
  );
}
