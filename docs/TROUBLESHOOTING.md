# Troubleshooting

Version-Timestamp: 2026-09-10 18:27:14 AST

| What you see | What to do |
| --- | --- |
| Repo URL gives 404 | Confirm the exact public URL. Private application URLs require separate authentication. Never paste tokens into chat. |
| Skill is missing | Start a fresh session; check the installed marketplace/version. For repo-only use, ask the agent to read the package's skills/project-starter/SKILL.md directly. |
| Python or Copier missing | Follow INSTALL.md and COMMANDS.md. Use the pinned environment; do not install every framework runtime. |
| Absolute --input/--plan/--target rejected | Keep --workspace absolute. Supply those three flags relative to that workspace, for example website or adoption-input.json. |
| Brief and state objectives differ | Copy the exact objective string into both fields, including punctuation and whitespace. |
| Input file missing or malformed | Check its filename relative to --workspace and validate the JSON. Default diagnostics name the relevant argument. |
| Existing files collide | Preserve them. Choose adoption for existing work; reconcile owned-path or policy conflicts. Never delete files to make the folder appear empty. |
| Existing starter identity found | Resume or recover the current installation. Do not initialize a second identity. |
| Finish refuses an instruction merge | Compare original bytes plus the planned block. A formatter, duplicate append, BOM or newline change can invalidate the exact comparison. |
| Source changed after preview | Inspect what changed and prepare a fresh reviewed plan if needed. Do not alter hashes to force the old plan. |
| Partial setup remains after failure | Preserve the plan and all existing output. Use matching-plan recovery; no blind cleanup or Git reset. |
| Symlink or unsupported filesystem error | Select a canonical supported workspace. Do not disable boundary checks. Windows initialization is unsupported. |
| Resume says needs_review/unavailable | Read the reported evidence or source-access gap. A missing Drive permission cannot be repaired by changing a hash. |
| New session seems to forget | Confirm a checkpoint was actually saved and the session opened the correct project. Ask it to read project instructions and run resume. Unsaved conversation is not captured. |
| Updated plugin, old project helpers | Expected: project copies require a separate reviewed upgrade. Do not overwrite customized helpers. |
| Public release verification fails | Keep the mismatched files for inspection. Obtain a clean copy or reconcile public changes into the private source before regenerating. Hashes are integrity checks, not signatures. |

For a difficult adoption error, --debug prints a local traceback. It can contain private paths or exception details. Redact it before sharing. A failed command does not authorize unrelated changes.

Public reports should include the kit version, operating system, Python/Copier versions, command shape and a small fictional reproduction. Leave out client names, source documents, credentials, raw traces and populated checkpoints.
