# Local Data Export

Sparkbot includes a read-only local Workstation export for backup and testing.

## Endpoint

```text
GET /local/export
```

The endpoint returns JSON from the local SQLite Workstation store. It includes local chat sessions with messages, local memory notes, and local work lane cards. The payload also includes export metadata such as `export_type`, `schema_version`, `exported_at`, and explicit unsupported-operation flags.

## Frontend Download

The Workstation shell includes a Local Data Export panel with an `Export JSON` button. The button fetches `/local/export` and downloads the response in the browser as a timestamped JSON file.

The export does not upload data. It creates a browser `Blob` from the fetched JSON and uses a local object URL only for the download action.

## Safety Boundary

The export path is intentionally narrow:

- No import endpoint.
- No cloud sync.
- No external upload.
- No credential export.
- No provider call.
- No model call.
- No scheduler, background job, or automatic backup.

Use `SPARKBOT_DATA_DIR` with a temporary directory when testing export behavior so smoke data stays outside the repository.
