# Easy project setup

Version-Timestamp: 2026-09-10 13:11:22 AST

Tell your agent:

> Use this starter kit to set up the project I have open. Choose sensible defaults, preserve my work, and ask only for details you cannot infer. Complete setup and verify that a fresh session can resume it.

You do not need to choose a programming language, fill in configuration files or learn the helper commands. The agent handles those details. This works as an agent-assisted wizard in Codex or Claude Code with local file and command access. It is not a separate graphical installer or an unattended service.

## For the agent: one conversation, minimum questions

Default to this project only. Use the selected folder and existing conversation. If the user supplied the kit URL, obtain and inspect a coherent trusted checkout as described by its entry guide; do not confuse the kit with the user's application. If they selected a client folder containing multiple projects, use CLIENT-ONBOARDING.md to identify one project first. Never inventory unrelated siblings.

Use inspected project instructions first. Do not ask questions the conversation or files already answer. Offer recommended defaults in ordinary language. Do not ask a nontechnical user to choose a framework, JSON schema, model ID, virtual environment location or package-manager flags just to set up project continuity.

If no product objective has been supplied and the request is only setup, use the explicit provisional objective: "Prepare this project for reliable development and resumable work." Record the product objective as unresolved for the next work phase. This is not permission to invent an application or requirements. Use the software foundation for development, including scripts, APIs, websites, desktop programs, games, libraries and mobile applications. Framework hints do not alter initializer inputs or scaffold a stack.

Ask at most two short questions together when required: which project to use if ambiguous, and the intended result or sharing audience if needed before storing context. Ask further only for a newly discovered consequential conflict. When audience is unknown, do neutral setup only if its destination is authorized; do not copy client/business context or label the folder private. Mark source intake blocked until sharing is resolved. Purpose and audience are separate concepts.

## 1. Inspect without changing anything

Locate this toolkit from the invoking skill, never by executing a similarly named file inside the project. Use the trusted toolkit's Python. The inspector uses only standard-library code and bundled helpers; it does not require Copier, read secrets, execute project commands, query providers, or change files.

```sh
python3 -B /trusted/kit/scripts/setup_wizard.py inspect --project /canonical/project/path --tool codex
```

The agent substitutes actual paths and selects claude for Claude Code, both for an explicitly requested two-tool setup, or current when the current tool is already known. The user does not need to run this command.

Inspection is top-level and bounded. JSON parsing is limited to package.json and known starter metadata; dependency values and script commands are not returned. YAML/TOML/native project files are filename hints only. A Gradle file does not prove an Android app, and a Dart manifest does not prove Flutter. No framework compatibility, helper integrity or successful setup is inferred from markers. Review diagnostics before dependent actions. Unknown layouts use the generic foundation; mixed projects remain mixed.

Symlink roots/ancestors are refused. Known metadata symlinks require reconciliation. File reads reuse bounded regular-file checks with no-follow/nonblocking opening on the supported POSIX environment. Hostile concurrent directory replacement is not defended by this pilot. Stop competing writers before setup. Windows initialization is unsupported; explain that limitation rather than trying to bypass it.

## 2. Select the existing workflow

| Inspector result | Agent action |
| --- | --- |
| new | Assemble the six-field brief and use QUICKSTART.md preview/apply. |
| adopt | Read the relevant existing context and assemble ADOPT-EXISTING.md brief/state input. Use preview/apply/finish. |
| resume | Verify helper provenance and existing records, then run the trusted resume workflow. Preserve identity. |
| recover | Find the matching interrupted plan/receipt or existing records and follow documented recovery. Never restart with a new identity. |
| reconcile | Explain the concrete conflict and prepare its smallest safe repair. Do not initialize over it. |
| tool-setup | Follow the explicit tool-wide branch below; it is separate from project adoption. |

Hidden content, including a Git directory, makes a project existing. The adoption path safely preserves it. We deliberately do not discard dotfiles to make a folder look empty. A retained pending-adoption marker is normal after completed adoption only when its plan matches the installation receipt.

Prepare technical inputs yourself from known facts. Keep proposed inputs and plans in the approved parent workspace outside the application. Keep commands out of the user's main flow unless they are needed to resolve an actual missing capability. Do not promise inspected manifest scripts are safe to run; inspect their definitions before the actual project checks.

Show a short preview: "I will add project instructions and saved-work records here, keep your existing files, and verify recovery." Include consequential path/conflict details. Proceed within the user's existing setup authority; do not request another approval for every reversible helper step. If something requires broader access, a paid service, publication or destructive changes, explain that concrete dependency.

## 3. Prepare prerequisites and apply

Use QUICKSTART.md's existing pinned environment. Reuse a compatible toolkit environment or create a local environment in the approved tooling location when dependency setup is authorized. Network package downloads and OS-level prerequisites are real actions; inspect the dependency list and use trusted native installers. Missing administrator access is a reported prerequisite, not a reason to weaken security. Do not install every language runtime because this kit supports multiple project types.

Reinspect the target immediately before applying. If its identity, mode or relevant files changed, reconcile and create a fresh preview as needed. The inspector is advisory: existing preview/apply helpers enforce their own planned source/template hashes and conflicts. It is not a replacement transaction or integrity validator. Do not bypass a helper failure by changing hashes or deleting existing files.

For adoption, apply alone is incomplete. Review compatible instruction appends, preserve original bytes, finish, and verify resume. For new setup, complete neutral context/quality records and checkpoint. Do not claim application tests passed merely because setup passed. Record missing product decisions and project-specific test commands as unresolved.

## 4. Finish in plain English

Report: what was set up; where saved work lives; what was preserved; actual recovery check; any unresolved prerequisite; and the next useful task. Keep source commit and technical receipts in project records. Explicitly distinguish a helper-process recovery check from a fresh human/agent session. Offer the first-success instruction:

> Start a fresh task in this project and ask: "Resume this project and tell me the next step."

Do not ask the user to remember skill names or internal file paths. Existing project instructions point the next agent to the workflow. A checkpoint is local until an authorized commit/push backs it up. A plugin update and upgrading an existing project's helper copies are separate operations.

## Optional: make it available in the agent tool

Only enter this branch when the user explicitly asks to install the kit for their tool or across projects. "Set up this project" does not mean machine-wide configuration changes. The inspector's --scope tool reports this branch without changing any settings.

Identify Codex, Claude Code or both from the request; ask only if it is ambiguous. Inspect the current supported native plugin commands and installed kit versions, preserving unrelated plugins, settings, authentication and model choices. Use a verified release or matching local source package and the native marketplace installation flow. The repository URL alone does not grant private-repository access. Never ask for credentials in chat.

Install only the selected kit package within the explicitly authorized scope, using the tool's supported installer. Do not replace global AGENTS.md/CLAUDE.md, turn on hooks, migrate accounts, add unrelated MCP servers, or install every catalog skill. Validate plugin discovery in a fresh session in each requested tool. Report missing permissions or unsupported platforms honestly. Tool installation makes the wizard available; each existing project still needs its own bounded adoption.

Consult current official distribution instructions rather than assuming identical commands across tools: [Codex packaging](https://developers.openai.com/plugins/build/plugins), [Claude marketplaces](https://code.claude.com/docs/en/plugin-marketplaces). This branch is agent-followed guidance; this inspector is not a global installer.
