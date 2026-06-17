# STAGE 6A.0 — CLI Runtime Boundary Precheck Report

Дата: 2026-06-17
Статус: completed
Тип: docs/precheck

## Проверка stage и архитектуры

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`
- Stage безопасен как audit-only: runtime-код, тесты, CLI-поведение, SQLite-схема и dataset/export форматы не менялись.
- Architecture guard: нарушений нет, потому что изменение ограничено factual report и lifecycle index cleanup.

## Инвентарь CLIContext

`CLIContext.__init__` сейчас принимает `AppRuntime` и `needs_client`.

Runtime resources:

- `runtime`: исходный `AppRuntime`.
- `settings`: `runtime.settings`.
- `paths`: `runtime.paths`.
- `pm`: `ProcessManager(lock_path=paths.lock_path)`.
- `storage`: `SQLiteStorage(paths.db_path, process_manager=pm)`, создается в `initialize`, запускает async writer через `start`.
- `client`: `TelethonClientWrapper(...)`, создается только при `needs_client=True`.
- `needs_client`: флаг Telegram-зависимого режима.
- `active_uid`: текущий user id для emergency JSON export.

Services:

- `db_exporter`: `DBExportService(storage, default_output_dir=paths.db_exports_dir)`, создается всегда после storage.
- `exporter`: `ExportService(client, storage, event_sink=render_service_event)`, только при `needs_client=True`.
- `private_archive`: `PrivateArchiveService(client, storage, base_dir=paths.private_dialogs_dir, event_sink=render_service_event)`, только при `needs_client=True`.
- `channel_exporter`: `ChannelExportService(client=client, base_dir=paths.channel_exports_dir, event_sink=render_service_event)`, только при `needs_client=True`.
- `retry_worker`: `RetryWorker(storage=storage, client=client, exporter=exporter, private_archive=private_archive)`, только при `needs_client=True`.
- `cleaner`: `CleanerService(client, storage, whitelist=settings.whitelist_chats, include_list=settings.include_chats, artifact_roots=paths.artifact_roots(), event_sink=render_service_event)`, создается всегда; в no-client режимах получает `client=None`.

CLI renderer / adapter dependencies:

- `render_service_event` передается в export/cleaner/private_archive/channel_export services.
- `setup_logging(level=settings.log_level, log_dir=paths.logs_dir)` вызывается в `initialize`.
- stdout/stderr lifecycle messages: SQLite open/ready, Telegram connecting/established, readable login failures.
- `emergency_callback` рендерит emergency JSON export status directly to stdout.

Compatibility attributes:

- `settings`, `paths`, `runtime`, `pm`, `storage`, `client`, `exporter`, `cleaner`, `db_exporter`, `private_archive`, `channel_exporter`, `retry_worker`, `alias_manager`, `active_uid`.
- `alias_manager`: `AliasManager(project_root=paths.project_root, python_executable=runtime.python_executable)`, CLI setup compatibility surface.

## Lifecycle

Initialize order:

1. `setup_logging`, `telemetry.reset`.
2. process lock acquire; lock failure prints `error_locked` and exits with code 1.
3. async SIGINT handler registration with `emergency_callback`.
4. SQLite storage create, startup messages, `await storage.start()`.
5. DB export service create.
6. if `needs_client=True`: Telegram wrapper create/connect; readable login error maps to stderr and `SystemExit(1)`; then Telegram-dependent services create.
7. Cleaner service create.

Shutdown order:

1. disconnect Telegram client if present.
2. close SQLite storage if present.
3. release process lock.

## `ctx.*` consumer inventory

Command/runtime dispatch:

- `run_cli`: creates `CLIContext(active_runtime, needs_client=_command_needs_client(command))`, calls `initialize`, dispatches handler, always calls `shutdown`.
- `main_menu`: creates `CLIContext(active_runtime, needs_client=True)`, calls `initialize`, reads `ctx.client.get_me()`, routes choices, always calls `shutdown`.
- `target`: bypasses full `CLIContext`; builds `SQLiteStorage` directly and passes `SimpleNamespace(storage=storage)`.
- `validate-dataset` and `inspect-dataset`: bypass `CLIContext` and call handlers with `ctx=None`.

CLI command handlers:

- `export`: `ctx.active_uid`, `ctx.client`, `_store_resolved_user`, `_run_export_sync`, `_emit_export_summary`, `ctx.pm.should_stop`.
- `export-pm`: `ctx.client`, `ctx.private_archive.archive_pm`, `ctx.storage` for retry enqueue on failure.
- `db-export`: `ctx.db_exporter.export_user_messages`.
- `export-channel`: `ctx.paths.channel_exports_dir`, `ctx.channel_exporter.export_channel`.
- `retry`: `ctx.storage.list_retry_tasks`, `ctx.storage.cleanup_retry_tasks`, `ctx.retry_worker.run_due_tasks`.
- `report`: `ctx.storage`, `ctx.paths.db_exports_dir`.
- `schedule`: `ctx.paths.project_root`, `ctx.runtime.python_executable`.
- `setup`: `ctx.alias_manager.install`, `ctx.alias_manager.get_alias_specs`.
- `delete`: `ctx.cleaner.purge_user_data`.
- `update`: `_sync_and_export_dirty_targets` uses `ctx.exporter`, `ctx.db_exporter`.
- `clean`: `ctx.cleaner.global_self_cleanup`.
- `target names`: `ctx.storage`.
- `validate-dataset` / `inspect-dataset`: no `ctx` dependency; `ctx` is deleted.

Menu handlers:

- export menu: `ctx.client`, `ctx.active_uid`, `ctx.pm.should_stop`, plus export summary dependencies.
- update menu: `ctx.exporter`, `ctx.db_exporter`.
- clean menu: `ctx.cleaner`.
- export PM menu: `ctx.client`, `ctx.private_archive`.
- delete data menu: `ctx.storage`, `ctx.cleaner`.
- schedule menu: `ctx.paths.project_root`, `ctx.runtime.python_executable`.
- setup menu: `ctx.alias_manager`.
- DB export menu: `ctx.storage`, `ctx.db_exporter`.
- channel export menu: passes full `ctx` to `_handle_export_channel_command`, which needs `paths.channel_exports_dir` and `channel_exporter`.
- retry menu: `ctx.storage`, `ctx.retry_worker`.
- report menu: `ctx.storage`, `ctx.paths.db_exports_dir`.

Support helpers:

- `_store_resolved_user`: `ctx.active_uid`, `ctx.storage.upsert_user`.
- `_run_export_sync`: `ctx.exporter`, `ctx.settings.chats_to_search_user_msgs`.
- `_emit_export_summary`: `ctx.db_exporter`, `ctx.storage`.
- `_sync_and_export_dirty_targets`: `ctx.exporter`, `ctx.db_exporter`.
- `_print_alias_install_result`: `ctx.alias_manager`.

Tests currently assert:

- no-client context leaves `ctx.client is None`, still starts storage and creates cleaner.
- live context wires event sinks and disconnects client on shutdown.
- login FloodWait/network errors render readable messages and exit with code 1 before Telegram-dependent services and cleaner are created.
- `report` runs with `needs_client=False`.
- `target names` uses local-only storage path and runtime can be built without API credentials.
- `export-channel` requires client.
- DB export TXT/JSON profile behavior is preserved.

## Grouped capabilities

- Runtime lifecycle: `runtime`, `settings`, `paths`, `pm`, `initialize`, `shutdown`, `active_uid`.
- Local storage/read-only commands: `storage`, `paths.db_exports_dir`.
- Telegram client resolution: `client`.
- User/group export: `exporter`, `db_exporter`, `storage`, `settings`, `pm`, `active_uid`.
- DB export/rendering: `db_exporter`, `storage`.
- Private archive: `private_archive`, `storage`.
- Channel export: `channel_exporter`, `paths.channel_exports_dir`.
- Retry queue: `retry_worker`, `storage`.
- Cleanup/delete: `cleaner`, `storage`.
- Scheduler/setup: `runtime.python_executable`, `paths.project_root`, `alias_manager`.
- CLI rendering/events: `render_service_event`, stdout/stderr messages, menu/report renderers.

## Proposed extraction order

1. Stage 6A.1: add guardrails and tests around current public CLI/runtime contract without moving construction.
2. Stage 6A.2: extract runtime resources first: process lock/signals, logging, telemetry reset, SQLite storage lifecycle, optional Telegram client creation/login error handling.
3. Stage 6A.3: extract service bundle construction over explicit runtime resources, preserving event sinks and no-client nullable client behavior.
4. Stage 6A.4: extract session lifecycle orchestration: initialize/shutdown ordering, lock release, storage close, client disconnect, emergency callback wiring.
5. Stage 6A.5: shrink `CLIContext` into a compatibility adapter exposing the same attributes while delegating resource/session/service construction.
6. Stage 6A.6: define headless runtime contract so non-CLI consumers can initialize runtime without importing CLI.

Smallest safe next implementation boundary for Stage 6A.1:

- Do not move construction yet.
- Add/adjust guardrail tests or docs only around: no-client commands, login error exit path, event sink wiring, shutdown ordering, and `CLIContext` compatibility attributes.
- Keep `CLIContext` public import and handler attribute names unchanged.

## Preservation contract

CLI:

- Preserve command names, flags, defaults, prompts, output strings, exit codes, help behavior, language binding, menu routing, and import compatibility.
- Preserve `run_cli` behavior for no command in non-TTY: print help and return.
- Preserve `validate-dataset` and `inspect-dataset` as filesystem-only commands with `ctx=None`.
- Preserve `target names` local-only storage path and no API credential requirement.
- Preserve `report`, `schedule`, `setup`, `db-export`, `retry` no-client behavior.
- Preserve `export-channel` as client-required.

SQLite/storage:

- No schema changes.
- Preserve SQLite open/ready messages, `SQLiteStorage(paths.db_path, process_manager=pm)`, `await storage.start()`, `await storage.close()`, direct target storage close, write queue behavior, and lock-aware stop propagation.

Dataset/export:

- No dataset format, filenames, output layout, manifest/state, TXT/JSONL, media/discussion, or export directory changes.
- Preserve DB export default output dir and channel export default output dir.

Retry:

- Preserve retry list/cleanup/run behavior and PM archive retry enqueue on archive failure.

Scheduler/setup:

- Preserve scheduler setup inputs: `paths.project_root` and `runtime.python_executable`.
- Preserve alias install behavior and printed alias specs.

Login/error handling:

- Preserve Telegram session path resolution for relative session names under `paths.project_root`.
- Preserve readable RPC/FloodWait/EOF/network login errors to stderr and `SystemExit(1)`.
- Preserve behavior where login failure happens after storage start and before Telegram-dependent services/cleaner are created.
- Preserve shutdown cleanup after login failure when caller reaches `shutdown`.

Signals/emergency:

- Preserve async SIGINT setup before long-running work.
- Preserve emergency JSON export when `active_uid` and `db_exporter` are set.
- Preserve `pm.should_stop()` checks during export interruption.

## Проверки

- `git diff --check`: passed.
- Pytest не запускался: stage audit-only, runtime/test files не изменялись; stage требует не запускать pytest, если runtime/test files не менялись.

## Измененные файлы

- `docs/stages/reports/STAGE_6A_0_CLI_RUNTIME_BOUNDARY_PRECHECK_REPORT.md`: создан factual precheck report.
- `docs/stages/completed/stage_6a_0_cli_runtime_boundary_precheck.md`: stage file перемещен из active в completed.
- `docs/stages/README.md`: lifecycle index обновлен; Stage 6A.0 убран из active и добавлена ссылка на report.

## Notes

- Для точной инвентаризации command handlers дополнительно проверен re-export target `tg_msg_manager/cli/commands/`, потому что `tg_msg_manager/cli_commands.py` только re-export wrapper.
- Runtime-код и тесты не изменялись.
