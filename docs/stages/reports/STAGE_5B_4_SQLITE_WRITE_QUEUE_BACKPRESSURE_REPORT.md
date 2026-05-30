# Stage 5B.4 - отчет по SQLite write queue backpressure

## Статус

Stage 5B.4 выполнен.

## Что изменено

- В `tg_msg_manager/infrastructure/storage/sqlite.py` очередь записи SQLite стала bounded: внутренний лимит `DEFAULT_WRITE_QUEUE_MAXSIZE = 10_000`.
- В `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py` enqueue для `save_message()` и `save_messages()` теперь выполняется через `await self._write_queue.put(...)`.
- При заполненной очереди добавлена телеметрия pressure:
  - `storage.queue_backpressure.wait_events`;
  - `storage.queue_backpressure.wait_seconds`.
- Размер фонового commit batch не изменен.

## Поведение

- Публичные async-сигнатуры `save_message()`, `save_messages()` и `flush()` сохранены.
- SQLite schema, migrations и `PRAGMA user_version` не менялись.
- CLI, dataset formats, state/incremental/force/no-new-work поведение не менялись.
- Очередь не сбрасывает записи silently: producers ждут свободный слот.
- `flush()` и `close()` продолжают дожидаться записи queued messages.

## Тесты

- Добавлены focused tests в `tests/infrastructure/storage/test_storage_sqlite.py`:
  - save waits when write queue is full;
  - flush drains all queued writes;
  - close drains queued writes before closing connection.

## Проверки

- `pytest tests/infrastructure/storage/test_storage_sqlite.py` - пройдено, 42 passed.
- `pytest tests/services/test_services.py` - пройдено, 40 passed.
- `python3 -m compileall tg_msg_manager` - пройдено.
- `ruff check tg_msg_manager tests` - пройдено.

## Skills

- stage-reviewer: applied from `.skills/stage-reviewer/SKILL.md`; verdict pass, blockers none.
- architecture-guard: applied from `.skills/architecture-guard/SKILL.md`; violations none.
- stage-completion-auditor: applied from `.skills/stage-completion-auditor/SKILL.md`; verdict complete, blockers none.

## Lifecycle

- Final report created before cleanup.
- Completed task file moved from `docs/stages/active/` to `docs/stages/completed/`.
- `docs/stages/README.md` updated to leave only unfinished/next active work.
