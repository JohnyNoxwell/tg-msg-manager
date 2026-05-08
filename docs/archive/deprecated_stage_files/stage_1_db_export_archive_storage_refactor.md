# STAGE 1 — DB EXPORT / ARCHIVE / STORAGE CONTRACTS REFACTOR

## 0. Назначение документа

Этот документ описывает следующий этап рефакторинга проекта `tg-msg-manager` после Stage 0.

Stage 0 разгрузил основные hot-path зоны:

- `ExportService`;
- `ContextEngine`;
- SQLite read-side;
- SQLite write-side;
- CLI entrypoint.

Stage 1 должен убрать новые точки архитектурного давления, которые стали видны после первого рефакторинга:

- `DBExportService`;
- `PrivateArchiveService`;
- слишком широкие storage interfaces;
- крупные service/event payload modules;
- не до конца оформленная analytics boundary;
- неопределенный статус legacy/context relation tables.

Цель Stage 1: подготовить проект к будущим расширениям без добавления новых продуктовых функций.

---

# 1. Главная цель Stage 1

Создать более устойчивую архитектурную основу для будущих направлений:

- DB-first exports;
- replayable exports;
- large dataset exports;
- private archive processing;
- AI-ready datasets;
- social graph;
- behavioral analytics;
- semantic search;
- multi-account / workspace isolation;
- API/dashboard layer.

На этом этапе нельзя реализовывать эти функции. Нужно подготовить архитектуру так, чтобы их можно было добавить позже без роста монолитов.

---

# 2. Главный инженерный диагноз

После Stage 0 основные риски сместились.

Раньше главными рисками были:

- слишком крупный `ExportService`;
- слишком крупный `ContextEngine`;
- смешанный SQLite read/write path.

Теперь главные риски:

1. `DBExportService` становится новым монолитом.
2. `PrivateArchiveService` может стать параллельным пайплайном с дублированием sync/export логики.
3. Storage interfaces слишком широкие и дают сервисам лишнее знание о хранилище.
4. Event/service payload models могут превратиться в общую DTO-свалку.
5. Analytics boundary есть, но пока недостаточно защищена правилами.
6. `message_context_links` / context relation tables требуют официального решения: first-class или legacy.
7. Live Telegram smoke coverage всё ещё слабое.

---

# 3. Строгие ограничения

## 3.1. Запрещено менять публичное поведение

Нельзя менять:

- CLI-команды;
- CLI-аргументы;
- дефолтные значения;
- формат существующих `.txt` exports;
- формат существующих `.json` / `.jsonl` exports, если они уже используются;
- имена экспортируемых файлов;
- имена export directories;
- логику incremental export;
- логику duplicate protection;
- логику target attribution;
- storage schema без явной миграции;
- текущие контекстные режимы.

## 3.2. Запрещено добавлять новые продуктовые функции

На Stage 1 нельзя добавлять:

- social graph;
- influence scoring;
- behavioral profiling;
- NLP;
- semantic search;
- embeddings;
- dashboard;
- REST API;
- web UI;
- multi-account;
- новые Telegram collectors;
- новые export modes;
- новые пользовательские CLI-команды.

Исключение: разрешены только внутренние compatibility commands/tests, если они нужны для проверки refactor. Они не должны становиться публичной feature surface без отдельного этапа.

## 3.3. Запрещено делать big-bang rewrite

Нельзя:

- переписывать проект целиком;
- менять БД;
- заменять SQLite;
- менять Telegram client adapter;
- менять весь export pipeline одним коммитом;
- удалять legacy paths без тестов;
- объединять уже разделенные Stage 0 модули обратно.

## 3.4. Запрещено смешивать refactor и feature development

Каждый коммит должен быть либо:

- extraction;
- rename;
- interface split;
- compatibility wrapper;
- test;
- docs update;
- dead-code/legacy cleanup.

Если изменение меняет поведение — остановиться и вынести в отдельный будущий stage.

---

# 4. Архитектурный результат Stage 1

После Stage 1 должно быть так:

1. `DBExportService` — тонкий orchestration facade.
2. DB export логика разделена на специализированные компоненты.
3. `PrivateArchiveService` не дублирует export/sync/write логику.
4. Storage contracts разделены по use-case protocols.
5. Event payloads разделены по доменам.
6. Analytics read model имеет явную директорию и правила.
7. Context relation tables имеют официальный статус.
8. Live/manual smoke checklist существует.
9. Документация отражает фактическую архитектуру.
10. Все тесты и regression checks проходят.

---

# 5. Целевые зоны Stage 1

Проверить фактические пути в проекте. Если имена отличаются, использовать ближайшие соответствующие модули по смыслу.

Основные зоны:

```text
tg_msg_manager/services/db_exporter.py
tg_msg_manager/services/private_archive.py
tg_msg_manager/infrastructure/storage/interface.py
tg_msg_manager/core/models/service_payloads.py
tg_msg_manager/infrastructure/storage/read/analytics/
tg_msg_manager/infrastructure/storage/write/
tg_msg_manager/services/context/
tg_msg_manager/services/export/
tests/
docs/
```

---

# 6. Порядок выполнения

Работать строго по этапам:

1. Зафиксировать Stage 1 baseline.
2. Разгрузить `DBExportService`.
3. Разгрузить `PrivateArchiveService`.
4. Разделить storage contracts.
5. Разделить service/event payload models.
6. Оформить analytics boundary.
7. Решить статус context relation tables.
8. Добавить live/manual smoke checklist.
9. Обновить architecture docs.
10. Провести финальную regression-проверку.
11. Создать Stage 1 report.

---

# 7. ЭТАП 1 — Stage 1 Baseline

## 7.1. Цель

Перед изменениями зафиксировать текущее состояние после Stage 0.

## 7.2. Атомарные задачи

### 7.2.1. Зафиксировать commit hash

Выполнить:

```bash
git rev-parse HEAD
git status --short
```

Зафиксировать:

- текущий commit hash;
- есть ли незакоммиченные изменения;
- текущую ветку.

### 7.2.2. Запустить полный test suite

Выполнить существующие команды проекта, например:

```bash
make test
make verify
```

Если таких команд нет, определить актуальные команды через README / pyproject.

Зафиксировать:

- команду;
- passed;
- failed;
- skipped;
- duration;
- ошибки, если есть.

### 7.2.3. Запустить линтеры и формат-проверки

Если доступны:

```bash
make lint
make format-check
```

Зафиксировать результат.

### 7.2.4. Запустить offline fixture E2E

Если есть fixture-based E2E:

```bash
python -m tests.test_fixture_e2e
```

Или актуальную команду проекта.

Зафиксировать:

- input fixture;
- output path;
- результат;
- изменился ли output.

### 7.2.5. Создать baseline document

Создать файл:

```text
docs/refactor/STAGE_1_BASELINE.md
```

Структура:

```markdown
# Stage 1 Baseline

## 1. Commit

## 2. Git status

## 3. Test commands

## 4. Test results

## 5. Fixture E2E results

## 6. Known pre-existing issues

## 7. Files targeted by Stage 1
```

## 7.3. Критерии приемки

Этап завершен, если:

- baseline создан;
- тесты запущены;
- ошибки до рефакторинга задокументированы;
- нет незафиксированных неизвестных регрессий.

---

# 8. ЭТАП 2 — Разгрузить DBExportService

## 8.1. Цель

`DBExportService` должен стать тонким orchestration layer.

Он не должен одновременно отвечать за:

- загрузку данных;
- построение export plan;
- skip policy;
- fingerprinting;
- state management;
- rendering;
- file writing;
- run reporting;
- error mapping;
- progress events.

## 8.2. Целевая структура

Создать директорию:

```text
tg_msg_manager/services/db_export/
    __init__.py
    service.py
    source_loader.py
    plan_builder.py
    skip_policy.py
    state_manager.py
    payload_writer.py
    txt_renderer.py
    jsonl_renderer.py
    manifest_writer.py
    event_emitter.py
    models.py
```

Если проект уже имеет похожую структуру, не дублировать. Улучшить текущую структуру.

Оставить старый файл `services/db_exporter.py` как compatibility wrapper, если он импортируется внешним кодом или тестами.

---

## 8.3. Атомарные задачи

### 8.3.1. Инвентаризировать текущий DBExportService

Открыть файл `db_exporter.py`.

Составить карту методов:

```text
docs/refactor/DB_EXPORT_SERVICE_SPLIT_MAP.md
```

Для каждого метода указать:

| Current method | Responsibility | Target module | Public/private | Covered by tests | Notes |
|---|---|---|---|---|---|

Категории ответственности:

- data loading;
- target resolving;
- author fingerprinting;
- export planning;
- unchanged/skip detection;
- export state read/write;
- text rendering;
- json/jsonl rendering;
- file rotation;
- manifest writing;
- progress/events;
- error handling.

### 8.3.2. Создать db_export package

Создать:

```text
tg_msg_manager/services/db_export/__init__.py
```

Экспортировать только стабильные публичные элементы:

```python
from .service import DBExportService
```

Не экспортировать внутренние helpers.

### 8.3.3. Перенести orchestration facade

Создать:

```text
tg_msg_manager/services/db_export/service.py
```

Перенести туда класс `DBExportService` или новый facade-класс.

Он должен только:

1. принять config/dependencies;
2. вызвать source loader;
3. вызвать plan builder;
4. применить skip policy;
5. вызвать state manager;
6. вызвать renderer/writer;
7. отправить events;
8. вернуть result object.

Он не должен:

- содержать raw SQL;
- форматировать строки сообщений;
- считать fingerprint вручную внутри метода;
- напрямую писать JSONL/TXT;
- знать детали file rotation;
- содержать длинные вложенные циклы.

### 8.3.4. Вынести source loader

Создать:

```text
tg_msg_manager/services/db_export/source_loader.py
```

Ответственность:

- загрузить сообщения из storage;
- загрузить user metadata;
- загрузить chat metadata;
- загрузить target links;
- подготовить immutable input для export planning.

Запрещено:

- форматировать export output;
- писать файлы;
- обновлять export state;
- решать skip policy.

Минимальная модель результата:

```python
@dataclass(frozen=True)
class DBExportSource:
    messages: Sequence[...]
    users: Mapping[...]
    chats: Mapping[...]
    target_links: Sequence[...]
```

Адаптировать под существующие модели проекта.

### 8.3.5. Вынести plan builder

Создать:

```text
tg_msg_manager/services/db_export/plan_builder.py
```

Ответственность:

- построить export plan;
- определить output path;
- определить export format;
- определить target author;
- определить диапазон сообщений;
- подготовить plan metadata.

Запрещено:

- читать storage напрямую;
- писать файлы;
- считать unchanged state;
- отправлять telemetry.

Минимальная модель:

```python
@dataclass(frozen=True)
class DBExportPlan:
    target_id: int | None
    output_path: Path
    format: str
    message_count: int
    created_at: datetime
```

### 8.3.6. Вынести skip policy

Создать:

```text
tg_msg_manager/services/db_export/skip_policy.py
```

Ответственность:

- определить, изменились ли данные;
- сравнить fingerprint/hash;
- решить, нужно ли писать новый export;
- вернуть structured decision.

Минимальная модель:

```python
@dataclass(frozen=True)
class SkipDecision:
    should_skip: bool
    reason: str
    previous_fingerprint: str | None
    current_fingerprint: str | None
```

Запрещено:

- удалять файлы;
- менять state;
- запускать render;
- принимать CLI args.

### 8.3.7. Вынести state manager

Создать:

```text
tg_msg_manager/services/db_export/state_manager.py
```

Ответственность:

- читать `export_targets`;
- читать `export_runs`;
- создавать/обновлять export run;
- сохранять fingerprint;
- сохранять last exported metadata;
- фиксировать status success/failure/skipped.

Запрещено:

- формировать payload;
- форматировать `.txt`;
- напрямую fetch из Telegram;
- содержать business policy, не связанную с state.

### 8.3.8. Вынести TXT renderer

Создать:

```text
tg_msg_manager/services/db_export/txt_renderer.py
```

Ответственность:

- преобразовать export source/records в TXT representation;
- соблюдать старый формат вывода;
- сохранять порядок сообщений;
- сохранять разделители;
- сохранять timestamp/nickname/user_id/username formatting.

Запрещено:

- писать файл напрямую;
- читать storage;
- менять state;
- выполнять Telegram fetch.

Важно: output TXT на fixture до/после refactor должен совпасть byte-for-byte, если старый формат считается контрактом.

### 8.3.9. Вынести JSONL renderer

Создать:

```text
tg_msg_manager/services/db_export/jsonl_renderer.py
```

Ответственность:

- преобразовать records в JSONL;
- сохранить текущую схему полей;
- обеспечить deterministic ordering;
- не добавлять новые поля без отдельного решения.

Запрещено:

- писать файл напрямую;
- обновлять export state;
- менять schema JSONL.

### 8.3.10. Вынести payload writer

Создать:

```text
tg_msg_manager/services/db_export/payload_writer.py
```

Ответственность:

- принимать rendered payload;
- писать в файл;
- использовать существующий file rotate writer, если есть;
- обеспечивать atomic write, если уже предусмотрено;
- возвращать write result.

Запрещено:

- решать, что экспортировать;
- форматировать сообщения;
- читать storage.

### 8.3.11. Вынести manifest writer

Создать:

```text
tg_msg_manager/services/db_export/manifest_writer.py
```

Ответственность:

- писать manifest/metadata рядом с export, если такая логика уже есть;
- сохранять fingerprint;
- сохранять count;
- сохранять created_at;
- сохранять source info.

Если manifest currently не существует — не добавлять новую публичную фичу. Разрешено создать внутренний helper только если он заменяет уже существующую manifest-like логику.

### 8.3.12. Вынести db export event emitter

Создать:

```text
tg_msg_manager/services/db_export/event_emitter.py
```

Ответственность:

- progress events;
- start/success/failure/skipped events;
- bridge to existing telemetry system.

Запрещено:

- держать business logic;
- делать events обязательными для unit tests;
- падать при отсутствии subscriber.

### 8.3.13. Оставить compatibility wrapper

Файл:

```text
tg_msg_manager/services/db_exporter.py
```

Должен стать wrapper:

```python
# Compatibility wrapper.
from tg_msg_manager.services.db_export.service import DBExportService
```

Если есть дополнительные public symbols — re-export их явно.

Добавить комментарий:

```python
# DEPRECATED: kept for backward-compatible imports.
# New code should import from tg_msg_manager.services.db_export.
```

### 8.3.14. Добавить тесты на DB export split

Минимальные тесты:

- source loader returns expected records from fixture;
- plan builder creates deterministic path/metadata;
- skip policy returns skip when fingerprint unchanged;
- txt renderer preserves previous output;
- jsonl renderer preserves previous schema;
- state manager updates run status;
- compatibility import still works.

## 8.4. Критерии приемки

Этап завершен, если:

- `DBExportService` стал facade;
- DB export logic разделена;
- старый import не сломан;
- DB export fixture output совпадает;
- тесты проходят;
- формат export не изменился;
- docs updated.

---

# 9. ЭТАП 3 — Разгрузить PrivateArchiveService

## 9.1. Цель

`PrivateArchiveService` не должен быть отдельным параллельным пайплайном, который дублирует sync/export/storage логику.

Он должен использовать общие компоненты:

- fetch orchestration;
- storage writers;
- target resolving;
- event emission;
- file/export writers;
- retry policy.

## 9.2. Целевая структура

Создать директорию:

```text
tg_msg_manager/services/private_archive/
    __init__.py
    service.py
    planner.py
    source_resolver.py
    media_policy.py
    archive_writer.py
    state_manager.py
    event_emitter.py
    models.py
```

Оставить `services/private_archive.py` как compatibility wrapper, если он уже используется.

---

## 9.3. Атомарные задачи

### 9.3.1. Инвентаризировать PrivateArchiveService

Создать файл:

```text
docs/refactor/PRIVATE_ARCHIVE_SPLIT_MAP.md
```

Для каждого метода указать:

| Current method | Responsibility | Target module | Shared component candidate | Notes |
|---|---|---|---|---|

Категории:

- planning;
- private dialog resolving;
- message fetching;
- media handling;
- archive writing;
- state/checkpoint;
- telemetry/progress;
- error handling.

### 9.3.2. Создать package

Создать:

```text
tg_msg_manager/services/private_archive/__init__.py
```

Экспортировать:

```python
from .service import PrivateArchiveService
```

### 9.3.3. Перенести service facade

Создать:

```text
tg_msg_manager/services/private_archive/service.py
```

Service должен:

- принимать dependencies;
- вызывать planner;
- использовать shared fetch orchestration там, где возможно;
- использовать state manager;
- использовать archive writer;
- отправлять events;
- возвращать structured result.

Service не должен:

- содержать Telegram-specific loops, если это можно делегировать;
- писать raw SQL;
- форматировать большие payloads;
- решать media policy inline.

### 9.3.4. Вынести planner

Создать:

```text
tg_msg_manager/services/private_archive/planner.py
```

Ответственность:

- определить scope приватного архива;
- определить user/dialog targets;
- определить режим обработки;
- определить output locations.

Запрещено:

- fetch messages;
- write files;
- mutate DB.

### 9.3.5. Вынести source resolver

Создать:

```text
tg_msg_manager/services/private_archive/source_resolver.py
```

Ответственность:

- разрешение приватных диалогов;
- сопоставление dialog/user metadata;
- подготовка source descriptors.

Запрещено:

- писать archive output;
- обновлять state;
- реализовывать retry policy.

### 9.3.6. Вынести media policy

Создать:

```text
tg_msg_manager/services/private_archive/media_policy.py
```

Ответственность:

- решать, что делать с media-only messages;
- определять download/skip behavior;
- определять naming/path policy для media, если уже есть;
- возвращать structured decision.

Запрещено:

- скачивать файл напрямую, если этим занимается отдельный adapter;
- писать message records;
- менять export state.

### 9.3.7. Вынести archive writer

Создать:

```text
tg_msg_manager/services/private_archive/archive_writer.py
```

Ответственность:

- запись archive files;
- append/overwrite policy;
- metadata sidecars, если есть;
- использование общего file writer, если возможно.

Запрещено:

- Telegram fetch;
- DB query;
- planning.

### 9.3.8. Вынести state manager

Создать:

```text
tg_msg_manager/services/private_archive/state_manager.py
```

Ответственность:

- read/write private archive progress;
- checkpoint;
- last processed message;
- success/failure state.

Запрещено:

- форматировать output;
- решать scope;
- выполнять Telegram calls.

### 9.3.9. Вынести event emitter

Создать:

```text
tg_msg_manager/services/private_archive/event_emitter.py
```

Ответственность:

- start/progress/success/failure events;
- bridge to existing telemetry.

Запрещено:

- business logic.

### 9.3.10. Убрать дублирование с export modules

Проверить, можно ли использовать уже существующие:

- `services/export/fetch_orchestrator.py`;
- `services/export/event_emitter.py`;
- file writer utilities;
- retry writer;
- checkpoint writer.

Если логика совпадает — переиспользовать.

Если логика похожа, но не идентична — выделить общий protocol/helper, но не ломать текущие сценарии.

### 9.3.11. Compatibility wrapper

Файл:

```text
tg_msg_manager/services/private_archive.py
```

Должен re-export новый service.

Добавить deprecated comment.

## 9.4. Критерии приемки

Этап завершен, если:

- `PrivateArchiveService` стал facade;
- дублирование с export/sync уменьшено;
- старые импорты работают;
- private archive tests проходят;
- CLI behavior не изменилось;
- output не изменился без решения.

---

# 10. ЭТАП 4 — Разделить Storage Contracts

## 10.1. Цель

Сузить storage interfaces.

Проблема широкого storage interface: сервисы получают доступ к лишним методам и начинают знать слишком много о storage layer.

Нужно заменить большой универсальный interface набором маленьких protocol/use-case contracts.

---

## 10.2. Целевая структура

Создать или привести к виду:

```text
tg_msg_manager/infrastructure/storage/contracts/
    __init__.py
    sync_storage.py
    export_storage.py
    db_export_storage.py
    context_storage.py
    private_archive_storage.py
    report_storage.py
    retry_storage.py
    analytics_storage.py
```

Если проект использует другое место для protocols — соблюдать стиль проекта.

---

## 10.3. Атомарные задачи

### 10.3.1. Инвентаризировать текущий storage interface

Открыть:

```text
tg_msg_manager/infrastructure/storage/interface.py
```

Создать:

```text
docs/refactor/STORAGE_CONTRACT_SPLIT_MAP.md
```

Для каждого метода указать:

| Method | Used by | Domain | New contract | Can be private | Notes |
|---|---|---|---|---|

Домены:

- sync;
- export;
- db_export;
- context;
- private_archive;
- report;
- retry;
- analytics;
- shared/common.

### 10.3.2. Создать SyncStorage protocol

Файл:

```text
contracts/sync_storage.py
```

Методы только для sync:

- read sync state;
- write sync state;
- upsert messages;
- upsert users;
- upsert chats;
- read last message checkpoint.

Не включать:

- db export methods;
- analytics methods;
- report generation methods.

### 10.3.3. Создать ExportStorage protocol

Файл:

```text
contracts/export_storage.py
```

Методы только для target/context export:

- read target user;
- read target messages;
- read message context;
- read target links;
- write export checkpoint, если нужно.

Не включать:

- private archive methods;
- analytics queries;
- retry internals.

### 10.3.4. Создать DBExportStorage protocol

Файл:

```text
contracts/db_export_storage.py
```

Методы только для DB-first export:

- read export source data;
- read/write export targets;
- read/write export runs;
- read fingerprint state;
- update DB export state.

Не включать:

- Telegram sync writes;
- private archive logic;
- context building logic.

### 10.3.5. Создать ContextStorage protocol

Файл:

```text
contracts/context_storage.py
```

Методы только для context engine:

- read message by id;
- read parent reply;
- read neighbor messages;
- read child replies, если есть;
- read context group.

Не включать:

- export formatting;
- report;
- analytics scoring.

### 10.3.6. Создать PrivateArchiveStorage protocol

Файл:

```text
contracts/private_archive_storage.py
```

Методы:

- read/write private archive state;
- read private dialog metadata;
- write private archive message metadata, если есть.

Не включать:

- normal group export;
- social graph;
- semantic search.

### 10.3.7. Создать ReportStorage protocol

Файл:

```text
contracts/report_storage.py
```

Методы:

- read report data;
- read stats;
- read retry summary;
- read export summary.

Не включать:

- write messages;
- write sync state.

### 10.3.8. Создать RetryStorage protocol

Файл:

```text
contracts/retry_storage.py
```

Методы:

- create failed item;
- update retry status;
- list pending retries;
- mark success/failure.

### 10.3.9. Создать AnalyticsStorage placeholder protocol

Файл:

```text
contracts/analytics_storage.py
```

На Stage 1 не реализовывать полноценную аналитику.

Разрешено создать минимальный protocol с комментариями:

```python
class AnalyticsStorage(Protocol):
    """Reserved read-only contract for future analytics projections."""
```

Если уже есть analytics read methods — перенести только read-only methods.

### 10.3.10. Обновить сервисы на узкие protocols

Заменить зависимости в сервисах:

Плохо:

```python
storage: Storage
```

Хорошо:

```python
storage: DBExportStorage
```

или:

```python
storage: ContextStorage
```

Каждый сервис должен получать только тот contract, который ему нужен.

### 10.3.11. Оставить compatibility interface

`interface.py` можно оставить как aggregator:

```python
from .contracts.sync_storage import SyncStorage
from .contracts.export_storage import ExportStorage
...
```

Не удалять сразу, если много импортов.

Добавить comment:

```python
# Compatibility aggregator. New code should depend on narrow contracts.
```

## 10.4. Критерии приемки

Этап завершен, если:

- contracts разделены;
- сервисы используют narrow contracts;
- старый interface не ломает импорты;
- тесты проходят;
- нет циклических импортов;
- storage layer не зависит от services.

---

# 11. ЭТАП 5 — Разделить Service/Event Payload Models

## 11.1. Цель

Предотвратить превращение `service_payloads.py` в DTO-монолит.

Payloads должны быть разделены по доменам.

---

## 11.2. Целевая структура

Создать:

```text
tg_msg_manager/core/models/payloads/
    __init__.py
    sync.py
    export.py
    db_export.py
    context.py
    private_archive.py
    retry.py
    report.py
    telemetry.py
```

Оставить старый:

```text
tg_msg_manager/core/models/service_payloads.py
```

как compatibility aggregator.

---

## 11.3. Атомарные задачи

### 11.3.1. Инвентаризировать payload models

Создать:

```text
docs/refactor/PAYLOADS_SPLIT_MAP.md
```

Для каждой модели:

| Current model | Domain | Target module | Used by | Public? |
|---|---|---|---|---|

### 11.3.2. Создать payloads package

Создать:

```text
core/models/payloads/__init__.py
```

Не импортировать всё автоматически, если это создаёт циклы.

### 11.3.3. Перенести sync payloads

Файл:

```text
core/models/payloads/sync.py
```

Модели:

- sync started;
- sync progress;
- sync completed;
- sync failed;
- checkpoint payloads.

Только если такие модели существуют.

### 11.3.4. Перенести export payloads

Файл:

```text
core/models/payloads/export.py
```

Модели:

- export started;
- export progress;
- export completed;
- export failed;
- target export payloads.

### 11.3.5. Перенести DB export payloads

Файл:

```text
core/models/payloads/db_export.py
```

Модели:

- DB export plan/result;
- DB export run;
- skip decision payload;
- fingerprint payload.

### 11.3.6. Перенести context payloads

Файл:

```text
core/models/payloads/context.py
```

Модели:

- context cluster;
- reply chain;
- neighbor window;
- context result;
- context quality markers.

### 11.3.7. Перенести private archive payloads

Файл:

```text
core/models/payloads/private_archive.py
```

Модели:

- archive plan;
- archive result;
- archive progress;
- media decision.

### 11.3.8. Перенести retry/report/telemetry payloads

Файлы:

```text
core/models/payloads/retry.py
core/models/payloads/report.py
core/models/payloads/telemetry.py
```

Переносить только существующие модели.

### 11.3.9. Оставить compatibility aggregator

Файл:

```text
core/models/service_payloads.py
```

Должен re-export старые symbols.

Добавить comment:

```python
# Compatibility aggregator.
# New code should import payloads from core.models.payloads.<domain>.
```

### 11.3.10. Обновить импорты постепенно

Обновить внутренние импорты в новых/затронутых модулях.

Не обязательно менять все старые импорты сразу, если это создает риск. Главное — новые модули должны использовать новые domain payload modules.

## 11.4. Критерии приемки

Этап завершен, если:

- payload models разделены по доменам;
- старые imports работают;
- нет import cycles;
- tests pass;
- new code не импортирует из monolithic `service_payloads.py`.

---

# 12. ЭТАП 6 — Оформить Analytics Boundary

## 12.1. Цель

Подготовить место для будущей аналитики так, чтобы она не была добавлена внутрь export/context/sync services.

Stage 1 не реализует аналитику. Он только фиксирует boundary.

---

## 12.2. Целевая структура

```text
tg_msg_manager/services/analytics/
    __init__.py
    README.md

tg_msg_manager/infrastructure/storage/read/analytics/
    __init__.py
    README.md
    interactions.py
    user_activity.py
    reply_graph.py
    dataset_projection.py
```

На Stage 1 эти модули могут быть пустыми или содержать только placeholder classes/functions, если это соответствует стилю проекта.

---

## 12.3. Атомарные задачи

### 12.3.1. Проверить существующую analytics directory

Если уже есть:

```text
infrastructure/storage/read/analytics/
```

Открыть и проверить:

- что там нет business logic;
- что там нет write operations;
- что там нет imports from services;
- что там нет Telegram calls.

### 12.3.2. Создать analytics README

Файл:

```text
tg_msg_manager/services/analytics/README.md
```

Содержание:

```markdown
# Analytics Boundary

This package is reserved for future read-only analytics services.

Rules:
- Analytics reads normalized storage data.
- Analytics does not fetch Telegram directly.
- Analytics does not mutate sync/export state.
- Analytics does not write message records.
- Analytics does not live inside ExportService, DBExportService, or ContextEngine.
- Analytics projections must use read-only storage contracts.
```

### 12.3.3. Создать read analytics README

Файл:

```text
tg_msg_manager/infrastructure/storage/read/analytics/README.md
```

Содержание:

```markdown
# Analytics Read Models

Read-only SQL projections for future analytics.

Allowed:
- interaction counts;
- reply graph projections;
- user activity timelines;
- dataset projections.

Forbidden:
- writes;
- Telegram calls;
- business decisions;
- export formatting.
```

### 12.3.4. Создать placeholder modules

Создать пустые модули:

```text
interactions.py
user_activity.py
reply_graph.py
dataset_projection.py
```

В каждом:

```python
"""Read-only projection helpers for future analytics.

No business logic should be added here during Stage 1.
"""
```

Не реализовывать scoring.

### 12.3.5. Добавить architecture rule

В `docs/ARCHITECTURE_RULES.md` добавить:

```markdown
## Analytics boundary

Future analytics must be implemented as read-only services over normalized storage projections.

Forbidden:
- adding analytics to ExportService;
- adding analytics to DBExportService;
- adding analytics to ContextEngine;
- adding analytics SQL to service layer;
- adding Telegram fetches to analytics.
```

## 12.4. Критерии приемки

Этап завершен, если:

- analytics boundary существует;
- docs запрещают добавление analytics в hot path;
- tests pass;
- analytics modules не содержат продуктовую логику.

---

# 13. ЭТАП 7 — Решить статус Context Relation Tables

## 13.1. Цель

Убрать архитектурную неопределенность вокруг context relation tables, например `message_context_links`.

Таблица/механизм должен быть либо:

1. first-class relation layer;
2. compatibility/legacy layer;
3. candidate for future migration.

Нельзя оставлять неопределенный статус.

---

## 13.2. Атомарные задачи

### 13.2.1. Найти все context relation tables

Поискать:

```bash
grep -R "message_context_links" -n .
grep -R "context_group" -n tg_msg_manager
grep -R "context_links" -n tg_msg_manager
```

Составить список:

- tables;
- writers;
- readers;
- migrations/schema definitions;
- tests;
- active hot path usage.

### 13.2.2. Создать context relation decision document

Создать:

```text
docs/refactor/CONTEXT_RELATION_TABLES_DECISION.md
```

Структура:

```markdown
# Context Relation Tables Decision

## 1. Existing tables

## 2. Current writers

## 3. Current readers

## 4. Current hot-path usage

## 5. Problems

## 6. Decision

Choose one:
- First-class relation layer
- Legacy compatibility layer
- Future migration candidate

## 7. Consequences

## 8. Follow-up tasks
```

### 13.2.3. Если таблица first-class

Если решено сделать `message_context_links` first-class:

- создать/проверить dedicated reader;
- создать/проверить dedicated writer;
- добавить tests;
- описать relation semantics;
- определить source of truth;
- определить relationship types.

Обязательные вопросы:

- связь target -> context message?
- связь message -> context_group?
- связь reply parent -> child?
- связь neighbor before/after?
- может ли одно сообщение быть в нескольких context groups?

### 13.2.4. Если таблица legacy

Если решено оставить как legacy:

- добавить комментарии в schema/writer;
- не использовать в новых hot-path features;
- задокументировать replacement:
  - `reply_to_id`;
  - `context_group_id`;
  - `message_target_links`;
  - другие active fields.

Добавить в docs:

```markdown
`message_context_links` is retained for compatibility. New context logic must not depend on it unless a migration decision changes its status.
```

### 13.2.5. Если future migration candidate

Если решение отложено:

- явно указать, почему;
- запретить новым функциям зависеть от таблицы до решения;
- создать TODO issue/doc section;
- добавить tests на текущее поведение, чтобы не сломать silently.

## 13.3. Критерии приемки

Этап завершен, если:

- все context relation tables найдены;
- создан decision document;
- статус таблиц ясен;
- future code rules обновлены;
- tests pass.

---

# 14. ЭТАП 8 — Live / Manual Smoke Checklist

## 14.1. Цель

Добавить ручной smoke checklist для сценариев, которые нельзя надежно покрыть unit/mock тестами.

Особенно важно для Telegram integration.

---

## 14.2. Создать файл

```text
docs/testing/LIVE_SMOKE_CHECKLIST.md
```

---

## 14.3. Содержание checklist

```markdown
# Live Smoke Checklist

## Preconditions

- Valid Telegram session exists.
- Test chat/dialog is available.
- Test user_id is known.
- DB backup created.
- Network available.

## Commands

### 1. Basic CLI help

Command:
```bash
python -m tg_msg_manager --help
```

Expected:
- command exits 0;
- help output contains main commands.

### 2. Minimal sync

Command:
```bash
<actual sync command with safe limit>
```

Expected:
- no crash;
- DB receives new/known messages;
- checkpoint updates correctly.

### 3. Flat export

Command:
```bash
<actual export command> --user-id <TEST_USER_ID> --flat --limit 1
```

Expected:
- output file created;
- target user's message appears;
- no unrelated messages included.

### 4. Deep context export

Command:
```bash
<actual export command> --user-id <TEST_USER_ID> --depth 2 --limit 1
```

Expected:
- output file created;
- target message included;
- context messages included;
- separators preserved.

### 5. DB export

Command:
```bash
<actual db export command>
```

Expected:
- output created;
- manifest/state updated if applicable;
- unchanged second run is skipped or handled as designed.

### 6. Private archive

Command:
```bash
<actual private archive command with safe target>
```

Expected:
- no crash;
- archive output created;
- checkpoint/state updated.

### 7. Retry/report

Command:
```bash
<actual retry/report command>
```

Expected:
- command exits 0;
- report contains expected sections.

## Result table

| Date | Commit | Tester | Scenario | Result | Notes |
|---|---|---|---|---|---|
```

Агент должен заменить placeholder commands на реальные команды проекта.

## 14.4. Критерии приемки

Этап завершен, если:

- checklist создан;
- команды соответствуют реальному CLI;
- expected results ясны;
- checklist не требует live CI;
- tests pass.

---

# 15. ЭТАП 9 — Документация архитектуры

## 15.1. Цель

Обновить архитектурные документы под Stage 1.

---

## 15.2. Атомарные задачи

### 15.2.1. Обновить PROJECT_ARCHITECTURE_OVERVIEW.md

Добавить:

- DB export package overview;
- private archive package overview;
- storage contracts overview;
- payloads package overview;
- analytics boundary;
- status of context relation tables.

Удалить или исправить устаревшие утверждения.

### 15.2.2. Обновить ARCHITECTURE_RULES.md

Добавить правила:

- DB export logic must not be added to facade file.
- Private archive must reuse shared pipeline components where possible.
- Services depend on narrow storage contracts.
- New payloads go to domain-specific payload modules.
- Analytics must be read-only and outside export/context hot path.
- Context relation tables must follow documented decision.

### 15.2.3. Обновить PR_CHECKLIST.md

Добавить пункты:

```markdown
- [ ] No new logic added to DBExportService facade
- [ ] No new logic added to PrivateArchiveService facade
- [ ] Service depends on narrow storage contract
- [ ] New payload models placed in domain payload module
- [ ] Analytics logic not added to export/context/db_export services
- [ ] Context relation table decision respected
- [ ] Live smoke checklist updated if Telegram behavior changed
```

### 15.2.4. Обновить CHANGELOG.md

Добавить запись:

```markdown
## Stage 1 Refactor

- Split DB export service into dedicated components.
- Split private archive service into dedicated components.
- Added narrow storage contracts.
- Split service payload models by domain.
- Formalized analytics boundary.
- Documented context relation table decision.
- Added live smoke checklist.
```

Не утверждать то, что фактически не сделано.

## 15.3. Критерии приемки

Этап завершен, если:

- architecture docs обновлены;
- changelog обновлен;
- docs не противоречат коду;
- tests pass.

---

# 16. ЭТАП 10 — Финальная Regression Проверка

## 16.1. Цель

Убедиться, что Stage 1 не изменил поведение.

---

## 16.2. Обязательные проверки

### 16.2.1. Full tests

Запустить:

```bash
make test
```

или актуальную команду.

### 16.2.2. Full verification

Запустить:

```bash
make verify
```

если есть.

### 16.2.3. CLI contract tests

Проверить:

- help;
- command inventory;
- known arguments;
- defaults.

### 16.2.4. DB export regression

Сравнить DB export output до/после refactor на fixture.

Требование:

- TXT output совпадает byte-for-byte;
- JSONL schema не изменилась;
- ordering стабилен;
- fingerprint behavior стабилен;
- skip behavior стабилен.

### 16.2.5. Private archive regression

Если есть fixture/test:

- output стабилен;
- checkpoint behavior стабилен;
- media policy behavior стабилен.

Если fixture отсутствует:

- задокументировать отсутствие;
- добавить минимальный unit-level test на planner/source resolver/writer.

### 16.2.6. Import compatibility check

Проверить, что старые импорты работают:

```python
from tg_msg_manager.services.db_exporter import DBExportService
from tg_msg_manager.services.private_archive import PrivateArchiveService
from tg_msg_manager.core.models.service_payloads import ...
from tg_msg_manager.infrastructure.storage.interface import ...
```

Адаптировать symbols к реальному проекту.

### 16.2.7. Circular import check

Запустить простой импорт основных модулей:

```bash
python - <<'PY'
import tg_msg_manager
import tg_msg_manager.services.export
import tg_msg_manager.services.context
import tg_msg_manager.services.db_export
import tg_msg_manager.services.private_archive
PY
```

Адаптировать под реальные модули.

## 16.3. Критерии приемки

Финальная проверка завершена, если:

- тесты проходят;
- verification проходит;
- output regression отсутствует;
- compatibility imports работают;
- нет circular imports;
- docs обновлены.

---

# 17. Stage 1 Report

После завершения создать:

```text
docs/refactor/STAGE_1_REFACTOR_REPORT.md
```

## 17.1. Структура отчета

```markdown
# Stage 1 Refactor Report

## 1. Summary

Кратко: что изменено.

## 2. Baseline

- Commit before:
- Commit after:
- Tests before:
- Tests after:

## 3. DBExportService split

| Old method/module | New module | Responsibility |
|---|---|---|

## 4. PrivateArchiveService split

| Old method/module | New module | Responsibility |
|---|---|---|

## 5. Storage contracts

| Old interface area | New contract | Used by |
|---|---|---|

## 6. Payload models

| Old model | New module |
|---|---|

## 7. Analytics boundary

Что создано и какие правила добавлены.

## 8. Context relation decision

Выбранный статус и последствия.

## 9. Behavior compatibility

- CLI changed: yes/no
- Export format changed: yes/no
- DB schema changed: yes/no
- Public imports changed: yes/no

## 10. Test results

Команды и результаты.

## 11. Known risks

Оставшиеся риски.

## 12. Deferred tasks

Что не сделано намеренно.

## 13. Recommended Stage 2

Что делать дальше.
```

---

# 18. Definition of Done

Stage 1 считается завершенным только если:

- [ ] Stage 1 baseline создан.
- [ ] Тесты до рефакторинга запущены.
- [ ] `DBExportService` разгружен.
- [ ] Старый `services/db_exporter.py` работает как compatibility wrapper.
- [ ] DB export output не изменился.
- [ ] `PrivateArchiveService` разгружен.
- [ ] Старый `services/private_archive.py` работает как compatibility wrapper.
- [ ] Storage contracts разделены по use cases.
- [ ] Services зависят от narrow contracts.
- [ ] Payload models разделены по доменам.
- [ ] Старый `service_payloads.py` работает как compatibility aggregator.
- [ ] Analytics boundary оформлена.
- [ ] Context relation tables имеют documented decision.
- [ ] Live smoke checklist создан.
- [ ] Architecture docs обновлены.
- [ ] PR checklist обновлен.
- [ ] Changelog обновлен.
- [ ] Full tests проходят.
- [ ] Verification проходит или причина отсутствия documented.
- [ ] Compatibility imports проходят.
- [ ] Circular imports отсутствуют.
- [ ] Stage 1 report создан.
- [ ] Новые продуктовые функции не добавлены.

---

# 19. Запрещенные решения

Во время Stage 1 нельзя:

- добавлять новые пользовательские функции;
- менять CLI;
- менять export format;
- менять default context depth;
- менять target attribution behavior;
- менять DB schema без migration note;
- добавлять analytics logic в export/context/db_export services;
- добавлять Telegram fetch в analytics;
- добавлять raw SQL в services;
- делать storage contracts шире ради удобства;
- удалять compatibility wrappers без необходимости;
- удалять legacy без import/test verification;
- делать global rename без тестов;
- смешивать Stage 1 с roadmap features.

---

# 20. Разрешенные решения

Во время Stage 1 можно:

- извлекать модули;
- создавать packages;
- создавать compatibility wrappers;
- добавлять narrow protocols;
- добавлять dataclasses/DTO, если они заменяют существующие implicit structures;
- переносить payload models;
- добавлять tests;
- добавлять docs;
- добавлять placeholder analytics boundary;
- добавлять manual smoke checklist;
- помечать legacy/deprecated code;
- упрощать orchestration logic без изменения поведения.

---

# 21. Приоритеты при конфликте решений

Если возникает конфликт, применять порядок:

1. Не ломать работоспособность.
2. Не менять публичное поведение.
3. Не менять export output.
4. Сохранить compatibility imports.
5. Снизить связанность.
6. Сузить contracts.
7. Разделить ответственность.
8. Улучшить читаемость.
9. Обновить документацию.

Если красивое архитектурное изменение угрожает стабильности — не делать его на Stage 1.

---

# 22. Краткая инструкция агенту

Работай маленькими изменениями.

После каждого логического extraction:

1. Запусти релевантные тесты.
2. Проверь импорты.
3. Проверь CLI contract, если затронут entrypoint.
4. Проверь fixture output, если затронут export.
5. Обнови split map или report.
6. Не добавляй новые функции.
7. Не меняй поведение.
8. Не оставляй новую архитектурную неопределенность.

Главный результат Stage 1: проект должен стать готовым к крупным расширениям без риска, что новые функции снова начнут наращивать монолиты.
