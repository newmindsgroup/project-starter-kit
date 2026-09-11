# Release validation and acceptance limits

Version-Timestamp: 2026-09-11 16:24:39 AST

Version 0.7.2 is a supervised pilot. It renames nested starter records to lowercase, adds a migration for projects created with 0.6, cleans up generated Markdown, and adds line-ending protection for starter records. The setup inspector and the new, adopt and resume helpers from 0.6.0 are unchanged in purpose.

0.7.1 corrects a packaging defect in 0.7.0: the plugin package omitted the new .gitattributes and .editorconfig templates, so projects set up through the plugin did not receive them. The adoption check from the anonymous public clone caught it. Tests now adopt and start projects using only the packaged scripts, and require every template and skill file to be packaged. The migration also reports case-only renames that Git has not recorded, a trap on macOS and Windows.

0.7.2 makes the upgrade helper refuse to stage while Git still records an old name. On macOS, committing before recording the renames and then resetting the checkout wrote an old name back to disk, after which one renamed file silently dropped out of a repository. The file was recovered intact from disk; the new check makes the same sequence stop before upgrading.

The private source keeps the raw test and review evidence. It is not copied here, because it can contain development paths and account metadata. This summary reports outcomes only.

## Checks run for this release

- The source suite passed 236 tests on macOS. One test, which needs a case-sensitive filesystem, was skipped there.
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
