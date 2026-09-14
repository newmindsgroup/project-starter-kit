---
name: starter-checkpoint
description: Save a handoff or meaningful progress checkpoint in an IDE Project Starter Kit project so another session can resume.
---

# Starter Checkpoint

Version-Timestamp: 2026-09-14 15:34:15 AST
Kit-Version: 0.7.3-pilot

Locate the root containing project.json and .starter/project_memory.py. If missing, report the prerequisite rather than initializing or overwriting identity.

Follow workflows/checkpoint-project.md. Run resume first and retain the exact current head. Assemble the nine state fields from actual work and authoritative sources, with a specific next action. Do not invent passing checks or approvals. Put the input JSON in a new project-local file; avoid credentials and raw transcripts.

Run the checkpoint command with --expected-head, then resume again and verify the saved state matches the intended handoff. A competing writer or stale head requires reconciliation, never blind retries. Checkpointing does not commit, push, deploy or change external systems. Report separately whether GitHub contains the latest work. Ask for no new authorization for a local checkpoint already requested by the user.
