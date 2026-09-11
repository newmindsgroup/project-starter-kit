# Naming conventions

Version-Timestamp: 2026-09-11 14:52:59 AST

These rules apply to the kit and to every project it generates. `tests/test_conventions.py` enforces them.

## The rule

Every file and folder name is lowercase kebab-case ASCII, with two exceptions.

1. **Root-level documents may be uppercase.** README.md, CHANGELOG.md, AUTHORS.md and START-HERE.md here, and PROJECT.md and QUALITY.md in a generated project. Uppercase at the root marks a file as read-first. The convention stops at the root.
2. **Names a tool requires keep their exact case at any depth.** SKILL.md is fixed by the Agent Skills specification. AGENTS.md and CLAUDE.md are agent entry points found by exact name. README.md is rendered by GitHub in any folder.

Python modules use snake_case, because Python cannot import a hyphenated module name. Dated records put the ISO date first, for example `2026-09-08-before-learning-cli.md`.

## What keeps its original name

Frozen evidence is never renamed, because its paths are part of what it records: `examples/`, `validation/`, `research/`, `recovery-evaluation/`, `experiments/`, the immutable learning records under `memory/learning/intake/` and the dated session notes under `memory/sessions/`. Changelog history describes names as they were.

## Renaming safely

A case-only rename, such as INDEX.md to index.md, is not a no-op on macOS and Windows. Their default filesystems are case-insensitive, so a check for index.md succeeds while only INDEX.md is on disk, and some tools then skip the rename. Rename through a temporary name or with `git mv`, and confirm the exact name from a directory listing rather than an existence check. `scripts/migrate_layout.py` does this for projects created before 0.7.0. In a Git repository on those systems, also record the rename explicitly with `git rm --cached OLD` and `git add NEW`, because `git add -A` does not record a change of case alone.

## Line endings

Starter records are verified by the SHA-256 of their exact bytes. The generated `.gitattributes` marks them `-text`, so Git never converts their line endings on checkout.
