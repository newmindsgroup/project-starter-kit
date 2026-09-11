# What lives where

Version-Timestamp: 2026-09-08T17:05:39.134927-04:00

This policy applies to both new projects and existing-project adoption. Storage follows ownership, audience and recovery needs. Google Drive and OneDrive are examples of source storage, not mandatory destinations for every file.

| Location | Keep here | Recovery meaning |
| --- | --- | --- |
| Approved client cloud folder or original provider | Original meetings, recordings, transcripts, contacts, contracts, client-supplied documents, large assets and native Google/Microsoft documents | This is the source of record. Access, retention and backup follow the client's policy. A Git clone does not recover it. |
| Approved project repository | Application code or business deliverables appropriate for that repo's audience; project brief; reviewed context summaries; source register; decisions; checkpoints; approved learning records; project instructions; helper scripts; validation commands and dependency definitions | Committed and pushed records travel with a clone. The repo must contain enough approved context to resume meaningfully and identify what still needs source access. |
| Local machine outside synced folders | Disposable caches, virtual environments, dependency installs, render scratch and private working files not approved for cloud sync | Recreate disposable tools from documented setup instructions. Local-only files need a separate approved backup if they are valuable. |
| Credential manager or approved secret store | Tokens, passwords, private keys and other secrets | Authenticate on the new machine through the approved provider. Secrets never belong in committed memory or ordinary synced project folders. |

A private repo is not automatic approval to copy client material. Repo membership can differ from Drive membership. Public or client-shared code repositories must not contain internal memory unless every included item is approved for that audience. Use an approved separate private project-records repository when necessary; document the code-to-records relationship and open the records workspace for its workflows.

## The bridge between cloud context and portable memory

Keep a source register in context/index.md. For each relevant source record its provider link or source-relative location, owner/audience, date/version, read coverage, what it supports, and how to refresh it. Do not store signed access URLs or credential-bearing links. Record facts, proposals, conflicts and unknowns distinctly.

Put a concise approved summary in the project repo. If exact content is needed for offline work, include a specifically approved, dated and redacted text snapshot with provenance. The snapshot is a copy, not a new master. Do not duplicate raw transcripts, contacts or contracts merely to make the repo feel complete.

The current client-link helper hashes selected text under a client ancestor. It does not follow Drive URLs, retrieve native documents, or resolve arbitrary sibling workspaces. For a code checkout outside the cloud client tree, use approved repo-local summaries/snapshots and source-register links. Their local changes can be hashed; changes to the remote original require explicit retrieval/review. A detached client-linked project reports unavailable rather than pretending that sources are current.

## Setup and adoption checklist

Before writing or uploading, identify the cloud-source location and audience, the actual Git root and repo audience, the memory destination, approved summary/snapshot scope, and a local tooling destination. Unknown sharing is unresolved, not private. Keep adoption plans in an approved private location because they contain current context and original instruction text. Never place the new project repo around the entire client archive.

The CLI accepts an explicit parent workspace and child project target. That workspace may be a local development directory instead of a cloud folder. Rendering scratch is created under that selected workspace; do not select a shared/synced location if the content is not approved there. .gitignore prevents Git inclusion only. It does not prevent Drive or OneDrive synchronization.

Before a handoff, save a checkpoint, review the exact Git upload scope and commit/push when authorized. A checkpoint alone does not update GitHub. On the next machine, clone the repo, authenticate to approved sources, recreate local tools and run resume. Report unavailable originals and stale snapshots. Test recovery with source access unavailable as well as available.

This starter kit's private GitHub backup stores the kit. Every client project needs its own explicit repository and source backup arrangement. Never infer full project backup from the kit's backup.
