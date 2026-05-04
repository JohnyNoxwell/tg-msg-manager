# STAGE 7 — Add Audit / Report Mode
## Цель этапа
Добавить read-only audit/report режим для оценки состояния БД, targets, checkpoints, context coverage, retry queue и export state. Отчет должен помогать понять полноту данных и проблемы pipeline.
## Общие правила для ИИ-агента
1. Работать маленькими коммитоподобными изменениями.
2. Не менять публичное поведение CLI без явного указания.
3. Не менять схему SQLite без миграции и теста.
4. После каждого блока запускать релевантные тесты.
5. Если обнаружено расхождение между docs и кодом — считать код источником истины, docs исправлять.
6. Не добавлять новые фичи внутрь refactor-блоков.
7. Не удалять legacy-файлы без маркировки и проверки импортов.

## Блок 1. Models и read queries

### Задача 1.1. Создать reporting models

Файлы:
- `tg_msg_manager/services/reporting/models.py`

Действия для агента:
1. Создать `DatabaseReport`, `TargetReport`, `ChatCoverageReport`, `UserCoverageReport`, `CheckpointReport`, `ContextCoverageReport`, `ExportStateReport`, `ReportWarning`.
2. Для TargetReport включить user_id, chat_id, author_name, message_count, context_count, first/last message, last_msg_id, tail_msg_id, is_complete, deep_mode, recursive_depth, last_sync_at, warnings.

Критерий готовности:
- Report data типизирован.
- JSON serialization работает.

### Задача 1.2. Добавить storage read methods

Файлы:
- `tg_msg_manager/infrastructure/storage/interface.py`
- `_sqlite_read_path.py`

Действия для агента:
1. Добавить database summary.
2. Добавить list sync targets.
3. Добавить target report.
4. Добавить chat/user coverage.
5. Добавить context coverage.
6. Добавить missing reply parent count.
7. Добавить orphan message count.
8. Не писать SQL в collector.

Критерий готовности:
- Reporting работает через storage abstraction.
- Все запросы read-only.

## Блок 2. Collector и warnings

### Задача 2.1. Реализовать ReportCollector

Файлы:
- `tg_msg_manager/services/reporting/collector.py`

Действия для агента:
1. Собрать database report из storage.
2. Собрать user/chat/target reports.
3. Прочитать `.export_state`, если есть.
4. Прочитать retry summary, если retry schema доступна.
5. Вернуть typed model, ничего не печатать.

Критерий готовности:
- Collector чисто собирает данные.
- Нет Telegram API calls.

### Задача 2.2. Реализовать coverage warning rules

Файлы:
- `tg_msg_manager/services/reporting/coverage.py`

Действия для агента:
1. Добавить warnings: target_not_complete, no_messages_for_target, no_context_messages, high_missing_parent_count, retry_queue_not_empty, failed_retry_tasks, export_manifest_missing, export_outdated, large_db_wal, legacy_config_detected, stale_sync.
2. Сделать thresholds documented или configurable.
3. Не выдавать subjective warnings.

Критерий готовности:
- Warnings deterministic.
- Каждый warning имеет причину и recommended action.

## Блок 3. Renderer

### Задача 3.1. Реализовать Markdown renderer

Файлы:
- `tg_msg_manager/services/reporting/renderer.py`

Действия для агента:
1. Секции: Database Summary, Targets, Chat Coverage, User Coverage, Context Coverage, Retry Queue, Export State, Warnings, Recommended Actions.
2. Для destructive commands писать предупреждение.
3. Recommended actions должны быть механическими: run retry, run db-export, run update.

Критерий готовности:
- Markdown читаемый.
- Рекомендации не опасны без предупреждения.

### Задача 3.2. Реализовать JSON renderer

Файлы:
- `tg_msg_manager/services/reporting/renderer.py`

Действия для агента:
1. Сериализовать typed report model.
2. Стабилизировать field names.
3. Не включать raw_payload и credentials.

Критерий готовности:
- JSON пригоден для automated checks.
- Нет приватных API secrets.

## Блок 4. CLI integration

### Задача 4.1. Добавить report subcommand

Файлы:
- `tg_msg_manager/cli.py`
- `COMMANDS.md`

Действия для агента:
1. Добавить `report`, `report user --user-id`, `report chat --chat-id`, `report target --user-id --chat-id`.
2. Флаги: `--format md|json`, `--output`, `--include-export-state`, `--include-retry`, `--warnings-only`.
3. Команда должна работать без Telegram client.
4. Если output указан — писать файл и печатать путь.

Критерий готовности:
- Audit report можно получить быстро и безопасно.
- Команда документирована.

## Блок 5. Export/retry integration

### Задача 5.1. Интегрировать export state и retry state

Файлы:
- `tg_msg_manager/services/reporting/collector.py`
- `tg_msg_manager/services/db_exporter.py`

Действия для агента:
1. Safe-read `.export_state` manifest.
2. Если manifest отсутствует — warning, не exception.
3. Если export parts отсутствуют — warning.
4. Если fingerprint outdated — warning.
5. Если retry API есть — добавить pending/failed counts; если нет — graceful skip.

Критерий готовности:
- Report показывает актуальность db-export.
- Report совместим до/после Stage 4.

## Блок 6. Tests

### Задача 6.1. Добавить report tests

Файлы:
- `tests/`

Действия для агента:
1. Покрыть empty DB, populated DB, complete/incomplete target, deep mode without context warning, retry warning, missing export manifest, Markdown shape, JSON shape, CLI output file, no Telegram client creation.

Критерий готовности:
- Report behavior покрыт.
- Все тесты проходят.

## Definition of Done
1. Есть `services/reporting/`.
2. Есть typed reports, collector, coverage rules, renderers.
3. CLI `report` работает read-only без Telegram.
4. Report показывает targets/checkpoints/context/retry/export state.
5. Все тесты проходят.
