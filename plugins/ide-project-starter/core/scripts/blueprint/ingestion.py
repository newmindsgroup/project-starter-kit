# Version-Timestamp: 2026-10-12 17:34:00 AST
"""Explicit bounded JSONL import. Raw content is transient and never persisted."""
import importlib
import json
import os
from pathlib import Path
from .contracts import require, TOKENS
from .adapters.common import make_event
from .ledger import digest

ADAPTERS = {'codex': 'codex', 'claude-code': 'claude_code', 'ollama': 'local'}
LIMIT = 1024 * 1024


def import_jsonl(path, binding: dict, adapter: str, ledger) -> dict:
    require(adapter in ADAPTERS, 'Unsupported adapter')
    make_event(binding, 'openai', 'codex', '2000-01-01T00:00:00Z', 'binding-validation',
               dict.fromkeys(TOKENS), 'unknown')
    source = Path(path).absolute()
    require(not any(p.is_symlink() for p in (source, *source.parents)), 'Symlink source refused')
    normalizer = importlib.import_module('.adapters.' + ADAPTERS[adapter], __package__).normalize
    source_id = digest([adapter, binding['session_id'], binding['machine_id']])
    fd = os.open(source, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd, 'rb') as handle:
        stat = os.fstat(handle.fileno())
        generation = digest([stat.st_dev, stat.st_ino, getattr(stat, 'st_birthtime', None)])
        prior = ledger.cursor(source_id)
        offset = prior['offset'] if prior and prior['generation'] == generation else 0
        require(stat.st_size >= offset, 'Source truncated; preserve cursor and reconcile')
        handle.seek(offset)
        events = []; scanned = 0; ignored = 0; complete_offset = offset
        while scanned < 10000:
            record_offset = handle.tell()
            raw = handle.readline(LIMIT + 1)
            if not raw: break
            require(len(raw) <= LIMIT, f'Source record refused at byte offset {record_offset}; cursor unchanged')
            if not raw.endswith(b'\n'): break
            try:
                record = json.loads(raw)
                normalized = normalizer(record, binding)
            except (ValueError, UnicodeError, KeyError, TypeError, AttributeError):
                raise ValueError(f'Source record refused at byte offset {record_offset}; cursor unchanged') from None
            events.extend(normalized); ignored += not normalized
            scanned += 1; complete_offset = handle.tell()
        after = os.fstat(handle.fileno())
        require(after.st_size >= stat.st_size, 'Source changed destructively; cursor unchanged')
        cursor = {'source_id': source_id, 'generation': generation, 'offset': complete_offset}
        outcome = ledger.ingest_batch(events, cursor)
    return {'status': 'imported', 'inserted': sum(r['status'] == 'inserted' for r in outcome['results']),
            'duplicates': sum(r['status'] == 'duplicate' for r in outcome['results']),
            'scanned': scanned, 'ignored': ignored,
            'pending_bytes': max(0, after.st_size - complete_offset),
            'coverage': 'selected_source_only', 'automatic_collection': False}
