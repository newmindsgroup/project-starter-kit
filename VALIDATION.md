# Release validation and acceptance limits

Version-Timestamp: 2026-09-10 18:27:14 AST

Version 0.6.0 is a supervised pilot. The generic setup inspector and the existing new/adopt/resume helpers are included. Framework detection is advisory.

The private source retains raw test and review evidence. It is not copied into this public release because it can contain development paths and account metadata. This public summary reports outcomes without exposing those records.

Release preparation checks cover the Python suite, deterministic package parity, public-export tests, local documentation links, targeted private-pattern scans, plugin manifest validation and desktop/mobile README rendering. The source suite passed all 199 tests, including eight public-export tests.

CLI help was checked with Codex 0.149.1 and Claude Code 2.1.261. Desktop and mobile README previews were inspected; all three graphics loaded and the mobile page fit its viewport.

Earlier wizard verification passed 191 source tests. Its independent review returned Claude Fable 5.1; follow-up inspector/package tests passed after the truncated-directory recovery fix. The public publication review returned Claude Opus 5. Two follow-up exporter regressions were demonstrated failing and then fixed; all 10 focused export tests passed. The full 199-test result predates those two additions. Eight package tests and one adoption rehearsal from the public staging layout passed.

Still unverified: an independent non-developer completing onboarding without assistance, a physical second computer, Windows initialization, all possible filesystems, and complete sensitive-data classification. A same-machine helper or clone rehearsal is not proof of those outcomes.

The package adds no background observer, network API integration, automatic publication or automatic project upgrades. Existing project tests, source access and backup arrangements remain project responsibilities.
