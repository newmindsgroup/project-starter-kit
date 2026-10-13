# Version-Timestamp: 2026-10-05 20:24:57 AST
"""Assistant message counters with cache categories separate from base input."""
from ..contracts import require
from .common import make_event


def normalize(source_record: dict, binding: dict) -> list:
    require(isinstance(source_record, dict), 'Invalid source record')
    if source_record.get('type') != 'assistant': return []
    message = source_record.get('message')
    require(isinstance(message, dict), 'Unsupported message format')
    request = message.get('id')
    require(isinstance(request, str) and 0 < len(request) <= 256, 'Missing message identity')
    raw = message.get('usage')
    require(isinstance(raw, dict), 'Unsupported usage format')
    details = raw.get('output_tokens_details') or {}
    require(isinstance(details, dict), 'Unsupported usage details')
    usage = {'input_tokens': raw.get('input_tokens'), 'output_tokens': raw.get('output_tokens'),
             'cached_input_tokens': raw.get('cache_read_input_tokens'),
             'cache_write_input_tokens': raw.get('cache_creation_input_tokens'),
             'reasoning_output_tokens': details.get('thinking_tokens')}
    return [make_event(binding, 'anthropic', 'claude-code', source_record.get('timestamp'),
                       request, usage, 'anthropic-exclusive', model=message.get('model'))]
