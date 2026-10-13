# Version-Timestamp: 2026-10-05 20:24:57 AST
from ..contracts import require, validate_event
from ..ledger import digest


def identity(*parts):
    return digest(list(parts))


def make_event(binding, provider, tool, timestamp, request, usage, semantics,
               mode='cumulative', model=None, duration=None):
    require(isinstance(binding, dict) and set(binding) == {
        'project_id', 'task_id', 'session_id', 'machine_id', 'tool_version', 'billing_basis'}, 'Invalid source binding')
    stream = identity(provider, binding['session_id'], request)
    event = {
        **binding, 'schema': 'blueprint-event.v1', 'event_id': identity(stream, timestamp, usage),
        'attempt_id': identity(stream, 'attempt'), 'parent_attempt_id': None,
        'stream_id': stream, 'provider': provider, 'tool': tool, 'model': model,
        'occurred_at': timestamp, 'observed_at': timestamp,
        'provenance': 'native', 'usage_mode': mode, 'usage': usage,
        'usage_semantics': semantics, 'duration_ms': duration,
        'unknown_reason': 'not_reported',
    }
    return validate_event(event)
