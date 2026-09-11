#!/usr/bin/env python3
# Version-Timestamp: 2026-09-10 13:12:49 AST
"""Read-only setup routing for an agent-assisted, project-first wizard."""
import argparse
import json
import os
from pathlib import Path
import sys
from project_learning import Invalid, Store, require, unique_object
from start_project import workspace_root

BASE = Path(__file__).resolve().parents[1]
ENTRY_LIMIT = 512
JSON_LIMIT = 128 * 1024


def inspect_project(project, scope='project', tool='current'):
    require(scope in {'project', 'tool'}, 'Choose project or tool setup')
    require(tool in {'current', 'codex', 'claude', 'both'}, 'Choose a supported agent tool')
    root = workspace_root(project)
    store = Store(root)
    diagnostics = []

    def problem(path):
        message = f'Cannot safely inspect {path}; review this input before dependent setup.'
        if message not in diagnostics:
            diagnostics.append(message)

    def probe(path):
        try:
            candidate = store.path(path)
            return candidate.exists()
        except (Invalid, OSError):
            problem(path)
            return None

    def record(path):
        try:
            data = store.read(path)
            require(len(data) <= JSON_LIMIT, 'Manifest too large')
            value = json.loads(data, object_pairs_hook=unique_object)
            require(isinstance(value, dict), 'Manifest must be an object')
            return value
        except (Invalid, OSError, ValueError, UnicodeError, RecursionError):
            problem(path)
            return None

    # Read a bounded set of top-level names, never source text or sibling folders.
    names = set()
    directory_names = set()
    truncated = False
    with os.scandir(root) as entries:
        for index, entry in enumerate(entries):
            if index >= ENTRY_LIMIT:
                truncated = True
                break
            names.add(entry.name)
            if entry.is_dir(follow_symlinks=False):
                directory_names.add(entry.name)
    if truncated:
        diagnostics.append('Top-level inventory is partial; the agent must resolve layout before setup.')

    # Only fixed metadata paths are probed, including when inventory is truncated.
    starter_exists = probe('.starter')
    identity = probe('project.json')
    runtime = probe('.starter/project_memory.py')
    receipt_exists = probe('.starter/installation.json')
    pending_exists = probe('.starter/adoption-pending.json')
    checkpoint = probe('memory/checkpoints/0001.json')
    metadata_unsafe = None in (starter_exists, identity, runtime, receipt_exists, pending_exists, checkpoint)
    receipt = record('.starter/installation.json') if receipt_exists else None
    pending = record('.starter/adoption-pending.json') if pending_exists else None
    identity_valid = False
    if identity:
        try:
            store.manifest()
            identity_valid = True
        except (Invalid, OSError, ValueError, TypeError, KeyError, AttributeError, RecursionError):
            problem('project.json')
            metadata_unsafe = True
    for value, present, schema, path in [
        (receipt, receipt_exists, 'installation.v1', '.starter/installation.json'),
        (pending, pending_exists, 'adoption-pending.v1', '.starter/adoption-pending.json'),
    ]:
        if present and (not value or value.get('schema') != schema or
                        not isinstance(value.get('plan_id'), str) or
                        len(value['plan_id']) != 64 or
                        any(c not in '0123456789abcdef' for c in value['plan_id'])):
            metadata_unsafe = True
            problem(path)
    if receipt and pending and receipt.get('plan_id') != pending.get('plan_id'):
        metadata_unsafe = True
        diagnostics.append('Installation and pending adoption refer to different plans; reconcile them.')

    if root == BASE:
        workflow = 'reconcile'
        diagnostics.append('This is the toolkit source. Select the intended application project instead.')
    elif metadata_unsafe:
        workflow = 'reconcile'
    elif identity_valid and runtime and receipt and checkpoint:
        workflow = 'resume'
    elif identity_valid or runtime or receipt_exists or pending_exists or starter_exists:
        workflow = 'recover'
    else:
        workflow = 'adopt' if names or truncated else 'new'

    hints = set()
    evidence = []
    package_exists = probe('package.json')
    if package_exists:
        package = record('package.json')
        if package is not None:
            dependencies = set()
            valid = True
            for field in ('dependencies', 'devDependencies', 'peerDependencies'):
                group = package.get(field, {})
                if not isinstance(group, dict):
                    valid = False
                    problem('package.json')
                    break
                dependencies.update(group)
            if valid:
                if 'expo' in dependencies:
                    hints.add('mobile-expo')
                elif 'react-native' in dependencies:
                    hints.add('mobile-react-native')
                if 'electron' in dependencies or '@tauri-apps/api' in dependencies:
                    hints.add('desktop')
                if dependencies & {'next', 'nuxt', '@sveltejs/kit', '@angular/core', 'astro'}:
                    hints.add('web')
                elif dependencies & {'react', 'vue', 'svelte'} and not hints:
                    hints.add('web')
                if package.get('workspaces'):
                    hints.add('mixed')
                if hints:
                    evidence.append('package.json: recognized dependency names or workspaces only')
    for filename, hint in [('Package.swift', 'apple-native'), ('build.gradle', 'android-or-jvm'),
                           ('build.gradle.kts', 'android-or-jvm'), ('pubspec.yaml', 'flutter-or-dart')]:
        if probe(filename):
            hints.add(hint)
            evidence.append(filename + ': filename only, contents not interpreted')
    if any(name.endswith(('.xcodeproj', '.xcworkspace')) for name in directory_names):
        hints.add('apple-native')
        evidence.append('Apple project directory marker: filename only')
    profile = 'mixed' if len(hints) > 1 or 'mixed' in hints else next(iter(hints), 'generic-development')
    if scope == 'tool':
        workflow = 'tool-setup'
    guidance = {
        'new': 'Use the existing new-project preview/apply workflow, then verify a saved checkpoint.',
        'adopt': 'Use the existing adoption preview/apply/finish workflow, preserving all existing work.',
        'resume': 'Inspect trusted helper provenance and verify resume; these markers alone do not prove integrity.',
        'recover': 'Recover the matching partial setup or existing state. Do not create another identity.',
        'reconcile': 'Resolve the reported metadata or target conflict before running setup helpers.',
        'tool-setup': 'Follow tool installation guidance after an explicit scoped setup request. This inspector changes no settings.',
    }
    return {
        'schema': 'setup-inspection.v1', 'project': str(root), 'scope': scope, 'tool': tool,
        'workflow': workflow, 'profile_hint': profile, 'compatibility': 'not_verified',
        'evidence': sorted(evidence), 'diagnostics': diagnostics,
        'inventory_truncated': truncated, 'writes_performed': False,
        'setup_complete': False, 'requires_verification': True,
        'next_action': guidance[workflow],
        'agent_guide': 'docs/setup-wizard.md',
        'questions_policy': 'Infer from the conversation first. Ask only unresolved purpose, target or sharing questions. Never ask the user to prepare JSON.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    inspect = commands.add_parser('inspect', help='Inspect only; do not change the project or agent setup')
    inspect.add_argument('--project', required=True)
    inspect.add_argument('--scope', choices=['project', 'tool'], default='project')
    inspect.add_argument('--tool', choices=['current', 'codex', 'claude', 'both'], default='current')
    args = parser.parse_args()
    try:
        print(json.dumps(inspect_project(args.project, args.scope, args.tool), indent=2))
        return 0
    except (Invalid, OSError, ValueError, TypeError, RuntimeError) as error:
        detail = str(error) if isinstance(error, Invalid) else 'Project is inaccessible or has invalid metadata; inspect the selected folder.'
        print('Setup inspection failed: ' + detail, file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
