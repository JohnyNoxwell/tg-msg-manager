# STAGE 2 — Context Pipeline Refactor

## Цель этапа

Разделить `DeepModeEngine` на тестируемые стратегии и resolver-компоненты, сохранив текущее поведение context extraction.

Этап продолжает foundation refactor и использует только те quality-related additions, которые нужны для внутренней декомпозиции pipeline.

## Статус выполнения

Обновлено: `2026-05-04`

- [x] `2.1` Re-audit deep-mode hotspots
- [x] `2.2` Baseline protection
- [x] `2.3` Typed context models
- [x] `2.4` Resolver extraction
- [x] `2.5` Fallback and cluster assembly
- [x] `2.6` Final verification

Закрыто в текущем проходе:
- текущая карта hot spots для `DeepModeEngine` пересобрана по фактическому коду и зафиксирована перед переносом;
- введён новый пакет `tg_msg_manager/services/context/` с typed models для candidate/cluster/request данных;
- local-cache и live-fetch responsibilities вынесены в `fetchers.py`;
- parent reply lookup вынесен в `resolvers.py` (`ParentReplyResolver`);
- child reply и thread/topic relation logic вынесены в `relationships.py`;
- cluster initialization, anchor selection, relation association и mutation rules вынесены в `clustering.py`;
- candidate-pool resolution и range-fill policy вынесены в `resolvers.py` (`CandidatePoolResolver`);
- time fallback selection и application вынесены в `fallback.py`;
- `DeepModeEngine` сохранён как orchestration wrapper с совместимыми internal method wrappers для текущих тестов;
- source metadata добавлен к internal context candidates:
  - `semantic_source`
  - `retrieval_source`
- live parent/range fetch fail paths теперь деградируют до storage-only поведения вместо обрыва всего deep extraction.

Текущая верификация:
- `python3 -m unittest tests.test_services tests.test_sync_system -q` -> `53 tests`, `OK`
- `make test` -> `130 tests`, `OK`
- `ruff check .` -> `OK`
- `ruff format --check .` -> `OK`

Итог этапа:
- `Stage 2` завершён;
- `DeepModeEngine` больше не смешивает storage/live/fallback обязанности в одном месте;
- context pipeline использует отдельные resolver boundaries и typed internal models;
- quality hooks остались внутренними и не выведены в отдельный user-facing surface.

Финальная форма orchestration и helper hotspots:
- `DeepModeEngine.extract_batch_context` -> около `74` строк
- `CandidatePoolResolver.fetch_live_range_fill` -> около `81` строк
- `TimeFallbackResolver.select_time_fallback` -> около `67` строк
- `TimeFallbackResolver.apply_time_fallback` -> около `63` строк
- `CandidatePoolResolver.fetch_candidate_pool` -> около `56` строк
- `ContextClusterAssembler.associate_candidates` -> около `50` строк

## Что делаем

- разбиваем `DeepModeEngine` на отдельные части:
  - local cache resolver;
  - live fetch resolver;
  - parent reply resolver;
  - child reply resolver;
  - thread/topic resolver;
  - fallback logic;
  - cluster assembly;
- вводим typed context structures там, где ещё остаются ad-hoc dict/list payloads;
- добавляем внутреннее source metadata к context candidates:
  - semantic source;
  - retrieval source;
- усиливаем tests для основных deep-mode сценариев до и после переноса.

## Что не делаем

- не добавляем отдельный user-facing quality CLI;
- не делаем отдельный report layer на этом этапе;
- не используем quality scores для фильтрации поведения;
- не добавляем analytics;
- не переписываем экспортный pipeline сверх границ Stage 1.

## Входные инварианты

- Stage 1 завершён без поломки export path;
- текущие deep-mode сценарии зафиксированы baseline tests;
- source metadata существует для объяснимости и отладки, а не как новая внешняя фича;
- любые новые internal models не должны тянуть за собой циклические импорты или новый публичный API без необходимости.

## Исполняемая очередь

### Блок 2.1 — Re-audit deep-mode hotspots

- пересобрать карту текущих перегруженных участков `tg_msg_manager/services/context_engine.py`;
- отделить уже выделенные helpers от зон, где ответственность всё ещё смешана;
- определить безопасный порядок экстракции: storage-first, then live fetch, then cluster/fallback composition.

### Блок 2.2 — Baseline protection

- подтвердить coverage для:
  - parent included;
  - child replies included;
  - topic/thread context;
  - local cache before live fetch;
  - live fetch fail path;
  - time fallback only when needed;
  - overlapping cluster merge behavior;
- если coverage пробита, сначала добавить tests.

### Блок 2.3 — Typed context models

- ввести компактные typed structures для request/candidate/result/cluster data;
- заменить только те ad-hoc структуры, которые реально мешают декомпозиции;
- не превращать этап в массовую замену всех внутренних контейнеров.

### Блок 2.4 — Resolver extraction

- выделить local-cache и live-fetch responsibilities;
- затем выделить parent/child/thread resolvers;
- каждый resolver должен иметь чёткую зону ответственности и собственный test surface;
- запретить потерю source metadata при merge и dedup.

### Блок 2.5 — Fallback and cluster assembly

- вынести fallback logic и cluster assembly из смешанного orchestration flow;
- сохранить текущие правила приоритета structural context над fallback additions;
- не вводить new scoring-driven behavior.

### Блок 2.6 — Final verification

- прогнать deep-mode-focused tests и полный suite;
- проверить, что export path продолжает использовать context pipeline без изменения поведения;
- зафиксировать, какие quality hooks остались внутренними и ещё не являются внешней функциональностью.

## Definition of Done

- `DeepModeEngine` больше не является монолитом со смешанными storage/live/fallback обязанностями;
- context pipeline использует понятные resolver boundaries;
- source metadata сохраняется по всему pipeline;
- нет нового user-facing surface;
- поведение подтверждено regression tests.

Статус:
- `Done` on `2026-05-04`.
