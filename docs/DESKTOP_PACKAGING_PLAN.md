# Windows desktop package

The public Roundtable now has a Tauri v2 Windows shell and an unsigned NSIS build workflow. The app and its two bundled Python executables are built exclusively from this repository. The package version is 0.2.0 and the application identity is `com.sparkpitlabs.sparkbot.public`.

## Runtime and safety

- The desktop starts its own backend on 127.0.0.1:18765 and waits for that process to report readiness. An occupied port fails startup; it never adopts or stops an unrelated backend.
- The backend accepts the exact desktop webview origins. Existing local host and owner-header checks remain active. No listener binds to the network interface.
- Closing the desktop closes the backend stdin pipe, requesting shutdown. The desktop waits up to five seconds before terminating its child. A desktop crash also closes the pipe.
- Room data retains the public runtime's user-data location. The installer does not migrate or delete data from other builds. Uninstall retains user data and connector profiles.
- The packaged connector is a separate foreground executable. The Add agent panel provides PowerShell commands using its installed path and the desktop URL. Python is bundled; agent CLIs and their login remain user prerequisites. No runner starts automatically.
- The frontend has no general shell permission. Its single desktop command returns the bundled connector path.
- No signing or automatic updater is configured. Updates are manually installed. Guests on other devices are not supported.

## Build

`.github/workflows/windows-installer.yml` builds on Windows. It runs the public safety scan, backend/frontend tests, freezes the backend and connector with PyInstaller, exercises the frozen backend, builds the desktop frontend and Tauri/NSIS installer, and uploads the installer with SHA256SUMS.txt and BUILD-NOTES.txt. It publishes an Actions artifact, not a GitHub Release.

For a local build, follow the workflow commands on Windows with Node 22, Python 3.12, Rust and Microsoft C++ build tools. Build frontend assets with `VITE_SPARKBOT_API_BASE_URL=http://127.0.0.1:18765` and `VITE_SPARKBOT_DESKTOP=true`. Cargo.lock and the npm lockfile are committed. Python build dependencies currently use bounded project requirements rather than a full transitive lock.

## Validation and remaining acceptance

The automated smoke test creates a disposable room, checks owner-header enforcement and desktop CORS, checks occupied-port rejection, restarts to verify data persistence, and verifies process exit. It makes no model calls.

A successful build is not installer acceptance. On a spare PC or Windows Sandbox, test install, first launch, room creation, an installed connector login and reply, close/reopen, reinstall/upgrade, and uninstall. Verify no backend process remains and saved data remains as documented. Check SmartScreen behavior for this unsigned pilot.

Signed: Atlas | 2026-11-09
