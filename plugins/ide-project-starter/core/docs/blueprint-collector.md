# Project Blueprint foundation commands

Version-Timestamp: 2026-10-12 17:34:00 AST
Status: optional manual helpers inside Project Starter Kit. No background collection or dashboard; distribution does not update installed plugins.

Use Python 3.10 or newer on POSIX. Work from this kit checkout or use its absolute script path. Choose private local storage outside Git and cloud sync. The final storage directory must have private permissions. The helper rejects symlink ancestry and unrelated databases. Storage location is a reviewed operator choice; the helper is not a cloud-sync permission scanner.

Every command requires --database and --project-id. Use the project's existing project.json UUID. For the kit itself, do not invent a generated project's identity or overwrite its current records. A selected native session and machine need stable opaque SHA256 IDs. No client names or native paths belong in these values.

```sh
python3 -B scripts/project_blueprint.py --help
python3 -B scripts/project_blueprint.py --database "$HOME/.local/share/project-blueprint/private/ledger.db" --project-id YOUR_EXISTING_PROJECT_UUID status
```

Status on an absent database reports not_configured and creates nothing. Importing a source or explicitly starting a timer creates the private ledger. Directory creation does not enable an observer.

Use ingest with --source, --adapter codex|claude-code|ollama, --session-id, --machine-id, --tool-version and --billing-basis unknown|subscription|api|local. Session/machine IDs require 64 lowercase hex characters. They are bindings, not proof of native ownership. Keep the same binding for repeat imports. Leave --task-id absent unless the entire selected source belongs to one task. Importing a whole historical session into the current task would misattribute its costs.

Import reads up to 10,000 complete lines of at most one MiB per call. Partial final lines wait for completion. Repeat manually while pending_bytes is positive. Source rotation has a generation-bound cursor. Destructive truncation and counter regressions require reconciliation, never automatic zeroing. Source records are parsed transiently; only validated metadata enters SQLite.

Status, report and export open the existing ledger read-only. Report separates token totals by usage semantics. Mixed or unknown semantics have no combined total or known subtotal. Report returns category totals, known subtotals, missing-category counts, unassigned events and latest source timestamp. It does not establish freshness beyond the selected import. Report --task-id filters by the explicit binding. No billed dollars, savings or human replacement estimates are fabricated.

Timer accepts start, pause, resume, switch, stop and summary, with --user-id as an opaque UUID4. Transitions also need --task-id and optional --activity briefing|chatting|authoring|supervising|reviewing|rework. --at supplies an explicit timezone-aware timestamp; otherwise current UTC is used. One active task per person avoids overlapping time charges. A switch closes the previous task and starts the next. Closed timer intervals are reported as explicit-timer time, not verified attention. Open intervals remain unresolved and unlogged time remains unknown. Command-line corrections and confirmations are described below; a graphical UI remains planned.

Export --output writes a create-only 0600 JSON usage-metadata backup. Restore --input validates checksum/project identity and creates a new ledger only. The default export excludes human timer transitions. Use --human-history for the scoped usage and human-history backup described below. Do not call usage-only export full project financial-history backup. Keep the private database backed up under an approved machine-local backup policy. A checksum detects accidental corruption, not hostile modification by someone who can recompute it.

No tool activation, provider call, background service, Obsidian setup, model routing or public publishing occurs from these commands. Natural-language access will be wired into the canonical starter skills after the early pilot. Until then these commands are deterministic tools available to an authorized agent or operator from the source checkout.

Malformed or unsupported source records refuse the batch and report a safe byte offset without raw content. Cursor remains unchanged. There is no automatic skip or quarantine; inspect the source locally and preserve original evidence before choosing an explicitly reviewed repair. A blocked source is incomplete coverage.

Interrupted first creation can leave an unrecognized or empty target. It is deliberately not reused automatically because an empty unrelated file is not proof of ownership. Preserve that target in private storage for inspection, choose a fresh target, and retry the reviewed import or restore. Restore never repairs or overwrites it. A failure during initialization may leave this inspectable target; it is not a completed restoration.

Event identities currently retain native timestamp text. Equivalent rewritten timestamps need reconciliation before importing a rewritten source. Changing identity normalization requires a migration policy to avoid duplicate events in existing ledgers. Reasoning usage remains unknown when the native provider does not report it.

## Human-history recovery and review

Version-Timestamp: 2026-10-13 08:05:28 AST

Export remains usage-only by default. Add --human-history to explicitly include project-scoped interval and amendment history in blueprint-export.v2. Voided and superseded evidence is included; choose an approved private destination. Legacy v1 remains supported and restored summaries warn human_history_not_in_backup. This is a snapshot of stored evidence, not proof of complete historical collection.

Timer list shows interval_id, revision_id, archived, start/end, current corrected task/activity, confirmed and voided. Archived open intervals remain unresolved and never restart a timer. Summary separates active_seconds and confirmed_seconds, and continues to report attention_verified false and unlogged_time unknown. Stop a live timer before correcting or voiding its interval.

Use timer confirm|correct|void with --user-id, --interval-id, --previous-revision, --reason and optional --at. correct additionally requires --task-id, --activity, --start-at and --end-at. Reasons: timer_left_running, wrong_task, wrong_activity, duplicate, user_review or manual_reconciliation. Correct supplies a complete replacement of those four fields. Confirm acknowledges the current revision; a later correction clears confirmation. Void is terminal. All edits preserve original evidence and prior revisions. Stale revisions are refused. Repeat identical submissions are idempotent. Review timestamps must follow the interval and prior amendment.

Closed intervals cannot overlap for one person across the locally stored history. Refusals reveal no other project IDs or times. A scoped restored ledger cannot detect overlaps against projects absent from that backup; cross-project reconciliation requires the approved original ledger. Open intervals remain unresolved rather than accruing invented time.

History export uses one SQLite read snapshot across usage, original projected intervals and revision chains. A cross-project switch closes the prior interval by timestamp while excluding destination IDs. Interval IDs hash the original start transition identity, original project and person; they remain unchanged across restores. Restoring does not remap people, merge histories or resume source cursors.

Restore validates checksum, allowlisted fields, project scope, revision order and closed overlaps before initializing a temporary private database. It publishes only a fully populated target using a create-only hard link on the same filesystem. Insert failures preserve the original source and leave no published target. A hard crash may leave a private restore-*.db staging file for manual inspection. Checksums provide corruption detection, not authenticity against deliberate rewriting. No overwrite or merge is supported.

Version-Timestamp: 2026-10-13 08:14:00 AST
A correction requires --activity explicitly; it does not default or silently reclassify time. Starts, resumes and switches inside existing corrected closed time are refused. Legacy backup warnings are project-scoped. Equivalent amendment timestamps normalize to UTC for duplicate replay. Corrupted revision history causes a conservative refusal requiring local inspection and recovery; no automatic quarantine or skip is performed.

The CLI restore reader retains its 16 MiB input bound. Larger histories need a separately reviewed import-size budget or controlled use of the Python API; do not assume every large CLI export can be restored through the bounded reader. Multi-batch restore is implemented in the API, and the pilot must record backup size and exercise its actual restore route.
