# STAGE 3 — Retry Reliability Layer

## Цель этапа

Превратить существующий `retry_queue` из частичной заготовки в рабочий механизм надёжного повторного выполнения ограниченного числа операций.

Этап считается частью foundation, потому что улучшает восстановление после сбоев без расширения предметной области продукта.

## Статус выполнения

Обновлено: `2026-05-04`

- [x] `3.1` Retry audit
- [x] `3.2` Typed retry model and storage lifecycle
- [x] `3.3` Backoff policy and handlers
- [x] `3.4` Worker and CLI
- [x] `3.5` Narrow service integration
- [x] `3.6` Final verification

Закрыто в текущем проходе:
- текущая `retry_queue` schema и точки использования зааудированы; подтверждено, что до этапа существовали только `enqueue/get/remove`;
- добавлены typed retry models и storage records с `status`, `target_user_id`, `payload_json`, `max_attempts`, timestamps и terminal state fields;
- реализована safe migration для legacy `retry_queue` и backfill lifecycle columns;
- storage API расширен методами:
  - `get_due_retry_tasks()`
  - `list_retry_tasks()`
  - `mark_retry_task_completed()`
  - `mark_retry_task_rescheduled()`
  - `mark_retry_task_failed()`
  - `cleanup_retry_tasks()`
- реализован deterministic retry backoff и explicit delay detection для исключений;
- реализован `RetryWorker` с поддержкой task types:
  - `sync_target`
  - `archive_pm`
- добавлен новый публичный CLI surface `retry`:
  - запуск due tasks
  - просмотр очереди
  - cleanup terminal rows
- narrow integration добавлена только в подтверждённые failure paths:
  - tracked sync during `update`
  - PM archive failures
- retry не превращён в общий job system и не внедрён cross-cutting по всему проекту.

Текущая верификация:
- `python3 -m unittest tests.test_retry_worker tests.test_storage_sqlite tests.test_sync_system tests.test_cli -q` -> `47 tests`, `OK`
- `make test` -> `137 tests`, `OK`
- `ruff check .` -> `OK`
- `ruff format --check .` -> `OK`

Итог этапа:
- `Stage 3` завершён;
- retry storage lifecycle теперь типизирован и проверяем;
- due tasks обрабатываются worker’ом с deterministic backoff;
- новый публичный CLI surface ограничен ровно одной командой: `retry`;
- интеграции остались узкими и привязаны к реальным operational failure paths.

Финальная форма retry hotspots:
- `SQLiteSyncStateMixin.enqueue_retry_task` -> около `67` строк
- `SQLiteSyncStateMixin.mark_retry_task_rescheduled` -> около `48` строк
- `RetryWorker._run_task` -> около `36` строк
- `TrackedSyncRunner.run` -> около `103` строк с встроенным enqueue-on-failure path
- `CLIContext.initialize` / `_handle_retry_command` обеспечивают отдельный public retry surface

## Что делаем

- приводим `retry_queue` к typed lifecycle model;
- добавляем минимально необходимую миграцию schema;
- вводим deterministic backoff policy;
- реализуем `RetryWorker`;
- добавляем CLI surface `retry`;
- интегрируем retry только в те failure-paths, где уже есть подтверждённая operational value.

## Что не делаем

- не превращаем retry в общий job system;
- не добавляем произвольные типы задач “на будущее”;
- не внедряем retry во все сервисы подряд;
- не смешиваем retry с analytics или reporting;
- не меняем существующие destructive semantics ради асинхронности.

## Входные инварианты

- foundation refactors завершены настолько, что retry можно внедрять в стабильные service boundaries;
- текущая retry schema и storage API сначала аудируются, потом меняются;
- backoff должен быть deterministic и тестируемым;
- migration должна быть безопасной для старых БД и подтверждаться тестами.

## Исполняемая очередь

### Блок 3.1 — Retry audit

- найти все текущие точки использования `retry_queue`;
- зафиксировать текущую schema, поля и реальные ограничения;
- определить минимальный набор task types, который нужен сейчас, а не гипотетически.

### Блок 3.2 — Typed retry model and storage lifecycle

- добавить typed task/status model;
- расширить storage API под due tasks, attempt tracking, done/failed transitions и cleanup;
- реализовать миграцию с safe defaults для старых rows.

### Блок 3.3 — Backoff policy and handlers

- реализовать deterministic retry backoff;
- поддержать explicit delays для случаев вроде `FloodWait`, если они уже доступны;
- описать handlers только для реально поддерживаемых retry tasks.

### Блок 3.4 — Worker and CLI

- реализовать `RetryWorker`;
- добавить readably scoped CLI command `retry`;
- CLI surface должен быть отдельным и понятным: это новый публичный интерфейс этого этапа.

### Блок 3.5 — Narrow service integration

- интегрировать retry только в подтверждённые failure paths;
- не превращать этап в массовый cross-cutting rewrite;
- каждую интеграцию сопровождать тестом, показывающим enqueue и дальнейший lifecycle задачи.

### Блок 3.6 — Final verification

- прогнать storage, concurrency и service tests, затрагивающие retry;
- проверить миграции на свежей и legacy DB;
- убедиться, что `retry` не меняет существующее поведение без явного вызова.

## Definition of Done

- retry storage lifecycle типизирован и проверяем;
- worker умеет обрабатывать due tasks с deterministic backoff;
- появился ровно один новый публичный CLI surface: `retry`;
- интеграции ограничены реальными failure paths;
- миграции и retry behavior подтверждены тестами.

Статус:
- `Done` on `2026-05-04`.
