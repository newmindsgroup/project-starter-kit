# From project lessons to kit releases

Version-Timestamp: 2026-09-08T17:48:04.992939-04:00

Use this loop after onboarding/adoption, at a meaningful milestone, after a user correction or verified recurring problem, and at the end of a pilot. It is invoked by the agent, not a background observer. Prefer reuse, a small existing-skill update, a deterministic test or no change over creating another skill.

## 1. Keep the original evidence in the project

Use the generated project_feedback.py helper (or the trusted toolkit copy for older projects). A report input has id, event_id, mode (new/adopt/resume/upgrade), outcome (pass/partial/fail), lesson, scope (project/kit), and sources (existing project-relative evidence files).

```sh
python3 -B .starter/project_feedback.py --root . report --input pilot-report-input.json
```

The immutable report lives under memory/feedback. It records the project identity and source hashes. Record actual outcomes, corrections and what should change, with the evidence needed to reproduce the problem. Reports do not count invented check outcomes or repeat copies of one event as new evidence. Keep source approvals and original project decisions separate from lessons.

## 2. Prepare a reviewed, sanitized packet

An export input contains report_id, kind (docs/skill/template/helper/test), summary and approved_for_kit:true. Write summary specifically for the kit: no client name, pricing, contacts, private source links, credentials or unnecessary project-specific details. Approval must already exist in the actual user-authorized workflow. A Boolean field is a record of that review, not permission by itself.

```sh
python3 -B .starter/project_feedback.py --root . export --input export-input.json --output approved-kit-feedback.json
```

Export checks source freshness. Its output includes only the sanitized summary, kind, timestamp and an opaque event key. No project name, project ID, report body, file paths or raw evidence is automatically exported. Pattern checking is not a complete sensitive-data classifier. The agent must inspect the exact packet and its authorized audience. Original evidence stays in the project. Do not copy every project's records into this repository.

## 3. Submit and triage in the kit

Copy only the reviewed packet into improvements/packets in the kit using a new filename. Then run the trusted source helper from the kit root:

```sh
python3 -B scripts/project_feedback.py --root . submit --input improvements/packets/PACKET.json
python3 -B scripts/project_feedback.py --root . status --id INBOX_ID
```

Equivalent kind/summary text after case/whitespace normalization points to the same inbox ID. A duplicate returns the existing item and does not increase a recurrence count. Semantic duplicates still require review. Repeated observation of one event is not independent confirmation. Different event evidence can be referenced in triage notes without duplicating the proposal.

Classify the smallest change and inspect existing skills. A project-specific exception stays local. A verified high-impact defect may warrant a fix after one occurrence; repetitions are useful evidence, not an arbitrary quota.

## 4. Implement, test and release

Record decisions with an input containing status, reason, evidence (existing kit-relative files) and release (null until released). Use the current head from status.

```sh
python3 -B scripts/project_feedback.py --root . decide --id INBOX_ID --input decision.json --expected-head HEAD
```

Lifecycle: open → triaged → implemented → released. Open/triaged/implemented may be rejected; implemented can return to triaged. Decisions are immutable, sequential and expected-head protected. Implemented/released require evidence; released requires a release reference. Evidence hashes record supporting files, not proof that their claims are true. The agent must actually execute checks and verify publication before recording released. These commands never commit, push, create issues or send messages.

Use release-checklist.md. Update canonical source, regenerate the plugin, add regression cases and document migrations. All projects do not automatically receive a release. Use project-upgrades.md for project copies and the native installer for the installed plugin.

## Measure usefulness

Review recovery accuracy, repeated mistakes, time/effort to onboard, unresolved source access, duplicate proposals and upgrade failures. Compare actual baseline and candidate behavior. Skill count and number of stored notes are not success measures. No model retraining, autonomous acceptance, universal watcher or automatic promotion is enabled.
