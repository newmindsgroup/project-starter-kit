# Project Blueprint capability matrix

Version-Timestamp: 2026-10-13 11:11:32 AST
Status: optional manual helpers inside Project Starter Kit. Packaging does not activate a collector.

| Surface | Token evidence | Model evidence | Timing | Charges | Current coverage |
| --- | --- | --- | --- | --- | --- |
| Codex 0.160.0 selected local JSONL | Native cumulative counters; cache/reasoning subcategories retained | Unknown for mixed session totals | Event timestamps; not task runtime | Unknown | Selected native record smoke test plus fixture imports |
| Claude Code 2.1.287 selected local JSONL | Native per-message cumulative counters | Message model when reported | Event timestamps; not human attention | Unknown | Selected native record smoke test plus streaming fixtures |
| Completed Ollama response | Input/output counts supplied by an instrumented caller | Response model | Native total duration in nanoseconds converted to milliseconds | No direct API bill inferred | Synthetic fixture contract only; no live runtime capture claimed |
| Codex app-server/desktop notifications | Not integrated | Not verified | Not verified | Not verified | Pending supported-surface probes |
| Claude OpenTelemetry exporter | Not activated | Not verified | Not verified | Not verified | Pending authorized machine setup |
| Human interaction | No tokens | Not applicable | Explicit start/pause/resume/switch/stop | Requires later hourly-cost profile | Basic timer implemented; attention remains unverified |

The installed Codex command and Claude Code command versions were read locally. Recent local native record shapes were inspected without printing content, paths or native identities. A selected record from each tool matched its normalized token fields, and replay was ignored. This is evidence for those records, not all sessions or ordinary desktop capture. No new hosted request was purchased for these probes.

The foundation imports only a selected source under an explicit project/session/machine binding. Task binding is optional and must cover the whole source. Raw provider identifiers are converted to opaque identities; original paths and prompts are not persisted. Tokens are not prices. Billing, subscription allocation, market human estimates and automatic collection remain unimplemented.

Format errors fail with no cursor advance. Unsupported non-usage records are ignored and counted; a source with no recognized usage is not proof of zero consumption. Cache and reasoning categories must not be added blindly to totals.

References checked for format context: [Codex protocol](https://github.com/openai/codex/blob/main/codex-rs/protocol/src/protocol.rs), [Claude monitoring](https://code.claude.com/docs/en/monitoring-usage), [Ollama generation response](https://docs.ollama.com/api/generate). Installed local observations remain the compatibility evidence for this candidate.
