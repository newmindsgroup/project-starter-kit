# Version-Timestamp: 2026-10-05 20:24:57 AST
"""Session totals cannot establish per-model or native task attribution."""
from ..contracts import TOKENS, require
from .common import make_event


def normalize(source_record: dict, binding: dict) -> list:
    require(isinstance(source_record, dict), 'Invalid source record')
    if source_record.get('type') != 'event_msg': return []
    payload = source_record.get('payload')
    require(isinstance(payload, dict), 'Unsupported source format')
    if payload.get('type') != 'token_count': return []
    info = payload.get('info')
    if info is None: return []
    require(isinstance(info, dict) and isinstance(info.get('total_token_usage'), dict), 'Unsupported usage format')
    usage = {name: info['total_token_usage'].get(name) for name in TOKENS}
    return [make_event(binding, 'openai', 'codex', source_record.get('timestamp'),
                       'session-total', usage, 'codex-inclusive')]
