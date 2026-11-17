# Sparkbot Roundtable v0.0.01

The first downloadable build of Sparkbot Roundtable for Windows, macOS and Linux.

Download page: https://sparkpit-labs.github.io/Sparkbot/

## What it is

A desktop app with a room on your own computer where you and your AI agents work together. You seat an agent (Claude Code, Codex, or any MCP agent), mention it with `@name` or everyone with `@all`, and the replies land in the room. The app runs its own local service on 127.0.0.1 and makes no model calls itself; each agent uses the CLI and sign-in you already have.

## Files

| System | File |
| --- | --- |
| Windows 10/11, 64-bit | `Sparkbot-Roundtable-v0.0.01-windows-x64-setup.exe` |
| macOS 11+, Apple silicon | `Sparkbot-Roundtable-v0.0.01-macos-arm64.dmg` |
| macOS 11+, Intel | `Sparkbot-Roundtable-v0.0.01-macos-x64.dmg` |
| Linux x86-64, AppImage | `Sparkbot-Roundtable-v0.0.01-linux-x64.AppImage` |
| Linux x86-64, Debian/Ubuntu | `Sparkbot-Roundtable-v0.0.01-linux-x64.deb` |

`SHA256SUMS.txt` lists the checksum of every file. `BUILD-NOTES.txt` names the source commit.

## Read this first

- **Unsigned.** No code-signing certificate is used. Windows SmartScreen and macOS Gatekeeper will warn on first launch; the download page shows the steps for each system. The macOS app is ad-hoc signed only and is not notarized.
- **Test coverage is uneven.** The Windows installer went through a hands-on pilot as 0.2.x pilot builds. The macOS and Linux packages are new here and have only had automated build and backend checks. Treat them as first tries.
- **No automatic updates.** Install a newer download over the old one.
- **One computer.** Guests on other devices are not supported.
- **Version numbers.** The public label is v0.0.01. Installers need a three-part number, so the app reports 0.0.1. This restarts numbering below the 0.2.x Windows pilot builds, which were never published.

## Changes since the Windows pilot (0.2.1)

- macOS (.dmg) and Linux (.AppImage, .deb) packages, built by `.github/workflows/release-desktop.yml`.
- The desktop shell finds its bundled backend and connector on every system, gives connector commands quoted for Terminal on macOS and Linux and for PowerShell on Windows, and shows a startup-failure message on macOS and Linux.
- Invite Wing: adding an agent and its one-time key now sit in a panel on the left of the room; the People list on the right keeps seats, Remove and Pause.
- A download page in `site/`, published with GitHub Pages.
