# Releasing the desktop app

`.github/workflows/release-desktop.yml` builds Sparkbot Roundtable for Windows (x64), macOS (Apple silicon and Intel) and Linux (x64), publishes the installers on a GitHub Release, and deploys the download page in `site/` to GitHub Pages at https://sparkpit-labs.github.io/Sparkbot/.

## One-time repository setup

1. **Settings, Pages, Build and deployment, Source: GitHub Actions.** Without this the `pages` job fails.
2. Settings, Actions, General: workflows need permission to run on this repository. No secrets are required; every build is unsigned.

## Cutting a release

1. Set the label and version in `site/release.json` (for example `v0.0.01` and `0.0.1`). Installers need a three-part version, so the two differ only in how the last number is written.
2. Put the same version in `src-tauri/tauri.conf.json`, `src-tauri/Cargo.toml` and the package entry in `src-tauri/Cargo.lock`. Update the links in `site/index.html` and add `docs/RELEASE_NOTES_<label>.md`.
3. Run `python scripts/release-info.py --check`. It fails if any copy disagrees.
4. Dry run: Actions, "Desktop release", Run workflow, leave "publish" unticked. Download the artifacts and try them.
5. Publish: push the tag (`git tag v0.0.01 && git push origin v0.0.01`), or run the workflow again with "publish" ticked. The Release is marked pre-release.

The workflow builds from the commit it runs on. Until the Round Table branches are merged to `main`, run it from the release branch or tag that branch.

## What each build does

Public safety scan, backend and frontend tests, PyInstaller freeze of the backend and connector, a smoke test of the frozen backend, the desktop frontend build, and a Tauri package: NSIS on Windows, .dmg on macOS, .deb and AppImage on Linux. Windows also runs the disposable install and uninstall check. Files are renamed to `Sparkbot-Roundtable-<label>-<system>` so the download page links never change shape.

## Known limits

- No code signing or notarization. macOS packages are ad-hoc signed so they can start on Apple silicon; users still approve the app in Privacy & Security.
- macOS and Linux have no installer-level acceptance test yet. A successful build is not proof that the app opens on a clean machine.
- An AppImage runs from a temporary mount, so the connector path shown in the app changes each time the app starts. Keep the app open while a connector runs, or use the .deb, which installs to a fixed path.
- No automatic updater.
