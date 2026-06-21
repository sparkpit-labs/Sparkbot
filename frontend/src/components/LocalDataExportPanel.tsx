import { useState } from "react";

import { buildLocalExportFilename, fetchLocalDataExport } from "../localWorkstation/localDataExport";

function downloadJsonFile(filename: string, payload: unknown) {
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export default function LocalDataExportPanel() {
  const [statusMessage, setStatusMessage] = useState("Local data export has not been run yet.");

  const exportLocalData = async () => {
    try {
      const payload = await fetchLocalDataExport();
      downloadJsonFile(buildLocalExportFilename(payload.exported_at), payload);
      setStatusMessage("Exported local Workstation JSON from the local backend.");
    } catch {
      setStatusMessage("Could not export local Workstation data. Start the local backend and retry.");
    }
  };

  return (
    <section className="local-runtime-panel" id="local-data-export" aria-labelledby="local-data-export-heading">
      <div className="local-runtime-heading">
        <p className="eyebrow">Available locally</p>
        <h2 id="local-data-export-heading">Local Data Export</h2>
        <p>Download a read-only JSON backup of local chat sessions, memory notes, and work lane cards.</p>
        <p className="capabilities-source">{statusMessage}</p>
      </div>

      <div className="local-runtime-card">
        <h3>Export boundary</h3>
        <p>This export reads local SQLite data and downloads JSON in the browser.</p>
        <p>No import, cloud sync, external upload, credential export, or provider call is implemented.</p>
        <div className="local-action-row">
          <button type="button" onClick={exportLocalData}>Export JSON</button>
        </div>
      </div>
    </section>
  );
}
