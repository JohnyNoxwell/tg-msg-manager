# STAGE 8 — Strengthen End-to-End and Fixture-Based Testing
## Цель этапа
Усилить тестовую базу: добавить обезличенные Telegram-like fixtures, fake Telegram client, fixture loaders и e2e tests для sync, context, export, retry и report. Тесты не должны ходить в сеть.
## Общие правила для ИИ-агента
1. Работать маленькими коммитоподобными изменениями.
2. Не менять публичное поведение CLI без явного указания.
3. Не менять схему SQLite без миграции и теста.
4. После каждого блока запускать релевантные тесты.
5. Если обнаружено расхождение между docs и кодом — считать код источником истины, docs исправлять.
6. Не добавлять новые фичи внутрь refactor-блоков.
7. Не удалять legacy-файлы без маркировки и проверки импортов.

## Блок 1. Fixture format

### Задача 1.1. Описать JSONL fixture format

Файлы:
- `tests/fixtures/telegram/README.md`

Действия для агента:
1. Определить поля: message_id, chat_id, user_id, author_name, timestamp, text, media_type, reply_to_id, fwd_from_id, context_group_id, is_service, media_ref, raw_payload.
2. Добавить advanced fields: reply_to_top_id, forum_topic_id, edit_date, reactions, deleted, fetch_error, download_error.
3. Запретить реальные user/chat data в fixtures.

Критерий готовности:
- Формат fixture документирован.
- Fake client может читать этот формат.

## Блок 2. Fake Telegram

### Задача 2.1. Реализовать FakeTelegramClient

Файлы:
- `tests/fakes/fake_telegram.py`

Действия для агента:
1. Поддержать `iter_messages(chat_id, ...)`.
2. Поддержать fetch by message id.
3. Поддержать fetch range.
4. Поддержать filter by sender_id и fallback-case.
5. Симулировать deleted/missing messages.
6. Симулировать FloodWait, permission error, media download.
7. Вести call history для assertions.

Критерий готовности:
- E2E tests не используют Telegram API.
- Поведение достаточно похоже на Telethon для нужных сценариев.

### Задача 2.2. Реализовать fixture loader

Файлы:
- `tests/fixtures/loaders.py`
- `tests/fakes/fake_storage_helpers.py`

Действия для агента:
1. Добавить `load_telegram_fixture(path)`.
2. Добавить `seed_storage_with_messages(storage, messages)`.
3. Добавить `create_temp_runtime(tmp_path)`.
4. Добавить helper для сравнения JSONL outputs.

Критерий готовности:
- Тесты не дублируют boilerplate.
- Fixtures легко переиспользовать.

## Блок 3. E2E sync/context

### Задача 3.1. Создать test_sync_e2e.py

Файлы:
- `tests/e2e/test_sync_e2e.py`

Действия для агента:
1. Покрыть first sync simple chat.
2. Покрыть incremental HEAD update.
3. Покрыть interrupted sync resume.
4. Покрыть TAIL completion.
5. Покрыть multi-target same chat with shared prefetch.
6. Покрыть duplicate dedup.
7. Покрыть edited message payload_hash change.
8. Покрыть service messages.

Критерий готовности:
- Sync проверяется end-to-end без сети.
- Проверяются storage state, sync_targets, message_target_links.

### Задача 3.2. Создать test_context_e2e.py

Файлы:
- `tests/e2e/test_context_e2e.py`

Действия для агента:
1. Покрыть parent reply included.
2. Покрыть child replies included.
3. Покрыть recursive depth.
4. Покрыть forum topic include/exclude.
5. Покрыть deleted parent marker.
6. Покрыть local cache before live fetch.
7. Покрыть time fallback condition.
8. Покрыть overlapping clusters merge.

Критерий готовности:
- Deep mode проверяется на реалистичных fixtures.
- Context group stability проверена.

## Блок 4. E2E export/retry/report

### Задача 4.1. Создать test_export_e2e.py

Файлы:
- `tests/e2e/test_export_e2e.py`

Действия для агента:
1. Покрыть JSONL compact export.
2. Покрыть TXT export.
3. Покрыть fingerprint skip.
4. Покрыть rebuild after DB changes.
5. Покрыть file rotation.
6. Покрыть writer state resume.
7. Покрыть include context quality, если Stage 6 выполнен.

Критерий готовности:
- Export проверяется от storage до файла.
- Manifest behavior покрыт.

### Задача 4.2. Создать retry/report e2e tests

Файлы:
- `tests/e2e/test_retry_e2e.py`
- `tests/e2e/test_report_e2e.py`

Действия для агента:
1. Для retry: temporary failure -> queued, worker succeeds later, max attempts -> failed, media retry complete file, delete already deleted = success, FloodWait -> next_attempt_at.
2. Для report: empty/populated DB, incomplete target warning, missing parent warning, retry warning, export outdated warning, JSON/Markdown shape.
3. Если соответствующие stages еще не внедрены — добавить skipped tests или TODO matrix, не ломая suite.

Критерий готовности:
- Retry/report имеют e2e покрытие или explicit placeholders.
- Suite не падает из-за невнедренных будущих фич.

## Блок 5. Fixtures

### Задача 5.1. Создать edge fixtures

Файлы:
- `tests/fixtures/telegram/`

Действия для агента:
1. Создать simple_chat.jsonl.
2. Создать reply_chain.jsonl.
3. Создать forum_topic.jsonl.
4. Создать multi_target.jsonl.
5. Создать deleted_parent.jsonl.
6. Создать edited_messages.jsonl.
7. Создать service_messages.jsonl.
8. Создать media_messages.jsonl.
9. Создать floodwait_scenario.jsonl.
10. Все IDs synthetic, timestamps deterministic, names обезличены.

Критерий готовности:
- Каждый edge case имеет fixture.
- Нет реальных приватных данных.

## Блок 6. Docs и test matrix

### Задача 6.1. Создать tests/README.md

Файлы:
- `tests/README.md`

Действия для агента:
1. Описать test layers: unit, fixture, e2e.
2. Описать как добавить fixture.
3. Описать как добавить fake Telegram behavior.
4. Описать команды запуска.
5. Зафиксировать запрет реальных данных и сети.

Критерий готовности:
- Новый разработчик может добавить тест корректно.
- Правила приватности ясны.

### Задача 6.2. Создать docs/TESTING_MATRIX.md

Файлы:
- `docs/TESTING_MATRIX.md`

Действия для агента:
1. Сделать таблицу feature -> unit tests -> fixture tests -> e2e tests -> missing coverage.
2. Включить config, storage, sync, deep context, db export, clean, private archive, retry, analytics, report, scheduler, alias manager.

Критерий готовности:
- Видны сильные и слабые места покрытия.
- Будущие тестовые задачи понятны.

## Definition of Done
1. Определен fixture JSONL format.
2. Есть FakeTelegramClient и fixture loader.
3. Есть e2e sync/context/export tests.
4. Есть retry/report tests или documented placeholders.
5. Есть edge case fixtures.
6. Есть tests README и testing matrix.
7. Тесты проходят без сети и реальных Telegram credentials.
