# Start your next project

Version-Timestamp: 2026-09-09T17:55:08.294286-04:00

Keep your company/client/project folders. After installing the private plugin, create or select a Codex project pointing to the intended local folder, then start a task inside it. In Claude Code, start a fresh session in that folder. Say:

> Use the project starter to onboard this client for [project]. Analyze the relevant existing material, explain what is known and missing, select the project folder, and prepare the next milestone. Here is the repository if applicable: [URL]. Preserve existing files.

Use the namespaced project-starter skill from ide-project-starter when multiple similarly named skills appear. In Claude Code its command is `/ide-project-starter:project-starter`; select the plugin's project-starter skill in Codex. Follow client-onboarding.md for the conversational wizard and source/privacy boundaries.

Before installation, explicitly point the AI to skills/project-starter/SKILL.md in this kit checkout. Repo-local discovery does not make the skill available in arbitrary client folders. plugin-installation.md records exact package and installation status.

Clone this repository to obtain the kit. Use its initializer to create each new project with a new identity; copying the whole kit would also copy its memory/evaluation records. Once onboarding is complete, open the selected project for daily work or explicitly select it while staying at the client root.

## Existing project

Say: "Use project-starter to adopt this existing project. Preserve its files and instructions, recover the current state, show the additions, and integrate portable memory." Follow adopt-existing.md. An existing starter project uses resume instead of a new identity.

For either mode, follow storage-boundaries.md: original client material stays at its approved source, approved summaries and project records go in the project repository, secrets stay in a credential store, and disposable tooling stays local where possible. Snapshots are optional and need approval; explicit source coverage and access gaps are required.

## First setup after cloning the kit

Use Python 3.10 or newer. Run from the kit root:

```sh
mkdir -p experiments/.tmp
python3 -m venv experiments/.venv
experiments/.venv/bin/python -m pip install -r experiments/requirements.lock.txt
```

This recreates the tested initialization environment using network package downloads. The lock file pins versions but does not contain artifact hashes; it is not an offline bundle or a complete supply-chain guarantee. No global installation is needed. Existing generated projects can resume using system Python without Copier.

## Manual initialization

Create a dedicated target and a six-field input file. Existing context first follows intake.md. For example:

```json
{
  "name": "My next project",
  "profile": "business",
  "objective": "Validate the proposed service before building it",
  "audience": "The intended customers",
  "constraints": ["No external publication without authorization"],
  "success_criteria": ["A documented first milestone and next action"]
}
```

For adoption, put these six fields under brief and provide a separate state object. brief.objective and state.objective must match exactly, including whitespace and punctuation. Adopt paths --target, --input and --plan are workspace-relative; state.sources is project-relative and excludes AGENTS.md and CLAUDE.md. See adopt-existing.md for concrete commands.

Save this as `projects/brief.json` inside the kit; create `projects/my-next-project`. Use software for a website or app; business for a business initiative or research without a software deliverable.

```sh
experiments/.venv/bin/python -B scripts/start_project.py preview --target projects/my-next-project --input projects/brief.json --plan projects/start-plan.json
experiments/.venv/bin/python -B scripts/start_project.py apply --plan projects/start-plan.json
```

Review the preview before apply. If paths collide, nothing is applied. Do not edit an integrity hash, remove original files or force overwrites to bypass it.

For a different dedicated projects workspace, pass `--workspace /absolute/projects-folder` before preview or apply. Target, input and plan remain relative to that workspace. Use the same workspace for both commands. The selected workspace must exist and cannot be the filesystem root, your home directory or a symlink. Plans bind to the canonical workspace; after moving a workspace, create a fresh preview instead of replaying an old plan. All work in the kit's current development/rehearsal stays within this repository.

## After initialization

Open the generated folder as the working project. Use `starter-resume`, `starter-checkpoint` or `starter-review` by name. In Codex use `$` mentions; in Claude use `/` commands. The skills are local to that project; no plugin or dedicated agent is needed.

The first session completes context/index.md and QUALITY.md, defines the first milestone, then saves a checkpoint. Meaningful work ends with another checkpoint. Fresh sessions run resume before changing files. The agent follows these instructions; there is no background observer saving every conversation.

The initializer creates the project's records, not a website framework, deployed app or operating business. Choose domain tools after the brief and constraints are understood.

GitHub backup requires an authorized commit and push of reviewed files. Checkpointing alone does not update GitHub. The kit repository backs up the kit; a future project's independent repository has its own backup status.

See ../validation/READINESS-RESULTS.md for tested versus pending capabilities and session-acceptance.md for the normal-session and second-computer checks.

## Platform limits

The initializer is a POSIX pilot tested on this Mac, with hard-link support required. Windows initialization is refused explicitly; Linux and other filesystems remain unverified. Normal CLI rendering writes to .starter-work/render in the selected workspace, so a packaged toolkit stays unchanged. Direct library render calls without a scratch argument still use the kit experimental folder and are intended for serialized development only. Workspaces with symlink ancestry are intentionally refused; select the canonical path instead (for example /private/tmp instead of /tmp on macOS).

Bundled template assets are UTF-8 text only. Generated helpers are invoked through Python; executable mode bits are not preserved or required. The receipt hashes content, not permissions. Runtime concurrency does not defend against malicious same-user directory replacement.
