# Upgrade existing project copies

Version-Timestamp: 2026-09-08T17:48:04.992939-04:00

Plugin installation and project-copy upgrades are separate. The installed plugin supplies the latest starting workflows. Existing project helper scripts, workflow documents and skills remain their own copies. Never replace a project's folder with a fresh template or reset its identity/history.

## Prepare the comparison

Use the trusted current toolkit, the existing project and an approved private parent workspace. Staging must be outside the project and inside that workspace. It can contain original instructions, check output and project context. Its privacy/backup requirements match the project. Settle current source-freshness failures and stop concurrent work before upgrading.

```sh
python3 -B TOOLKIT/scripts/upgrade_project.py --workspace WORKSPACE preview --target PROJECT --stage upgrade-candidate
python3 -B TOOLKIT/scripts/upgrade_project.py --workspace WORKSPACE check --stage upgrade-candidate
```

Preview compares managed files against the original installation receipt or latest upgrade receipts. Local customizations, missing baseline files or untracked collisions stop the automatic path. Prepare a manual three-way migration when necessary; do not replace baseline hashes to pretend custom work is unmodified.

The stage contains plan.json, candidate files, original files, changes.diff and, after checks, checks.json. The managed set is narrowly limited to runtime helpers, three project skills in both tool directories, workflow documents, the skill comparison catalog and storage guidance. It excludes project identity, checkpoints, learning records, source links, business context, application code, root instructions and Git configuration. A missing new managed file can be added; changed existing managed files require baseline agreement.

Review the candidate helper code as part of the trusted toolkit release before running check. Checks execute Python with your current user permissions; this tool does not sandbox unknown code. Check executes the verified candidate memory/learning helpers against the actual project records with read-only commands. It requires resume to report current available context. It is a compatibility check for this kit, not a rerun of application tests or a complete security audit. Run the actual project's required checks separately when relevant.

## Apply the reviewed changes

Read the diff and check results first. The agent copies only the approved changed candidates into their exact project-relative paths, rechecking the original hashes immediately before each write. This manual edit is within an explicitly authorized upgrade; it is not performed by the CLI. Preserve original bytes in the stage and do not edit other files. Do not reformat or customize candidates during this upgrade. If an unexpected edit or interruption occurs, stop and reconcile the existing stage rather than blindly applying a new one.

```sh
python3 -B TOOLKIT/scripts/upgrade_project.py --workspace WORKSPACE finish --stage upgrade-candidate
```

Finish requires the checked plan, exact candidate bytes, the same baseline and unchanged protected records. It reruns compatibility checks before creating an immutable upgrade receipt. The original installation receipt remains untouched. There is no approval implied by merely creating a plan. A completed upgrade is not a global plugin installation receipt.

## Recovery and rollback

Keep the full stage until checks and backup complete. A failed staging run leaves its plan and any completed files; preserve them and choose a fresh stage after inspection. A failed check leaves the project unchanged. If failure occurs during manual application, use the plan's before/after hashes and original files to restore only paths still matching the candidate, or complete the reviewed changes. Preserve unexpected edits. New candidate-only files may be removed only after confirming they still match their recorded candidate hash and contain no subsequent work.

Rollback is a reviewed manual operation. No broad delete/reset or automatic destructive rollback command is provided. After a completed receipt, record any later reversal as a separately reviewed migration; never rewrite receipt history. Shared/cloud concurrent writes and power-loss transactions are not solved by these helpers. Project work must be serialized through the upgrade.

On another computer, clone approved project records, recreate local tools, authenticate to necessary sources and run resume. The kit does not copy credentials, globally install plugins, or guarantee provider access. Plans depend on the exact toolkit release; if toolkit bytes change, preserve the old stage and generate a fresh reviewed plan.

Installation and upgrade receipts are local recovery metadata, not authenticated provenance. The original installation receipt has no seal; upgrade receipts have unkeyed hashes. Deliberate edits with recomputed hashes and deletion of the last receipt cannot be reliably detected without a separate trusted backup. Compare approved Git history when metadata is suspect. Do not rebaseline a customization to bypass review.

## From 0.6 to 0.7: lowercase record names

Version 0.7.0 renamed context/INDEX.md, context/STORAGE.md, memory/INDEX.md, memory/STATE.md and the profile WORK.md file to lowercase. A project created earlier migrates once, before its next upgrade. The upgrade helper refuses to stage while old names remain.

```sh
"$KIT/experiments/.venv/bin/python" -B "$KIT/scripts/migrate_layout.py" --workspace "$WORKSPACE" preview --target website --stage layout-migration
# Before apply: review each file under layout-migration/candidate/ against layout-migration/original/.
"$KIT/experiments/.venv/bin/python" -B "$KIT/scripts/migrate_layout.py" --workspace "$WORKSPACE" apply --stage layout-migration
"$KIT/experiments/.venv/bin/python" -B "$KIT/scripts/migrate_layout.py" --workspace "$WORKSPACE" finish --stage layout-migration
```

Preview writes a sealed plan, exact candidate instruction files and their originals outside the project. Apply checks everything before changing anything, renames records through a temporary name so a case-only rename also works on case-insensitive filesystems, and replaces an instruction file with its reviewed candidate only while the file still matches its staged original. Record content never changes. Inside an adoption block, candidates use the new names and move headings one level down so the host file keeps a single title. Finish verifies every rename and candidate, appends a checkpoint with the same state and renamed sources, and records a receipt under .starter/migration-receipts/. Then run the ordinary upgrade to receive the 0.7 helpers, workflows and skills.
