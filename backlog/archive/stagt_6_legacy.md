# STAGE 6 — Add Context Extraction Quality Metrics
## Цель этапа
Добавить deterministic quality metadata для context clusters: откуда контекст взят, насколько он структурный, использовался ли fallback, есть ли missing parents/fetch failures и confidence score.
## Общие правила для ИИ-агента
1. Работать маленькими коммитоподобными изменениями.
2. Не менять публичное поведение CLI без явного указания.
3. Не менять схему SQLite без миграции и теста.
4. После каждого блока запускать релевантные тесты.
5. Если обнаружено расхождение между docs и кодом — считать код источником истины, docs исправлять.
6. Не добавлять новые фичи внутрь refactor-блоков.
7. Не удалять legacy-файлы без маркировки и проверки импортов.

## Блок 1. Модель качества

### Задача 1.1. Создать ContextQualityMetrics

Файлы:
- `tg_msg_manager/services/context/models.py`
- `tg_msg_manager/core/models/context_quality.py`

Действия для агента:
1. Добавить поля cluster_id, target_user_id, chat_id, message_count, target_message_count, context_message_count.
2. Добавить reply_edge_count, parent_reply_count, child_reply_count, thread_context_count, time_fallback_count.
3. Добавить live_fetch_count, local_cache_count, missing_parent_count, failed_fetch_count.
4. Добавить fallback_used, has_parent, has_child_reply, has_thread_context, time_span_seconds, confidence, quality_flags.

Критерий готовности:
- Модель сериализуется в JSON.
- Модель не зависит от Telegram client.

### Задача 1.2. Добавить source metadata к candidates

Файлы:
- `tg_msg_manager/services/context/`

Действия для агента:
1. Для каждого context candidate хранить semantic_source: target, parent_reply, child_reply, thread, time_fallback.
2. Хранить retrieval_source: local_cache или live_fetch.
3. Обновить resolvers, чтобы source не терялся при merge.

Критерий готовности:
- Понятно, почему сообщение попало в cluster.
- Понятно, откуда оно было получено.

## Блок 2. Scorer

### Задача 2.1. Реализовать ContextQualityScorer

Файлы:
- `tg_msg_manager/services/context/scoring.py`

Действия для агента:
1. Посчитать все count-поля.
2. Посчитать time span.
3. Сформировать flags: no_structural_context, only_time_fallback, missing_reply_parent, live_fetch_failed, large_time_gap, single_message_cluster, mixed_thread_context.
4. Рассчитать confidence: base 0.10, parent +0.25, child +0.20, thread +0.20, reply_edge>=3 +0.10, multiple target +0.10, fallback -0.10, caps for fallback-only/single-message, penalties for missing/fail, clamp 0..1.
5. Не использовать score для фильтрации сообщений на этом этапе.

Критерий готовности:
- Score deterministic.
- Same cluster -> same score.

## Блок 3. Storage/export

### Задача 3.1. Выбрать и реализовать storage strategy

Файлы:
- `tg_msg_manager/infrastructure/storage/`
- `docs/ARCHITECTURE.md`

Действия для агента:
1. Если `context_group_id` стабилен — создать таблицу `context_cluster_quality`.
2. Если нет — сначала экспортировать metrics без storage migration.
3. Если создается таблица: context_group_id TEXT PRIMARY KEY, target_user_id, chat_id, metrics_json, confidence, updated_at.
4. Добавить storage API upsert/get/iter quality.

Критерий готовности:
- Выбранный подход документирован.
- Storage migration безопасна, если она есть.

### Задача 3.2. Обновить JSONL/TXT export

Файлы:
- `tg_msg_manager/services/db_exporter.py`
- `COMMANDS.md`

Действия для агента:
1. Добавить флаг `--include-context-quality` для JSONL.
2. Добавить флаг `--include-quality` для human export, если нужно.
3. Если metrics нет — не падать.
4. Не менять старый compact export без флага.

Критерий готовности:
- AI JSONL может содержать quality hints.
- Backward compatibility сохранена.

## Блок 4. Quality report

### Задача 4.1. Добавить CLI context-quality

Файлы:
- `tg_msg_manager/cli.py`
- `tg_msg_manager/services/reporting/`
- `COMMANDS.md`

Действия для агента:
1. Команды: `context-quality --user-id`, `context-quality --chat-id`, combined filters.
2. Считать total clusters, average/median confidence, fallback clusters, missing parents, failed fetch, low-confidence clusters.
3. Добавить confidence buckets: 0-0.20, 0.21-0.45, 0.46-0.70, 0.71-0.90, 0.91-1.00.
4. Команда работает без Telegram API.

Критерий готовности:
- Пользователь видит качество dataset.
- Отчет read-only.

## Блок 5. Tests

### Задача 5.1. Покрыть scoring и export

Файлы:
- `tests/`

Действия для агента:
1. Тест parent only score.
2. Тест child replies score.
3. Тест thread context score.
4. Тест only fallback cap.
5. Тест missing parent penalty.
6. Тест failed fetch penalty.
7. Тест single message cap.
8. Тест JSON serialization.
9. Тест export with quality flag.
10. Тест quality report buckets.

Критерий готовности:
- Scoring правила зафиксированы тестами.
- Все тесты проходят.

## Definition of Done
1. Есть `ContextQualityMetrics`.
2. Candidates имеют semantic/retrieval source.
3. Есть deterministic scorer.
4. Quality export добавлен без ломки старого формата.
5. Есть `context-quality` report.
6. Все тесты проходят.
