# STAGE 6C.0 — SQLITE WRITER FLUSH FAILURE DIAGNOSIS REPORT

Статус: complete

## Проверенные файлы

- `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py`
- `tg_msg_manager/infrastructure/storage/sqlite.py`
- `tests/infrastructure/storage/test_storage_sqlite.py`

## Результат диагностики

- Дефект подтверждён.
- `_background_writer` извлекает элементы через `_write_queue.get()` и `get_nowait()`.
- `_save_batches_by_target` вызывается до `task_done()`.
- При исключении из `_save_batches_by_target` выполнение переходит в общий `except`, а уже извлечённые элементы не подтверждаются через `task_done()`.
- `flush()` ждёт `_write_queue.join()`, поэтому после такого сбоя может зависнуть навсегда.

## Изменения

- Runtime code: не изменялся.
- Tests: не изменялись.
- Docs: создан этот отчёт.

## Проверки

- `pytest tests/infrastructure/storage/test_storage_sqlite.py -k "flush_drains_all_queued_writes or save_message_waits_when_write_queue_is_full"`: passed

## Навыки

- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `bugfix-stage-writer: applied from .skills/bugfix-stage-writer/SKILL.md`
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`

## Сохранено

- CLI behavior: да
- SQLite schema: да
- Dataset/output formats: да
- Runtime behavior: да, runtime не менялся

## Завершение

- Stage 6C.0 complete.
