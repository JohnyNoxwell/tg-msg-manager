# STAGE 6B.1 DIRECT PM ARCHIVE FAILURE EXIT CODE REPORT

Статус: complete

## Что исправлено

- Прямой `export-pm` больше не возвращается успешно, если текущий `archive_pm` падает.
- Retry-task enqueue через `enqueue_archive_pm_retry_task` сохранён.
- Текущий `logger.error("Error during PM archive: ...")` сохранён, затем команда завершает direct CLI path через `SystemExit(1)`.

## Изменённые файлы

- `tg_msg_manager/cli/commands/export.py`
- `tests/cli/test_cli.py`
- `CHANGELOG.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_6b_1_direct_pm_archive_failure_exit_code.md`
- `docs/stages/reports/STAGE_6B_1_DIRECT_PM_ARCHIVE_FAILURE_EXIT_CODE_REPORT.md`

## Проверки

- `pytest tests/cli/test_cli.py -k "export_failure_exits_non_zero or export_pm_enqueues_retry_on_failure"`: passed
- `python3 -m compileall tg_msg_manager`: passed
- `pytest tests/cli/test_cli.py tests/architecture/test_static_boundaries.py`: passed
- `ruff check tg_msg_manager/cli/commands/export.py tests/cli/test_cli.py`: passed
- `git diff --check`: passed

## Сохранено

- CLI command names, flags и defaults не менялись.
- Retry enqueue на PM archive failure сохранён и покрыт тестом.
- Archive data flow, output layout и SQLite schema не менялись.
- Новые runtime dependencies не добавлялись.

## Не запускалось

- Live Telegram PM archive smoke не запускался: stage требует mocked regression без network access.

## Skills

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`

## Итог

- Stage 6B.1 complete.
