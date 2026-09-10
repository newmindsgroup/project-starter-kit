# Adopt an existing project

Version-Timestamp: 2026-09-09T17:55:08.294286-04:00
Status: supervised adoption. Existing application layout remains intact.

Invoke project-starter and say "Adopt this existing project." The same four skills serve both starting modes. Read STORAGE-BOUNDARIES.md first. Identify the actual project/repository root, source material, storage audiences, existing instructions, uncommitted work and any existing memory system. No Git operation, provider action or dependency execution is an intake side effect.

## Review current understanding

Prepare a reviewed JSON input with two objects: brief (the six QUICKSTART fields) and state (objective, constraints, decisions, completed, checks, blockers, next_action, external_actions and sources). Use actual current work, not invented historical checkpoints. Check claims are labeled as historical unless rerun. sources contains explicitly selected, existing project-relative UTF-8 documents, not secrets or instruction files being appended. Inaccessible materials remain gaps. brief.objective and state.objective must match exactly, including whitespace, capitalization and punctuation. Copy the same string into both fields. This is required in addition to the six-field brief described in QUICKSTART.md.

## Preview, add, integrate, verify

Use the trusted toolkit's pinned Python/Copier environment. The workspace is an approved parent folder. In this example it contains an existing website/ project, adoption-input.json and, after preview, adoption-plan.json.

**Path rule:** --workspace is absolute. --target, --input and --plan are workspace-relative, not relative to the shell's current folder. Absolute values for those three arguments are deliberately refused with an argument-specific message. Symlinks and traversal remain refused. Keep input and plan outside the target and inside the workspace. state.sources is different: its entries are relative to the selected project, for example brief.md inside website/, and must exclude AGENTS.md and CLAUDE.md.

```sh
KIT="/absolute/path/to/ide-project-starter-kit"
WORKSPACE="/absolute/path/to/client-folder"

"$KIT/experiments/.venv/bin/python" -B "$KIT/scripts/adopt_project.py" --workspace "$WORKSPACE" preview --target website --input adoption-input.json --plan adoption-plan.json
"$KIT/experiments/.venv/bin/python" -B "$KIT/scripts/adopt_project.py" --workspace "$WORKSPACE" apply --plan adoption-plan.json
```

Preview writes only the plan and temporary rendering scratch. The plan records SHA-256 hashes of raw UTF-8 bytes, original preserved text, exact additions and exact append blocks. Review it before apply. The plan can contain confidential current context and instructions. Preserve it as the recovery record in an approved destination.

The helper preserves existing README.md, PROJECT.md, QUALITY.md, context/INDEX.md and profile work documents. It creates missing standard files. Existing AGENTS.md and CLAUDE.md receive proposed append blocks, not automatic replacement. Review all existing rules and block content for compatibility. Append the returned UTF-8 block bytes exactly once, retaining every original byte, including BOM, CRLF and missing final newline. This append is a deliberate agent-performed edit within the authorized adoption, not a separate request for blanket approval. Never change earlier instructions to force completion. If policy conflicts require a semantic merge, stop this automatic path and prepare a separately reviewed manual migration.

The CLI never overwrites existing files. Existing identity/runtime, learning/checkpoint records or other owned-path collisions block preview. Use resume for an already-adopted project; a different existing memory system needs explicit migration mapping. This is not a universal converter.

```sh
"$KIT/experiments/.venv/bin/python" -B "$KIT/scripts/adopt_project.py" --workspace "$WORKSPACE" finish --plan adoption-plan.json
python3 -B "$WORKSPACE/website/.starter/project_memory.py" --root "$WORKSPACE/website" resume
python3 -B "$WORKSPACE/website/.starter/project_learning.py" --root "$WORKSPACE/website" validate
```

Finish checks original prefixes plus exact append blocks, all generated additions and selected sources. Only then does it create checkpoint 1 and the installation receipt. It adds the project brief/context/quality sources to checkpoint evidence. Confirm recovered objective, decisions, completed work and next action, then rerun relevant actual project checks. Finish is not proof those project checks passed.

## Recovery and withdrawal

Only one adoption/operator may change the target at a time. The create-only .starter/adoption-pending.json marker binds the target to the plan before other additions. It remains as provenance after completion. A different plan cannot take over. Repeating apply with the same unchanged plan completes matching partial additions. Repeating finish can complete a matching checkpoint-before-receipt interruption. A completed receipt returns already_adopted; run resume separately to check current state.

Keep the plan until adoption is verified and backed up. If it is lost or edited, restore its exact reviewed copy. Never remove the marker or edit hashes to bypass conflict checks. Changed sources, original files or generated additions require reconciliation, not blind retries. No transaction spans agent edits, helper writes or cloud synchronization.

For a reviewed rollback before ordinary project work, use the plan's created-path/hash list to identify only unchanged starter additions. Restore instruction files from their preserved original bytes only if the current file exactly equals original plus the planned block. Preserve any later edits or records. Delete no unrelated files and do not reset Git. No automatic destructive rollback command is provided. If safe integration is unsuitable, use the companion workflow in INTAKE.md with its separate discovery and source-freshness limits.

Existing .gitignore is preserved exactly, including negations. Review its coverage and the actual staged upload scope before publication; adoption does not promise that an old ignore file covers every sensitive path. Do not run a formatter on instruction files before finish. The permitted result is exactly the original bytes followed by the planned block, with no extra trailing bytes.

Preview and apply expose unapplied_ignore_rules when an existing .gitignore is preserved. This is a non-binding comparison aid, not permission to append the rules. Review their interaction with existing negations and the exact staged set. A missing .gitignore is created from the template.

## Diagnosing a failed command

A missing input or plan reports the argument, relative filename and exception class. Malformed JSON reports the input/plan argument. Other caught failures report the exception class and operation, with an OS filename when available. No record contents are printed by these default diagnostics.

Add --debug before or after the subcommand for a local traceback, for example append --debug to the preview command above. Tracebacks can contain private paths, source lines or exception messages. Inspect and redact them before sharing; never publish raw client debug logs by default. A failure does not authorize deleting partial work or replaying external actions.
