---
name: starter-resume
description: Recover saved state and continue a project initialized with the IDE Project Starter Kit after a new session or tool switch.
---

# Starter Resume

Version-Timestamp: 2026-09-11 15:58:29 AST
Kit-Version: 0.7.0-pilot

Locate the project root containing project.json and .starter/project_memory.py from the current workspace. Do not use a different project's helper. If either is missing, stop recovery and report the missing prerequisite.

If context/INDEX.md or memory/STATE.md exists, the project predates kit 0.7.0. Stop and follow the trusted toolkit's docs/project-upgrades.md to run migrate_layout.py before resuming.

Read PROJECT.md, context/index.md and QUALITY.md. Follow workflows/resume-project.md. Run `python3 -B .starter/project_memory.py resume` from that root, then inspect the actual files and Git status when applicable. Explain objective, accepted decisions, last recorded checks, blockers and next action. Distinguish recorded claims from current verification. Reconcile stale sources or a corrupt chain before continuing dependent work. Never replay an external action from memory without reconciling its outcome and authority.

Continue the user's authorized task and checkpoint meaningful progress using workflows/checkpoint-project.md. For a simple read-only status request, report without manufacturing a new checkpoint.

Inspect client_context in the resume response when present. A stale or unavailable client association blocks reliance on the affected shared evidence until reconciled. Do not silently rebind to a nearby client folder.
