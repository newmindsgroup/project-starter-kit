# Version-Timestamp: 2026-10-05 20:24:57 AST
"""Import completed Ollama responses supplied by an instrumented caller."""
from ..contracts import count, require
from .common import make_event


def normalize(source_record: dict, binding: dict) -> list:
    require(isinstance(source_record, dict), 'Invalid local response')
    if source_record.get('done') is not True: return []
    duration = source_record.get('total_duration'); count(duration)
    timestamp = source_record.get('created_at')
    usage = {'input_tokens': source_record.get('prompt_eval_count'),
             'output_tokens': source_record.get('eval_count'),
             'cached_input_tokens': None, 'cache_write_input_tokens': None,
             'reasoning_output_tokens': None}
    return [make_event(binding, 'local', 'ollama', timestamp,
                       timestamp, usage, 'local', mode='delta', model=source_record.get('model'),
                       duration=None if duration is None else duration // 1000000)]
