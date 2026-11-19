# Sparkbot Roundtable

Sparkbot Roundtable is a free, open-source desktop workspace where you and your AI agents collaborate in shared conversation rooms. Create a room, connect your agents, and direct the discussion with mentions. Each participant's replies remain in the room's conversation history.

Built and maintained by SparkPit Labs. Licensed under the [MIT License](LICENSE).

**[Download Sparkbot Roundtable](https://sparkpit-labs.github.io/Sparkbot/)** | [Release notes](https://github.com/sparkpit-labs/Sparkbot/releases/tag/v0.0.01) | [Report an issue](https://github.com/sparkpit-labs/Sparkbot/issues)

## Download

The current desktop release is **v0.0.01**, an early public pre-release. The download page provides installation instructions and packages for these platforms:

| Platform | Package |
| --- | --- |
| Windows 10 or 11, 64-bit | Per-user `.exe` installer |
| macOS 11 or later, Apple silicon | ARM64 `.dmg` |
| macOS 11 or later, Intel | x64 `.dmg` |
| Linux, x86-64 | `.AppImage` or `.deb` for Debian/Ubuntu |

The public release label is `v0.0.01`; the app's package version is `0.0.1`. Earlier Windows pilot builds used `0.2.x` numbering.

Packages are unsigned; macOS packages are ad-hoc signed and are not notarized. Operating-system trust warnings may appear. Use the official downloads and compare the file's SHA-256 hash with [SHA256SUMS.txt](https://github.com/sparkpit-labs/Sparkbot/releases/download/v0.0.01/SHA256SUMS.txt). A matching checksum confirms the file matches the published artifact; it is not a security certification. [BUILD-NOTES.txt](https://github.com/sparkpit-labs/Sparkbot/releases/download/v0.0.01/BUILD-NOTES.txt) identifies the build's source commit.

Windows packaging has undergone a hands-on pilot. The macOS and Linux packages have automated build checks, but have not yet completed equivalent hands-on installation testing. There is no automatic updater; install updates manually from the download page. Close the app and its agent runners before updating.

## What you can do

- Create local rooms and keep a persistent conversation history.
- Add named AI-agent seats through the Invite Wing.
- Ask one agent with `@name`, or address all connected agents with `@all`.
- See agent presence and job activity alongside the discussion.
- Pause work, resume it, or remove an agent's seat.
- Connect an interactive MCP-compatible agent session to read and post in a room.

Automatic replies use a separate agent runner that you start on your computer. An installed agent or a created seat alone does not start that runner. Agent messages do not automatically trigger other agents.

## Get started

1. **Install and open the app.** Choose the package for your operating system from the [download page](https://sparkpit-labs.github.io/Sparkbot/). The desktop package includes its local backend and connector; a separate Python installation is not required to use the packaged app.
2. **Prepare your agent.** Install and sign in to a [supported agent CLI](https://github.com/sparkpit-labs/Sparkbot/blob/v0.0.01/docs/ROUND_TABLE_SHELL.md) on the same computer. Agent software, accounts, subscriptions, usage limits, and charges are provided separately by the agent's provider.
3. **Create a room.** Open Round Table and choose **New room**. You can write messages without selecting a model or connecting an agent.
4. **Add an agent.** In the room's **Invite Wing**, choose the agent type, enter a name, and select **Add agent**. Keep the one-time seat key private.
5. **Connect the seat.** Follow the two commands shown by the app: first save the seat using the key, then start its runner. Use the commands generated for your installed app and operating system. Keep the runner's terminal open; `Ctrl+C` stops it.
6. **Start the discussion.** Send a message using the seat's displayed `@name`. Use `@all` to ask all connected agents. Replies appear in the room.

For MCP setup, runner behavior, and API details, see the [Roundtable guide for this release](https://github.com/sparkpit-labs/Sparkbot/blob/v0.0.01/docs/ROUND_TABLE_SHELL.md). Its Python examples are for source installations; desktop users should use the bundled-connector commands shown in the app.

## Privacy and access

The desktop app listens on the loopback interface (`127.0.0.1`), and room data is stored locally. It does not require a Sparkbot account or provider API keys to create rooms.

**Local storage does not mean every conversation stays offline.** When you ask a connected agent to reply, its runner provides room context to the agent's CLI. That CLI may send the context to its provider using your existing sign-in. The provider's terms, privacy policy, and usage limits apply.

Seat keys grant access to a specific room. The backend stores key hashes; the local connector saves the key in its user profile so it can reconnect. Treat that profile as sensitive. Do not include seat keys, authentication files, or private conversations in issue reports. Removing a seat revokes its access.

The built-in automatic runners are configured for text responses with agent tools disabled. This is not a general-purpose tool-execution environment. Interactive MCP sessions use the configuration of their host agent; do not assume they inherit the automatic runner's restrictions.

## Current limits

- Rooms are local to one computer. People joining from other devices are not supported in this release.
- Automatic agent replies require the app and the corresponding foreground runner to remain open.
- Automatic runners return text; they do not edit files or execute tasks discussed in a room.
- A cloud-backed agent needs network access and an eligible provider account. Sparkbot does not include model access or subscription credits.
- Other Sparkbot surfaces may be previews or development features. Their presence in the interface does not establish production readiness.

## Troubleshooting and feedback

**An agent is not replying:** check that its CLI is installed and signed in, its runner is open, the room is not paused, and the message uses the correct `@name`. Review the runner's console and the room's activity status for a failure or usage limit.

**An update cannot replace a file:** close Sparkbot and the agent runners, then retry the installer.

**Something else fails:** [open an issue](https://github.com/sparkpit-labs/Sparkbot/issues) with your operating system, package version, steps to reproduce, and the relevant error text. Remove keys and private content before attaching logs or screenshots. Follow [SECURITY.md](SECURITY.md) for security reports; do not post sensitive exploit details publicly.

## Source code and development

The downloadable app is built from the **[v0.0.01 release tag](https://github.com/sparkpit-labs/Sparkbot/tree/v0.0.01)**. The repository's `main` branch currently follows a separate public development baseline and does not match that desktop release. Use the tag when inspecting, reproducing, or modifying the downloaded app:

```bash
git clone --branch v0.0.01 https://github.com/sparkpit-labs/Sparkbot.git
cd Sparkbot
```

This checks out the release in detached-HEAD mode. Create a branch before making changes. Building from source requires development tools; downloading a desktop package does not. Refer to the documentation at the same tag as your checkout:

- [Development setup](https://github.com/sparkpit-labs/Sparkbot/blob/v0.0.01/docs/DEVELOPMENT.md)
- [Roundtable and agent integration](https://github.com/sparkpit-labs/Sparkbot/blob/v0.0.01/docs/ROUND_TABLE_SHELL.md)
- [Desktop release workflow](https://github.com/sparkpit-labs/Sparkbot/blob/v0.0.01/docs/RELEASING.md)

For work on `main`, start with the [documentation index](docs/README.md), [development guide](docs/DEVELOPMENT.md), and [validation guide](docs/VALIDATION.md). These documents describe that branch and may differ from the downloadable release.

## Contributing

Bug reports, documentation improvements, and focused contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md), identify the branch or release your change targets, and distinguish implemented behavior from planned work.

Run the relevant checks for your checkout before submitting a pull request:

```bash
bash scripts/check-public-safety.sh
bash scripts/validate-public-shell.sh
```

The validation script runs backend and frontend checks without starting long-running services. Keep changes scoped and exclude credentials, generated installers, local profiles, and private data.

## License and project

Sparkbot is released under the [MIT License](LICENSE). Third-party agent software and services remain subject to their own licenses and terms.

Maintained by **SparkPit Labs**. Visit [sparkpitlabs.com](https://sparkpitlabs.com) for project information.
