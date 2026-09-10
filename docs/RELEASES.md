# Releases and drift prevention

Version-Timestamp: 2026-09-10 18:27:14 AST

The private development repository is the single source of truth. The public repository contains generated releases, including public-facing documentation maintained in that private source. The recorded source commit identifies provenance; it does not make private history accessible.

## What the manifest proves

release-manifest.json lists SHA-256 digests of raw file bytes using exact, case-sensitive relative paths. It excludes itself to avoid self-reference. Mode bits are not hashed. The release uses .gitattributes to disable Git line-ending conversion, and exported paths must be normalized and free of traversal or case collisions.

Hashes detect accidental changes when compared with a trusted manifest. They are not a cryptographic signature, proof of authorship or protection against someone replacing both files and manifest.

## Verify a checkout

Run this read-only check from the public repo root using Python 3.10 or newer:

```sh
python3 - <<'PY'
import hashlib, json
from pathlib import Path
root = Path('.')
manifest = json.loads((root / 'release-manifest.json').read_text())
expected = manifest['files']
actual = set()
for p in root.rglob('*'):
    name = p.as_posix()
    if name == '.git' or name.startswith('.git/'):
        continue
    if p.is_symlink():
        raise SystemExit('Symlink found: ' + name)
    if p.is_file():
        actual.add(name)
if actual != set(expected) | {'release-manifest.json'}:
    raise SystemExit('File list differs; use a clean checkout')
for name, wanted in expected.items():
    p = Path(name)
    if p.is_absolute() or '..' in p.parts:
        raise SystemExit('Unsafe manifest path')
    if hashlib.sha256(p.read_bytes()).hexdigest() != wanted:
        raise SystemExit('Changed file: ' + name)
print('Verified', manifest['version'], manifest['source_commit'])
PY
```

Extra local files also produce a mismatch. Use a clean tooling checkout for verification; keep environments outside it. A passing check validates recorded file bytes, not runtime compatibility or source permissions.

## Maintainer release sequence

1. Reconcile feedback and changes into the private source, including public documentation templates. Run relevant tests, package checks, content/visual checks and independent review.
2. Commit that source. Export from the exact commit into a new staging directory; the exporter reads Git objects, not mutable working files, and does not contact GitHub.
3. Verify every package file against its package manifest and every public file against its release manifest. Review the public file list and content for private material.
4. For an update, first verify the current public checkout against the last trusted release. If it differs, preserve the changes and reconcile them upstream. Do not reset or overwrite unexpected public work.
5. Compare old and new release manifests. Review additions, modifications and removals. Apply that reviewed replacement to a clean release branch, removing only obsolete tracked distribution files.
6. Publish through an authorized Git workflow. Verify the remote commit, anonymous access and a fresh clone. Record the release evidence privately.

The exporter is create-only and does not update or delete files in an existing public checkout. Future releases use a new staging directory plus the reviewed Git diff above. No unattended publisher, automatic merge or team-project upgrade is enabled.

The plugin identifier stays ide-project-starter, and its entry skill stays project-starter. Existing project helper copies require their own reviewed upgrade.
