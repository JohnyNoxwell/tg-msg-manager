# Stage 5O.3 — отчет

Дата: 2026-06-05

## Итог

Stage 5O.3 выполнен. Parser-local `assert` в обработке `--max-media-size` заменен на явную ошибку argparse. Принятые значения и публичный CLI contract не изменены.

## Измененные файлы

- `tg_msg_manager/cli_parser.py` — добавлена явная `argparse.ArgumentTypeError`, если parser helper вернул `None`.
- `tests/cli/test_channel_export_cli.py` — добавлен focused regression test для явного rejection пути без зависимости от `assert`.
- `tg_msg_manager/cli/__init__.py` — восстановлен non-TTY no-command help path при переданном runtime; это потребовалось для обязательной проверки `pytest tests/cli` и не меняет command surface.
- `docs/stages/reports/STAGE_5O_3_CLI_PARSER_MEDIA_SIZE_ERROR_REPORT.md` — создан этот отчет.
- `docs/stages/README.md` — обновлен lifecycle stage.
- `docs/stages/completed/stage_5o_3_cli_parser_media_size_error.md` — task moved from active to completed.

## Поведение

- Валидные `--max-media-size` значения продолжают парситься через существующий `parse_media_size`.
- Невалидные значения продолжают завершать argparse parsing через `SystemExit`.
- Оптимизированный Python mode больше не может обойти fallback rejection путь, потому что он не зависит от `assert`.
- CLI команды, имена flags, defaults, dataset/media/discussion behavior и SQLite schema не изменялись.

## Проверки

- `pytest tests/cli` — passed, 86 passed.
- `python3 -m compileall tg_msg_manager` — passed.
- `ruff check tg_msg_manager/cli_parser.py tg_msg_manager/cli/__init__.py tests/cli` — passed.

## Навыки

- `stage-reviewer`: applied from `.skills/stage-reviewer/SKILL.md`
- `architecture-guard`: applied from `.skills/architecture-guard/SKILL.md`
- `stage-completion-auditor`: applied from `.skills/stage-completion-auditor/SKILL.md`

## Статус

Complete.
