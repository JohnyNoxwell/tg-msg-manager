# STAGE 6B.0 DIRECT EXPORT FAILURE EXIT CODE REPORT

Статус: complete

## Что исправлено

- Прямой `export` больше не возвращается успешно при исключении в `_run_export_sync`.
- При обычной ошибке сохраняется текущий `logger.error("Error during export: ...")`, затем команда завершает direct CLI path через `SystemExit(1)`.
- Emergency-stop ветка `ctx.pm.should_stop()` сохранена: обработчик возвращается без нового exit.

## Изменённые файлы

- `tg_msg_manager/cli/commands/export.py`
- `tests/cli/test_cli.py`
- `CHANGELOG.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_6b_0_direct_export_failure_exit_code.md`
- `docs/stages/reports/STAGE_6B_0_DIRECT_EXPORT_FAILURE_EXIT_CODE_REPORT.md`

## Проверки

- `pytest tests/cli/test_cli.py -k "export_failure_exits_non_zero or export_pm_enqueues_retry_on_failure"`: passed
- `python3 -m compileall tg_msg_manager`: passed
- `pytest tests/cli/test_cli.py tests/architecture/test_static_boundaries.py`: passed
- `ruff check tg_msg_manager/cli/commands/export.py tests/cli/test_cli.py`: passed
- `git diff --check`: passed

## Сохранено

- CLI command names, flags и defaults не менялись.
- Output files, output directory layout, JSONL/TXT formats и SQLite schema не менялись.
- Export data flow не менялся, кроме ненулевого direct-command exit при ошибке.
- Interactive menu behavior намеренно не менялся.

## Не запускалось

- Live Telegram export smoke не запускался: stage требует mocked regression без network access.

## Skills

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`

## Итог

- Stage 6B.0 complete.
