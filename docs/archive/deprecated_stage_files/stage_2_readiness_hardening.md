# STAGE 2 — READINESS / HARDENING PASS

## 0. Назначение документа

Этот документ описывает короткий Stage 2 для проекта `tg-msg-manager`.

Это не новый большой рефакторинг и не этап добавления функций.

Цель: зафиксировать архитектурную консистентность после Stage 1, закрыть оставшиеся риски и подготовить проект к безопасному расширению.

После Stage 2 можно переходить к новым направлениям:

- analytics read models;
- interaction graph;
- dataset projection;
- semantic search;
- AI-ready exports;
- future dashboard/API;
- future multi-account/workspace design.

Но на Stage 2 эти функции НЕ реализуются.

---

# 1. Главный диагноз

После Stage 1 проект уже имеет нормальную модульную структуру:

```text
services/export/
services/context/
services/db_export/
services/private_archive/
services/analytics/
infrastructure/storage/contracts/
core/models/payloads/
```

Главные проблемы прошлого этапа в основном закрыты:

- `DBExportService` больше не должен иметь две активные реализации;
- `PrivateArchiveService` больше не должен иметь две активные реализации;
- storage contracts вынесены;
- payload models разнесены;
- private archive split выполнен;
- DB export split выполнен;
- Stage 1 reports/audits появились.

Оставшиеся риски:

1. `PROJECT_ARCHITECTURE_OVERVIEW.md` может быть устаревшим.
2. Wrapper-файлы могут снова начать расти.
3. `services/private_archive.py` рядом с пакетом `services/private_archive/` остаётся потенциальной import-ловушкой.
4. Фасады могут снова стать монолитами.
5. Live smoke checklist может быть недостаточно конкретным.
6. Raw/code formatting нужно проверить и зафиксировать.
7. Нужны guard tests, чтобы прошлые проблемы не вернулись.

---

# 2. Строгие ограничения

## 2.1. Запрещено добавлять новые функции

На Stage 2 нельзя добавлять:

- analytics;
- social graph;
- influence scoring;
- behavioral profiling;
- NLP;
- semantic search;
- embeddings;
- dashboard;
- REST API;
- multi-account;
- workspace system;
- новые export modes;
- новые CLI-команды;
- новые Telegram collectors.

## 2.2. Запрещено менять публичное поведение

Нельзя менять:

- CLI command names;
- CLI arguments;
- default values;
- export format;
- export filenames;
- export directory layout;
- DB schema;
- target attribution;
- context depth;
- sync behavior;
- retry behavior;
- report format.

## 2.3. Запрещено делать архитектурный rewrite

Нельзя:

- переписывать проект заново;
- менять SQLite;
- менять Telegram adapter;
- переименовывать крупные пакеты без необходимости;
- делать массовый перенос файлов без конкретной причины;
- удалять compatibility wrappers без audit и тестов.

## 2.4. Разрешено

Можно:

- добавлять guard tests;
- обновлять архитектурную документацию;
- усиливать compatibility tests;
- проверять import resolution;
- добавлять smoke checklist;
- добавлять lint/format checks;
- помечать wrapper-файлы как protected;
- добавлять архитектурные ограничения в docs;
- исправлять documentation drift;
- исправлять форматирование, если оно реально повреждено.

---

# 3. Целевой результат Stage 2

После Stage 2 должно быть так:

1. Архитектурные документы соответствуют фактическому коду.
2. Wrapper-файлы защищены тестами.
3. Нет риска возврата двойных реализаций.
4. Import resolution для `private_archive` зафиксирован.
5. Фасады защищены от нового роста.
6. Live smoke checklist содержит реальные команды.
7. Format/lint/test verification пройдены.
8. Проект готов к следующему feature stage.

---

# 4. Definition of Done

Stage 2 считается завершённым только если:

- [ ] `PROJECT_ARCHITECTURE_OVERVIEW.md` обновлён под текущее состояние.
- [ ] Wrapper guard tests добавлены.
- [ ] Guard tests проверяют отсутствие class definitions в wrapper-файлах.
- [ ] Compatibility imports проверены тестами.
- [ ] Import resolution для `services.private_archive` задокументирован.
- [ ] Shadow-wrapper риск закрыт или явно зафиксирован.
- [ ] Facade growth protection добавлен в docs/checklist.
- [ ] Live smoke checklist содержит реальные команды или безопасные шаблоны с переменными.
- [ ] `compileall` проходит.
- [ ] `ruff format --check` проходит или эквивалент проекта проходит.
- [ ] `ruff check` проходит или эквивалент проекта проходит.
- [ ] `make test` проходит.
- [ ] `make verify` проходит, если команда есть.
- [ ] `CHANGELOG.md` обновлён.
- [ ] `docs/refactor/STAGE_2_READINESS_REPORT.md` создан.
- [ ] Новые продуктовые функции не добавлены.

---

# 5. Порядок выполнения

Работать строго по этапам:

1. Зафиксировать baseline.
2. Проверить форматирование и compileall.
3. Добавить wrapper guard tests.
4. Проверить import resolution.
5. Защитить фасады от роста.
6. Обновить architecture overview.
7. Обновить live smoke checklist.
8. Обновить changelog.
9. Провести финальные проверки.
10. Создать Stage 2 report.

---

# 6. ЭТАП 1 — Baseline

## 6.1. Цель

Зафиксировать текущее состояние перед Stage 2.

## 6.2. Атомарные задачи

### 6.2.1. Проверить git state

Выполнить:

```bash
git status --short
git rev-parse HEAD
git branch --show-current
```

Создать файл:

```text
docs/refactor/STAGE_2_READINESS_BASELINE.md
```

Записать:

```markdown
# Stage 2 Readiness Baseline

## 1. Commit

## 2. Branch

## 3. Git status

## 4. Current known risks

## 5. Commands to be run
```

### 6.2.2. Запустить текущие тесты

Выполнить:

```bash
make test
```

Если команды нет — использовать актуальную команду из README/Makefile/pyproject.

### 6.2.3. Запустить verify

Выполнить:

```bash
make verify
```

Если команды нет — записать, что verify command отсутствует.

### 6.2.4. Зафиксировать результаты

В `STAGE_2_READINESS_BASELINE.md` добавить:

```markdown
## Test results

| Command | Result | Notes |
|---|---|---|
```

## 6.3. Критерии приемки

Этап завершён, если:

- baseline file создан;
- тесты запущены;
- результаты зафиксированы.

---

# 7. ЭТАП 2 — Format / Compile / Import Sanity

## 7.1. Цель

Проверить, что файлы не повреждены после рефакторинга и нормально читаются инструментами.

## 7.2. Атомарные задачи

### 7.2.1. Compileall

Выполнить:

```bash
python3 -m compileall tg_msg_manager
```

Если ошибка — исправить до продолжения.

### 7.2.2. Ruff check

Выполнить:

```bash
ruff check tg_msg_manager tests
```

Если проект использует другую команду — использовать её.

### 7.2.3. Ruff format check

Выполнить:

```bash
ruff format --check tg_msg_manager tests
```

Если проект использует `black`, `isort` или `make format-check`, использовать фактическую команду.

### 7.2.4. Проверить подозрительно короткие raw-файлы

Проверить ключевые файлы:

```bash
wc -l tg_msg_manager/services/db_exporter.py
wc -l tg_msg_manager/services/db_export/service.py
wc -l tg_msg_manager/services/private_archive.py
wc -l tg_msg_manager/services/private_archive/service.py
```

Если файл реально сохранён в 1–4 строки из-за minified formatting — отформатировать нормально.

### 7.2.5. Import smoke

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
print("import smoke ok")
PY
```

## 7.3. Критерии приемки

Этап завершён, если:

- compileall проходит;
- lint проходит;
- format check проходит;
- key files имеют нормальное форматирование;
- import smoke проходит.

---

# 8. ЭТАП 3 — Wrapper Guard Tests

## 8.1. Цель

Гарантировать, что старые wrapper-файлы не превратятся обратно в активные реализации.

## 8.2. Protected wrapper files

Проверить и защитить:

```text
tg_msg_manager/services/db_exporter.py
tg_msg_manager/services/private_archive.py
tg_msg_manager/core/models/service_payloads.py
tg_msg_manager/infrastructure/storage/interface.py
```

## 8.3. Атомарные задачи

### 8.3.1. Создать тестовый файл

Создать:

```text
tests/test_architecture_wrappers.py
```

Если в проекте уже есть architecture tests — добавить туда.

### 8.3.2. Добавить guard для DBExportService

Тест должен проверять:

1. `db_exporter.py` не содержит `class DBExportService`.
2. Старый import указывает на новый класс.

Пример:

```python
from pathlib import Path


def test_db_exporter_wrapper_has_no_active_class_definition():
    path = Path("tg_msg_manager/services/db_exporter.py")
    text = path.read_text(encoding="utf-8")
    assert "class DBExportService" not in text


def test_db_exporter_compat_import_points_to_new_service():
    from tg_msg_manager.services.db_export.service import DBExportService
    from tg_msg_manager.services.db_exporter import DBExportService as CompatDBExportService

    assert CompatDBExportService is DBExportService
```

### 8.3.3. Добавить guard для PrivateArchiveService

Тест должен проверять:

1. compatibility entrypoint не содержит активной реализации;
2. import указывает на новый package service;
3. import resolution не ломается.

Пример:

```python
from pathlib import Path


def test_private_archive_wrapper_has_no_active_class_definition():
    path = Path("tg_msg_manager/services/private_archive.py")
    if path.exists():
        text = path.read_text(encoding="utf-8")
        assert "class PrivateArchiveService" not in text


def test_private_archive_compat_import_points_to_new_service():
    from tg_msg_manager.services.private_archive.service import PrivateArchiveService
    from tg_msg_manager.services.private_archive import PrivateArchiveService as CompatPrivateArchiveService

    assert CompatPrivateArchiveService is PrivateArchiveService
```

Если из-за file/package conflict import path отличается — адаптировать тест и задокументировать фактическое решение.

### 8.3.4. Добавить guard для service_payloads

Если `service_payloads.py` является aggregator, тест должен проверять, что новые primary models живут в `core/models/payloads/`.

Минимально:

```python
def test_service_payloads_is_compatibility_aggregator():
    from pathlib import Path

    path = Path("tg_msg_manager/core/models/service_payloads.py")
    text = path.read_text(encoding="utf-8")
    assert "Compatibility" in text or "compatibility" in text
```

Не делать тест слишком хрупким, если файл всё ещё легитимно содержит re-export aliases.

### 8.3.5. Добавить guard для storage interface

Если `interface.py` является aggregator, тест должен проверять, что он не содержит concrete SQLite implementation.

Минимально:

```python
def test_storage_interface_has_no_sqlite_queries():
    from pathlib import Path

    path = Path("tg_msg_manager/infrastructure/storage/interface.py")
    text = path.read_text(encoding="utf-8").lower()
    assert "select " not in text
    assert "insert " not in text
    assert "update " not in text
    assert "delete " not in text
```

Если в interface есть docstring с SQL words — сделать проверку менее грубой или исключить docstrings.

### 8.3.6. Запустить architecture tests

Выполнить:

```bash
pytest tests/test_architecture_wrappers.py
```

## 8.4. Критерии приемки

Этап завершён, если:

- guard tests добавлены;
- wrapper-файлы защищены;
- compatibility imports работают;
- tests проходят.

---

# 9. ЭТАП 4 — Private Archive Shadow Wrapper Risk

## 9.1. Цель

Зафиксировать и, если возможно, устранить риск конфликта между:

```text
tg_msg_manager/services/private_archive.py
tg_msg_manager/services/private_archive/
```

## 9.2. Атомарные задачи

### 9.2.1. Проверить import resolution

Выполнить:

```bash
python3 - <<'PY'
import tg_msg_manager.services.private_archive as pa
print("module:", pa)
print("file:", getattr(pa, "__file__", None))
print("has service:", hasattr(pa, "PrivateArchiveService"))
PY
```

### 9.2.2. Создать audit note

Создать или обновить:

```text
docs/refactor/PRIVATE_ARCHIVE_IMPORT_RESOLUTION.md
```

Записать:

```markdown
# Private Archive Import Resolution

## 1. Existing paths

## 2. Python import result

## 3. Active implementation

## 4. Compatibility path

## 5. Risk

## 6. Decision

## 7. Guard tests
```

### 9.2.3. Выбрать решение

Preferred outcome:

```text
tg_msg_manager/services/private_archive/               -> active package
tg_msg_manager/services/private_archive.py             -> absent or harmless wrapper
```

Если файл `private_archive.py` можно безопасно удалить после миграции импортов:

1. проверить все imports;
2. заменить старые imports;
3. удалить файл;
4. оставить compatibility через package `__init__.py`;
5. обновить docs/tests.

Если удалять рискованно:

1. оставить файл;
2. сделать его минимальным wrapper;
3. добавить guard test;
4. явно описать риск в docs.

### 9.2.4. Проверить CLI

Найти CLI wiring для `export-pm`.

Убедиться, что команда использует active package implementation.

## 9.3. Критерии приемки

Этап завершён, если:

- import resolution зафиксирован;
- решение documented;
- guard test существует;
- CLI не использует старую active implementation.

---

# 10. ЭТАП 5 — Facade Growth Protection

## 10.1. Цель

Защитить фасады от нового роста.

Фасады должны быть orchestration-only. Новая логика должна уходить в компоненты.

## 10.2. Protected facades

Список:

```text
tg_msg_manager/services/export/service.py
tg_msg_manager/services/context/engine.py
tg_msg_manager/services/db_export/service.py
tg_msg_manager/services/private_archive/service.py
```

## 10.3. Атомарные задачи

### 10.3.1. Зафиксировать текущие размеры

Выполнить:

```bash
wc -l tg_msg_manager/services/export/service.py
wc -l tg_msg_manager/services/context/engine.py
wc -l tg_msg_manager/services/db_export/service.py
wc -l tg_msg_manager/services/private_archive/service.py
```

Записать результат в:

```text
docs/refactor/FACADE_SIZE_BASELINE.md
```

### 10.3.2. Добавить правило в architecture docs

В `docs/ARCHITECTURE_RULES.md` добавить:

```markdown
## Facade growth protection

The following modules are orchestration facades:
- services/export/service.py
- services/context/engine.py
- services/db_export/service.py
- services/private_archive/service.py

New business logic must not be added directly to these files.
If a facade grows because of a new concern, extract a dedicated component first.
```

### 10.3.3. Добавить PR checklist item

В `docs/PR_CHECKLIST.md` добавить:

```markdown
- [ ] No new business logic added to orchestration facades
- [ ] New feature logic lives in a dedicated component
- [ ] Facade size increase is justified or avoided
```

### 10.3.4. Опционально добавить soft test

Не делать слишком хрупкий line-count test, если проект активно развивается.

Разрешено добавить informational architecture test, который печатает/проверяет грубый предел, например:

```python
def test_facades_are_not_extremely_large():
    from pathlib import Path

    max_lines = 450
    paths = [
        Path("tg_msg_manager/services/export/service.py"),
        Path("tg_msg_manager/services/context/engine.py"),
        Path("tg_msg_manager/services/db_export/service.py"),
        Path("tg_msg_manager/services/private_archive/service.py"),
    ]

    for path in paths:
        if path.exists():
            assert len(path.read_text(encoding="utf-8").splitlines()) <= max_lines
```

Если текущие фасады уже больше лимита — не добавлять failing test. Зафиксировать baseline и добавить checklist-only guard.

## 10.4. Критерии приемки

Этап завершён, если:

- facade baseline создан;
- architecture rules обновлены;
- PR checklist обновлён;
- нет новых крупных методов в фасадах.

---

# 11. ЭТАП 6 — Обновить PROJECT_ARCHITECTURE_OVERVIEW.md

## 11.1. Цель

Синхронизировать главный архитектурный документ с текущим состоянием после Stage 1/Stage 2.

## 11.2. Что проверить

Обновить:

- актуальную дату;
- актуальный test count;
- актуальные active services;
- статус compatibility wrappers;
- статус DB export split;
- статус private archive split;
- storage contracts;
- payloads package;
- analytics boundary;
- context relation table decision;
- known bottlenecks;
- live smoke limitations.

## 11.3. Удалить устаревшие утверждения

Удалить или исправить, если они больше неверны:

- `db_exporter.py` как active large service;
- `private_archive.py` как active large service;
- `service_payloads.py` как primary model source;
- `interface.py` как единственный storage interface;
- старый test count;
- устаревшие Stage 0-only notes.

## 11.4. Добавить актуальное состояние

Добавить раздел:

```markdown
## Current post-Stage-2 architecture status

- DB export active implementation:
- Private archive active implementation:
- Compatibility wrappers:
- Storage contracts:
- Payload modules:
- Analytics boundary:
- Context relation decision:
- Test status:
```

## 11.5. Критерии приемки

Этап завершён, если:

- overview соответствует коду;
- устаревшие данные исправлены;
- known risks актуальны.

---

# 12. ЭТАП 7 — Live Smoke Checklist

## 12.1. Цель

Сделать manual smoke checklist пригодным к реальному использованию.

## 12.2. Файл

Проверить или создать:

```text
docs/testing/LIVE_SMOKE_CHECKLIST.md
```

## 12.3. Обязательные сценарии

Checklist должен содержать:

1. Help command.
2. Minimal sync.
3. Flat export.
4. Deep context export.
5. DB export.
6. Private archive / export-pm.
7. Retry list/run.
8. Report.
9. Clean dry-run, если команда есть.
10. Delete dry-run / safe mode, если команда есть.

## 12.4. Команды

Не оставлять placeholder:

```text
<actual command>
```

Использовать реальные команды или безопасные шаблоны с переменными:

```bash
tg-msg-manager export --user-id "$TEST_USER_ID" --limit 1
```

Для каждой переменной указать:

```markdown
Required variables:
- TEST_USER_ID
- TEST_CHAT_ID
- TEST_OUTPUT_DIR
```

## 12.5. Expected results

Для каждого сценария указать:

- expected exit code;
- expected console output;
- expected DB side effect;
- expected file side effect;
- rollback/cleanup notes;
- what counts as failure.

## 12.6. Критерии приемки

Этап завершён, если:

- checklist exists;
- commands are concrete;
- expected results are concrete;
- no unsafe destructive command runs without dry-run/safe mode.

---

# 13. ЭТАП 8 — Architecture Rules / AGENTS.md Sync

## 13.1. Цель

Убедиться, что `AGENTS.md`, `docs/ARCHITECTURE_RULES.md` и `docs/PR_CHECKLIST.md` синхронизированы.

## 13.2. Атомарные задачи

### 13.2.1. Проверить AGENTS.md

Если `AGENTS.md` есть в корне:

- проверить, что он запрещает добавлять логику в wrappers;
- проверить, что он запрещает raw SQL in services;
- проверить, что он защищает facades;
- проверить, что он упоминает storage contracts;
- проверить, что он упоминает analytics boundary.

Если `AGENTS.md` отсутствует — создать из актуальных architecture rules.

### 13.2.2. Синхронизировать docs/ARCHITECTURE_RULES.md

Убедиться, что правила не противоречат `AGENTS.md`.

### 13.2.3. Синхронизировать docs/PR_CHECKLIST.md

Checklist должен включать:

```markdown
- [ ] Wrapper guard tests still pass
- [ ] No duplicate active service implementation
- [ ] No business logic added to compatibility wrappers
- [ ] No raw SQL added to services
- [ ] No new logic added to orchestration facades
- [ ] Storage contracts remain narrow
- [ ] Export output regression checked if export touched
- [ ] Live smoke checklist updated if Telegram behavior touched
```

## 13.3. Критерии приемки

Этап завершён, если:

- AGENTS.md существует;
- architecture rules синхронизированы;
- PR checklist обновлён.

---

# 14. ЭТАП 9 — Changelog

## 14.1. Цель

Зафиксировать Stage 2 как hardening/readiness pass.

## 14.2. Добавить запись

В `CHANGELOG.md` добавить:

```markdown
## Stage 2 Readiness / Hardening

- Updated architecture overview to match post-Stage-1 structure.
- Added wrapper guard tests for compatibility entrypoints.
- Verified DB export and private archive compatibility imports.
- Documented private archive import resolution.
- Added facade growth protection rules.
- Updated live smoke checklist with concrete commands.
- Verified compile, lint, format, test, and import smoke checks.
```

Не утверждать то, что фактически не сделано.

## 14.3. Критерии приемки

Этап завершён, если changelog обновлён и соответствует фактическим изменениям.

---

# 15. ЭТАП 10 — Финальные проверки

## 15.1. Выполнить полный набор проверок

Выполнить:

```bash
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
make test
make verify
```

Если проект использует другие команды — использовать фактические.

## 15.2. Выполнить wrapper tests

```bash
pytest tests/test_architecture_wrappers.py
```

## 15.3. Выполнить import smoke

```bash
python3 - <<'PY'
import tg_msg_manager
import tg_msg_manager.services.export
import tg_msg_manager.services.context
import tg_msg_manager.services.db_export
import tg_msg_manager.services.private_archive

from tg_msg_manager.services.db_export.service import DBExportService
from tg_msg_manager.services.db_exporter import DBExportService as CompatDBExportService
assert CompatDBExportService is DBExportService

from tg_msg_manager.services.private_archive.service import PrivateArchiveService
from tg_msg_manager.services.private_archive import PrivateArchiveService as CompatPrivateArchiveService
assert CompatPrivateArchiveService is PrivateArchiveService

print("stage 2 import smoke ok")
PY
```

Адаптировать private archive import, если принято другое compatibility решение.

## 15.4. Выполнить duplicate class check

```bash
grep -R "class DBExportService" -n tg_msg_manager
grep -R "class PrivateArchiveService" -n tg_msg_manager
```

Ожидаемое:

- no class definition in wrapper files;
- one active class definition per service.

## 15.5. Критерии приемки

Этап завершён, если:

- all checks pass;
- wrapper guards pass;
- imports pass;
- duplicate class check clean;
- docs updated.

---

# 16. Stage 2 Report

Создать:

```text
docs/refactor/STAGE_2_READINESS_REPORT.md
```

## 16.1. Структура отчёта

```markdown
# Stage 2 Readiness / Hardening Report

## 1. Summary

Кратко: что было сделано.

## 2. Baseline

- Commit:
- Branch:
- Initial test status:

## 3. Wrapper guard tests

| Wrapper | Guard status | Compatibility import |
|---|---|---|

## 4. Private archive import resolution

- Active package:
- Compatibility path:
- Risk:
- Decision:

## 5. Facade growth protection

| Facade | Current line count | Rule |
|---|---|---|

## 6. Documentation updates

Список обновлённых документов.

## 7. Live smoke checklist

Что обновлено.

## 8. Final checks

| Command | Result |
|---|---|

## 9. Remaining risks

Оставшиеся риски.

## 10. Ready for next stage?

Yes/No.

## 11. Recommended next stage

Например:
- Stage 3 Analytics Read Models
- Stage 3 Interaction Graph Foundation
- Stage 3 Dataset Projection
```

## 16.2. Критерии приемки

Отчёт должен быть конкретным: не писать “done”, если проверка не выполнялась.

---

# 17. Что НЕ делать на Stage 2

Не делать:

- новых CLI-команд;
- новых export режимов;
- новых таблиц;
- новой аналитики;
- scoring пользователей;
- NLP;
- embeddings;
- dashboard;
- multi-account;
- замену SQLite;
- переписывание Telegram adapter;
- удаление совместимости без тестов.

---

# 18. Ожидаемый итог

После Stage 2 проект должен быть в состоянии:

```text
architecture docs match code
wrappers protected
facades protected
imports stable
tests pass
live smoke documented
ready for feature expansion
```

После этого можно начинать следующий stage уже как feature foundation, например:

```text
Stage 3 — Analytics Read Models
```

или:

```text
Stage 3 — Interaction Graph Foundation
```
