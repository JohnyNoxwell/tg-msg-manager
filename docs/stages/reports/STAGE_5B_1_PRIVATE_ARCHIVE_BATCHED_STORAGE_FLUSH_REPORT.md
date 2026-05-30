# Stage 5B.1 Private Archive Batched Storage Flush Report

## Статус

- Stage 5B.1 выполнен.
- Пользовательская CLI-поверхность, имена файлов, layout архива, retry-формат и SQLite schema не менялись.

## Изменения

- `tg_msg_manager/services/private_archive/stream_processor.py`: сохранение каждого PM-сообщения ставится в storage queue с `flush=False`.
- `tg_msg_manager/services/private_archive/service.py`: добавлен один `await storage.flush()` после завершения streaming и до `emit_completed()` / `mark_synced()`.
- `tg_msg_manager/infrastructure/storage/contracts/private_archive_storage.py`: narrow private archive storage contract явно включает lifecycle `flush()`.
- `tests/services/private_archive/test_private_archive_components.py`: добавлены проверки `flush=False`, порядка `flush -> completed -> mark_synced`, и exception path без `mark_synced()`.

## Поведение

- Порядок записи текста архива и media download сохранен.
- При исключении из stream processing цель не помечается synced.
- Изменение `PrivateArchiveService` является только orchestration wiring: один final flush перед completed/synced state, без новой feature logic.
- SQLite schema, migrations, CLI commands, output text, media policy и retry task format не изменялись.

## Проверки

- `pytest tests/services/private_archive/test_private_archive_components.py`: passed, 9 passed.
- `python3 -m compileall tg_msg_manager`: passed.
- `ruff check tg_msg_manager tests`: passed.

## Skills

- `stage-reviewer`: applied from `.skills/stage-reviewer/SKILL.md`; preflight blockers не выявлены.
- `architecture-guard`: applied from `.skills/architecture-guard/SKILL.md`; protected facade change ограничен orchestration, storage boundary сохранен.
- `stage-completion-auditor`: applied from `.skills/stage-completion-auditor/SKILL.md`; blockers не выявлены.

## Lifecycle

- Отчет создан до cleanup.
- Completed task file moved to `docs/stages/completed/`.
- `docs/stages/README.md` updated.
