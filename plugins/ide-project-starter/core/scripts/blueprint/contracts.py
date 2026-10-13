# Version-Timestamp: 2026-10-05 20:24:57 AST
"""Strict durable metadata. No prompt, content, path or credential fields."""
from copy import deepcopy
from datetime import datetime
import re
import uuid

TOKENS = {'input_tokens', 'output_tokens', 'cached_input_tokens',
          'cache_write_input_tokens', 'reasoning_output_tokens'}
FIELDS = {'schema', 'event_id', 'project_id', 'task_id', 'session_id', 'attempt_id',
          'parent_attempt_id', 'machine_id', 'provider', 'model', 'tool', 'tool_version',
          'occurred_at', 'observed_at', 'billing_basis', 'provenance', 'usage_mode',
          'stream_id', 'usage', 'usage_semantics', 'duration_ms', 'unknown_reason'}
REASONS = {'not_reported', 'source_unavailable', 'format_drift', 'unattributed'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def opaque(value):
    require(isinstance(value, str) and re.fullmatch(r'[a-f0-9]{64}', value), 'Invalid opaque identity')
    return value


def project_id(value):
    require(isinstance(value, str), 'Project identity required')
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError):
        raise ValueError('Invalid project identity') from None
    require(str(parsed) == value and parsed.version == 4, 'Expected canonical UUID4 identity')
    return value


def timestamp(value):
    require(isinstance(value, str) and len(value) <= 40, 'Invalid timestamp')
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        raise ValueError('Invalid timestamp') from None
    require(parsed.tzinfo is not None and parsed.utcoffset() is not None, 'Timezone required')
    return parsed


def count(value):
    require(value is None or type(value) is int and 0 <= value <= 2**63 - 1, 'Invalid count')


def validate_event(event: dict) -> dict:
    require(isinstance(event, dict) and set(event) == FIELDS, 'Unexpected or missing event fields')
    require(event['schema'] == 'blueprint-event.v1', 'Unsupported event schema')
    for key in ('event_id', 'session_id', 'attempt_id', 'machine_id', 'stream_id'):
        opaque(event[key])
    if event['parent_attempt_id'] is not None:
        opaque(event['parent_attempt_id'])
        require(event['parent_attempt_id'] != event['attempt_id'], 'Self-parent refused')
    project_id(event['project_id'])
    if event['task_id'] is not None:
        project_id(event['task_id'])
    for key in ('model', 'tool_version'):
        value = event[key]
        require(value is None or isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:+-]{0,79}', value)
                and not value.startswith(('sk-', 'ghp_', 'github_pat_')), 'Invalid model/version metadata')
    for key, allowed in {
        'provider': {'openai', 'anthropic', 'local'},
        'tool': {'codex', 'claude-code', 'ollama', 'manual'},
        'billing_basis': {'subscription', 'api', 'local', 'unknown'},
        'provenance': {'native', 'derived', 'manual'},
        'usage_mode': {'delta', 'cumulative'},
        'usage_semantics': {'codex-inclusive', 'anthropic-exclusive', 'local', 'unknown'},
    }.items():
        require(isinstance(event[key], str) and event[key] in allowed, 'Invalid event category')
    timestamp(event['occurred_at']); timestamp(event['observed_at'])
    require(isinstance(event['usage'], dict) and set(event['usage']) == TOKENS, 'Invalid usage fields')
    for value in event['usage'].values(): count(value)
    count(event['duration_ms'])
    require(event['unknown_reason'] is None or isinstance(event['unknown_reason'], str) and event['unknown_reason'] in REASONS, 'Invalid unknown reason')
    if any(value is None for value in event['usage'].values()) or event['duration_ms'] is None or event['task_id'] is None or event['model'] is None:
        require(event['unknown_reason'] in REASONS, 'Unknown values require a reason')
    if event['usage_semantics'] == 'codex-inclusive':
        for sub, total in [('cached_input_tokens', 'input_tokens'), ('reasoning_output_tokens', 'output_tokens')]:
            a, b = event['usage'][sub], event['usage'][total]
            require(a is None or b is None or a <= b, 'Invalid included token subcategory')
    return deepcopy(event)


def resolve_project(identity: str, registry: dict) -> dict:
    project_id(identity)
    require(isinstance(registry, dict) and isinstance(registry.get('projects'), list), 'Invalid registry')
    matches = [row for row in registry['projects'] if isinstance(row, dict) and row.get('project_id') == identity]
    require(len(matches) == 1 and matches[0].get('enabled') is True, 'Project missing, ambiguous or disabled')
    return deepcopy(matches[0])
