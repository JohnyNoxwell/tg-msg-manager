All notable changes to this project will be documented in this file in both English and Russian.
Все значимые изменения проекта фиксируются в этом файле на английском и русском языках.

## [4.2.28] - 2026-05-09

### Added (EN)
- **Stage 4A Dataset Validation / Inspection**: Added read-only `validate-dataset` and `inspect-dataset` commands for channel export datasets, with Markdown and JSON reports.
- **Dataset Validators**: Added JSONL, manifest, state, media, and discussion validators under `tg_msg_manager/services/dataset_validation/` without changing exporter behavior or schemas.

### Added (RU)
- **Stage 4A dataset validation / inspection**: Добавлены read-only команды `validate-dataset` и `inspect-dataset` для channel export datasets с Markdown и JSON отчётами.
- **Dataset validators**: Добавлены JSONL, manifest, state, media и discussion validators в `tg_msg_manager/services/dataset_validation/` без изменений exporter behavior или schemas.

## [4.2.27] - 2026-05-09

### Added (EN)
- **Stage 3E.5 Interactive Channel Export Options Parity**: Interactive menu item `10` now prompts for discussion mode, max comments per post, force re-export, output directory, max media size, and media types while preserving direct CLI defaults for empty answers.

### Added (RU)
- **Stage 3E.5 parity интерактивного channel export**: Интерактивный пункт меню `10` теперь запрашивает discussion mode, max comments per post, force re-export, output directory, max media size и media types, сохраняя defaults прямой CLI-команды при пустом вводе.

## [4.2.26] - 2026-05-08

### Changed (EN)
- **Stage 3D.0 Documentation Governance**: Reorganized documentation into `docs/architecture/`, `docs/development/`, `docs/stages/active/`, `docs/stages/completed/`, `docs/stages/reports/`, `docs/roadmap/`, and `docs/archive/`.
- **Agent Contract**: Rewrote `AGENTS.md` as the concise repository-level agent contract with protected boundaries, documentation map, stage workflow, and stop-and-report conditions.
- **Root Documentation Alignment**: Added root links to the new documentation map without changing runtime behavior or CLI contracts.

### Изменения (RU)
- **Stage 3D.0 documentation governance**: Документация разнесена по `docs/architecture/`, `docs/development/`, `docs/stages/active/`, `docs/stages/completed/`, `docs/stages/reports/`, `docs/roadmap/` и `docs/archive/`.
- **Agent contract**: `AGENTS.md` переписан как краткий repository-level contract для агентов с protected boundaries, documentation map, stage workflow и stop-and-report conditions.
- **Выравнивание root docs**: В корневые документы добавлены ссылки на новую карту документации без изменений runtime behavior или CLI contracts.

## [4.2.25] - 2026-05-08

### Added (EN)
- **Stage 3C Channel Discussion Context Export**: Added explicit `export-channel --discussion full` support for linked discussion comments as dataset files, while keeping the default `--discussion none`.
- **Discussion Dataset Files**: Added `discussion_comments.jsonl`, `discussion_comments.txt`, `discussion_threads.jsonl`, and `discussion_export_state.json` for current-run channel posts only.
- **Discussion Comment Limit**: Added `--max-comments-per-post` with a default of `100`.
- **Stage 3B Media Download Hardening**: Added `ChannelMediaDownloader` under `services/channel_export/` with file hashing, existing-file reuse, size/type guardrails, and per-media failure recording for direct channel export.
- **Channel Export Media Controls**: Added `--max-media-size` and `--media-types` for `export-channel`, while keeping `--media metadata` as the default and requiring explicit `--media full` for downloads.
- **Media Download Event Surface**: Added `channel_export.media_progress`, `channel_export.media_downloaded`, `channel_export.media_skipped`, and `channel_export.media_failed` events plus CLI progress rendering.

### Changed (EN)
- **Discussion Export State Safety**: Discussion state is filesystem-local, separate from `channel_export_state.json`, and no-new-posts runs do not refetch old discussion threads or mutate discussion state.
- **Manifest / CLI Discussion Summary**: Channel export manifest and CLI summary now include discussion counts when `--discussion full` is used.
- **Direct Channel Export Full Media**: `export-channel --media full` now downloads media into `media/`, computes `sha256`, skips reusable files as `already_exists`, and records final statuses in `media_manifest.jsonl`.
- **Manifest / State Media Summary**: Channel export manifest/state now track detailed media counters for downloaded, existing, skipped-by-size, skipped-by-type, and failed media records.

### Добавлено (RU)
- **Stage 3C Channel Discussion Context Export**: Добавлена явная поддержка `export-channel --discussion full` для linked discussion comments как dataset files; default остаётся `--discussion none`.
- **Discussion dataset files**: Добавлены `discussion_comments.jsonl`, `discussion_comments.txt`, `discussion_threads.jsonl` и `discussion_export_state.json` только для channel posts текущего run.
- **Лимит discussion comments**: Добавлен `--max-comments-per-post` с default `100`.
- **Stage 3B Media Download Hardening**: Для direct channel export добавлен `ChannelMediaDownloader` в `services/channel_export/` с file hashing, reuse существующих файлов, size/type guardrails и фиксацией per-media failures.
- **Media controls для channel export**: Для `export-channel` добавлены `--max-media-size` и `--media-types`, при этом default остаётся `--media metadata`, а загрузка файлов требует явного `--media full`.
- **Event surface для media download**: Добавлены события `channel_export.media_progress`, `channel_export.media_downloaded`, `channel_export.media_skipped` и `channel_export.media_failed` вместе с CLI progress rendering.

### Изменения (RU)
- **Безопасность discussion state**: Discussion state хранится только в filesystem, отдельно от `channel_export_state.json`; no-new-posts runs не перечитывают старые threads и не меняют discussion state.
- **Discussion summary в manifest/CLI**: Manifest channel export и CLI summary теперь включают discussion counts при использовании `--discussion full`.
- **Full media в direct channel export**: `export-channel --media full` теперь скачивает media в `media/`, считает `sha256`, переиспользует существующие файлы как `already_exists` и пишет финальные статусы в `media_manifest.jsonl`.
- **Детальный media summary в manifest/state**: Manifest и filesystem-state channel export теперь хранят отдельные счётчики для downloaded, existing, skipped-by-size, skipped-by-type и failed media records.

## [4.2.24] - 2026-05-07

### Added (EN)
- **Stage 3A.1 Channel Export State**: Added per-dataset `channel_export_state.json` with last exported message id, aggregate counters, and safe post-success state persistence for `export-channel`.
- **Channel Export Progress Events**: Added dedicated `channel_export.started`, `channel_export.channel_resolved`, `channel_export.state_loaded`, `channel_export.progress`, `channel_export.no_new_posts`, `channel_export.completed`, and `channel_export.failed` service events plus CLI rendering.

### Changed (EN)
- **Incremental Channel Export**: `export-channel` now reuses filesystem state to append only new posts to `messages.jsonl`, `messages.txt`, and `media_manifest.jsonl` instead of always rebuilding the dataset.
- **Force Re-export Semantics**: `export-channel --force` now ignores existing state, overwrites dataset payload files, and recreates state from a clean full export.
- **Streaming Writer Path**: Channel export no longer materializes the full mapped-record list for full exports; payload writing now runs through a streaming session that tracks counters and progress.

### Добавлено (RU)
- **Stage 3A.1 состояние channel export**: Для `export-channel` добавлен per-dataset файл `channel_export_state.json` с last exported message id, агрегатными счётчиками и безопасным обновлением state только после успешного завершения записи.
- **События прогресса channel export**: Добавлены отдельные service events `channel_export.started`, `channel_export.channel_resolved`, `channel_export.state_loaded`, `channel_export.progress`, `channel_export.no_new_posts`, `channel_export.completed` и `channel_export.failed` вместе с CLI-рендерингом.

### Изменения (RU)
- **Инкрементальный channel export**: `export-channel` теперь использует filesystem-state и append-only дописывает только новые посты в `messages.jsonl`, `messages.txt` и `media_manifest.jsonl`, а не всегда перестраивает dataset целиком.
- **Семантика принудительного re-export**: `export-channel --force` теперь игнорирует существующий state, перезаписывает dataset payload-файлы и пересоздаёт state из чистого full export.
- **Стриминговый writer path**: Для full export больше не материализуется полный список mapped-records; запись теперь идёт через streaming session с подсчётом статистики и progress callbacks.

## [4.2.23] - 2026-05-07

### Added (EN)
- **Stage 3A Direct Channel Export Surface**: Added the `export-channel` CLI command and wired a dedicated `ChannelExportService` into the CLI runtime without modifying the existing `export`, `db-export`, `export-pm`, or context/export hot-path services.
- **Filesystem Dataset Layout**: Added the `exports/channels/` runtime root and documented the Stage 3A dataset layout with `manifest.json`, `messages.jsonl`, `messages.txt`, and `media_manifest.jsonl`.
- **Stage 3A Docs and Smoke Guidance**: Added command/docs coverage, live smoke guidance, and a dedicated Stage 3A report for direct channel export.

### Changed (EN)
- **Media Mode Safety**: Stage 3A keeps `metadata` as the safe default; `--media full` is exposed for future hardening without changing the default dataset-projection path.
- **Verification Stability**: Final Stage 3A verification now runs green after tightening SQLite migration idempotency, avoiding WAL reconfiguration on read-only connections, and cleaning up test database sidecar files more reliably.
- **Interactive Menu Surface**: The `tg` control center now exposes `export-channel` and uses two-digit menu numbering with backward-compatible short inputs.
- **Channel Export Guardrails**: `export-channel` now fails with explicit messages for groups/supergroups, keeps Stage 3A scoped to broadcast channels, and normalizes nested datetime values in JSONL export payloads.

### Добавлено (RU)
- **CLI surface для Stage 3A Direct Channel Export**: Добавлена команда `export-channel` и wiring отдельного `ChannelExportService` в CLI runtime без изменений существующих hot-path сервисов `export`, `db-export`, `export-pm` и context/export pipeline.
- **Файловый dataset layout**: Добавлен runtime-root `exports/channels/` и задокументирован Stage 3A dataset layout с `manifest.json`, `messages.jsonl`, `messages.txt` и `media_manifest.jsonl`.
- **Документация и live smoke для Stage 3A**: Добавлены command/docs coverage, live smoke guidance и отдельный Stage 3A report для прямого экспорта каналов.

### Изменения (RU)
- **Безопасность media mode**: В Stage 3A безопасным default остаётся `metadata`; `--media full` виден в CLI как явный opt-in для следующего этапа hardening без изменения default-поведения dataset export.
- **Стабильность verification**: Финальный verification Stage 3A теперь проходит в зелёном статусе после усиления идемпотентности SQLite-миграции, отказа от WAL reconfiguration на read-only connections и более надёжной очистки sidecar-файлов тестовых БД.
- **Interactive menu surface**: В `tg` control center добавлен `export-channel`, а главное меню переведено на двузначную нумерацию с сохранением backward-compatible коротких вводов.
- **Guardrails для channel export**: `export-channel` теперь выдаёт явные ошибки для groups/supergroups, сохраняет Stage 3A в пределах broadcast channels и нормализует вложенные `datetime` значения в JSONL payload.

## [4.2.22] - 2026-05-06

### Fixed (EN)
- **Update Summary Counters**: Fixed tracked `update` per-user summary lines so `without context` / `with context` show messages newly synced in the current run instead of cumulative historical totals already stored for that target.

### Added (EN)
- Added regression coverage for tracked-update breakdown deltas so large historical target totals no longer leak into the current-run summary.

### Исправлено (RU)
- **Счётчики summary для update**: Исправлен per-user итог команды `update`: значения `without context` / `with context` теперь показывают сообщения, досинхронизированные в текущем запуске, а не накопительные historical totals цели из локальной БД.

### Добавлено (RU)
- Добавлено regression-покрытие для delta-breakdown в tracked update, чтобы большие исторические totals цели больше не попадали в summary текущего запуска.

## [4.2.21] - 2026-05-05

### Changed (EN)
- **Update Summary Output**: Changed the `update` CLI summary from one aggregate `processed/targets` block to per-user lines that show the target name plus message totals without context and with context.

### Added (EN)
- Added regression coverage for tracked-update summary rendering and per-user tracked-sync breakdown aggregation.

### Изменения (RU)
- **Вывод summary для update**: Итог `update` переведён с одного агрегатного блока `processed/targets` на построчный вывод по пользователям: имя цели, число сообщений без контекста и число сообщений с контекстом.

### Добавлено (RU)
- Добавлено regression-покрытие для рендера tracked-update summary и агрегации per-user breakdown в tracked sync.

## [4.2.20] - 2026-05-05

### Changed (EN)
- **Stage 2 Readiness / Hardening**: Updated the architecture overview to match the post-Stage-1 package structure, compatibility-wrapper status, storage-contract split, payload-module split, analytics boundary, and current verification state.
- **Facade Protection**: Added explicit facade-growth guardrails to the architecture docs and PR checklist so orchestration modules stay orchestration-only.
- **Live Smoke Hardening**: Expanded the manual smoke checklist with concrete `retry`, `clean --dry-run`, and delete-safety guidance.

### Added (EN)
- Added wrapper guard coverage in `tests/test_architecture_wrappers.py`.
- Added `docs/refactor/STAGE_2_READINESS_BASELINE.md`, `docs/refactor/PRIVATE_ARCHIVE_IMPORT_RESOLUTION.md`, `docs/refactor/FACADE_SIZE_BASELINE.md`, and `docs/refactor/STAGE_2_READINESS_REPORT.md`.

### Изменения (RU)
- **Stage 2 Readiness / Hardening**: Архитектурный overview обновлён под post-Stage-1 структуру пакетов, статус compatibility wrappers, split storage contracts, split payload modules, analytics boundary и текущее verification-состояние.
- **Защита фасадов**: В architecture docs и PR checklist добавлены явные guardrails против роста orchestration-модулей в сторону бизнес-логики.
- **Усиление live smoke**: Manual smoke checklist расширен конкретными сценариями для `retry`, `clean --dry-run` и безопасного использования `delete`.

### Добавлено (RU)
- Добавлено wrapper guard-покрытие в `tests/test_architecture_wrappers.py`.
- Добавлены `docs/refactor/STAGE_2_READINESS_BASELINE.md`, `docs/refactor/PRIVATE_ARCHIVE_IMPORT_RESOLUTION.md`, `docs/refactor/FACADE_SIZE_BASELINE.md` и `docs/refactor/STAGE_2_READINESS_REPORT.md`.

## [4.2.19] - 2026-05-05

### Changed (EN)
- **Stage 1 Consistency Pass**: Closed the remaining post-refactor drift by migrating stale internal imports to the new DB export package entrypoint and finishing narrow-contract usage in private archive state management.
- **Private Archive Facade Tightening**: Extracted PM archive media download and message-stream processing into dedicated `media_downloader.py` and `stream_processor.py` components so `PrivateArchiveService` stays an orchestration facade.
- **Entrypoint Verification**: Audited DB export and private archive entrypoints, verified compatibility imports, and documented the package-vs-file import resolution for `services/private_archive`.

### Added (EN)
- Added compatibility import regression coverage in `tests/test_compat_imports.py`.
- Added `docs/refactor/STAGE_1_CONSISTENCY_BASELINE.md`, `docs/refactor/DB_EXPORT_ENTRYPOINT_AUDIT.md`, `docs/refactor/PRIVATE_ARCHIVE_ENTRYPOINT_AUDIT.md`, and `docs/refactor/STAGE_1_CONSISTENCY_REPORT.md`.

### Изменения (RU)
- **Stage 1 Consistency Pass**: Закрыт оставшийся post-refactor drift: stale internal imports переведены на новый package entrypoint DB export, а private archive state path доведён до narrow-contract схемы.
- **Ужесточение private archive facade**: PM archive media download и message-stream processing вынесены в отдельные `media_downloader.py` и `stream_processor.py`, чтобы `PrivateArchiveService` оставался orchestration facade.
- **Проверка entrypoint’ов**: Проведён аудит DB export и private archive entrypoint’ов, проверены compatibility imports и задокументировано package-vs-file import resolution для `services/private_archive`.

### Добавлено (RU)
- Добавлено regression-покрытие compatibility imports в `tests/test_compat_imports.py`.
- Добавлены `docs/refactor/STAGE_1_CONSISTENCY_BASELINE.md`, `docs/refactor/DB_EXPORT_ENTRYPOINT_AUDIT.md`, `docs/refactor/PRIVATE_ARCHIVE_ENTRYPOINT_AUDIT.md` и `docs/refactor/STAGE_1_CONSISTENCY_REPORT.md`.

## [4.2.18] - 2026-05-05

### Changed (EN)
- **Stage 1 Refactor**: Split `DBExportService` into a thin facade plus dedicated source-loading, planning, skip-policy, state, payload-writing, rendering, and event modules under `tg_msg_manager/services/db_export/`.
- **Private Archive Boundaries**: Split PM archive orchestration into a dedicated `tg_msg_manager/services/private_archive/` package with planner, source-resolver, media-policy, archive-writer, state-manager, and event-emitter components.
- **Narrow Storage Contracts**: Moved service-facing storage protocols into `tg_msg_manager/infrastructure/storage/contracts/` and kept `interface.py` as a compatibility aggregator.
- **Payload Domain Split**: Moved service/event payload models into `tg_msg_manager/core/models/payloads/` and kept `service_payloads.py` as a compatibility aggregator.
- **Architecture Guardrails**: Formalized the analytics boundary, documented the context relation table decision, and added a live/manual Telegram smoke checklist.

### Added (EN)
- Added `docs/refactor/STAGE_1_BASELINE.md`, service split maps, storage/payload split maps, and the context-relation decision document.
- Added `docs/testing/LIVE_SMOKE_CHECKLIST.md`.
- Added analytics placeholder packages under `tg_msg_manager/services/analytics/` and `tg_msg_manager/infrastructure/storage/read/analytics/`.

### Изменения (RU)
- **Stage 1 Refactor**: `DBExportService` разделён на thin facade и выделенные модули source loading, planning, skip policy, state, payload writing, rendering и events в `tg_msg_manager/services/db_export/`.
- **Границы private archive**: Оркестрация PM archive вынесена в пакет `tg_msg_manager/services/private_archive/` с planner, source resolver, media policy, archive writer, state manager и event emitter.
- **Узкие storage contracts**: Сервисные storage protocols перенесены в `tg_msg_manager/infrastructure/storage/contracts/`, а `interface.py` оставлен compatibility aggregator.
- **Payload split по доменам**: Service/event payload models перенесены в `tg_msg_manager/core/models/payloads/`, а `service_payloads.py` оставлен compatibility aggregator.
- **Архитектурные guardrails**: Формализована analytics boundary, задокументировано решение по context relation tables и добавлен live/manual Telegram smoke checklist.

### Добавлено (RU)
- Добавлены `docs/refactor/STAGE_1_BASELINE.md`, split maps сервисов, storage/payload split maps и документ с решением по context relation tables.
- Добавлен `docs/testing/LIVE_SMOKE_CHECKLIST.md`.
- Добавлены analytics placeholder packages в `tg_msg_manager/services/analytics/` и `tg_msg_manager/infrastructure/storage/read/analytics/`.

## [4.2.17] - 2026-05-04

### Changed (EN)
- **Stage 0 Completion**: Completed the refactor baseline gate by turning `cli.py` into a thin compatibility entrypoint, splitting DB export helpers into dedicated modules, and reducing the old SQLite read-path monolith to an aggregator over grouped read mixins.
- **Behavior Freeze**: Kept the public CLI surface unchanged while adding explicit regression coverage for parser defaults and command inventory.
- **Architecture Guardrails**: Added Stage 0 baseline/smoke/audit documentation plus formal architecture rules so future features do not grow inside the remaining hot-path files.

### Added (EN)
- Added `tg_msg_manager/cli_parser.py`, `tg_msg_manager/cli_commands.py`, `tg_msg_manager/cli_menu.py`, and `tg_msg_manager/cli_support.py`.
- Added `tg_msg_manager/services/db_export/` for manifest, JSONL, TXT, and export-plan helpers.
- Added `tg_msg_manager/infrastructure/storage/read/` for grouped message/target/context/export/reporting reads.
- Added `docs/ARCHITECTURE_RULES.md` and Stage 0 reports under `docs/refactor/`.

### Изменения (RU)
- **Завершение Stage 0**: Завершён baseline refactor-gate: `cli.py` стал thin compatibility entrypoint, DB export helper-логика вынесена в отдельные модули, а старый монолит `_sqlite_read_path.py` сведён к aggregator-слою поверх сгруппированных read mixins.
- **Заморозка поведения**: Публичный CLI surface сохранён без изменений; добавлено явное regression-покрытие для parser defaults и command inventory.
- **Архитектурные guardrails**: Добавлены Stage 0 baseline/smoke/audit документы и формальные architecture rules, чтобы будущие features не росли внутри оставшихся hot-path файлов.

### Добавлено (RU)
- Добавлены `tg_msg_manager/cli_parser.py`, `tg_msg_manager/cli_commands.py`, `tg_msg_manager/cli_menu.py` и `tg_msg_manager/cli_support.py`.
- Добавлен пакет `tg_msg_manager/services/db_export/` для manifest, JSONL, TXT и export-plan helpers.
- Добавлен пакет `tg_msg_manager/infrastructure/storage/read/` для grouped message/target/context/export/reporting reads.
- Добавлены `docs/ARCHITECTURE_RULES.md` и Stage 0 отчёты в `docs/refactor/`.

## [4.2.16] - 2026-05-04

### Changed (EN)
- **Alias Consistency**: Reworked alias installation to use one canonical alias-spec list for both Unix and Windows, eliminating drift between shells and platforms.
- **New Quick Commands**: Added `tgrt` for `retry` and `tgrp` for `report`, so alias installation now covers the current operational CLI surfaces introduced during the foundation backlog.
- **Setup Surface Alignment**: Updated setup/help/docs strings so the documented alias list matches the aliases actually installed.
- **Interactive Menu Coverage**: Added `R` and `P` hotkeys to the terminal control-center so `retry` and `report` are available from the interactive console utility, not only as direct CLI commands.

### Fixed (EN)
- Fixed Windows alias installation so destructive cleanup shortcuts include the same `--yes` confirmation bypass as Unix aliases.

### Изменения (RU)
- **Консистентность алиасов**: Установка алиасов переведена на один canonical alias-spec список для Unix и Windows, чтобы убрать drift между shell/platform реализациями.
- **Новые быстрые команды**: Добавлены `tgrt` для `retry` и `tgrp` для `report`, так что alias-installation теперь покрывает актуальные operational CLI surfaces из foundation backlog.
- **Выравнивание setup surface**: Обновлены setup/help/docs строки, чтобы документированный список алиасов совпадал с реально устанавливаемыми командами.
- **Покрытие интерактивного меню**: В terminal control-center добавлены hotkeys `R` и `P`, так что `retry` и `report` доступны не только как прямые CLI-команды, но и из консольной утилиты.

### Исправления (RU)
- Исправлена установка Windows-алиасов: destructive shortcut для cleanup теперь тоже включает `--yes`, как и Unix-версия.

## [4.2.15] - 2026-05-04

### Changed (EN)
- **Stage 5 Completion**: Completed the fixture and E2E hardening stage by adding a fully offline Telegram-like test harness that exercises the foundation pipeline without Telethon or network access.
- **Deterministic Fixture Coverage**: The project now has anonymized JSONL Telegram fixtures for missing-parent recovery, duplicate messages, edited payload refresh, retryable tracked-sync failure, and report/export diagnostics.
- **Foundation Verification Boundary**: `sync`, `context`, `db-export`, `retry`, and `report` are now verifiable through real service/storage flows backed by fixture runtime helpers instead of isolated mocks only.

### Added (EN)
- Added `tg_msg_manager/testing/` with fixture loaders, export normalization helpers, a reusable temp runtime, and `FakeTelegramClient`.
- Added fixture-format documentation in `tests/fixtures/stage5/README.md`.
- Added fixture-backed E2E coverage in `tests/test_fixture_e2e.py`.

### Изменения (RU)
- **Завершение Stage 5**: Завершён этап fixture/E2E hardening: добавлена полностью оффлайн test harness, которая прогоняет foundation pipeline без Telethon и без сетевого доступа.
- **Детерминированное fixture-покрытие**: В проекте теперь есть anonymized JSONL fixtures для missing-parent recovery, duplicate messages, обновления edited payload, retryable tracked-sync failure и report/export diagnostics.
- **Граница foundation verification**: Пути `sync`, `context`, `db-export`, `retry` и `report` теперь проверяются через реальные service/storage flows поверх fixture runtime helpers, а не только через изолированные mocks.

### Добавлено (RU)
- Добавлен `tg_msg_manager/testing/` с fixture loaders, export normalization helpers, reusable temp runtime и `FakeTelegramClient`.
- Добавлена документация формата fixtures в `tests/fixtures/stage5/README.md`.
- Добавлено fixture-backed E2E покрытие в `tests/test_fixture_e2e.py`.

## [4.2.14] - 2026-05-04

### Changed (EN)
- **Stage 4 Completion**: Completed the audit/report read-side by adding a read-only reporting collector, typed audit models, deterministic warning rules, and a dedicated `report` CLI surface that works without Telegram access.
- **Read-Side Observability**: SQLite read-path now exposes compact reporting queries for database summary, tracked target state, and retry queue state, while export artifact state is derived from the local `DB_EXPORTS` filesystem only.
- **Deterministic Diagnostics**: Formal warning rules now cover incomplete targets, missing target/context coverage, stale sync state, high missing-parent signals, retry backlog, failed retry tasks, and missing export artifacts when linked data exists.

### Added (EN)
- Added `tg_msg_manager/core/models/reporting.py` for typed audit/reporting models.
- Added `tg_msg_manager/services/reporting.py` with `ReportCollector` plus Markdown and JSON renderers.
- Added regression coverage for reporting storage summaries, warning generation, renderer determinism, and the read-only CLI `report` command.

### Изменения (RU)
- **Завершение Stage 4**: Завершён audit/report read-side: добавлены read-only reporting collector, typed audit models, deterministic warning rules и отдельный CLI surface `report`, работающий без Telegram access.
- **Read-side observability**: SQLite read-path теперь отдаёт компактные reporting queries для database summary, tracked target state и retry queue state, а export artifact state собирается только из локального `DB_EXPORTS` filesystem.
- **Детерминированная диагностика**: Формальные warning rules теперь покрывают incomplete targets, missing target/context coverage, stale sync state, high missing-parent signals, retry backlog, failed retry tasks и missing export artifacts при наличии linked data.

### Добавлено (RU)
- Добавлен `tg_msg_manager/core/models/reporting.py` для typed audit/reporting models.
- Добавлен `tg_msg_manager/services/reporting.py` с `ReportCollector` и Markdown/JSON renderers.
- Добавлено regression-покрытие для reporting storage summaries, генерации warnings, детерминированности renderers и read-only CLI-команды `report`.

## [4.2.13] - 2026-05-04

### Changed (EN)
- **Stage 3 Completion**: Completed the retry reliability layer by upgrading the old `retry_queue` stub into a typed lifecycle with due-task reads, terminal states, deterministic backoff, and cleanup support.
- **Narrow Operational Integration**: Tracked sync failures during `update` now enqueue retryable `sync_target` tasks instead of aborting the whole tracked run, and failed PM archives now enqueue `archive_pm` retry tasks for later replay.
- **New CLI Surface**: Added a dedicated `retry` command for listing queued tasks, running due tasks, and cleaning terminal retry rows without affecting normal command behavior.

### Added (EN)
- Added `tg_msg_manager/core/models/retry.py` for typed retry status/type models and retry run stats.
- Added `tg_msg_manager/services/retry_worker.py` with deterministic backoff policy, supported retry handlers, and due-task execution.
- Added storage lifecycle support for retry completion, reschedule, failure, cleanup, and legacy schema migration.
- Added regression coverage for retry migration, retry worker execution, tracked-sync enqueue behavior, and CLI retry handling.

### Изменения (RU)
- **Завершение Stage 3**: Завершён retry reliability layer: старая заготовка `retry_queue` превращена в типизированный lifecycle с due-task чтением, terminal states, deterministic backoff и cleanup support.
- **Узкая operational integration**: Ошибки tracked sync во время `update` теперь ставят retryable `sync_target` tasks вместо обрыва всего tracked run, а провалившиеся PM archives ставят `archive_pm` retry tasks для последующего повтора.
- **Новый CLI surface**: Добавлена отдельная команда `retry` для просмотра очереди, запуска due tasks и очистки terminal retry rows без изменения обычного поведения остальных команд.

### Добавлено (RU)
- Добавлен `tg_msg_manager/core/models/retry.py` для typed retry status/type models и retry run stats.
- Добавлен `tg_msg_manager/services/retry_worker.py` с deterministic backoff policy, поддерживаемыми retry handlers и исполнением due tasks.
- Добавлена storage lifecycle-поддержка для retry completion, reschedule, failure, cleanup и миграции legacy schema.
- Добавлено regression-покрытие для retry migration, retry worker execution, tracked-sync enqueue behavior и CLI retry handling.

## [4.2.12] - 2026-05-04

### Changed (EN)
- **Stage 2 Completion**: Completed the context-pipeline refactor by turning `DeepModeEngine` into an orchestration wrapper over dedicated context resolvers, typed candidate/cluster models, and explicit fallback assembly helpers.
- **Deep Mode Boundaries**: Parent lookup, storage-range hydration, live range fill, reply/topic relationship detection, cluster assembly, and time-fallback selection are now split across focused `services/context/` modules instead of living inside one mixed engine class.
- **Deep Mode Reliability**: Live parent/range fetch failures in deep mode now degrade gracefully to storage-only results instead of aborting the whole context extraction path.

### Added (EN)
- Added `tg_msg_manager/services/context/models.py` for typed context candidates, cluster state, and compact request models.
- Added `tg_msg_manager/services/context/fetchers.py` for local-storage and live Telegram fetch resolvers.
- Added `tg_msg_manager/services/context/relationships.py` for child-reply and thread/topic relation helpers.
- Added `tg_msg_manager/services/context/clustering.py` for cluster initialization, anchor selection, association, and cluster mutation rules.
- Added `tg_msg_manager/services/context/resolvers.py` for parent lookup and candidate-pool resolution.
- Added `tg_msg_manager/services/context/fallback.py` for time-fallback selection and application.
- Added regression coverage for source-metadata preservation and deep-mode live-fetch fail paths.

### Изменения (RU)
- **Завершение Stage 2**: Завершён refactor context-pipeline: `DeepModeEngine` превращён в orchestration-wrapper поверх выделенных context resolvers, typed candidate/cluster models и отдельных fallback/assembly helpers.
- **Границы Deep Mode**: Parent lookup, storage-range hydration, live range fill, reply/topic relationship detection, cluster assembly и time-fallback selection теперь разнесены по специализированным модулям `services/context/`, а не живут внутри одного смешанного engine-класса.
- **Надёжность Deep Mode**: Ошибки live parent/range fetch в deep mode теперь деградируют до storage-only результата и не валят весь context extraction path.

### Добавлено (RU)
- Добавлен `tg_msg_manager/services/context/models.py` для typed context candidates, cluster state и компактных request-models.
- Добавлен `tg_msg_manager/services/context/fetchers.py` для local-storage и live Telegram fetch resolvers.
- Добавлен `tg_msg_manager/services/context/relationships.py` для child-reply и thread/topic relation helpers.
- Добавлен `tg_msg_manager/services/context/clustering.py` для cluster initialization, anchor selection, association и правил мутации кластеров.
- Добавлен `tg_msg_manager/services/context/resolvers.py` для parent lookup и candidate-pool resolution.
- Добавлен `tg_msg_manager/services/context/fallback.py` для time-fallback selection и application.
- Добавлено regression-покрытие для сохранения source metadata и deep-mode live-fetch fail paths.

## [4.2.11] - 2026-05-04

### Changed (EN)
- **Stage 1 Completion**: Completed the Stage 1 export-pipeline refactor by moving remaining range-worker execution, tracked-target synchronization orchestration, and dialog-target resolution out of `ExportService` into dedicated `services/sync/` modules.
- **Exporter Responsibility Narrowing**: `ExportService` now stays focused on orchestration and service-event boundaries while scan-buffer processing, batch flushing, tracked-target loops, and dialog-target resolution are delegated to reusable sync helpers.

### Added (EN)
- Added `tg_msg_manager/services/sync/range_scanner.py` for scan-buffer processing, worker checkpointing, flat/deep batch flushing, and per-range execution.
- Added `tg_msg_manager/services/sync/tracked_runner.py` for tracked-target synchronization loops built on top of the existing planner.
- Added `tg_msg_manager/services/sync/dialog_targets.py` for targeted-dialog resolution and supported-dialog filtering helpers.

### Изменения (RU)
- **Завершение Stage 1**: Завершён `Stage 1` refactor export-pipeline: оставшиеся range-worker execution, tracked-target synchronization orchestration и dialog-target resolution вынесены из `ExportService` в отдельные модули `services/sync/`.
- **Сужение ответственности ExportService**: `ExportService` теперь сосредоточен на orchestration и service-event boundaries, а scan-buffer processing, batch flushing, tracked-target loops и dialog-target resolution делегированы переиспользуемым sync helpers.

### Добавлено (RU)
- Добавлен `tg_msg_manager/services/sync/range_scanner.py` для scan-buffer processing, worker checkpointing, flat/deep batch flushing и исполнения отдельных scan ranges.
- Добавлен `tg_msg_manager/services/sync/tracked_runner.py` для tracked-target synchronization loops поверх уже существующего planner.
- Добавлен `tg_msg_manager/services/sync/dialog_targets.py` для targeted-dialog resolution и фильтрации поддерживаемых dialog targets.

## [4.2.10] - 2026-05-04

### Changed (EN)
- **Sync Chat Orchestration**: Continued Stage 1 by extracting sync execution-plan building and terminal no-range completion checks out of `sync_chat()`, which further narrows the core orchestration path without changing CLI-visible behavior.
- **Range Execution Boundaries**: `_scan_range()` now delegates message-stream selection, skip guards, and completion-flag decisions to dedicated sync helpers instead of carrying those execution-policy branches inline.

### Added (EN)
- Added `tg_msg_manager/services/sync/execution_plan.py` for sync execution-plan construction and empty-range terminal-history decisions.
- Added targeted sync helper coverage indirectly through the existing exporter/service regression suite, which remains green after the extraction batches.

### Изменения (RU)
- **Оркестрация sync_chat**: Продолжен `Stage 1`: построение sync execution plan и terminal no-range completion checks вынесены из `sync_chat()`, что ещё сильнее сужает основной orchestration path без изменения CLI-visible поведения.
- **Границы range execution**: `_scan_range()` теперь делегирует выбор message stream, skip guards и completion-flag decisions выделенным sync helpers, вместо того чтобы держать эти execution-policy ветки прямо внутри себя.

### Добавлено (RU)
- Добавлен `tg_msg_manager/services/sync/execution_plan.py` для построения sync execution plan и решений по terminal-history completion при пустых ranges.
- Дополнительное покрытие новых sync helpers подтверждается существующим exporter/service regression suite, который остаётся зелёным после extraction batches.

## [4.2.9] - 2026-05-04

### Changed (EN)
- **Export Service Decomposition**: Continued Stage 1 refactoring by extracting sync-target identity/mode resolution, tracked-target planning, scan message-stream selection, scan skip guards, and scan completion-flag logic out of the hottest `ExportService` paths into dedicated `services/sync/` helpers.
- **Tracked Sync Coordination**: `sync_all_tracked()` now uses a dedicated tracked-target planner for entity/current-max/status/prefetch preparation instead of keeping that coordination logic embedded directly in the service hot path.

### Added (EN)
- Added `tg_msg_manager/services/sync/targets.py` for sync-target identity resolution and active mode/status derivation.
- Added `tg_msg_manager/services/sync/tracked_targets.py` for tracked-target planning and shared head-prefetch coordination.
- Added `tg_msg_manager/services/sync/scan_execution.py` for scan-stream selection, scan skip rules, and terminal completion-flag helpers.

### Изменения (RU)
- **Декомпозиция ExportService**: Продолжен `Stage 1` refactor: identity/mode resolution для sync-target, tracked-target planning, выбор scan message stream, skip guards и completion-flag logic вынесены из самых горячих участков `ExportService` в отдельные helper-модули `services/sync/`.
- **Координация tracked sync**: `sync_all_tracked()` теперь использует отдельный planner для entity/current-max/status/prefetch подготовки, вместо того чтобы держать эту coordination-логику прямо в горячем service path.

### Добавлено (RU)
- Добавлен `tg_msg_manager/services/sync/targets.py` для identity resolution цели и вычисления активного sync mode/status.
- Добавлен `tg_msg_manager/services/sync/tracked_targets.py` для tracked-target planning и shared head-prefetch coordination.
- Добавлен `tg_msg_manager/services/sync/scan_execution.py` для выбора scan-stream, skip-правил и completion-flag helper-логики.

## [4.2.8] - 2026-05-04

### Changed (EN)
- **Export Pipeline Boundaries**: Continued the Stage 1 backlog work by extracting scan-range planning and scan-checkpoint outcome logic out of `ExportService` into dedicated `services/sync/` helpers while keeping the service-level wrappers and runtime behavior intact.
- **Backlog Progress Discipline**: Stage 1 now records concrete completed sub-work in the active backlog instead of treating the file as a static future checklist.

### Added (EN)
- Added `tg_msg_manager/services/sync/scan_ranges.py` for pure scan-range building and tail checkpoint resolution.
- Added `tg_msg_manager/services/sync/checkpoints.py` for pure scan outcome summarization before storage/event side effects are applied.
- Added regression coverage that the extracted sync helpers stay contract-compatible with the `ExportService` wrappers.

### Изменения (RU)
- **Границы export pipeline**: Продолжена работа по `Stage 1` backlog: логика scan-range planning и scan-checkpoint outcome вынесена из `ExportService` в выделенные helper-модули `services/sync/`, при этом service-level wrappers и runtime behavior сохранены.
- **Дисциплина фиксации прогресса**: В `Stage 1` теперь отражён конкретный выполненный sub-work, а не только статичный чеклист на будущее.

### Добавлено (RU)
- Добавлен `tg_msg_manager/services/sync/scan_ranges.py` для pure-логики построения диапазонов сканирования и расчёта tail-checkpoint.
- Добавлен `tg_msg_manager/services/sync/checkpoints.py` для pure-суммаризации scan results до применения storage/event side effects.
- Добавлено regression-покрытие, подтверждающее совместимость extracted sync helpers с wrapper-методами `ExportService`.

## [4.2.7] - 2026-05-04

### Changed (EN)
- **Foundation Backlog Rebaseline**: Replaced the old overlapping staged backlog with a shorter foundation-first execution queue (`Stage 0` through `Stage 5`) and moved analytics / advanced context-quality work into a post-foundation roadmap bucket.
- **Stage 0 Documentation Sync**: Aligned `config.example.json` with the real `Settings` model and added a concise runtime-configuration section to `README.md` so the documented config surface matches the current code.
- **Backlog Progress Tracking**: Started recording execution progress directly inside active backlog stages instead of leaving stage files as static design notes.

### Fixed (EN)
- Fixed read-side export row typing so `context_group_id` remains a string-compatible field instead of drifting to `Optional[int]` in `UserExportRow`.
- Fixed Stage 0 quality-gate noise in legacy/maintenance scripts by classifying their status explicitly and normalizing their formatting for `ruff`.

### Added (EN)
- Added a regression assertion that streamed export rows preserve string `context_group_id` values.
- Added explicit status docstrings to the local maintenance scripts so broken legacy helpers no longer look like supported runtime tooling.

### Изменения (RU)
- **Пересборка foundation backlog**: Старый пересекающийся staged backlog заменён на более короткую foundation-first очередь исполнения (`Stage 0` ... `Stage 5`), а analytics / advanced context-quality вынесены в post-foundation roadmap bucket.
- **Синхронизация Stage 0 документации**: `config.example.json` приведён в соответствие с реальной моделью `Settings`, а в `README.md` добавлен компактный раздел по runtime-конфигурации, чтобы документированный config surface совпадал с текущим кодом.
- **Учёт прогресса по backlog**: Прогресс выполнения теперь фиксируется прямо в активных stage-файлах, а не остаётся только в виде статических design notes.

### Исправления (RU)
- Исправлен type drift в read-side export rows: `context_group_id` снова трактуется как строково-совместимое поле, а не как `Optional[int]` в `UserExportRow`.
- Убран Stage 0 noise в quality gates от legacy/maintenance scripts: их статус явно классифицирован, а форматирование выровнено под `ruff`.

### Добавлено (RU)
- Добавлена regression-проверка, что streamed export rows сохраняют строковые значения `context_group_id`.
- Во все локальные maintenance scripts добавлены явные status-docstrings, чтобы broken legacy helpers больше не выглядели как поддерживаемый runtime tooling.

## [4.2.6] - 2026-05-03

### Changed (EN)
- **Runtime Bootstrap**: Replaced the implicit package-level runtime path assumptions with explicit `AppRuntime` / `AppPaths` composition so CLI entrypoints, storage paths, export roots, scheduler setup, and alias installation all resolve from one injected runtime object.
- **CLI Presentation Boundary**: Moved raw TTY input, service-event rendering, target-list rendering, update summaries, and pause/menu helpers into `cli_io.py`, leaving `cli.py` focused on runtime wiring and command/menu orchestration.
- **Typed Contracts Sweep**: Replaced the remaining loose dict/tuple payloads across tracked sync reports, service events, scheduler/alias setup results, storage read models, export rows, maintenance records, and PM archive stats with typed DTO/record models while preserving mapping-style compatibility where older tests still rely on it.
- **Localized Runtime Context**: Switched i18n state to a `ContextVar`-backed runtime scope so CLI parsing, help text, and handlers stay bound to the invocation language instead of one mutable module-global flag.

### Added (EN)
- Added `PROJECT_ARCHITECTURE_OVERVIEW.md`, a full architecture handoff document describing the codebase structure, algorithms, operational flows, and known constraints for external analysis.
- Added `scripts/export_user_context_from_db.py` for targeted context exports directly from SQLite when investigating one user and their related chat context offline.
- Added regression coverage for runtime-aware CLI bootstrapping, typed alias/scheduler contracts, context-local i18n, typed storage read records, typed tracked-sync reports, and typed PM archive/export payloads.

### Fixed (EN)
- Fixed scheduler setup, alias installation, and local artifact cleanup flows so they no longer depend on the current working directory or a hardcoded local virtualenv path.
- Fixed event/UI coupling by removing service-owned terminal rendering from the remaining export, cleaner, and PM archive flows, which reduces presentation leakage inside application services.

### Изменения (RU)
- **Runtime Bootstrap**: Неявные package-level предположения о путях и окружении заменены на явную композицию `AppRuntime` / `AppPaths`, так что CLI entrypoints, storage paths, export-директории, scheduler setup и установка алиасов теперь резолвятся из одного injected runtime object.
- **Граница CLI Presentation**: Raw TTY input, рендер service-events, вывод списков целей, update-summary и menu/pause helpers вынесены в `cli_io.py`, а `cli.py` оставлен в роли слоя runtime wiring и command/menu orchestration.
- **Переход на typed contracts**: Оставшиеся loose dict/tuple payloads в tracked sync reports, service events, результатах scheduler/alias setup, storage read models, export rows, maintenance records и PM archive stats заменены на typed DTO/record models с сохранением mapping-style совместимости там, где старые тесты еще на нее опираются.
- **Локализованный runtime context**: Состояние i18n переведено на `ContextVar`-scope, чтобы CLI parsing, help-text и handlers были привязаны к языку конкретного запуска, а не к одной глобально мутируемой module-level переменной.

### Добавлено (RU)
- Добавлен `PROJECT_ARCHITECTURE_OVERVIEW.md` — полный handoff-документ по архитектуре, алгоритмам, operational flow и ограничениям проекта для внешнего анализа.
- Добавлен `scripts/export_user_context_from_db.py` для точечных context-export выгрузок напрямую из SQLite при офлайн-разборе одной цели и связанных сообщений.
- Добавлено regression-покрытие для runtime-aware CLI bootstrapping, typed alias/scheduler contracts, context-local i18n, typed storage read records, typed tracked-sync reports и typed payloads в PM archive/export flows.

### Исправления (RU)
- Исправлены scheduler setup, установка алиасов и очистка локальных артефактов: эти сценарии больше не зависят от текущей рабочей директории или захардкоженного пути к локальному virtualenv.
- Исправлена связность между event/UI-слоем и сервисами: из оставшихся export/cleaner/PM archive flows убран сервисный terminal rendering, что уменьшает presentation leakage внутри application services.

## [4.2.5] - 2026-04-27

### Changed (EN)
- **Docs/CLI Alignment**: Synchronized `README.md`, `COMMANDS.md`, and in-app copy with the current menu layout, alias set, scheduler scope, export format semantics, and neutral sample IDs.
- **Service Rendering Boundary**: Moved user-facing progress/status rendering for export, cleanup, and PM archive flows behind a lightweight service-event sink so `services/` no longer own direct terminal output.
- **Storage Contracts**: Split the monolithic storage typing into narrower service-oriented protocols while preserving `SQLiteStorage` as the compatible umbrella backend.
- **Shared Quality Gates**: Added repo-level `make lint`, `make format-check`, `make test`, and `make verify` workflows backed by `ruff`, and wired CI to the same `make verify` entrypoint.

### Fixed (EN)
- Fixed CLI `db-export` semantics so `db-export --user-id <ID>` writes TXT again, while `--json` explicitly opts into the compact JSONL export.
- Fixed CLI `export --json` semantics so the final post-sync export format now matches the flag: plain `export` produces TXT, `export --json` produces JSONL.
- Fixed no-subcommand CLI usage outside an interactive TTY to print parser help instead of crashing on raw terminal input handling.
- Removed dead public flags that did not affect runtime behavior (`update --force-resync`, `clean --user-id`) so the documented CLI surface matches the real one.

### Изменения (RU)
- **Выравнивание docs и CLI**: `README.md`, `COMMANDS.md` и in-app тексты синхронизированы с текущей структурой меню, набором алиасов, реальным scope планировщика, семантикой форматов экспорта и нейтральными sample ID.
- **Граница рендеринга сервисов**: Пользовательский вывод прогресса/статуса для export, cleanup и PM archive переведён на лёгкий service-event sink, так что слой `services/` больше не рисует терминал напрямую.
- **Контракты storage**: Монолитная типизация storage разделена на более узкие service-oriented протоколы, при этом `SQLiteStorage` сохранён как совместимый umbrella backend.
- **Общие quality gates**: Добавлены единые `make lint`, `make format-check`, `make test` и `make verify` на базе `ruff`, а CI переведён на тот же entrypoint `make verify`.

### Исправления (RU)
- Исправлена семантика CLI `db-export`: `db-export --user-id <ID>` снова пишет TXT, а `--json` теперь явно включает компактный JSONL-экспорт.
- Исправлена семантика CLI `export --json`: итоговый post-sync export теперь реально зависит от флага — обычный `export` пишет TXT, `export --json` пишет JSONL.
- Исправлен запуск CLI без subcommand вне интерактивного TTY: теперь выводится parser help, а не происходит падение на raw-input обработке.
- Убраны мёртвые публичные флаги, не влияющие на runtime (`update --force-resync`, `clean --user-id`), чтобы документированный CLI surface совпадал с реальным.

## [4.2.4] - 2026-04-26

### Changed (EN)
- **Update UX Notes**: Documented that `update/tgu` can spend time in a shared head prefetch phase before visible per-target progress appears, especially after a large interrupted export.
- **Target Status Visibility**: Primary target listings now show explicit `Done` / `Incomplete` state instead of relying only on message counters.

### Fixed (EN)
- Fixed sync freshness semantics so `register_target()`, `update_last_msg_id()`, and `update_sync_tail()` no longer refresh `last_sync_at` during partial progress or startup bookkeeping.
- Fixed interrupted multi-range history resume so tail checkpoints only advance across the highest contiguous completed prefix, preventing broken `tail_msg_id = 0` / `is_complete = 0` states after `Ctrl+C`.
- Fixed terminal history resume so targets that legitimately reach the bottom (`tail_msg_id <= 1`) can be finalized on the next pass instead of hanging forever as incomplete.
- Fixed emergency AI JSON export after `SIGINT` when the fast row-export path skipped an unchanged file via manifest reuse.

### Изменения (RU)
- **Примечание по UX обновления**: Задокументировано, что `update/tgu` может тратить заметное время на фазу shared head prefetch до появления видимого прогресса по целям, особенно после большого прерванного экспорта.
- **Видимость статуса целей**: В списках primary targets теперь явно показывается состояние `Готово` / `Не докачано`, а не только счётчики сообщений.

### Исправления (RU)
- Исправлена семантика freshness: `register_target()`, `update_last_msg_id()` и `update_sync_tail()` больше не обновляют `last_sync_at` во время частичного прогресса или стартового bookkeeping.
- Исправлена докачка многодиапазонной истории после прерывания: tail-checkpoint теперь двигается только по верхнему непрерывному префиксу реально пройденных диапазонов, что убирает битые состояния вида `tail_msg_id = 0` при `is_complete = 0` после `Ctrl+C`.
- Исправлена финализация терминального хвоста истории: цели, которые реально дошли до дна (`tail_msg_id <= 1`), теперь могут закрываться на следующем проходе, а не висеть бесконечно в incomplete-state.
- Исправлен emergency AI JSON export после `SIGINT`, когда fast row-export path переиспользовал manifest и падал на unchanged-файле.

## [4.2.3] - 2026-04-25

### Changed (EN)
- **Default Deep Depth**: Deep exports now default to depth `2`, which keeps structural reply/topic context while avoiding the noisier time-based fallback unless depth `3` is requested explicitly.
- **Safe Sync/Export Acceleration**: Optimized the local hot path without increasing Telegram request pressure: deferred SQLite flushes out of per-batch sync loops, replaced per-message target-link checks with batched lookups, batched parent fetches from storage in Deep Mode, and buffered DB export file writes.
- **Runtime Telemetry**: Added stage-level timings and counters for Telegram I/O, Deep Mode expansion, SQLite queue/flush/commit work, and DB export writing. The latest summary is now written to `LOGS/telemetry_latest.json` and emitted as structured log events during bulk updates.

### Fixed (EN)
- Fixed mixed timestamp handling between live Telegram messages and SQLite-loaded messages by normalizing deserialization to UTC-aware datetimes, preventing `offset-naive` vs `offset-aware` comparison errors during deep scans.
- Fixed AI JSONL key ordering so `edit_date` is emitted first when present, improving manual inspection of edited messages.

### Added (EN)
- Added `scripts/reset_and_seed_targets.py` to wipe local DB/export artifacts and reseed `sync_targets` from `DB_TARGETS.txt` before a full fresh `update`.

### Изменения (RU)
- **Глубина Deep Mode по умолчанию**: Глубокий экспорт теперь по умолчанию использует глубину `2`, сохраняя структурный контекст по reply/topic без лишнего time-fallback, если явно не запрошена глубина `3`.
- **Безопасное ускорение sync/export**: Локальный hot path ускорен без роста давления на Telegram API: `flush` вынесен из каждого batch-цикла, проверка target-link переведена на пакетные запросы, parent lookup в Deep Mode стал пакетным, а запись DB-export файлов буферизована.
- **Runtime-метрики**: Добавлены тайминги и счётчики по стадиям Telegram I/O, расширения Deep Mode, SQLite queue/flush/commit и записи DB export. Последняя сводка теперь сохраняется в `LOGS/telemetry_latest.json` и логируется как structured events во время массового `update`.

### Исправления (RU)
- Исправлена обработка смешанных timestamp между live-сообщениями Telegram и сообщениями, загруженными из SQLite: десериализация нормализована в UTC-aware `datetime`, что убирает ошибку сравнения `offset-naive` и `offset-aware` дат в deep scan.
- Исправлен порядок ключей в AI JSONL: при наличии `edit_date` теперь выводится первым, чтобы edited messages было проще читать глазами.

### Добавлено (RU)
- Добавлен `scripts/reset_and_seed_targets.py` для полной очистки локальной БД/экспортов и повторного заполнения `sync_targets` из `DB_TARGETS.txt` перед полным новым `update`.

## [4.2.2] - 2026-04-25

### Changed (EN)
- **Deep Mode Context Selection**: Reworked Deep Mode to prefer structural Telegram links (`reply_to_id`, reply chains, topic metadata) over loose message-id proximity, which sharply reduces unrelated context noise.
- **AI-Optimized DB Export**: `db-export --json` now emits a compact AI-oriented JSONL profile by default. The export keeps graph-relevant fields such as reply links, topic/thread metadata, edit timestamps, and cluster identifiers while dropping bulky raw Telethon payloads.
- **Writer State Location**: Export rotation state files are now stored under `DB_EXPORTS/.writer_state/` instead of cluttering the export directory root, with legacy state files migrated lazily.

### Fixed (EN)
- Fixed DB export naming so the filename prefix falls back to the target's real `author_name` from messages when the normalized `users` record is empty, instead of defaulting to raw numeric IDs.

### Изменения (RU)
- **Выбор контекста в Deep Mode**: Deep Mode переработан так, чтобы опираться на структурные Telegram-связи (`reply_to_id`, reply-chain, metadata topic/thread), а не на рыхлую близость по `message_id`, что заметно уменьшает шум в контексте.
- **AI-оптимизированный DB Export**: `db-export --json` теперь по умолчанию пишет компактный AI-ориентированный JSONL-профиль. Экспорт сохраняет поля, важные для графового анализа: reply-связи, metadata topic/thread, `edit_date` и cluster identifiers, но убирает тяжёлый raw Telethon payload.
- **Новый путь для writer state**: Состояние ротации экспорта теперь хранится в `DB_EXPORTS/.writer_state/`, а не засоряет корень каталога выгрузки; старые state-файлы лениво мигрируются.

### Исправления (RU)
- Исправлен нейминг DB-export файлов: если нормализованная запись в `users` пуста, префикс имени файла теперь берётся из реального `author_name` в сообщениях, а не скатывается к числовому ID.

## [4.2.1] - 2026-04-25

### Fixed (EN)
- Fixed `update` so it synchronizes every tracked primary target instead of only the currently outdated subset.
- Fixed whole-chat target handling during bulk update runs: targets with `user_id == chat_id` are now synchronized as full-chat targets instead of being misrouted as sender-filtered exports.

### Исправления (RU)
- Исправлена команда `update`: теперь она проходит по всем tracked primary targets, а не только по текущему устаревшему подмножеству.
- Исправлена обработка full-chat targets при массовом обновлении: цели с `user_id == chat_id` теперь синхронизируются как целый чат, а не ошибочно как экспорт с фильтром по отправителю.

## [4.2.0] - 2026-04-25

### Changed (EN)
- **SQLite Storage Refactor**: Split the storage layer into schema, write-path, read-path, and sync-state modules while preserving the public `SQLiteStorage` API.
- **Connection Discipline**: Centralized writes behind a locked shared transaction and moved read queries to dedicated read connections for more predictable SQLite usage.
- **Deep Mode Write Path**: Batched clustered/context message persistence to reduce write amplification during deep exports.
- **Export Semantics**: Clarified `--limit` behavior so it caps work inside a single `sync_chat` instead of multiplying across parallel workers.
- **TXT Rotation Resume**: Added sidecar writer state so text exports resume cleanly across runs without losing part counters.
- **Project Operations**: Added a minimal GitHub Actions CI workflow, local verification commands, and explicit known limitations in the docs.

### Fixed (EN)
- Fixed sync target freshness detection so old targets are not re-scanned forever after successful sync.
- Fixed target checkpoint corruption where context messages could advance another user's `last_msg_id`.
- Fixed cross-chat Deep Mode collisions by scoping processed message tracking to `(chat_id, message_id)`.
- Fixed `get_messages` FloodWait retries to preserve `limit`.
- Fixed PM archive persistence so archived PM messages are attributed to the target and refresh sync timestamps.
- Fixed CLI `delete` initialization so purge flows work even without a live Telegram client.
- Fixed orphan `message_target_links` cleanup when deleting messages from storage.
- Fixed signal handling tests so the full test suite no longer kills itself with a real `SIGINT`.

### Изменения (RU)
- **Рефактор SQLite Storage**: Хранилище разделено на модули schema, write-path, read-path и sync-state без изменения публичного API `SQLiteStorage`.
- **Дисциплина соединений**: Все записи централизованы через общий lock и shared transaction, а чтение переведено на отдельные read connections.
- **Deep Mode Write Path**: Сохранение кластеров и контекста переведено на пакетные записи, чтобы уменьшить write amplification при глубоких экспортах.
- **Семантика экспорта**: Поведение `--limit` уточнено: теперь ограничение действует в рамках одного `sync_chat`, а не умножается на число параллельных воркеров.
- **Resume для TXT-ротации**: Добавлено sidecar-состояние writer'а, чтобы текстовый экспорт корректно продолжался между запусками.
- **Операционная часть проекта**: Добавлены минимальный GitHub Actions CI, команды локальной проверки и раздел с known limitations в документации.

### Исправления (RU)
- Исправлено определение устаревших целей: старые targets больше не пересканируются бесконечно после успешной синхронизации.
- Исправлена порча checkpoint'ов, при которой контекстные сообщения могли продвигать `last_msg_id` другого пользователя.
- Исправлены cross-chat коллизии в Deep Mode: tracking обработанных сообщений теперь использует пару `(chat_id, message_id)`.
- Исправлены ретраи `get_messages` после FloodWait: теперь сохраняется `limit`.
- Исправлена запись `export-pm`: сообщения лички теперь корректно атрибутируются цели и обновляют sync timestamp.
- Исправлена инициализация CLI-команды `delete`, чтобы purge-сценарии работали без live Telegram client.
- Исправлена очистка orphan `message_target_links` при удалении сообщений из storage.
- Исправлены signal tests: полный test suite больше не убивает сам себя реальным `SIGINT`.

## [4.1.0] - 2026-04-21

### Changed (EN)
- **Enhanced CLI UX**: Redesigned user selection lists with better formatting: `author_name (ID) | Group Name`.
- **Interactive Sync Controls**: Added real-time prompts for Deep Mode and Recursive Depth in the main export menu.
- **Improved Progress Reporting**: Implemented a live counter showing the number of messages exported and the current Message ID being scanned.
- **Chat-like TXT Export**: Completely redesigned the plain text output with message grouping, date headers, and reply quotes for better readability.
- **Metadata Integrity**: Added explicit chat metadata tracking (`upsert_chat`) and fixed name mix-ups in the storage layer.
- **Infrastructure**: Optimized `.gitignore` for better protection of session and database artifacts.
- **Reliability & Performance**: 
  - Fixed a critical issue where emergency JSON exports were bypassed on Ctrl+C by switching to async-native signal handling.
  - Implemented 'Cached Skip' optimization: synchronized scans now skip context extraction for already-processed messages, drastically improving resume speed.
  - Resolved `TypeError` in the global update service and missing type imports.

### Изменения (RU)
- **Улучшенный интерфейс CLI**: Переработаны списки выбора пользователей: теперь отображается `Имя автора (ID) | Название группы`.
- **Интерактивное управление синхронизацией**: Добавлен запрос параметров Deep Mode и глубины рекурсии при запуске экспорта.
- **Улучшенная индикация прогресса**: Добавлен живой счетчик выгруженных сообщений и текущего ID сканируемого сообщения.
- **TXT-экспорт в стиле чата**: Полностью изменен формат текстовых файлов — теперь сообщения группируются по автору, добавлены заголовки дат и цитаты ответов.
- **Целостность данных**: Добавлено отслеживание метаданных групп и исправлена путаница имен пользователей и чатов.
- **Инфраструктура**: Оптимизирован `.gitignore` для надежного исключения файлов сессий и баз данных.
- **Надежность и Скорость**: 
  - Исправлена критическая проблема с игнорированием Ctrl+C и сбоем аварийного экспорта.
  - Внедрена оптимизация «Пропуск кеша», ускоряющая повторную синхронизацию в десятки раз.
  - Исправлен `TypeError` в режиме общего обновления и ошибки импортов.

### Fixed
- Resolved `AttributeError` in `DBExportService` related to wrong message ID attribute.
- Fixed `SyntaxError` (indentation) in `ExporterService` after UI updates.
- Corrected logic in `sync_chat` to prioritize user name for sync target registration.

## [4.0.0] - 2026-04-20
### Added
- **Target Attribution System**: Implemented a reference-counting mechanism using `message_target_links`. Every message and its surrounding context is now explicitly linked to a primary sync target.
- **Smart Purge (Garbage Collection)**: Redesigned the data removal logic. Context messages are now only deleted from the database if they are no longer referenced by any active sync target, preventing data orphans and preserving shared conversation context.
- **Async-Native Signal Handling**: Refactored the core process manager to use `asyncio.EventLoop.add_signal_handler`. This ensures immediate and reliable response to Ctrl+C (SIGINT) even during heavy I/O or network operations.
- **Emergency JSON Dumps**: Guaranteed export of partial data to `DB_EXPORTS/*.jsonl` upon interruption. The CLI now provides explicit feedback and the filesystem path of the dump.
- **Stateful Resume Engine**: Implemented a dual-sync model (Head/Tail) tracking synchronization boundaries per target. The system now skips already-synced history blocks and resumes instantly.

### Changed
- **Database Schema**: Significant upgrades to support normalization (`users`, `chats`, `message_target_links`).
- **Worker Logic**: Added granular shutdown checks to all export workers for immediate termination upon interrupt signals.
- **CLI UX**: Enhanced 24-bit ANSI gradient aesthetics and interactive sub-menu navigation.

### Fixed
- Resolved `NameError` in `process.py` by restoring missing `asyncio` imports.
- Fixed `AttributeError` in `Exporter` related to missing `should_stop` method in storage.
- Corrected database initialization logic to prevent missing table errors after full wipes.

## [3.5.0] - Previously
- Refactored project into modular `core/`, `services/`, `infrastructure/` layers.
- Implemented `TelethonClientWrapper` with advanced throttling and FloodWait protection.
- Added interactive terminal sub-menus with raw input support.
- Centralized logging into `LOGS/` directory.
