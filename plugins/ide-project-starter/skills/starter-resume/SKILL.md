---
name: starter-resume
description: Recover saved state and continue a project initialized with the IDE Project Starter Kit after a new session or tool switch.
---

# Starter Resume

Version-Timestamp: 2026-09-14 15:34:15 AST
Kit-Version: 0.7.3-pilot

Locate the project root containing project.json and .starter/project_memory.py from the current workspace. Do not use a different project's helper. If either is missing, stop recovery and report the missing prerequisite.

Check exact directory-entry names, not Path.exists or shell -e: on a case-insensitive filesystem those also match lowercase files. List context/ and memory/ and compare the entry strings exactly; if access is unavailable, report layout verification as unavailable rather than infer it. Only actual entries named context/INDEX.md or memory/STATE.md indicate the legacy layout. If either exact legacy name is present, follow the trusted toolkit's docs/project-upgrades.md before resuming.

Read PROJECT.md, context/index.md and QUALITY.md. Follow workflows/resume-project.md. Run `python3 -B .starter/project_memory.py resume` from that root, then inspect the actual files and Git status when applicable. Explain objective, accepted decisions, last recorded checks, blockers and next action. Distinguish recorded claims from current verification. Reconcile stale sources or a corrupt chain before continuing dependent work. Never replay an external action from memory without reconciling its outcome and authority.

A retained .starter/adoption-pending.json is not by itself unfinished adoption. Inspect .starter/installation.json and project.json: receipt schema installation.v1 with project_id equal to project.json project_id, receipt plan_id equal to the adoption-pending.v1 marker plan_id, and a valid checkpoint chain are evidence that finish completed. Report the retained marker and the matching evidence when concluding adoption completed. A missing, malformed or mismatched receipt requires reconciliation. Do not remove markers, rerun finish or declare adoption incomplete merely because the marker remains. Distinguish completed kit adoption from an application brief or quality checklist that still needs work.

Continue the user's authorized task and checkpoint meaningful progress using workflows/checkpoint-project.md. For a simple read-only status request, report without manufacturing a new checkpoint.

Inspect client_context in the resume response when present. A stale or unavailable client association blocks reliance on the affected shared evidence until reconciled. Do not silently rebind to a nearby client folder.
