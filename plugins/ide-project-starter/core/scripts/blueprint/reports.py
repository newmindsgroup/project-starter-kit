# Version-Timestamp: 2026-10-12 17:34:00 AST
"""Bounded measured totals and explicit missing evidence. No fabricated billing."""
from datetime import datetime, timezone
from .contracts import TOKENS


def report(ledger, project_id: str, filters: dict) -> dict:
    rows = ledger.query(project_id, filters)
    def totals(selected):
        result = {}
        for name in sorted(TOKENS):
            values = [r['effective_usage'][name] for r in selected]
            unknown = sum(v is None for v in values)
            subtotal = sum(v for v in values if v is not None)
            result[name] = {'total': None if unknown or not selected else subtotal,
                            'known_subtotal': subtotal, 'unknown_events': unknown}
        return result
    semantics = sorted({r['usage_semantics'] for r in rows})
    grouped = {key: totals([r for r in rows if r['usage_semantics'] == key]) for key in semantics}
    usage = totals(rows)
    if len(semantics) > 1 or 'unknown' in semantics:
        for value in usage.values():
            value.update(total=None, known_subtotal=None, reason='incompatible_or_unknown_semantics')
    times = [r['occurred_at'] for r in rows]
    return {'schema': 'blueprint-report.v1', 'Version-Timestamp': datetime.now(timezone.utc).isoformat(),
            'project_id': project_id, 'filters': filters, 'event_count': len(rows),
            'session_count': len({r['session_id'] for r in rows}),
            'attempt_count': len({r['attempt_id'] for r in rows}),
            'unassigned_events': sum(r['task_id'] is None for r in rows),
            'usage': usage, 'usage_by_semantics': grouped, 'actual_cost': None, 'human_time': None,
            'coverage': {'collection': 'selected_source_only' if rows else 'no_data',
                         'billing': 'unreconciled', 'human_attention': 'untracked'},
            'latest_event_at': max(times, key=lambda t: datetime.fromisoformat(t.replace('Z', '+00:00'))) if times else None,
            'automatic_collection': False,
            'notes': ['Cache and reasoning fields may be included subcategories; do not sum all fields.',
                      'Selected imports do not establish complete project coverage or paid charges.']}
