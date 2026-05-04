# STAGE 1 — Export Pipeline Refactor

## Цель этапа

Довести `ExportService` до роли фасада и orchestration entrypoint, а не центрального контейнера всей sync-логики.

Этап опирается на уже выполненные рефакторинги из `TODO.md` и не должен заново выполнять то, что уже выделено в helpers, typed DTO и event abstractions.

## Статус выполнения

Обновлено: `2026-05-04`

- [x] `1.1` Re-audit remaining hotspots
- [x] `1.2` Baseline protection
- [x] `1.3` Scan range and planning boundaries
- [x] `1.4` Checkpoint and target coordination boundaries
- [x] `1.5` Execution and progress routing
- [x] `1.6` Final verification

Закрыто в текущем проходе:
- карта remaining hotspots пересобрана по фактическому `exporter.py`;
- scan range planning вынесен в `tg_msg_manager/services/sync/scan_ranges.py`;
- scan checkpoint outcome logic вынесен в `tg_msg_manager/services/sync/checkpoints.py`;
- progress reporter вынесен в `tg_msg_manager/services/sync/progress.py`;
- target identity/mode resolution вынесены в `tg_msg_manager/services/sync/targets.py`;
- tracked-target planning и shared prefetch coordination вынесены в `tg_msg_manager/services/sync/tracked_targets.py`;
- scan stream selection, skip guards и completion flags вынесены в `tg_msg_manager/services/sync/scan_execution.py`;
- sync execution-plan building и empty-range terminal completion вынесены в `tg_msg_manager/services/sync/execution_plan.py`;
- range-worker execution, buffer processing и flat/deep batch flushing вынесены в `tg_msg_manager/services/sync/range_scanner.py`;
- tracked-target synchronization loop вынесен в `tg_msg_manager/services/sync/tracked_runner.py`;
- targeted dialog resolution и supported-dialog filtering вынесены в `tg_msg_manager/services/sync/dialog_targets.py`;
- service wrappers сохранены для совместимости текущих тестов и internal call sites;
- добавлены helper-compatibility regression tests.

Текущая верификация:
- `python3 -m unittest tests.test_services tests.test_sync_system -q` -> `49 tests`, `OK`
- `make test` -> `126 tests`, `OK`
- `ruff check .` -> `OK`
- `ruff format --check .` -> `OK`
- CLI help surface для `root` и `update` повторно проверен без падений

Итог этапа:
- `Stage 1` завершён;
- `ExportService` больше не держит внутри range-worker internals, tracked-target loop и dialog-target resolution;
- оставшиеся относительно крупные методы в `ExportService` являются orchestration glue, а не контейнерами execution logic.

Финальная форма orchestration hotspots:
- `sync_chat` -> около `126` строк
- `sync_all_dialogs_for_user` -> около `91` строк
- `_prepare_sync_target` -> около `80` строк
- `_finalize_sync_chat` -> около `64` строк
- `_run_sync_ranges` -> около `53` строк
- `_scan_range` -> около `50` строк

## Что делаем

- повторно аудируем только те части `ExportService`, которые всё ещё перегружены;
- выделяем устойчивые компонентные границы вокруг:
  - scan range planning/building;
  - checkpoint orchestration;
  - target registry и tracked-target coordination;
  - execution pipeline;
  - progress/event routing;
- сохраняем совместимость существующего CLI surface и runtime wiring;
- укрепляем tests там, где рефакторинг касается оставшихся hot paths.

## Что не делаем

- не меняем публичное CLI behavior;
- не меняем sync semantics ради “красоты архитектуры”;
- не повторяем уже завершённые экстракции из `TODO.md`;
- не добавляем новые продуктовые функции;
- не переносим в этот этап retry/report/analytics.

## Входные инварианты

- Stage 0 завершён и дал стабильный baseline;
- `TODO.md` считается фильтром против повторного выполнения уже закрытых refactor blocks;
- `ExportService` можно дробить только по реальным текущим hot spots, а не по первоначальному wish-list;
- storage contracts меняются только если это нужно для оставшейся перегруженной логики и сопровождается тестами.

## Исполняемая очередь

### Блок 1.1 — Re-audit remaining hotspots

- пересобрать карту ещё перегруженных методов `tg_msg_manager/services/exporter.py`;
- отделить уже решённые зоны от реально активных;
- зафиксировать безопасный порядок переноса: от pure planning logic к orchestration-adjacent code.

### Блок 1.2 — Baseline protection

- подтвердить coverage для сценариев:
  - first sync;
  - incremental update;
  - resume after interruption;
  - tracked targets;
  - multi-target same chat;
  - deep mode integration on export path;
- если конкретный hotspot не прикрыт, добавить минимальный test before refactor.

### Блок 1.3 — Scan range and planning boundaries

- изолировать planning/building части, которые ещё живут внутри `ExportService`;
- builder/planner не должен ходить в Telegram и не должен писать в storage;
- все checkpoint values и mode flags передавать явно.

### Блок 1.4 — Checkpoint and target coordination boundaries

- отделить checkpoint orchestration от range planning и transport-level iteration;
- отделить tracked target coordination от message iteration;
- сохранить текущие target attribution и tail-progress invariants.

### Блок 1.5 — Execution and progress routing

- сузить responsibility `ExportService` до orchestration и delegation;
- вынести остатки execution-specific plumbing, если они всё ещё смешаны с planning logic;
- не ломать event payload contracts и CLI rendering.

### Блок 1.6 — Final verification

- прогнать exporter-heavy tests и полный suite;
- убедиться, что поведение tracked sync и single-target sync не изменилось;
- зафиксировать оставшиеся exporter hotspots, если они сознательно отложены.

## Definition of Done

- `ExportService` стал заметно уже по ответственности, а не только по числу строк;
- scan planning, checkpoints, target coordination и execution имеют читаемые границы;
- не повторены уже закрытые refactors из `TODO.md`;
- CLI behavior и sync semantics сохранены;
- refactor подтверждён regression tests.

Статус:
- `Done` on `2026-05-04`.
