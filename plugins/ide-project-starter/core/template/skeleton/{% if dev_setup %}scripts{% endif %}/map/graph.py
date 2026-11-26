#!/usr/bin/env python3
# Version-Timestamp: 2026-11-26 11:08:42 AST
"""Build this project's local code graph with its own pinned graphify runtime.

  python3 scripts/map/graph.py lock WHEEL_DIR [--replace]
      Write scripts/map/requirements.txt from wheels you downloaded and vetted.
      Standard library only, offline.
  .local/tools/graphify-X.Y.Z/bin/python -I scripts/map/graph.py build
      Write graphify-out/graph.json and GRAPH_REPORT.md with the network blocked.
      -I keeps user site-packages and PYTHON* variables out of the run.

build refuses to run unless its interpreter is the virtual environment
.local/tools/graphify-X.Y.Z of this checkout (or of the main checkout when this
is a Git worktree), started with -I, graphify is imported from inside that
environment and the installed graphifyy is exactly the locked version.
The network block is applied when this file is imported, so it also covers
worker processes that graphify starts (spawn and forkserver re-import it).
It never follows symlinks, skips local tools and generated output, sets no hooks
and makes no model calls. Setup and limits: docs/map/README.md.
"""
import argparse
import hashlib
import importlib.util
import os
from pathlib import Path
import platform
import re
import socket
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
LOCK = Path(__file__).resolve().parent / 'requirements.txt'
EXCLUDES = ['.local', '.git', '.starter', '.starter-work', '.starter-tools', '.agents', '.claude', '.codex',
            'graphify-out', 'node_modules', '.venv', 'venv', 'dist', 'build', 'coverage', '.next']
WHEEL = re.compile(r'^(?P<name>[A-Za-z0-9_.]+)-(?P<version>[0-9A-Za-z.!+]+)-.+\.whl$')
PIN = re.compile(r'^graphifyy==(?P<version>[0-9A-Za-z.!+]+)[ \t]+--hash=sha256:(?P<hash>[0-9a-f]{64})[ \t]*$', re.M)


class Refused(Exception):
    pass


def block_network():
    def refuse(*_args, **_kwargs):
        raise OSError('network access is blocked while the code map builds')
    socket.socket.connect = refuse
    socket.socket.connect_ex = refuse
    socket.create_connection = refuse
    socket.getaddrinfo = refuse


# At import time, not inside build(): graphify's process-pool workers re-import
# this file as their main module, so each of them is blocked too.
block_network()


def pinned():
    text = LOCK.read_text(encoding='utf-8') if LOCK.is_file() else ''
    match = PIN.search(text)
    if not match:
        raise Refused('scripts/map/requirements.txt has no hash-locked graphifyy line; follow docs/map/README.md first')
    return match.group('version')


def lock(wheel_dir, replace):
    folder = Path(wheel_dir).resolve()
    if not folder.is_dir():
        raise Refused(f'{wheel_dir} is not a folder of downloaded wheels')
    others = [p.name for p in folder.iterdir() if p.is_file() and not p.name.endswith('.whl')]
    if others:
        raise Refused('only wheels can be locked; remove or vet these first: ' + ', '.join(sorted(others)))
    rows = {}
    for wheel in sorted(folder.glob('*.whl')):
        match = WHEEL.match(wheel.name)
        if not match or wheel.is_symlink():
            raise Refused('unexpected wheel file: ' + wheel.name)
        name = re.sub(r'[-_.]+', '-', match.group('name')).lower()
        line = f"{name}=={match.group('version')} --hash=sha256:{hashlib.sha256(wheel.read_bytes()).hexdigest()}"
        if name in rows and rows[name] != line:
            raise Refused(f'two different wheels for {name}; keep the one for this platform only')
        rows[name] = line
    if 'graphifyy' not in rows:
        raise Refused('no graphifyy wheel in ' + wheel_dir)
    current = LOCK.read_text(encoding='utf-8') if LOCK.is_file() else ''
    if PIN.search(current) and not replace:
        raise Refused('requirements.txt already locks a version; pass --replace after vetting the new one')
    graphify = rows.pop('graphifyy')
    text = ('# Hash lock for the code map runtime, written by `python3 scripts/map/graph.py lock`.\n'
            f'# Platform {platform.system()} {platform.machine()}, Python {platform.python_version()}.\n'
            '# Check the graphifyy hash against your vetting log before installing. See docs/map/README.md.\n'
            + graphify + '\n' + ''.join(rows[n] + '\n' for n in sorted(rows)))
    LOCK.write_text(text, encoding='utf-8')
    print(f'graph.py: locked {len(rows) + 1} wheels in scripts/map/requirements.txt ({graphify.split(" ")[0]})')


def main_checkout(root):
    try:
        common = subprocess.run(['git', '-C', str(root), 'rev-parse', '--path-format=absolute', '--git-common-dir'],
                                capture_output=True, text=True, check=True, timeout=30).stdout.strip()
        return Path(common).resolve().parent
    except (OSError, subprocess.SubprocessError):
        return root


def check_runtime(root, version):
    prefix = Path(sys.prefix)
    if sys.prefix == sys.base_prefix:
        raise Refused('run build from the pinned virtual environment, not a system Python')
    if prefix.name != f'graphify-{version}' or prefix.parent.name != 'tools' or prefix.parent.parent.name != '.local':
        raise Refused(f'interpreter {sys.executable} is not .local/tools/graphify-{version}')
    owner = prefix.parent.parent.parent.resolve()
    if owner not in {root.resolve(), main_checkout(root)}:
        raise Refused('the runtime belongs to another project; build only with this project\'s own runtime')
    if not sys.flags.isolated:
        raise Refused('start the runtime with -I, as docs/map/README.md shows')
    spec = importlib.util.find_spec('graphify')
    if spec is None or not spec.origin:
        raise Refused('graphify is not installed in the pinned runtime')
    if not Path(spec.origin).resolve().is_relative_to(prefix.resolve()):
        raise Refused(f'graphify is imported from {spec.origin}, outside the pinned runtime')
    from importlib.metadata import PackageNotFoundError, version as installed
    try:
        found = installed('graphifyy')
    except PackageNotFoundError:
        raise Refused('graphifyy is not installed in the pinned runtime') from None
    if found != version:
        raise Refused(f'installed graphifyy {found} differs from the locked {version}')


def build(root):
    for key in [k for k in os.environ if k.startswith('GRAPHIFY_')]:
        del os.environ[key]
    os.environ['GRAPHIFY_SKIP_HOOK'] = '1'
    version = pinned()
    check_runtime(root, version)
    try:
        from graphify.analyze import god_nodes, suggest_questions, surprising_connections
        from graphify.build import build_from_json
        from graphify.cluster import cluster, score_all
        from graphify.detect import detect
        from graphify.export import to_json
        from graphify.extract import extract
        from graphify.report import generate
    except ImportError as error:
        raise Refused(f'graphifyy {version} does not offer the API this wrapper uses ({error}); review the wrapper before upgrading') from None
    found = detect(root, follow_symlinks=False, google_workspace=False, extra_excludes=EXCLUDES, gitignore=True)
    code = [Path(f) for f in found.get('files', {}).get('code', [])]
    ast = extract(code, cache_root=root, root=root) if code else {'nodes': [], 'edges': []}
    extraction = {'nodes': ast['nodes'], 'edges': ast['edges'], 'hyperedges': [], 'input_tokens': 0, 'output_tokens': 0}
    graph = build_from_json(extraction, root=root)
    communities = cluster(graph)
    labels = {cid: f'Community {cid}' for cid in communities}
    try:
        sha = subprocess.run(['git', '-C', str(root), 'rev-parse', '--verify', '-q', 'HEAD'], capture_output=True,
                             text=True, timeout=30).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        sha = None
    out = root / 'graphify-out'
    out.mkdir(exist_ok=True)
    report = generate(graph, communities, score_all(graph, communities), labels, god_nodes(graph),
                      surprising_connections(graph, communities), found, {'input': 0, 'output': 0}, root.name,
                      suggested_questions=suggest_questions(graph, communities, labels), built_at_commit=sha)
    (out / 'GRAPH_REPORT.md').write_text(report, encoding='utf-8')
    to_json(graph, communities, str(out / 'graph.json'), force=True, built_at_commit=sha, community_labels=labels)
    print(f'graph.py: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} links, {len(communities)} communities in graphify-out/')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('lock', help='write requirements.txt from downloaded wheels')
    p.add_argument('wheels')
    p.add_argument('--replace', action='store_true', help='replace an existing lock after vetting the new version')
    sub.add_parser('build', help='build the graph of the checkout that holds this script')
    args = parser.parse_args(argv)
    try:
        if args.command == 'lock':
            lock(args.wheels, args.replace)
        else:
            build(ROOT)
        return 0
    except Refused as error:
        print('graph.py: ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
