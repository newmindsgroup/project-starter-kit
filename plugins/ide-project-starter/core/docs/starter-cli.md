# Start, resume and checkpoint

Version-Timestamp: 2026-09-08T15:03:37.044204-04:00
Status: v0.2 supervised pilot with business/software profiles and a private GitHub backup. No global installation. See quickstart.md for the shortest path.

## What is ready

The bundled template uses the tested Copier 9.18.2 environment for rendering. It adds a project brief, context register, shared Codex/Claude entry files, quality requirements, four workflow documents and three project skills for both tools and portable Python helpers. Every generated project receives a new random identity. Copying an existing project preserves that identity and its checkpoint chain.

The template adds one business/ or software/ work index. It does not move an existing application's files, choose an application framework, install an observer or invent passing quality checks. Future profile combinations remain open.

## Preview and initialize

Run from the starter-kit root. By default target folders, input and plans are confined to the kit workspace. An explicit --workspace /absolute/dedicated-folder before the subcommand selects a different boundary. All paths stay relative to that boundary. Both commands must use the same canonical workspace; new v2 plans refuse replay elsewhere. Old v1 plans are accepted only at the default kit root and still must pass render hash checks. Create a new target directory before running preview. Use the input structure shown in examples/business-input-2026-09-08T130000AST.json, changing the six fields to fit the project.

```sh
mkdir -p projects/my-project
experiments/.venv/bin/python -B scripts/start_project.py preview --target projects/my-project --input examples/business-input-2026-09-08T130000AST.json --plan examples/my-project-plan.json
experiments/.venv/bin/python -B scripts/start_project.py apply --plan examples/my-project-plan.json
```

The preview writes its plan and disposable rendering files under .starter-work/render in the selected workspace, never project target files. Review its create, same and conflicts lists. Apply is the explicit local write step. The plan fixes the brief, identity, version timestamp and output hashes. Template changes after preview require a new plan. Plans are integrity-checked records, not signed authorization tokens.

A conflicting existing README, PROJECT, entry file or other template-owned path stops the entire preflight. Preserve the original and use a new destination or resolve the adoption separately. There is no force overwrite or automatic merge flag. Follow intake.md for companion-folder adoption or a reviewed manual integration. Unrelated existing files stay in place. An unchanged repeat of a completed plan preserves edits and returns already_initialized, which is not a health assertion.

No arbitrary repository URL is fetched. Creating or publishing a remote repository remains a separately scoped step. Existing Git repositories can receive additive files when no owned path conflicts, but this tool does not inspect Git status; the start workflow requires that inspection. No global onboarding overlay is applied to this Drive-backed folder.

## Recover work

From a generated project folder:

```sh
python3 -B .starter/project_memory.py resume
python3 -B .starter/project_learning.py validate
```

Python 3.10 or newer is needed by the portable helpers. They use only the standard library; Copier is needed at initialization, not to resume. Actual cross-version and operating-system compatibility still require testing.

Resume returns the latest objective, constraints, decisions, completed work, recorded checks, blockers, next action, external action notes and head digest. Source changes produce needs_review. Even ready_for_context_review requires inspecting actual files and applicable Git status. A valid chain proves neither completed work nor current external state.

The stable memory/state.md points to the checkpoint reader. It is not a second writable state summary. Both AGENTS.md and CLAUDE.md point to the same procedure. Their contents have been inspected, but automatic loading in new Codex/Claude sessions remains untested.

## Save a checkpoint

Follow workflows/checkpoint-project.md. Prepare a JSON file inside the project with the nine documented state fields, retain the head from resume, and run:

```sh
python3 -B .starter/project_memory.py checkpoint --input checkpoint-input.json --expected-head HEAD_FROM_RESUME
```

Checks and action receipts must describe what actually happened. The command records claims, it does not perform the checks or repeat actions. Proposed decisions do not become accepted policy. The complete state snapshot is intentional so recovery does not depend on reconstructing conversation history.

Every checkpoint is create-only, numbered, linked to the previous digest and hashed as canonical JSON. A stale head or a competing writer fails. Re-read and reconcile; do not retry blindly. This is same-filesystem collision protection, not cross-machine locking or cloud synchronization assurance. The older learning-proposal lifecycle still requires serialized operations.

## Failure and recovery

Initialization publishes individual complete files and writes a receipt last. It is not a multi-file transaction. If interrupted, preserve the plan and output, inspect any .pending-* artifacts, then reapply the same plan only after reconciliation. Identical existing output can be completed; edited partial output is refused. No rollback deletes files automatically. The plan lists the intended paths and hashes for a reviewed cleanup.

Runtime records detect corrupt chains and changed sources. Preserve conflicting or damaged files and recover from trusted originals. Hashes are not signatures and can be recomputed by a writer. No automatic backup, restore, power-loss guarantee or distributed recovery is claimed. Hidden/sensitive source paths and selected secret patterns are rejected; these checks are not complete classification. Google Drive sync is unaffected by Git ignore rules.

## Evidence and next gate

Historical starter results and synthetic business/software fixtures are retained in the private development source. They are not distributed in the runtime package. See the public release VALIDATION.md for current acceptance evidence.

Before release: verify actual IDE entry behavior, another-machine recovery, complete dependency/license suitability, and an explicit adoption procedure for colliding existing documents. Template upgrades and learned-skill evaluation/promotion remain separate work. No extra plugin is needed for this pilot.

## Review clarifications

Plan files stay at the explicit relative --plan path inside the starter workspace, outside the target. Publication requests file mode 0600; this does not control cloud-provider access or existing parent permissions. Retain the plan while recovery or provenance is needed, then apply the project's reviewed retention policy. Receipts contain schema, timestamp, project/plan IDs and output path hashes, not source content. The brief remains in the plan and should be classified accordingly.

Publication does not hard-link from the Copier staging folder to the target. It writes a fresh temporary file in each destination parent, links it to the final name there, then removes the temporary name. Thus staging may be on another device without creating a cross-device link. Unsupported destination hard links still fail. Rendering temporary folders are removed after use. An interrupted publication may leave a .pending-* artifact requiring inspection.

The initializer enforces Copier 9.18.2 and compares actual rendered bytes to the saved plan. It does not reject every different Python or Jinja patch version if those bytes are identical. The experimental environment's dependency versions are recorded separately; compatibility outside that environment remains unverified.

Checkpoint hashes use UTF-8 of Python json.dumps with ensure_ascii=False, sort_keys=True, indent=2 and one trailing newline. Duplicate JSON keys are rejected. Strings are not Unicode-normalized; number encoding follows Python JSON. No cross-language canonicalization standard is claimed. The digest excludes only the sha256 field itself. A writer who rewrites the full chain and recomputes every digest can evade drift detection.

An empty or truncated checkpoint is a hard validation error with nonzero exit status, never a silent fallback to an older checkpoint. Stale readable sources instead return needs_review. The model recovery exercise was one local Gemma trial, checking objective, next action, blocker, latest check and lack of external action authority. It does not establish a success rate or validate all nine state fields.
