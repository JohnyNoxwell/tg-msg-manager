# STAGE 6C.1 — SQLITE WRITER FAILED BATCH QUEUE ACCOUNTING REPORT

Статус: complete

## Изменённые файлы

- `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py`
- `tg_msg_manager/infrastructure/storage/sqlite.py`
- `tests/infrastructure/storage/test_storage_sqlite.py`
- `docs/stages/reports/STAGE_6C_1_SQLITE_WRITER_FAILED_BATCH_QUEUE_ACCOUNTING_REPORT.md`

## Исправление

- Подтверждение элементов очереди перенесено в `finally`, поэтому уже извлечённые элементы получают `task_done()` даже при ошибке batch commit.
- Ошибка background writer сохраняется на экземпляре storage.
- `flush()` после `_write_queue.join()` поднимает `RuntimeError` с исходной ошибкой как причиной и очищает сохранённую ошибку после сообщения вызывающему коду.
- Добавлен regression test для падения `_save_batches_by_target`: `flush()` не зависает, а завершается ошибкой в ограниченный таймаут.

## Проверки

- `python3 -m compileall tg_msg_manager/infrastructure/storage`: passed
- `pytest tests/infrastructure/storage/test_storage_sqlite.py -k "flush or write_queue or batch"`: passed
- `ruff check tg_msg_manager/infrastructure/storage/_sqlite_write_path.py tg_msg_manager/infrastructure/storage/sqlite.py tests/infrastructure/storage/test_storage_sqlite.py`: passed

## Сохранено

- CLI behavior: да
- SQLite schema: да
- Dataset/output formats: да
- Queue backpressure behavior: да
- Successful async write path: да

## Не запускалось

- `make test`: не запускался, scope stage ограничен SQLite write-path regression checks.
- `make verify`: не запускался, scope stage ограничен SQLite write-path regression checks.

## Навыки

- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `bugfix-stage-writer: applied from .skills/bugfix-stage-writer/SKILL.md`
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`

## Завершение

- Stage 6C.1 complete.
