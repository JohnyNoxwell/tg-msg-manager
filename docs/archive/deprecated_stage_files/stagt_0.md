# STAGE 0 — Foundation Stabilization

## Цель этапа

Стабилизировать текущую кодовую базу перед дальнейшими рефакторингами и расширением функционала.

Этап заменяет старые `Stage 0` и `Stage 1` и служит входной точкой в foundation backlog.

Результат этапа:
- зафиксирован baseline текущего состояния;
- test/lint/help checks проходят;
- `Settings`, `config.example.json` и актуальная документация не расходятся;
- `scripts/` классифицированы и не выглядят как случайный legacy-набор;
- критические инварианты защищены regression tests;
- крупные сервисы пока не переписываются.

## Статус выполнения

Обновлено: `2026-05-04`

- [x] `0.1` Baseline checks
- [x] `0.2` Config and docs alignment
- [x] `0.3` Scripts classification
- [x] `0.4` Invariant regression coverage
- [x] `0.5` Minimal corrective fixes
- [x] `0.6` Final verification

Итог текущего прохода:
- `make test` -> `122 tests`, `OK`
- `ruff check .` -> `OK`
- `ruff format --check .` -> `OK`
- CLI help surface для `export`, `update`, `db-export`, `clean`, `delete` проверен без падений

## Что делаем

- зафиксировать baseline текущего состояния репо и test surface;
- синхронизировать `Settings`, `config.example.json`, `README.md`, `COMMANDS.md`;
- классифицировать `scripts/` как `active`, `maintenance`, `deprecated` или `broken legacy`;
- закрыть и/или задокументировать drift-зоны, начиная с `context_group_id`;
- усилить regression coverage для известных архитектурных инвариантов;
- делать только низкорисковые исправления и helper extractions, если они нужны для читабельности и уже покрыты тестами.

## Что не делаем

- не меняем публичное CLI behavior;
- не добавляем новые CLI команды;
- не меняем формат экспорта;
- не переписываем `ExportService`;
- не переписываем `DeepModeEngine`;
- не меняем sync algorithm;
- не добавляем `retry`, `report` или `analytics` features;
- не делаем schema changes без отдельной миграции и тестов;
- не запускаем live Telegram операции.

## Входные инварианты

- источником истины считаются текущий код, `backlog/archive/TODO.md`, существующие тесты и актуальные runtime contracts;
- уже выполненные задачи из `backlog/archive/TODO.md` не должны заново попадать в execution scope;
- если docs расходятся с кодом, правим docs, а не придумываем новую runtime-семантику;
- любые исправления должны быть обратимо объяснимы и не должны менять пользовательское поведение.

## Исполняемая очередь

### Блок 0.1 — Baseline checks

- зафиксировать `git status`;
- прогнать актуальные команды качества:
  - `make test` или эквивалентный test suite;
  - `ruff check .`;
  - `ruff format --check .`;
- проверить CLI help surface:
  - `python3 -m tg_msg_manager.cli --help`;
  - `export --help`;
  - `update --help`;
  - `db-export --help`;
  - `clean --help`;
  - `delete --help`.

### Блок 0.2 — Config and docs alignment

- извлечь фактическую модель `Settings` из `tg_msg_manager/core/config.py`;
- привести `config.example.json` к актуальным полям и alias semantics;
- убрать из `README.md` и `COMMANDS.md` устаревшие config-описания;
- при необходимости создать компактный config note в backlog или docs, но без избыточной документационной ветки.

### Блок 0.3 — Scripts classification

- проверить каждый файл в `scripts/`;
- определить, какие скрипты всё ещё соответствуют текущей архитектуре;
- для `deprecated` и `broken legacy` добавить явную пометку в docstring с причиной и альтернативой;
- не удалять скрипты только ради уборки.

### Блок 0.4 — Invariant regression coverage

- убедиться, что тестами защищены:
  - target attribution;
  - HEAD/TAIL checkpoint behavior;
  - deep-mode order of preference;
  - `db-export` without Telegram access;
  - `delete` vs `clean`;
  - `context_group_id` drift;
- если теста не хватает, добавить минимальный regression test без изменения поведения.

### Блок 0.5 — Minimal corrective fixes

- исправлять только подтверждённые drift/problems;
- разрешены только узкие изменения в типах, docs, guards и small pure helpers;
- запрещены скрытые рефакторинги под видом “подготовки”.

### Блок 0.6 — Final verification

- повторно прогнать quality gates;
- повторно проверить CLI help surface;
- убедиться, что foundation backlog может безопасно перейти к Stage 1 без открытых базовых противоречий.

## Definition of Done

- baseline checks проходят без live Telegram действий;
- `config.example.json` соответствует актуальному `Settings`;
- `scripts/` классифицированы и не вводят в заблуждение;
- критические инварианты защищены тестами или явно задокументированы как pending edge cases;
- нет дублирования scope со следующим этапом;
- не изменены CLI behavior, export format и destructive semantics.
