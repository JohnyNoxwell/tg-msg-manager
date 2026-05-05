# Private Archive Split Map

| Current method | Responsibility | Target module | Shared component candidate | Notes |
|---|---|---|---|---|
| `__init__` | dependency wiring | `services/private_archive/service.py` | `FileRotateWriter`, service events | Keep constructor surface stable |
| `_emit_event` | event sink bridge | `services/private_archive/event_emitter.py` | `core.service_events.emit_service_event` | Pure event plumbing |
| `_get_user_folder_name` | deterministic archive folder naming | `services/private_archive/planner.py` | `utils.ui.UI.format_name` | Preserve output path contract |
| `_media_category` | media categorization policy | `services/private_archive/media_policy.py` | none | Pure policy |
| `_download_media` | media target path + Telegram download | `services/private_archive/service.py` + `media_policy.py` | `TelegramClientInterface.download_media` | Keep adapter call outside policy module |
| `_prepare_archive_context` | target/archive scope resolution | `services/private_archive/planner.py` | `utils.ui.UI.format_name` | Produces archive paths and labels |
| `_ensure_archive_dirs` | archive directory creation | `services/private_archive/archive_writer.py` | filesystem writer utilities | Keep file IO outside facade |
| `_initial_media_stats` | stats initialization | `services/private_archive/models.py` | none | Simple domain data |
| `_initial_archive_stats` | transfer stats initialization | `services/private_archive/models.py` | none | Simple domain data |
| `_emit_archive_start` | started event payload | `services/private_archive/event_emitter.py` | `PrivateArchiveStartedPayload` | Event-only responsibility |
| `_emit_archive_progress` | progress event payload | `services/private_archive/event_emitter.py` | `PrivateArchiveProgressPayload` | Event-only responsibility |
| `_emit_archive_complete` | completed event payload | `services/private_archive/event_emitter.py` | `PrivateArchiveCompletedPayload` | Event-only responsibility |
| `_track_media_stats` | media stats mutation | `services/private_archive/media_policy.py` / `models.py` | none | Domain-level counting logic |
| `_process_archive_media` | download/skip decision + media event | `services/private_archive/service.py` + `media_policy.py` + `event_emitter.py` | telemetry, Telegram adapter | Split policy from side effects |
| `_archive_message` | save message, process media, append log | `services/private_archive/service.py` + `archive_writer.py` | storage write path, `FileRotateWriter` | Keep orchestration thin |
| `_archive_message_stream` | iterate PM history and emit progress | `services/private_archive/service.py` | Telegram iterator, event emitter | Main orchestration loop |
| `archive_pm` | end-to-end PM archive orchestration | `services/private_archive/service.py` | storage state, event emitter, writer | Final facade method |
| `_format_pm_log` | PM log rendering | `services/private_archive/archive_writer.py` | none | Preserve text output contract |
