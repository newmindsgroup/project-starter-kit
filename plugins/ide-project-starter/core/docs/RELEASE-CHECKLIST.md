# Starter-kit release checklist

Version-Timestamp: 2026-09-08T17:48:04.992939-04:00

Use this checklist for each released improvement. A checklist entry or model review is not evidence that a check ran. Retain actual commands, results, versions, failures and review dispositions.

1. Triage sanitized inbox items. Name the verified problem, scope, acceptance behavior, reuse alternatives and affected projects. Link each change to an inbox ID or an explicit user request.
2. Capture a failing regression when changing behavior. Update canonical source under scripts/, skills/ or template/, never only generated package copies. Preserve existing fixtures and project identities.
3. Run the applicable behavior and compatibility checks:

```sh
python3 -B -m unittest discover -s tests -v
python3 -B scripts/check_learning_code.py
python3 -B scripts/project_learning.py validate
python3 -B scripts/build_plugin.py
python3 -B scripts/build_plugin.py --check
```

4. Validate both native plugin manifests, each canonical/bundled skill and marketplace source/version consistency. Run rendered checks when visuals change. Test packaged initialization, adoption and staged upgrades; inspect failure/recovery behavior. Report missing scanners or untested platforms instead of treating them as passed.
5. Run the required independent review with actual evidence. Resolve valid findings and rerun affected checks. Security, privacy, stability, reliability and applicable client-specific requirements still apply.
6. Set config/plugin-release.json's version and real timestamp. Update Claude marketplace version, CHANGELOG, README, current project state and release notes. Rebuild after source/version changes and verify exact package parity. State compatibility, migration/withdrawal instructions and remaining limits. Source changes invalidate old staged upgrade plans.
7. Inspect the exact staged file list and credential patterns. Keep client data out of unapproved Git scope. Commit with actual tool/computer/version attribution and push only under existing authorization. Verify remote SHA and private visibility. Test a fresh GitHub clone when recovery behavior changes.
8. Record inbox items as released only after verifying the published commit/release. Reference actual test/review evidence. The decision command records a claim; it does not check GitHub or publish anything itself.
9. Update the installed plugin through its native installer when authorized. Separately offer PROJECT-UPGRADES.md to existing project copies. Do not silently upgrade every client or accept new skills into their policies.

No weekly schedule or background watcher is enabled by this checklist. Run it at actual milestones and when meaningful feedback justifies a change.
