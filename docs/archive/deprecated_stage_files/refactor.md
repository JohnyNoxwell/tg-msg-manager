# STAGE 0 — REFACTOR FOUNDATION

## 0. Назначение документа

Этот документ описывает задачи для агента, который должен выполнить архитектурный рефакторинг проекта `tg-msg-manager` перед дальнейшим расширением функциональности.

Главная цель: укрепить фундамент приложения без изменения пользовательского поведения, CLI-команд, формата существующих экспортов и текущей логики синхронизации.

Рефакторинг должен быть безопасным, поэтапным и проверяемым.

---

# 1. Главная цель рефакторинга

Подготовить проект к дальнейшему масштабированию:

- deep context export;
- incremental export update;
- target-based exports;
- social graph / interaction mapping;
- behavioral analytics;
- semantic search;
- multi-account support;
- dashboard / API layer;
- более сложные стратегии контекстного анализа.

Текущая проблема: часть hot-path логики сосредоточена в слишком крупных сервисах и инфраструктурных файлах. При добавлении новых функций эти файлы начнут расти, смешивать ответственность и становиться fragile core.

Рефакторинг должен уменьшить связанность и разделить ответственность.

---

# 2. Строгие ограничения

## 2.1. Нельзя менять публичное поведение

Запрещено менять:

- названия CLI-команд;
- аргументы CLI-команд;
- дефолтные значения аргументов;
- формат вывода в консоль, если он используется тестами;
- формат существующих экспортируемых `.txt` файлов;
- имена существующих директорий экспорта;
- схему работы incremental sync;
- поведение deep-context export;
- логику выбора target user по `user_id`;
- текущую SQLite schema без отдельной миграции.

Если изменение поведения кажется необходимым — не делать его в этом этапе. Зафиксировать как TODO в отдельном разделе.

## 2.2. Нельзя добавлять новые продуктовые функции

Этот этап только про рефакторинг.

Запрещено добавлять:

- social graph;
- scoring пользователей;
- NLP-анализ;
- semantic search;
- dashboard;
- API;
- multi-account;
- новые export modes;
- новые CLI-команды, кроме строго служебных, если они уже предусмотрены архитектурой.

## 2.3. Нельзя ломать существующие тесты

Перед каждым крупным изменением:

1. Запустить текущие тесты.
2. Зафиксировать результат.
3. Внести минимальный refactor.
4. Запустить тесты снова.
5. Если тесты упали — исправить до перехода к следующему блоку.

## 2.4. Нельзя делать большой переписанный монолит

Запрещено:

- переписывать весь проект заново;
- заменять SQLite на другую БД;
- менять Telethon/Telegram integration layer;
- объединять уже разделенные слои обратно;
- переносить бизнес-логику в CLI;
- переносить SQL-запросы в сервисы верхнего уровня;
- добавлять аналитику внутрь `ExportService`;
- добавлять аналитику внутрь `ContextEngine`.

---

# 3. Архитектурные правила после рефакторинга

После выполнения этапа должны соблюдаться правила:

1. CLI остается thin layer.
2. CLI только парсит параметры и вызывает application/service layer.
3. Сервисный слой не должен содержать SQL.
4. Storage layer не должен знать о CLI.
5. Context logic не должна выполнять Telegram fetch напрямую.
6. Export logic не должна решать низкоуровневые SQL-детали.
7. Analytics не должна жить внутри export/context hot path.
8. Новые функции не добавляются в уже перегруженные файлы.
9. Каждый модуль имеет одну главную ответственность.
10. Любой refactor должен быть покрыт smoke/test проверкой.

---

# 4. Hot-path файлы, которые нужно разгрузить

Проверить фактические имена файлов в проекте. Если имя отличается, найти ближайший соответствующий файл по смыслу.

Основные кандидаты:

- `services/exporter.py`
- `services/context_engine.py`
- `services/private_archive.py`
- `infrastructure/storage/_sqlite_write_path.py`
- SQLite read-side aggregator modules
- CLI bootstrap / runtime entrypoints

Цель не удалить эти файлы, а уменьшить их ответственность.

---

# 5. Порядок выполнения

Работать строго по этапам:

1. Зафиксировать baseline.
2. Зафиксировать тесты и smoke-сценарии.
3. Разгрузить `ExportService`.
4. Разгрузить `ContextEngine`.
5. Разгрузить SQLite write-path.
6. Проверить read-side storage.
7. Отделить legacy/deprecated код.
8. Зафиксировать архитектурные правила.
9. Обновить документацию.
10. Финальная проверка.

Нельзя перескакивать к следующему этапу, если предыдущий не проверен.

---

# 6. ЭТАП 1 — Baseline и safety net

## 6.1. Цель

Перед изменениями зафиксировать текущее рабочее состояние проекта.

## 6.2. Атомарные задачи

### 6.2.1. Проверить структуру проекта

- Открыть корень проекта.
- Найти README.
- Найти архитектурную документацию.
- Найти директории:
  - `core`;
  - `services`;
  - `infrastructure`;
  - `cli`;
  - `tests`;
  - `scripts`, если есть.
- Зафиксировать текущую структуру в заметках агента.

### 6.2.2. Запустить тесты

- Определить тестовый раннер:
  - `pytest`;
  - `unittest`;
  - project-specific command.
- Запустить полный набор тестов.
- Зафиксировать:
  - команду запуска;
  - количество passed;
  - количество failed;
  - текст ошибок, если есть.

### 6.2.3. Запустить smoke-сценарии

Если в проекте есть smoke scripts или fixture-based E2E tests:

- Запустить sync smoke.
- Запустить context export smoke.
- Запустить export update smoke, если есть.
- Запустить retry/report smoke, если есть.
- Зафиксировать результаты.

### 6.2.4. Создать baseline note

Создать или обновить файл:

`docs/refactor/STAGE_0_BASELINE.md`

Внести туда:

- дату;
- commit hash;
- команду запуска тестов;
- результат тестов;
- список smoke-сценариев;
- известные проблемы до рефакторинга.

## 6.3. Критерии приемки

Этап завершен, если:

- тесты запущены;
- smoke-сценарии запущены или явно указано, почему не запущены;
- baseline зафиксирован в markdown-файле;
- нет незадокументированных исходных ошибок.

---

# 7. ЭТАП 2 — Зафиксировать публичное CLI-поведение

## 7.1. Цель

Гарантировать, что refactor не изменит поведение CLI.

## 7.2. Атомарные задачи

### 7.2.1. Найти CLI entrypoints

Проверить файлы:

- `cli.py`;
- `main.py`;
- `tg_msg_manager/cli.py`;
- `src/.../cli.py`;
- `pyproject.toml`;
- `setup.cfg`;
- `setup.py`.

Найти все console scripts.

### 7.2.2. Составить список CLI-команд

Для каждой команды зафиксировать:

- имя команды;
- аргументы;
- обязательные параметры;
- необязательные параметры;
- дефолтные значения;
- ожидаемый эффект.

Создать файл:

`docs/refactor/CLI_CONTRACT.md`

### 7.2.3. Добавить CLI contract tests

Если тестов нет:

- создать минимальные тесты help-output;
- проверить, что команды доступны;
- проверить, что старые аргументы принимаются;
- проверить, что help не падает.

Не проверять точный полный текст help, если он нестабилен. Проверять наличие ключевых команд и аргументов.

### 7.2.4. Проверить backward compatibility

После каждого изменения CLI:

- запускать CLI contract tests;
- не менять command names;
- не менять argument names;
- не менять defaults.

## 7.3. Критерии приемки

Этап завершен, если:

- создан `CLI_CONTRACT.md`;
- есть тесты, которые защищают базовую CLI-совместимость;
- текущие команды работают как до рефакторинга.

---

# 8. ЭТАП 3 — Разгрузить ExportService

## 8.1. Цель

Уменьшить ответственность `ExportService`.

`ExportService` должен быть orchestrator, а не складом всей логики экспорта, контекста, Telegram-fetch, checkpoint и записи.

## 8.2. Целевая структура

Создать или привести к похожей структуре:

```text
services/export/
    __init__.py
    service.py
    planner.py
    target_resolver.py
    fetch_orchestrator.py
    checkpoint_manager.py
    export_writer.py
    event_emitter.py
    models.py
```

Если структура проекта уже использует другой стиль — соблюдать существующий стиль, но сохранить разделение ответственности.

## 8.3. Атомарные задачи

### 8.3.1. Проанализировать текущий ExportService

- Открыть файл export service.
- Найти все публичные методы.
- Найти все приватные методы.
- Сгруппировать методы по ответственности:
  - planning;
  - target resolving;
  - Telegram fetching;
  - context integration;
  - DB write;
  - checkpoint;
  - formatting;
  - telemetry/events;
  - error handling.

### 8.3.2. Создать карту ответственности

Создать файл:

`docs/refactor/EXPORT_SERVICE_SPLIT_MAP.md`

Для каждого метода указать:

- текущее имя;
- текущий файл;
- ответственность;
- новый целевой модуль;
- переносится или остается;
- покрыт ли тестом.

### 8.3.3. Вынести planning logic

Создать модуль:

`services/export/planner.py`

Перенести туда только логику планирования экспорта.

Минимальные функции/классы:

- построение export plan;
- расчет диапазона сообщений;
- определение режима экспорта;
- подготовка target scope.

Запрещено:

- выполнять Telegram fetch;
- писать в SQLite;
- форматировать `.txt`;
- менять checkpoint.

### 8.3.4. Вынести target resolving

Создать модуль:

`services/export/target_resolver.py`

Перенести туда:

- разрешение target user по `user_id`;
- сопоставление target user с known identities;
- обработку nickname changes, если уже есть;
- подготовку target metadata для экспорта.

Запрещено:

- делать запись export file;
- менять основной sync state;
- смешивать target resolving с context building.

### 8.3.5. Вынести fetch orchestration

Создать модуль:

`services/export/fetch_orchestrator.py`

Перенести туда:

- вызовы Telegram client adapter;
- batching;
- pagination;
- retry delegation;
- обработку fetch limits.

Запрещено:

- хранить SQL;
- напрямую форматировать export text;
- принимать CLI args напрямую.

### 8.3.6. Вынести checkpoint management

Создать модуль:

`services/export/checkpoint_manager.py`

Перенести туда:

- чтение checkpoint;
- обновление checkpoint;
- проверку last exported message;
- защиту от duplicate export.

Checkpoint manager должен работать через storage interfaces, а не через raw SQL в сервисе.

### 8.3.7. Вынести file writing

Создать модуль:

`services/export/export_writer.py`

Перенести туда:

- создание export path;
- append-only запись;
- разделители;
- формат блока сообщений;
- update existing user file;
- работу с `EXPORTED_USRS`, если такая логика уже есть.

Запрещено:

- решать, какие сообщения надо экспортировать;
- ходить в Telegram;
- изменять database state.

### 8.3.8. Вынести event emission

Создать модуль:

`services/export/event_emitter.py`

Перенести туда:

- service events;
- telemetry events;
- progress events;
- report hooks.

Запрещено:

- добавлять бизнес-логику внутрь event emitter;
- делать emitter обязательным для чистых unit-тестов.

### 8.3.9. Оставить ExportService тонким

После переноса `ExportService` должен:

- принимать зависимости;
- вызывать planner;
- вызывать resolver;
- вызывать fetch orchestrator;
- вызывать context service, если нужно;
- вызывать writer;
- вызывать checkpoint manager;
- возвращать результат.

Он не должен:

- содержать SQL;
- содержать форматирование export file;
- содержать сложную context logic;
- содержать длинные вложенные циклы.

## 8.4. Критерии приемки

Этап завершен, если:

- `ExportService` стал orchestration layer;
- большая часть приватной логики вынесена в dedicated modules;
- CLI поведение не изменилось;
- export tests проходят;
- smoke export проходит;
- публичный API сервиса сохранен или адаптирован через compatibility wrapper.

---

# 9. ЭТАП 4 — Разгрузить ContextEngine

## 9.1. Цель

Разделить разные стратегии контекстного анализа.

`ContextEngine` не должен одновременно отвечать за reply-chain, neighbor-window, cluster building, dedup, scoring и форматирование.

## 9.2. Целевая структура

```text
services/context/
    __init__.py
    engine.py
    reply_chain_resolver.py
    neighbor_window_resolver.py
    cluster_builder.py
    deduplicator.py
    scope_policy.py
    models.py
```

## 9.3. Атомарные задачи

### 9.3.1. Проанализировать текущий ContextEngine

- Найти все методы.
- Разделить их по ответственности:
  - reply-to resolution;
  - parent message lookup;
  - child/reaction lookup;
  - neighbor messages before/after;
  - grouping into context cluster;
  - deduplication;
  - fallback behavior;
  - confidence/quality markers, если есть.

### 9.3.2. Создать карту разделения

Создать файл:

`docs/refactor/CONTEXT_ENGINE_SPLIT_MAP.md`

Для каждого метода указать:

- текущее имя;
- новая ответственность;
- новый модуль;
- тестовое покрытие;
- риски изменения поведения.

### 9.3.3. Вынести reply-chain resolver

Создать:

`services/context/reply_chain_resolver.py`

Он отвечает только за:

- поиск replied-to message;
- построение цепочки reply;
- ограничение глубины reply-chain;
- защиту от циклов;
- отсутствие reply target.

Запрещено:

- добавлять neighbor-window;
- форматировать export;
- писать в файл.

### 9.3.4. Вынести neighbor-window resolver

Создать:

`services/context/neighbor_window_resolver.py`

Он отвечает только за:

- N сообщений до target message;
- M сообщений после target message;
- ограничение по chat_id;
- ограничение по времени, если уже есть;
- стабильный порядок сообщений.

Запрещено:

- строить reply tree;
- делать NLP;
- писать в SQLite.

### 9.3.5. Вынести cluster builder

Создать:

`services/context/cluster_builder.py`

Он отвечает за:

- объединение reply-chain и neighbor-window;
- сортировку сообщений;
- присвоение `context_group_id`, если применимо;
- построение context cluster object.

Запрещено:

- делать fetch из Telegram;
- напрямую читать SQL;
- принимать CLI args.

### 9.3.6. Вынести deduplication

Создать:

`services/context/deduplicator.py`

Он отвечает за:

- удаление дублей по `message_id`;
- сохранение стабильного порядка;
- защиту от повторного включения target message;
- предотвращение пересечения соседних кластеров, если такая логика уже есть.

### 9.3.7. Вынести scope policy

Создать:

`services/context/scope_policy.py`

Он отвечает за правила:

- глубина контекста;
- лимиты before/after;
- max reply depth;
- fallback при отсутствии reply;
- поведение для media-only сообщений;
- поведение для deleted/unavailable messages.

### 9.3.8. Оставить ContextEngine фасадом

`ContextEngine` должен:

- принимать policy;
- вызывать resolvers;
- вызывать cluster builder;
- возвращать context result.

Он не должен:

- содержать SQL;
- форматировать export;
- управлять Telegram fetch;
- содержать длинные условные ветки по всем режимам.

## 9.4. Критерии приемки

Этап завершен, если:

- context logic разделена по стратегиям;
- старые context tests проходят;
- deep-context export дает тот же результат на fixtures;
- поведение с reply-to не изменилось;
- поведение neighbor-window не изменилось.

---

# 10. ЭТАП 5 — Разгрузить SQLite write-path

## 10.1. Цель

Разделить запись в SQLite по доменным операциям.

Write-path не должен быть одним большим файлом, где смешаны messages, users, target links, context links, checkpoints, retry state и reports.

## 10.2. Целевая структура

```text
infrastructure/storage/write/
    __init__.py
    connection.py
    transaction.py
    message_writer.py
    user_writer.py
    target_link_writer.py
    context_writer.py
    checkpoint_writer.py
    retry_writer.py
    report_writer.py
```

Если текущая структура уже частично разделена, не дублировать. Улучшить существующее разделение.

## 10.3. Атомарные задачи

### 10.3.1. Проанализировать `_sqlite_write_path.py`

- Найти все функции.
- Сгруппировать по типу записи:
  - messages;
  - users;
  - chats;
  - target links;
  - context links;
  - sync state;
  - checkpoints;
  - retries;
  - reports;
  - telemetry.

### 10.3.2. Создать карту разделения

Создать файл:

`docs/refactor/SQLITE_WRITE_PATH_SPLIT_MAP.md`

Для каждой функции указать:

- текущее имя;
- целевой writer;
- транзакционные требования;
- используется ли batch insert;
- есть ли side effects.

### 10.3.3. Вынести message writer

Создать:

`infrastructure/storage/write/message_writer.py`

Он отвечает за:

- insert/update messages;
- batch upsert messages;
- сохранение message metadata;
- обработку конфликтов по message_id/chat_id.

Запрещено:

- писать checkpoint;
- писать export files;
- решать target attribution.

### 10.3.4. Вынести user writer

Создать:

`infrastructure/storage/write/user_writer.py`

Он отвечает за:

- insert/update users;
- nickname updates;
- username updates;
- сохранение user identity history, если уже есть.

Запрещено:

- экспортировать user files;
- смешивать user write с message write без транзакционного координатора.

### 10.3.5. Вынести target link writer

Создать:

`infrastructure/storage/write/target_link_writer.py`

Он отвечает за:

- запись `message_target_links`;
- связь message -> target user;
- тип связи, если есть;
- dedup links.

Запрещено:

- решать саму target attribution policy;
- читать Telegram напрямую.

### 10.3.6. Вынести context writer

Создать:

`infrastructure/storage/write/context_writer.py`

Он отвечает за:

- запись context group metadata;
- запись context links, если таблица используется;
- compatibility с legacy context tables.

Если `message_context_links` является legacy:

- не удалять таблицу;
- пометить в документации;
- не использовать как primary hot path без отдельного решения.

### 10.3.7. Вынести checkpoint writer

Создать:

`infrastructure/storage/write/checkpoint_writer.py`

Он отвечает за:

- sync checkpoint;
- export checkpoint;
- last processed message id;
- last exported message id;
- atomic update.

### 10.3.8. Вынести retry writer

Создать:

`infrastructure/storage/write/retry_writer.py`

Он отвечает за:

- failed item storage;
- retry status;
- retry counters;
- last error;
- next retry time, если есть.

### 10.3.9. Вынести transaction coordinator

Создать:

`infrastructure/storage/write/transaction.py`

Он отвечает за:

- начало транзакции;
- commit;
- rollback;
- batch policy;
- write lock behavior;
- shared connection rules.

Запрещено:

- размещать domain-specific SQL в transaction coordinator.

### 10.3.10. Сохранить compatibility layer

Если старые сервисы импортируют `_sqlite_write_path.py`, оставить compatibility wrapper:

- старые функции должны вызывать новые writer modules;
- deprecated imports не должны ломаться сразу;
- добавить TODO на удаление wrapper в следующем этапе.

## 10.4. Критерии приемки

Этап завершен, если:

- write-path разделен;
- старые импорты не сломаны или мигрированы;
- DB tests проходят;
- sync smoke проходит;
- export smoke проходит;
- нет raw SQL в service layer.

---

# 11. ЭТАП 6 — Проверить SQLite read-side

## 11.1. Цель

Убедиться, что read-side storage не превращается обратно в монолит.

## 11.2. Атомарные задачи

### 11.2.1. Найти read-side modules

Проверить:

- message queries;
- user queries;
- context queries;
- export queries;
- report queries;
- stats queries.

### 11.2.2. Проверить ответственность

Каждый read module должен отвечать за один тип чтения.

Плохо:

```text
sqlite_reader.py
```

содержит всё.

Хорошо:

```text
message_reader.py
user_reader.py
context_reader.py
export_reader.py
analytics_reader.py
```

### 11.2.3. Проверить отсутствие business logic

Read-side modules могут:

- выполнять SQL;
- маппить rows в модели;
- возвращать DTO.

Read-side modules не должны:

- решать export policy;
- строить context clusters;
- форматировать файлы;
- выполнять Telegram fetch;
- делать scoring пользователей.

### 11.2.4. Подготовить analytics read boundary

Создать пустой или минимальный namespace:

```text
infrastructure/storage/read/analytics/
```

или аналогичный, если стиль проекта другой.

Не реализовывать аналитику. Только подготовить место и правило: будущие analytics queries живут здесь, а не в export/context service.

## 11.3. Критерии приемки

Этап завершен, если:

- read-side разделен или задокументирован;
- нет очевидного монолитного reader growth point;
- analytics boundary подготовлен;
- тесты проходят.

---

# 12. ЭТАП 7 — Legacy и deprecated код

## 12.1. Цель

Снизить риск путаницы из-за старых скриптов, таблиц и compatibility paths.

## 12.2. Атомарные задачи

### 12.2.1. Найти legacy scripts

Проверить директории:

- `scripts`;
- `legacy`;
- `tools`;
- корень проекта;
- старые one-off файлы.

### 12.2.2. Классифицировать каждый script

Для каждого файла определить:

- active;
- compatibility;
- manual tool;
- deprecated;
- unknown.

### 12.2.3. Создать legacy inventory

Создать файл:

`docs/refactor/LEGACY_INVENTORY.md`

Для каждого legacy-файла указать:

- путь;
- назначение;
- используется ли сейчас;
- можно ли удалить;
- почему пока не удаляется;
- чем заменить.

### 12.2.4. Пометить deprecated code

Если код нельзя удалить:

- добавить docstring/comment `DEPRECATED`;
- указать replacement;
- указать planned removal stage.

Пример:

```python
# DEPRECATED: kept for backward compatibility.
# Use infrastructure.storage.write.message_writer instead.
# Planned removal: Stage 1 cleanup after compatibility tests.
```

### 12.2.5. Не удалять без тестов

Удалять legacy-файлы можно только если:

- есть доказательство, что они не импортируются;
- тесты проходят;
- CLI не использует их;
- есть запись в changelog.

## 12.3. Критерии приемки

Этап завершен, если:

- создан `LEGACY_INVENTORY.md`;
- deprecated paths помечены;
- ничего критичное не удалено вслепую;
- тесты проходят.

---

# 13. ЭТАП 8 — Архитектурные guardrails

## 13.1. Цель

Зафиксировать правила, чтобы после рефакторинга новые функции не портили архитектуру.

## 13.2. Атомарные задачи

### 13.2.1. Создать architecture rules document

Создать файл:

`docs/ARCHITECTURE_RULES.md`

Включить правила:

- CLI thin only.
- Services do not contain SQL.
- Storage does not import services.
- Context logic is isolated.
- Export logic is orchestration only.
- Analytics reads normalized data.
- No new features in hot-path files.
- No raw Telegram calls outside adapter/fetch layer.
- No direct filesystem writes outside writer/export modules.
- No schema changes without migration note.

### 13.2.2. Добавить hot-path protection note

В `docs/ARCHITECTURE_RULES.md` добавить список файлов, куда запрещено добавлять новые крупные функции:

- `services/exporter.py`;
- `services/context_engine.py`;
- `services/private_archive.py`;
- `_sqlite_write_path.py`;
- другие найденные hot-path файлы.

Новые функции должны создаваться в новых dedicated modules.

### 13.2.3. Добавить PR/refactor checklist

Создать файл:

`docs/PR_CHECKLIST.md`

Минимальный checklist:

```markdown
- [ ] CLI behavior unchanged
- [ ] Tests pass
- [ ] Smoke scenario checked
- [ ] No raw SQL in service layer
- [ ] No new feature added to hot-path files
- [ ] New module has single responsibility
- [ ] Docs updated if architecture changed
- [ ] Legacy path marked if retained
```

### 13.2.4. Обновить README или architecture overview

Добавить короткий раздел:

- где живет CLI;
- где живет service orchestration;
- где живет context logic;
- где живет storage write;
- где в будущем должна жить analytics logic.

## 13.3. Критерии приемки

Этап завершен, если:

- создан `ARCHITECTURE_RULES.md`;
- создан `PR_CHECKLIST.md`;
- README/architecture overview обновлен;
- правила соответствуют фактической структуре проекта.

---

# 14. ЭТАП 9 — Тестовое покрытие после refactor

## 14.1. Цель

Проверить, что refactor не изменил поведение.

## 14.2. Минимальные проверки

### 14.2.1. Unit tests

Запустить все unit tests.

### 14.2.2. CLI tests

Проверить:

- help;
- основные команды;
- backward-compatible args.

### 14.2.3. Storage tests

Проверить:

- message write;
- user write;
- target links;
- context links;
- checkpoint write;
- retry write.

### 14.2.4. Export tests

Проверить:

- обычный export;
- deep context export;
- reply context export;
- append-only update;
- duplicate protection.

### 14.2.5. Fixture-based E2E

Проверить полный сценарий:

```text
fixture input -> sync -> context build -> export -> update -> report
```

### 14.2.6. Regression check

Сравнить output до и после refactor на одном и том же fixture.

Если output отличается:

- объяснить почему;
- если отличие не планировалось — исправить;
- если отличие неизбежно — вынести в отдельное решение, но не смешивать с этим refactor stage.

## 14.3. Критерии приемки

Этап завершен, если:

- тесты проходят;
- smoke проходит;
- fixture output не изменился без причины;
- regressions отсутствуют или задокументированы.

---

# 15. Финальный отчет агента

После завершения refactor агент должен создать файл:

`docs/refactor/STAGE_0_REFACTOR_REPORT.md`

## 15.1. Структура отчета

```markdown
# Stage 0 Refactor Report

## 1. Summary

Кратко: что изменено.

## 2. Files changed

Таблица:
| File | Change type | Reason |

## 3. Extracted modules

Таблица:
| Old location | New module | Responsibility |

## 4. Behavior compatibility

- CLI changed: yes/no
- Export format changed: yes/no
- DB schema changed: yes/no
- Tests passed: yes/no

## 5. Test results

Команды и результаты.

## 6. Known risks

Список оставшихся рисков.

## 7. Deferred tasks

Что не сделано намеренно и почему.

## 8. Next recommended stage

Что делать после этого refactor.
```

---

# 16. Definition of Done

Stage 0 считается завершенным только если выполнены все условия:

- [x] Baseline зафиксирован.
- [x] CLI contract зафиксирован.
- [x] Тесты проходят.
- [x] Smoke-сценарии проходят или причины пропуска документированы.
- [x] `ExportService` разгружен.
- [x] `ContextEngine` разгружен.
- [x] SQLite write-path разделен.
- [x] Read-side storage проверен.
- [x] Legacy inventory создан.
- [x] Architecture rules созданы.
- [x] PR checklist создан.
- [x] README/architecture overview обновлен.
- [x] Финальный refactor report создан.
- [x] Публичное CLI-поведение не изменено.
- [x] Export output не изменен без отдельного решения.
- [x] Новые продуктовые функции не добавлены.

---

# 17. Запрещенные решения

Во время этого этапа нельзя:

- менять CLI UX;
- менять формат `.txt` exports;
- менять naming exported user files;
- менять default context depth;
- менять default sync behavior;
- менять SQLite schema без миграции;
- добавлять social graph;
- добавлять NLP;
- добавлять scoring;
- добавлять dashboard;
- добавлять API;
- добавлять multi-account;
- удалять legacy без проверки импортов;
- смешивать refactor и feature development;
- делать “big bang rewrite”.

---

# 18. Разрешенные решения

Во время этого этапа можно:

- переносить код в новые модули;
- добавлять compatibility wrappers;
- добавлять unit tests;
- добавлять smoke tests;
- добавлять документацию;
- добавлять internal DTO/models;
- добавлять protocols/interfaces;
- улучшать naming внутри private/internal API;
- уменьшать размер hot-path файлов;
- удалять dead code только при доказанной безопасности;
- помечать legacy code deprecated;
- улучшать dependency injection;
- упрощать циклы и условия без изменения поведения.

---

# 19. Приоритеты для агента

Если возникает конфликт между задачами, применять приоритет:

1. Сохранить работоспособность.
2. Не менять публичное поведение.
3. Не ломать тесты.
4. Уменьшить связанность.
5. Разделить ответственность.
6. Улучшить читаемость.
7. Обновить документацию.

Если изменение повышает красоту кода, но рискует поведением — не делать.

---

# 20. Короткая инструкция для агента

Выполняй refactor маленькими шагами.

После каждого логического переноса:

1. Запусти релевантные тесты.
2. Проверь CLI contract.
3. Проверь smoke, если затронут hot path.
4. Зафиксируй изменение в refactor report.
5. Не добавляй новые функции.
6. Не меняй поведение без отдельного решения.

Главный результат этого этапа: проект должен стать легче расширять, но пользователь не должен заметить изменений в работе приложения.
