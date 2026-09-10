# Safety and reporting

Version-Timestamp: 2026-09-10 18:27:14 AST

Run setup only in a selected, authorized project. Keep one writer per target. Preserve existing files, identity and interrupted plans. Do not remove conflict markers or change hashes to make an operation pass.

The helpers enforce bounded reads, selected path restrictions and create-only writes. They do not provide a complete secret scanner, an access-control boundary against a malicious local user or a distributed transaction across cloud-synced machines.

For a suspected vulnerability, avoid posting exploit details, credentials or private project material in a public issue. Ask the maintainer for a private reporting channel before sharing sensitive evidence. For ordinary bugs, a small fictional reproduction and version information are sufficient.

Dependencies are pinned by version, not by artifact hash. Review their terms and suitability before sensitive or production use.
