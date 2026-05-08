# STAGE 1 CONSISTENCY PASS — CLOSE UNFINISHED REFACTORING ISSUES

## 0. Назначение документа

Этот документ описывает задачи для Codex/AI-агента, который должен доделать незакрытые проблемы после Stage 1 refactor в проекте `tg-msg-manager`.

Это не новый feature stage.

Цель: привести код, документацию и архитектурные контракты к консистентному состоянию после уже проведённого рефакторинга.

---

# 1. Главный диагноз

После Stage 1 в проекте появились правильные новые пакеты:

```text
tg_msg_manager/services/db_export/
tg_msg_manager/services/private_archive/
tg_msg_manager/infrastructure/storage/contracts/
tg_msg_manager/core/models/payloads/
tg_msg_manager/services/analytics/
```

Но есть признаки незавершённого рефакторинга:

1. Старые hot-path файлы могут всё ещё содержать полноценную реализацию, а не compatibility wrapper.
2. Возможна двойная реализация `DBExportService`.
3. Возможна двойная реализация `PrivateArchiveService`.
4. Документация может быть устаревшей относительно новой структуры.
5. Stage 1 baseline/report/decision docs могут отсутствовать.
6. Некоторые facade-сервисы всё ещё могут содержать лишнюю operational logic.
7. Regression-проверки для DB export / private archive могли быть не зафиксированы.

Главная задача: устранить двойные источники истины и зафиксировать фактическую архитектуру.

---

# 2. Строгие ограничения

## 2.1. Запрещено менять пользовательское поведение

Нельзя менять:

- CLI-команды;
- CLI-аргументы;
- дефолтные значения;
- формат `.txt` export;
- формат `.json` / `.jsonl` export;
- имена файлов экспорта;
- директории экспорта;
- логику incremental sync;
- логику duplicate protection;
- target attribution;
- context depth;
- retry behavior;
- report format;
- SQLite schema.

## 2.2. Запрещено добавлять новые функции

Не добавлять:

- analytics;
- social graph;
- scoring;
- NLP;
- semantic search;
- embeddings;
- web dashboard;
- REST API;
- multi-account;
- новые export modes;
- новые CLI commands.

## 2.3. Запрещено делать большой rewrite

Нельзя:

- переписывать проект заново;
- менять storage engine;
- менять Telegram adapter;
- менять архитектуру всего проекта одним коммитом;
- удалять compatibility wrappers без проверки импортов;
- удалять legacy code без тестов.

## 2.4. Разрешено

Можно:

- превращать старые файлы в compatibility wrappers;
- переносить остаточную логику в уже созданные новые модули;
- обновлять импорты;
- добавлять тесты на compatibility imports;
- обновлять документацию;
- создавать Stage 1 report;
- добавлять regression checks;
- помечать deprecated paths;
- исправлять документационный drift.

---

# 3. Definition of Done

Этот consistency pass считается завершённым только если:

- [ ] Нет двух активных реализаций `DBExportService`.
- [ ] Нет двух активных реализаций `PrivateArchiveService`.
- [ ] `services/db_exporter.py` является compatibility wrapper или явно задокументирован как active entrypoint.
- [ ] `services/private_archive.py` является compatibility wrapper или явно задокументирован как active entrypoint.
- [ ] CLI использует актуальные новые сервисы.
- [ ] Старые импорты остаются рабочими.
- [ ] `PROJECT_ARCHITECTURE_OVERVIEW.md` обновлён.
- [ ] `docs/refactor/STAGE_1_REFACTOR_REPORT.md` создан.
- [ ] `docs/refactor/STAGE_1_BASELINE.md` создан или восстановлен по текущему состоянию.
- [ ] Context relation table decision documented.
- [ ] Live smoke checklist существует или обновлён.
- [ ] DB export regression проверен.
- [ ] Private archive smoke/regression проверен.
- [ ] Full tests проходят.
- [ ] Import smoke проходит.
- [ ] Circular imports отсутствуют.
- [ ] Новые продуктовые функции не добавлены.

---

# 4. Порядок выполнения

Работать строго по этапам:

1. Зафиксировать текущее состояние.
2. Проверить двойные реализации.
3. Исправить `DBExportService` entrypoints.
4. Исправить `PrivateArchiveService` entrypoints.
5. Проверить CLI wiring.
6. Проверить storage contracts usage.
7. Проверить payload compatibility.
8. Дожать private archive facade.
9. Обновить архитектурную документацию.
10. Создать Stage 1 report.
11. Провести regression/import/smoke проверки.

---

# 5. ЭТАП 1 — Зафиксировать текущее состояние

## 5.1. Цель

Перед исправлениями получить точный baseline.

## 5.2. Атомарные задачи

### 5.2.1. Проверить git state

Выполнить:

```bash
git status --short
git rev-parse HEAD
git branch --show-current
```

Зафиксировать результат в:

```text
docs/refactor/STAGE_1_CONSISTENCY_BASELINE.md
```

### 5.2.2. Запустить тесты

Выполнить доступные команды:

```bash
make test
make verify
```

Если команды отличаются — использовать фактические команды из `README.md`, `Makefile`, `pyproject.toml`.

Зафиксировать:

- команду;
- результат;
- количество passed/failed/skipped;
- ошибки, если есть.

### 5.2.3. Проверить compileall

Выполнить:

```bash
python3 -m compileall tg_msg_manager
```

Цель: обнаружить синтаксические ошибки после переносов модулей.

### 5.2.4. Проверить импорт основных пакетов

Выполнить:

```bash
python3 - <<'PY'
import tg_msg_manager
import tg_msg_manager.services.export
import tg_msg_manager.services.context
import tg_msg_manager.services.db_export
import tg_msg_manager.services.private_archive
import tg_msg_manager.infrastructure.storage.contracts
import tg_msg_manager.core.models.payloads
print("imports ok")
PY
```

Если импорт падает — исправить до продолжения.

## 5.3. Критерии приемки

Этап завершён, если:

- baseline создан;
- тесты запущены;
- compileall пройден или ошибки зафиксированы;
- import smoke пройден или ошибки зафиксированы.

---

# 6. ЭТАП 2 — Найти двойные реализации

## 6.1. Цель

Установить, есть ли два активных источника истины для одних и тех же сервисов.

## 6.2. Атомарные задачи

### 6.2.1. Проверить DBExportService

Выполнить:

```bash
grep -R "class DBExportService" -n tg_msg_manager
grep -R "from .*db_exporter import DBExportService" -n .
grep -R "from .*db_export.* import DBExportService" -n .
grep -R "DBExportService" -n tg_msg_manager tests
```

Создать файл:

```text
docs/refactor/DB_EXPORT_ENTRYPOINT_AUDIT.md
```

Записать:

- где объявлен `DBExportService`;
- какие файлы его импортируют;
- какой implementation реально используется CLI;
- какие тесты используют старый путь;
- какие тесты используют новый путь.

### 6.2.2. Проверить PrivateArchiveService

Выполнить:

```bash
grep -R "class PrivateArchiveService" -n tg_msg_manager
grep -R "from .*private_archive import PrivateArchiveService" -n .
grep -R "PrivateArchiveService" -n tg_msg_manager tests
```

Создать файл:

```text
docs/refactor/PRIVATE_ARCHIVE_ENTRYPOINT_AUDIT.md
```

Записать:

- где объявлен `PrivateArchiveService`;
- какие файлы его импортируют;
- какой implementation реально используется CLI;
- какие тесты используют старый путь;
- какие тесты используют новый путь.

### 6.2.3. Проверить wrapper-файлы

Открыть:

```text
tg_msg_manager/services/db_exporter.py
tg_msg_manager/services/private_archive.py
```

Классифицировать каждый:

- pure compatibility wrapper;
- compatibility wrapper with extra symbols;
- active implementation;
- mixed old/new file.

### 6.2.4. Принять решение

Для каждого файла выбрать один статус:

```text
1. Compatibility wrapper only
2. Active implementation
3. Deprecated but still temporarily active
```

Предпочтительный статус: `Compatibility wrapper only`.

## 6.3. Критерии приемки

Этап завершён, если:

- найдено точное количество реализаций;
- понятно, какой сервис реально используется;
- создан audit document для DB export;
- создан audit document для private archive.

---

# 7. ЭТАП 3 — Исправить DBExportService entrypoint

## 7.1. Цель

Устранить двойной источник истины для `DBExportService`.

Правильное целевое состояние:

```text
tg_msg_manager/services/db_export/service.py      -> реальная реализация
tg_msg_manager/services/db_exporter.py            -> compatibility wrapper
```

## 7.2. Атомарные задачи

### 7.2.1. Сравнить старую и новую реализации

Сравнить:

```text
tg_msg_manager/services/db_exporter.py
tg_msg_manager/services/db_export/service.py
```

Определить:

- какие методы есть только в старом файле;
- какие методы есть только в новом файле;
- какие методы отличаются;
- какие public symbols нужно сохранить.

### 7.2.2. Перенести недостающую логику в новый package

Если в `db_exporter.py` есть актуальная логика, которой нет в новом package:

- перенести её в соответствующий модуль:
  - `source_loader.py`;
  - `plan_builder.py`;
  - `skip_policy.py`;
  - `state_manager.py`;
  - `txt_renderer.py`;
  - `jsonl_renderer.py`;
  - `payload_writer.py`;
  - `manifest_writer.py`;
  - `event_emitter.py`;
  - `models.py`;
  - `service.py`, только если это orchestration.

Запрещено переносить всё в `service.py`, если логика имеет отдельную ответственность.

### 7.2.3. Убедиться, что новый DBExportService покрывает старый public API

Проверить public methods старого класса.

Для каждого метода:

- сохранить;
- или сделать compatibility method;
- или доказать, что он private/internal и не используется.

Если метод использовался тестами/CLI — сохранить.

### 7.2.4. Превратить `db_exporter.py` в wrapper

Целевой вид:

```python
"""Compatibility wrapper for DB export service.

New code should import from tg_msg_manager.services.db_export.
"""

from tg_msg_manager.services.db_export.service import DBExportService

__all__ = ["DBExportService"]
```

Если есть дополнительные public symbols — re-export явно.

### 7.2.5. Добавить тест compatibility import

Создать или обновить тест:

```python
def test_db_exporter_compat_import():
    from tg_msg_manager.services.db_exporter import DBExportService as Old
    from tg_msg_manager.services.db_export.service import DBExportService as New

    assert Old is New
```

Если `Old is New` невозможно из-за wrapper design, проверить хотя бы, что оба указывают на один behavior-compatible class.

### 7.2.6. Проверить CLI wiring

Найти CLI-команду `db-export`.

Убедиться, что она использует новый `DBExportService` напрямую или через wrapper, который re-export'ит новую реализацию.

Запрещено оставлять CLI на старой реализации.

### 7.2.7. Запустить DB export tests

Запустить релевантные тесты:

```bash
pytest tests -k "db_export or dbexport or export"
```

Если тестовая структура другая — использовать релевантную команду.

## 7.3. Критерии приемки

Этап завершён, если:

- `DBExportService` объявлен в одном active месте;
- `db_exporter.py` больше не содержит старую реализацию;
- старый import работает;
- CLI использует новую реализацию;
- DB export tests проходят.

---

# 8. ЭТАП 4 — Исправить PrivateArchiveService entrypoint

## 8.1. Цель

Устранить двойной источник истины для `PrivateArchiveService`.

Правильное целевое состояние:

```text
tg_msg_manager/services/private_archive/service.py      -> реальная реализация
tg_msg_manager/services/private_archive.py              -> compatibility wrapper
```

## 8.2. Атомарные задачи

### 8.2.1. Сравнить старую и новую реализации

Сравнить:

```text
tg_msg_manager/services/private_archive.py
tg_msg_manager/services/private_archive/service.py
```

Определить:

- какие методы есть только в старом файле;
- какие методы есть только в новом файле;
- какие методы отличаются;
- какие public symbols нужно сохранить.

### 8.2.2. Перенести недостающую логику в новый package

Если в `private_archive.py` есть актуальная логика, которой нет в новом package:

- перенести её в:
  - `planner.py`;
  - `source_resolver.py`;
  - `media_policy.py`;
  - `archive_writer.py`;
  - `state_manager.py`;
  - `event_emitter.py`;
  - `models.py`;
  - `service.py`, только если это orchestration.

Запрещено переносить всё в `service.py`.

### 8.2.3. Сохранить public API

Проверить public methods старого `PrivateArchiveService`.

Сохранить совместимость для методов, которые используются:

- CLI;
- tests;
- docs;
- external imports внутри проекта.

### 8.2.4. Превратить `private_archive.py` в wrapper

Целевой вид:

```python
"""Compatibility wrapper for private archive service.

New code should import from tg_msg_manager.services.private_archive.
"""

from tg_msg_manager.services.private_archive.service import PrivateArchiveService

__all__ = ["PrivateArchiveService"]
```

Если нужны дополнительные public symbols — re-export явно.

### 8.2.5. Добавить тест compatibility import

Создать или обновить тест:

```python
def test_private_archive_compat_import():
    from tg_msg_manager.services.private_archive import PrivateArchiveService as New
    from tg_msg_manager.services.private_archive.service import PrivateArchiveService as NewDirect

    assert New is NewDirect
```

Важно: если одновременно существует файл `services/private_archive.py` и пакет `services/private_archive/`, Python import conflict возможен. Проверить фактическое поведение импорта.

Если конфликт есть, выбрать безопасное решение:

- либо оставить только package;
- либо переименовать compatibility file после миграции импортов;
- либо обеспечить package import через корректную структуру.

Не ломать CLI.

### 8.2.6. Проверить CLI wiring

Найти CLI-команду `export-pm` или private archive command.

Убедиться, что команда использует новую реализацию.

### 8.2.7. Запустить private archive tests

Запустить релевантные тесты:

```bash
pytest tests -k "private_archive or archive or export_pm"
```

Если тестовая структура другая — использовать фактическую команду.

## 8.3. Критерии приемки

Этап завершён, если:

- `PrivateArchiveService` имеет один active implementation;
- старый import работает или мигрирован безопасно;
- CLI использует новую реализацию;
- tests проходят;
- import conflict отсутствует.

---

# 9. ЭТАП 5 — Проверить Python import conflict для file/package names

## 9.1. Цель

Убедиться, что одновременное наличие файла и пакета с похожим именем не создаёт конфликтов.

Особенно проверить:

```text
tg_msg_manager/services/private_archive.py
tg_msg_manager/services/private_archive/
```

В Python файл и директория с одинаковым именем в одном package обычно конфликтуют. Это нужно проверить фактически.

## 9.2. Атомарные задачи

### 9.2.1. Выполнить import resolution check

Выполнить:

```bash
python3 - <<'PY'
import tg_msg_manager.services.private_archive as pa
print(pa)
print(getattr(pa, "__file__", None))
print(hasattr(pa, "PrivateArchiveService"))
PY
```

Зафиксировать:

- какой путь импортируется;
- файл или package;
- есть ли `PrivateArchiveService`.

### 9.2.2. Проверить db_export import

Выполнить:

```bash
python3 - <<'PY'
import tg_msg_manager.services.db_export as de
print(de)
print(getattr(de, "__file__", None))
print(hasattr(de, "DBExportService"))
PY
```

### 9.2.3. Устранить конфликт

Если `private_archive.py` блокирует импорт пакета `private_archive/`, нужно выбрать одно:

Вариант A — preferred:

- удалить/переименовать файл `private_archive.py` только после миграции импортов;
- оставить compatibility через package `__init__.py`;
- обновить все imports.

Вариант B — если удаление рискованно:

- оставить файл как active compatibility entrypoint;
- не использовать package import path `services.private_archive`;
- документировать ограничение;
- запланировать migration.

Предпочтительно добиться чистого package import.

## 9.3. Критерии приемки

Этап завершён, если:

- import resolution понятен;
- конфликтов нет;
- compatibility imports покрыты тестами.

---

# 10. ЭТАП 6 — Проверить Storage Contracts usage

## 10.1. Цель

Убедиться, что новые storage contracts реально используются, а не просто лежат рядом.

## 10.2. Атомарные задачи

### 10.2.1. Проверить импорты широкого interface

Выполнить:

```bash
grep -R "infrastructure.storage.interface" -n tg_msg_manager tests
grep -R "from .*storage.interface import" -n tg_msg_manager tests
```

Классифицировать использования:

- acceptable compatibility import;
- old import that should migrate;
- test-only import;
- aggregator import.

### 10.2.2. Проверить использование contracts

Выполнить:

```bash
grep -R "contracts" -n tg_msg_manager
grep -R "SyncStorage\\|ExportStorage\\|DBExportStorage\\|ContextStorage\\|PrivateArchiveStorage" -n tg_msg_manager
```

### 10.2.3. Обновить новые сервисы на narrow contracts

Особенно проверить:

```text
services/db_export/
services/private_archive/
services/context/
services/export/
```

Каждый сервис должен зависеть от узкого contract, если contract существует.

### 10.2.4. Оставить interface.py как aggregator

Если `interface.py` нужен для compatibility:

- оставить;
- добавить комментарий;
- не добавлять туда новую бизнес-логику;
- новые сервисы не должны зависеть от него без причины.

### 10.2.5. Добавить architecture rule

В `docs/ARCHITECTURE_RULES.md` добавить или проверить правило:

```markdown
New services must depend on narrow storage contracts, not on the compatibility storage interface aggregator.
```

## 10.3. Критерии приемки

Этап завершён, если:

- новые сервисы используют narrow contracts;
- `interface.py` не является активным dumping ground;
- старые imports либо совместимы, либо мигрированы;
- tests проходят.

---

# 11. ЭТАП 7 — Проверить Payload compatibility

## 11.1. Цель

Убедиться, что `core/models/service_payloads.py` не является двойным источником моделей.

## 11.2. Атомарные задачи

### 11.2.1. Найти импорты старого payload файла

Выполнить:

```bash
grep -R "service_payloads" -n tg_msg_manager tests
```

Классифицировать:

- compatibility import;
- old import to migrate;
- test-only import;
- external/public import.

### 11.2.2. Проверить новые payload modules

Проверить:

```text
core/models/payloads/
```

Убедиться, что доменные модели лежат в правильных файлах:

- sync;
- export;
- db_export;
- context;
- private_archive;
- retry;
- report;
- telemetry.

### 11.2.3. Превратить `service_payloads.py` в compatibility aggregator

Если файл всё ещё содержит активные primary definitions:

- перенести их в domain module;
- re-export из `service_payloads.py`;
- добавить deprecated/compatibility comment.

Пример:

```python
"""Compatibility aggregator for service payload models.

New code should import from tg_msg_manager.core.models.payloads.<domain>.
"""

from tg_msg_manager.core.models.payloads.export import ExportStartedPayload
...
```

### 11.2.4. Добавить compatibility import tests

Проверить, что старые импорты работают.

## 11.3. Критерии приемки

Этап завершён, если:

- primary payload definitions живут в domain modules;
- `service_payloads.py` является aggregator;
- старые imports работают;
- нет import cycles.

---

# 12. ЭТАП 8 — Дожать PrivateArchiveService facade

## 12.1. Цель

Если новый `private_archive/service.py` всё ещё содержит слишком много operational logic, вынести её в отдельные компоненты.

Особенно проверить методы:

- media download;
- media processing;
- message stream processing;
- per-message archive orchestration.

## 12.2. Атомарные задачи

### 12.2.1. Найти крупные методы

Выполнить:

```bash
python3 - <<'PY'
from pathlib import Path
p = Path("tg_msg_manager/services/private_archive/service.py")
text = p.read_text()
print("lines:", len(text.splitlines()))
PY
```

Ручно просмотреть методы.

Кандидаты на вынос:

```text
_download_media
_process_archive_media
_archive_message
_archive_message_stream
```

### 12.2.2. Создать stream processor, если нужно

Если service содержит stream loop, создать:

```text
tg_msg_manager/services/private_archive/stream_processor.py
```

Ответственность:

- обработка потока сообщений;
- вызов media policy;
- вызов archive writer;
- вызов state manager;
- возврат progress/result.

Запрещено:

- CLI parsing;
- raw SQL;
- direct export formatting outside writer;
- global state.

### 12.2.3. Создать media downloader, если нужно

Если service содержит прямую download logic, создать:

```text
tg_msg_manager/services/private_archive/media_downloader.py
```

Ответственность:

- делегировать media download adapter/client;
- возвращать structured result;
- не решать archive policy.

### 12.2.4. Оставить service facade тонким

После выноса `PrivateArchiveService` должен:

- собрать dependencies;
- вызвать planner/source resolver;
- вызвать stream processor;
- вызвать state manager;
- вернуть result.

Он не должен содержать большие loops и media download details.

### 12.2.5. Добавить unit tests

Добавить тесты:

- stream processor handles empty stream;
- stream processor calls writer;
- media policy decision respected;
- media download failure handled;
- state manager called on success/failure.

## 12.3. Критерии приемки

Этап завершён, если:

- private archive facade уменьшен;
- operational loops вынесены;
- media download logic изолирована;
- tests проходят;
- behavior не изменён.

---

# 13. ЭТАП 9 — Обновить архитектурные документы

## 13.1. Цель

Убрать documentation drift.

## 13.2. Обновить PROJECT_ARCHITECTURE_OVERVIEW.md

Проверить и обновить:

- текущую структуру `services/db_export/`;
- текущую структуру `services/private_archive/`;
- статус старых wrapper-файлов;
- storage contracts;
- payloads package;
- analytics boundary;
- текущий test count;
- текущие bottlenecks;
- SQLite write-path limitations;
- live smoke limitations.

Удалить устаревшие утверждения, например:

- что `db_exporter.py` всё ещё основной крупный сервис, если он стал wrapper;
- что `service_payloads.py` — primary model file, если он стал aggregator;
- что `interface.py` — primary storage interface, если есть narrow contracts.

## 13.3. Обновить docs/ARCHITECTURE_RULES.md

Добавить/проверить разделы:

```markdown
## Compatibility wrappers

The following files are compatibility wrappers only:
- tg_msg_manager/services/db_exporter.py
- tg_msg_manager/services/private_archive.py
- tg_msg_manager/core/models/service_payloads.py
- tg_msg_manager/infrastructure/storage/interface.py

New code must not add business logic to these files.
```

Если какой-то файл не wrapper — явно указать фактический статус.

## 13.4. Обновить docs/PR_CHECKLIST.md

Добавить:

```markdown
- [ ] No duplicate active service implementation introduced
- [ ] Compatibility wrappers still point to new implementation
- [ ] Import smoke test passes
- [ ] Architecture docs match actual code
- [ ] Stage report updated if refactor-related
```

## 13.5. Обновить CHANGELOG.md

Добавить запись:

```markdown
## Stage 1 Consistency Pass

- Removed duplicate active service implementations.
- Converted legacy service entrypoints to compatibility wrappers.
- Verified DB export and private archive entrypoints.
- Updated architecture overview after Stage 1 refactor.
- Added compatibility import checks.
- Documented remaining limitations and follow-up tasks.
```

Не утверждать то, что фактически не сделано.

## 13.6. Критерии приемки

Этап завершён, если:

- docs соответствуют коду;
- устаревшие claims удалены;
- wrapper status зафиксирован;
- changelog обновлён.

---

# 14. ЭТАП 10 — Context Relation Tables Decision

## 14.1. Цель

Зафиксировать статус context relation tables.

## 14.2. Атомарные задачи

### 14.2.1. Найти context relation usage

Выполнить:

```bash
grep -R "message_context_links" -n .
grep -R "context_group_id" -n tg_msg_manager tests
grep -R "context_links" -n tg_msg_manager tests
```

### 14.2.2. Создать decision document

Создать:

```text
docs/refactor/CONTEXT_RELATION_TABLES_DECISION.md
```

Структура:

```markdown
# Context Relation Tables Decision

## 1. Existing relation structures

## 2. Writers

## 3. Readers

## 4. Hot-path usage

## 5. Current source of truth

## 6. Decision

Choose one:
- First-class relation layer
- Legacy compatibility layer
- Future migration candidate

## 7. Rules for new code

## 8. Follow-up tasks
```

### 14.2.3. Применить решение в docs

Обновить:

```text
PROJECT_ARCHITECTURE_OVERVIEW.md
docs/ARCHITECTURE_RULES.md
```

Указать, можно ли новым функциям использовать эти таблицы.

## 14.3. Критерии приемки

Этап завершён, если:

- decision document создан;
- статус таблиц ясен;
- architecture docs обновлены.

---

# 15. ЭТАП 11 — Live Smoke Checklist

## 15.1. Цель

Проверить, что live/manual проверки существуют и соответствуют реальному CLI.

## 15.2. Атомарные задачи

### 15.2.1. Проверить наличие файла

Проверить:

```text
docs/testing/LIVE_SMOKE_CHECKLIST.md
```

Если файла нет — создать.

### 15.2.2. Заполнить реальные команды

Checklist должен содержать реальные команды проекта для:

- help;
- minimal sync;
- flat export;
- deep context export;
- db export;
- private archive / export-pm;
- retry;
- report.

Не оставлять placeholder вида:

```text
<actual command>
```

Если безопасную команду нельзя указать без локального окружения — написать шаблон с переменными:

```bash
tg-msg-manager export --user-id "$TEST_USER_ID" --limit 1
```

и описать переменные.

### 15.2.3. Добавить expected results

Для каждой команды указать:

- expected exit code;
- expected output;
- expected file/db side effect;
- что считается failure.

## 15.3. Критерии приемки

Этап завершён, если:

- checklist существует;
- placeholder-команды заменены;
- expected behavior описан.

---

# 16. ЭТАП 12 — Финальные проверки

## 16.1. Full tests

Выполнить:

```bash
make test
```

или фактическую команду проекта.

## 16.2. Full verify

Выполнить:

```bash
make verify
```

если команда есть.

## 16.3. Compileall

Выполнить:

```bash
python3 -m compileall tg_msg_manager
```

## 16.4. Import smoke

Выполнить:

```bash
python3 - <<'PY'
import tg_msg_manager

from tg_msg_manager.services.db_export.service import DBExportService
from tg_msg_manager.services.db_exporter import DBExportService as DBExportServiceCompat

assert DBExportServiceCompat is DBExportService

try:
    from tg_msg_manager.services.private_archive.service import PrivateArchiveService
    from tg_msg_manager.services.private_archive import PrivateArchiveService as PrivateArchiveServiceCompat
    assert PrivateArchiveServiceCompat is PrivateArchiveService
except Exception as exc:
    raise AssertionError(f"private archive compatibility import failed: {exc}") from exc

import tg_msg_manager.infrastructure.storage.contracts
import tg_msg_manager.core.models.payloads

print("import smoke ok")
PY
```

Адаптировать, если import path отличается из-за package/file conflict.

## 16.5. DB export regression

Запустить fixture DB export до/после или существующий regression test.

Проверить:

- TXT output stable;
- JSONL schema stable;
- ordering stable;
- fingerprint/skip behavior stable.

## 16.6. Private archive regression

Если есть offline test — запустить.

Если нет — добавить минимальные unit tests для:

- planner;
- source resolver;
- media policy;
- archive writer;
- state manager;
- service facade.

## 16.7. Проверить отсутствие двойных классов

Выполнить:

```bash
grep -R "class DBExportService" -n tg_msg_manager
grep -R "class PrivateArchiveService" -n tg_msg_manager
```

Ожидаемое:

- `DBExportService` объявлен только в новом active module;
- `PrivateArchiveService` объявлен только в новом active module;
- wrapper-файлы не содержат class definitions.

## 16.8. Критерии приемки

Финальные проверки пройдены, если:

- tests pass;
- compileall pass;
- import smoke pass;
- DB export regression pass;
- no duplicate active service class definitions;
- docs updated.

---

# 17. Финальный отчёт

Создать:

```text
docs/refactor/STAGE_1_CONSISTENCY_REPORT.md
```

Структура:

```markdown
# Stage 1 Consistency Report

## 1. Summary

Кратко: какие незакрытые проблемы исправлены.

## 2. Baseline

- Commit:
- Branch:
- Tests before:
- Known issues before:

## 3. Duplicate implementation audit

### DBExportService

- Active implementation:
- Compatibility wrapper:
- Old imports:
- Fixed issues:

### PrivateArchiveService

- Active implementation:
- Compatibility wrapper:
- Old imports:
- Fixed issues:

## 4. Import compatibility

| Import path | Status |
|---|---|

## 5. Storage contracts

Что проверено и что осталось.

## 6. Payload compatibility

Что проверено и что осталось.

## 7. Private archive facade

Что вынесено / что оставлено.

## 8. Context relation tables decision

Краткое решение.

## 9. Documentation updates

Список обновлённых файлов.

## 10. Test results

Команды и результаты.

## 11. Remaining risks

Оставшиеся риски.

## 12. Recommended next step

Что делать после закрытия consistency pass.
```

---

# 18. Что НЕ делать в этом pass

Не делать:

- analytics;
- social graph;
- semantic search;
- NLP;
- dashboard;
- multi-account;
- schema migration;
- Telegram adapter rewrite;
- export format redesign;
- CLI redesign;
- performance tuning без тестов;
- массовое переименование без необходимости.

---

# 19. Ожидаемый итог

После выполнения этого файла проект должен находиться в состоянии:

```text
1 active implementation per service
old files = compatibility wrappers
docs match code
tests pass
imports stable
no duplicate service truth
ready for next planned feature stage
```

Только после этого можно переходить к следующим крупным расширениям.
