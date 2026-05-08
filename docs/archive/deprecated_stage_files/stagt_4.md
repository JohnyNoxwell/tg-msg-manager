# STAGE 4 — Audit / Report Read-Side

## Цель этапа

Добавить read-only диагностический слой, который помогает понять состояние локальной БД и pipeline после foundation refactors и retry integration.

Этап сознательно уже не про “аналитику”, а про operational observability и безопасную диагностику.

## Статус выполнения

Обновлено: `2026-05-04`

- [x] `4.1` Reporting models and read-side API
- [x] `4.2` Collector and warning rules
- [x] `4.3` Renderers and CLI
- [x] `4.4` Final verification

Закрыто в текущем проходе:
- добавлены typed reporting models для database/target/retry/export/warning summaries;
- SQLite read-side расширен read-only queries для:
  - database summary;
  - target summaries;
  - retry summary;
- реализован `ReportCollector`, который читает только storage/filesystem и не ходит в Telegram;
- export artifact state определяется только из локального `DB_EXPORTS`;
- реализованы formal deterministic warnings:
  - incomplete target;
  - no target messages;
  - no context coverage;
  - high missing-parent signals;
  - retry queue not empty;
  - failed retry tasks;
  - stale sync;
  - missing export state;
- добавлены Markdown и JSON renderers;
- добавлен новый read-only CLI surface `report`, работающий без Telegram credentials;
- этап не зашёл в analytics scope и не ввёл новый orchestration subsystem.

Текущая верификация:
- `python3 -m unittest tests.test_reporting tests.test_storage_sqlite tests.test_cli -q` -> `34 tests`, `OK`
- `make test` -> `140 tests`, `OK`
- `ruff check .` -> `OK`
- `ruff format --check .` -> `OK`

Итог этапа:
- `Stage 4` завершён;
- report-сборка идёт только через read-side data sources;
- warnings формальны, объяснимы и детерминированы;
- новый публичный surface ограничен ровно одной read-only командой: `report`;
- analytics scope не смешан с operational diagnostics.

Финальная форма reporting hotspots:
- `ReportCollector._build_warnings` -> около `109` строк
- `SQLiteReadPathMixin.get_report_target_summaries` -> около `70` строк
- `render_report_markdown` -> около `58` строк
- `ReportCollector._collect_export_states` -> около `43` строк
- `SQLiteReadPathMixin.get_report_database_summary` -> около `41` строк
- `SQLiteReadPathMixin.get_report_retry_summary` -> около `33` строк

## Что делаем

- создаём typed reporting models;
- расширяем storage read-side queries для:
  - database summary;
  - targets;
  - checkpoints;
  - context coverage;
  - retry state;
  - export state, если он локально доступен;
- реализуем collector и deterministic warnings;
- добавляем Markdown и JSON renderers;
- добавляем read-only CLI command `report`.

## Что не делаем

- не добавляем keyword/topic analysis;
- не строим graph analytics;
- не используем Telegram API;
- не превращаем report в новый orchestration subsystem;
- не дублируем analytics backlog под другим именем.

## Входные инварианты

- Stage 3 завершён, поэтому retry state уже имеет смысл диагностировать;
- report работает только через storage/filesystem read paths;
- warnings должны быть объяснимыми и deterministic;
- любые thresholds должны быть документированы или явно зафиксированы в коде.

## Исполняемая очередь

### Блок 4.1 — Reporting models and read-side API

- определить компактные typed models для database/target/checkpoint/context/retry/export summaries;
- добавить read-only storage methods;
- запретить SQL в collector layer.

### Блок 4.2 — Collector and warning rules

- собрать единый `ReportCollector`, который ничего не печатает и не ходит в Telegram;
- реализовать только формальные warnings:
  - incomplete target;
  - no target messages;
  - no context coverage;
  - high missing-parent signals;
  - retry queue not empty / failed tasks;
  - stale sync / missing export state, если применимо.

### Блок 4.3 — Renderers and CLI

- реализовать markdown/json renderers;
- добавить read-only CLI subcommand `report`;
- убедиться, что новый CLI surface не влияет на старые команды.

### Блок 4.4 — Final verification

- прогнать reporting/storage/CLI tests;
- проверить, что `report` работает без Telegram credentials;
- проверить, что вывод детерминирован на одинаковом локальном состоянии.

## Definition of Done

- появился ровно один новый read-only CLI surface: `report`;
- report-сборка идёт только через read-side data sources;
- warnings формальны и объяснимы;
- этап не заходит в analytics scope;
- поведение подтверждено тестами.

Статус:
- `Done` on `2026-05-04`.
