# Release validation and acceptance limits

Version-Timestamp: 2026-09-11 16:04:41 AST

Version 0.7.0 is a supervised pilot. It renames nested starter records to lowercase, adds a migration for projects created with 0.6, cleans up generated Markdown, and adds line-ending protection for starter records. The setup inspector and the new, adopt and resume helpers from 0.6.0 are unchanged in purpose.

The private source keeps the raw test and review evidence. It is not copied here, because it can contain development paths and account metadata. This summary reports outcomes only.

## Checks run for this release

- The source suite passed 231 tests on macOS. One test, which needs a case-sensitive filesystem, was skipped there.
- Continuous integration passed the same suite on Linux with Python 3.10 and Python 3.14. On Linux the case-sensitive test ran.
- The learning-code import gate, learning-record validation and plugin package parity checks all passed.
- A freshly generated project has no nested uppercase names and no double blank lines in its Markdown.
- Every relative link in the kit's live documentation resolves with exact letter case.
- A fictional project was adopted using only the scripts in this public release, from an anonymous clone. Resume recovered its state, and its original files were preserved.

## Independent review

An independent review before release found six defects in the new migration and adoption paths, two of them release blockers. All six are fixed and covered by regression tests. A second independent review verified the fixes by reproducing each original failure, including crash and tamper tests. It found one remaining gap and three minor points, which were then fixed.

## Still unverified

The following have not been demonstrated:

- an independent non-developer completing onboarding without assistance
- a physical second computer
- Windows initialization
- every possible filesystem
- complete classification of sensitive data

A helper or clone rehearsal on the same machine does not prove those outcomes.

The package adds no background observer, network API integration, automatic publication or automatic project upgrades. Existing project tests, source access and backup arrangements remain project responsibilities.
