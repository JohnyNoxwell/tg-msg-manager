# Export Service Split Map

Old hot-path file: `tg_msg_manager/services/exporter.py`

Current compatibility surface:

- `tg_msg_manager/services/exporter.py` -> thin wrapper
- implementation lives in `tg_msg_manager/services/export/service.py`

## Method Map

| Method | Responsibility | Target module | Outcome |
| --- | --- | --- | --- |
| `__init__` | compose orchestrator dependencies | `services/export/service.py` | kept as thin facade |
| `_emit_event` | service event emission | `services/export/event_emitter.py` | split |
| `request_stop` | cooperative stop | `services/export/service.py` | kept |
| `try_fetch_missing_reply` | placeholder hook | `services/export/service.py` | kept |
| `_build_scan_ranges` | scan planning | `services/export/planner.py` | split |
| `_resolve_tail_progress_checkpoint` | tail checkpoint resolution | `services/export/planner.py` | split |
| `_prefetch_chat_head_messages` | shared HEAD prefetch | `services/export/fetch_orchestrator.py` | split |
| `_resolve_target_report_name` | tracked sync report naming | `services/export/target_resolver.py` | split |
| `_ensure_user_stats_entry` | tracked sync stats initialization | `services/export/target_resolver.py` | split |
| `_enqueue_tracked_sync_retry_task` | retry queue delegation | `services/export/service.py` | kept thin |
| `sync_chat` | main chat sync entrypoint | `services/export/chat_sync.py` | split |
| `sync_all_dialogs_for_user` | multi-dialog orchestration | `services/export/dialog_sync.py` | split |
| `sync_all_outdated` | tracked target selection | `services/export/service.py` | kept thin |
| `sync_all_tracked` | tracked target selection | `services/export/service.py` | kept thin |
| `_sync_target_items` | tracked runner dispatch | `services/export/fetch_orchestrator.py` + `services/sync/tracked_runner.py` | split |

## Result

- `tg_msg_manager/services/exporter.py` is now a 6-line compatibility wrapper.
- `tg_msg_manager/services/export/service.py` is a 192-line facade that delegates planning, target resolution, range execution, dialog sync, and checkpoint application to dedicated modules.
- `chat_sync.py` owns chat-level orchestration and finalization.
- `dialog_sync.py` owns bulk dialog scanning and event sequencing.
