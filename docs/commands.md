# Technical setup and recovery recipes

Version-Timestamp: 2026-09-10 18:27:14 AST

These examples are for an agent or operator who wants the exact commands. Most users can use the README prompt. Replace illustrative paths with approved real locations. One operator should change a target at a time.

## Resolve paths and prerequisites

KIT is the public checkout. CORE contains the matching package helpers and template. WORKSPACE is the application's parent, not the toolkit. The child website folder is the target.

```sh
KIT="/absolute/tooling/project-starter-kit"
CORE="$KIT/plugins/ide-project-starter/core"
WORKSPACE="/absolute/work/Acme"
ENV="/absolute/approved-tooling/starter-venv"

python3 -m venv "$ENV"
"$ENV/bin/python" -m pip install -r "$CORE/experiments/requirements.lock.txt"
```

Python 3.10 or newer is required; initialization enforces Copier 9.18.2. The lock pins versions but not artifact hashes. Setup downloads packages and is not an offline bundle. Use an existing compatible environment when available. Keep environments out of synced client storage where practical.

The workspace and target must exist before preview. Create only the intended new folders, within approved scope. Paths with symlink ancestry are refused. On macOS, /tmp is often a symlink; use the canonical path returned by your filesystem tools. Windows initialization is unsupported.

## Inspect without applying

```sh
python3 -B "$CORE/scripts/setup_wizard.py" inspect --project "$WORKSPACE/website"
```

Review the returned mode, diagnostics and required verification. The inspector does not install anything or prove an existing runtime is trustworthy.

## New project input

Save new-input.json in WORKSPACE, outside website:

```json
{
  "name": "Website project",
  "profile": "software",
  "objective": "Prepare the website project foundation",
  "audience": "The project team",
  "constraints": ["Preserve approved source material"],
  "success_criteria": ["Recover the first saved checkpoint"]
}
```

Use software for a software deliverable. Use business for a business or research initiative without a software deliverable. This does not select a framework.

```sh
"$ENV/bin/python" -B "$CORE/scripts/start_project.py" --workspace "$WORKSPACE" preview --target website --input new-input.json --plan new-plan.json
```

Review the proposed create/same/conflict lists. When within the user's authorized setup:

```sh
"$ENV/bin/python" -B "$CORE/scripts/start_project.py" --workspace "$WORKSPACE" apply --plan new-plan.json
```

Complete the context register and actual quality requirements, then save the first checkpoint using the recipe below.

## Existing-project input

Save adoption-input.json in WORKSPACE. All nine state fields are required:

```json
{
  "brief": {
    "name": "Existing website",
    "profile": "software",
    "objective": "Continue the existing website",
    "audience": "The project team",
    "constraints": ["Preserve current files and history"],
    "success_criteria": ["Recover the current handoff"]
  },
  "state": {
    "objective": "Continue the existing website",
    "constraints": ["Preserve current files and history"],
    "decisions": [],
    "completed": [],
    "checks": ["Application checks have not been rerun"],
    "blockers": [],
    "next_action": "Review the next website milestone",
    "external_actions": [],
    "sources": []
  }
}
```

Replace this example with actual inspected facts. Empty lists mean no entries have been established, not proof that no history exists. Missing history belongs in blockers or the context register.

brief.objective and state.objective must match exactly, including whitespace. sources contains selected existing UTF-8 paths relative to website, such as context/approved-brief.md. Do not include secrets or AGENTS.md/CLAUDE.md, which may be appended during adoption.

```sh
"$ENV/bin/python" -B "$CORE/scripts/adopt_project.py" --workspace "$WORKSPACE" preview --target website --input adoption-input.json --plan adoption-plan.json
"$ENV/bin/python" -B "$CORE/scripts/adopt_project.py" --workspace "$WORKSPACE" apply --plan adoption-plan.json
```

**Before finish:** inspect the plan's exact entry append proposals, read existing instructions and append only compatible blocks, preserving every original byte. The helper does not perform a semantic merge. Do not use a formatter or duplicate the append. Reconcile conflicting instructions instead.

```sh
"$ENV/bin/python" -B "$CORE/scripts/adopt_project.py" --workspace "$WORKSPACE" finish --plan adoption-plan.json
python3 -B "$WORKSPACE/website/.starter/project_memory.py" --root "$WORKSPACE/website" resume
python3 -B "$WORKSPACE/website/.starter/project_learning.py" --root "$WORKSPACE/website" validate
```

Apply alone is not completed adoption. Finish verifies the exact integration, then writes checkpoint 1 and its installation receipt. Review the recovered state and run the application's real checks separately.

[Full adoption contract](../plugins/ide-project-starter/core/docs/adopt-existing.md)

## Save and resume a checkpoint

Save checkpoint-input.json inside the project with exactly the nine state fields from the adoption example's state object. Select evidence paths that actually exist and are approved for the project.

For an initialized project without a checkpoint:

```sh
python3 -B "$WORKSPACE/website/.starter/project_memory.py" --root "$WORKSPACE/website" checkpoint --input checkpoint-input.json --expected-head none
```

For later checkpoints, first run resume and supply the returned head in place of none. A stale head is a conflict to reconcile, not a value to bypass.

```sh
python3 -B "$WORKSPACE/website/.starter/project_memory.py" --root "$WORKSPACE/website" resume
```

The command records check claims; it does not execute them. Save and back up approved files through an authorized Git workflow. Do not upload private checkpoint inputs or adoption plans simply because they exist.

## Recover interrupted work

Keep the exact original plan. Repeating apply with that same unchanged plan can complete matching partial output. Edited output, changed source files or another plan cause conflicts. Do not delete pending markers, rewrite receipts or edit hashes to bypass them.

For adoption, perform any missing compatible entry appends and run finish. A retained adoption-pending marker can remain after completion as provenance. Resume still verifies current saved state.

[Recovery limits](../plugins/ide-project-starter/core/docs/adopt-existing.md) · [Troubleshooting](troubleshooting.md)
