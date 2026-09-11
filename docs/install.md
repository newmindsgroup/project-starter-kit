# Install or use a checkout

Version-Timestamp: 2026-09-10 18:27:14 AST

## Option A: repository link, no plugin

In a Codex project task or Claude Code session opened in your project, paste the repository URL and ask it to follow START-HERE.md. The agent can obtain a tooling checkout and use its skills directly. A plugin is optional; local file/command access and runtime prerequisites are not.

For a manual checkout, choose a tooling folder outside the application:

```sh
git clone https://github.com/newmindsgroup/project-starter-kit.git
```

The checkout contains a release manifest. Follow [releases.md](releases.md) to verify it, then follow [commands.md](commands.md). Cloning does not install Python, authenticate to your client sources or initialize your application.

## Option B: native plugin installation

The public marketplace is named **project-starter-kit**. The plugin is named **ide-project-starter**. A private development marketplace may have another name; do not replace an existing registration merely because the plugin name matches.

These commands were checked against the local Codex and Claude CLI help during release preparation. If your version does not support them, update through its official installer or use Option A. Do not paste a CLI command into an unrelated app console.

### Codex CLI

```sh
codex plugin marketplace add newmindsgroup/project-starter-kit
codex plugin add ide-project-starter@project-starter-kit
```

Create or select your Codex project, then open a fresh task. Select the plugin's project-starter skill or ask it to set up the project using that skill.

### Claude Code CLI

```sh
claude plugin marketplace add newmindsgroup/project-starter-kit
claude plugin install ide-project-starter@project-starter-kit --scope user
```

Restart Claude Code. Inside a session, invoke:

```text
/ide-project-starter:project-starter
```

If similarly named skills are installed from private and public sources, identify the marketplace and version explicitly. Prefer one chosen release for the current setup; do not mix helpers from different installations.

### Alternative: a local marketplace

After cloning, supply the absolute checkout path instead of owner/repo to the marketplace-add command. This is useful when reviewing a pinned checkout or when remote fetching is unavailable. Use the same public marketplace name for installation.

Installation changes the chosen tool's settings/cache. It does not scan all your projects, install an observer or adopt existing projects automatically. Dependency setup still follows the command guide.

## Verify discovery

Start a fresh session and ask the agent to report the plugin version and the four available workflows. Then run a read-only inspection of a disposable project. Discovery alone is not proof of a completed adoption. Finish one small project milestone, checkpoint and recover in another session.

## Updates and removal

Use the tool's native marketplace refresh and plugin-update flow for the exact public marketplace. Review release notes first. Current Claude CLI exposes `claude plugin marketplace update project-starter-kit` and `claude plugin update ide-project-starter@project-starter-kit`; check `--help` for your installed version. For Codex, inspect the current marketplace and plugin update/add commands before changing its configuration.

Use native removal commands for the exact plugin and marketplace if you want to uninstall. Your projects' saved records and copied helpers remain in their own folders. Removing the plugin does not remove project memory.

Do not publish plugin caches, local authentication or complete user settings as part of a project backup.
