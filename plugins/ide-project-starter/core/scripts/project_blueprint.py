#!/usr/bin/env python3
# Version-Timestamp: 2026-10-13 08:14:00 AST
"""Explicit local Project Blueprint commands. No observer or provider execution."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sqlite3
import sys
from blueprint.contracts import project_id, require
from blueprint.human_time import HumanTimer, KINDS
from blueprint.ingestion import import_jsonl
from blueprint.ledger import Ledger
from blueprint.reports import report


def save_private(path, value):
    target = Path(path).absolute()
    require(not any(p.is_symlink() for p in (target, *target.parents)), 'Symlink export refused')
    data = (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as handle:
        handle.write(data); handle.flush(); os.fsync(handle.fileno())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', required=True, help='Explicit private local storage path, outside sync and Git')
    parser.add_argument('--project-id', required=True, help='Existing canonical project UUID; does not create a new project')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('status')
    p = sub.add_parser('report'); p.add_argument('--task-id')
    p = sub.add_parser('ingest')
    p.add_argument('--source', required=True)
    p.add_argument('--adapter', choices=['codex', 'claude-code', 'ollama'], required=True)
    p.add_argument('--session-id', required=True, help='Opaque SHA256 identity for this selected native session')
    p.add_argument('--machine-id', required=True, help='Opaque SHA256 machine identity')
    p.add_argument('--tool-version', required=True)
    p.add_argument('--task-id', help='Only when the entire selected source belongs to this task')
    p.add_argument('--billing-basis', choices=['unknown', 'api', 'subscription', 'local'], default='unknown')
    p = sub.add_parser('export'); p.add_argument('--output', required=True, help='Approved private backup destination; create-only')
    p.add_argument('--human-history',action='store_true',help='Explicitly include scoped human intervals and amendment history')
    p = sub.add_parser('restore'); p.add_argument('--input', required=True)
    p = sub.add_parser('timer')
    p.add_argument('action', choices=['start','pause','resume','switch','stop','summary','list','confirm','correct','void'])
    p.add_argument('--user-id', required=True, help='Opaque UUID4 for the person; no name')
    p.add_argument('--task-id')
    p.add_argument('--activity', choices=sorted(KINDS))
    p.add_argument('--at', help='Explicit timestamp, or current UTC time')
    p.add_argument('--interval-id')
    p.add_argument('--previous-revision')
    p.add_argument('--reason')
    p.add_argument('--start-at')
    p.add_argument('--end-at')
    args = parser.parse_args()
    try:
        identity = project_id(args.project_id)
        database = Path(args.database).absolute()
        if args.command == 'status' and not database.exists():
            result = {'status': 'not_configured', 'project_id': identity, 'automatic_collection': False}
        elif args.command == 'restore':
            source = Path(args.input)
            require(source.stat().st_size <= 16 * 1024 * 1024, 'Backup exceeds import limit')
            packet = json.loads(source.read_bytes())
            require(isinstance(packet, dict), 'Invalid backup object')
            require(packet.get('project_id') == identity, 'Backup belongs to another project')
            Ledger.restore(database, packet)
            result = {'status': 'restored', 'project_id': identity, 'automatic_collection': False}
        else:
            require(args.command in ('ingest', 'timer') or database.is_file(), 'Ledger absent; configure explicit private storage first')
            ledger = Ledger(database, read_only=args.command in ('report', 'status', 'export') or args.command=='timer' and args.action in ('summary','list'))
            if args.command in ('report', 'status'):
                filters = {'task_id': args.task_id} if getattr(args, 'task_id', None) else {}
                result = report(ledger, identity, filters)
            elif args.command == 'timer':
                timer = HumanTimer(ledger, identity)
                if args.action == 'summary':
                    result = timer.summary(args.user_id)
                elif args.action=='list':
                    result={'intervals':timer.intervals(args.user_id)}
                elif args.action in ('confirm','correct','void'):
                    require(args.interval_id is not None and args.previous_revision is not None and args.reason is not None,'Revision identity and reason required')
                    replacement=None
                    if args.action=='correct':
                        require(args.task_id is not None and args.activity is not None and args.start_at is not None and args.end_at is not None,'Correction bounds, task and activity required')
                        replacement={'task_id':args.task_id,'activity_kind':args.activity,'start_at':args.start_at,'end_at':args.end_at}
                    result=timer.amend(args.user_id,args.interval_id,args.previous_revision,args.action,
                        args.at or datetime.now(timezone.utc).isoformat(),args.reason,replacement)
                else:
                    require(args.task_id is not None, 'Task identity required')
                    result = timer.transition(args.user_id,args.task_id,args.action,
                        args.at or datetime.now(timezone.utc).isoformat(),args.activity or 'supervising')
            elif args.command == 'ingest':
                binding = {'project_id': identity, 'task_id': args.task_id,
                           'session_id': args.session_id, 'machine_id': args.machine_id,
                           'tool_version': args.tool_version, 'billing_basis': args.billing_basis}
                result = import_jsonl(args.source, binding, args.adapter, ledger)
            else:
                save_private(args.output, ledger.export_history(identity) if args.human_history else ledger.export(identity))
                result = {'status': 'exported', 'project_id': identity, 'backup_contains': 'usage_and_human_history' if args.human_history else 'usage_metadata_only'}
        print(json.dumps(result, indent=2, allow_nan=False))
        return 0
    except ValueError as error:
        message = str(error)
        if message.startswith('Source record refused at byte offset '):
            print(message, file=sys.stderr)
        else:
            print('Blueprint operation refused. Inspect source format, identity and private storage; originals preserved.', file=sys.stderr)
        return 1
    except (OSError, sqlite3.Error, KeyError, TypeError):
        print('Blueprint operation refused. Inspect source format, identity and private storage; originals preserved.', file=sys.stderr)
        return 1


if __name__ == '__main__': sys.exit(main())
