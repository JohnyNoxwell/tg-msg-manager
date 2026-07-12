# ОТЧЁТ STAGE 7C.2 — LEGACY NULL DISCUSSION BATCH COMPATIBILITY

Статус: complete

## Дефект и исправление

На VPS два completed schema 1.0 dataset с `discussion: null` отклонялись командой `update-channels` с `Manifest discussion must be a JSON object`.

`ChannelBatchOptionsBuilder` теперь трактует только missing/null `discussion` как read-time `{"mode": "none"}`. Manifest не переписывается. Ненулевые scalar/list значения по-прежнему отклоняются.

## Изменённые файлы

- `tg_msg_manager/services/channel_export/batch_options.py`
- `tests/services/channel_export/test_channel_batch_update.py`
- `COMMANDS.md`
- `docs/architecture/DATASET_FORMAT.md`
- stage/report/index lifecycle files.

## Сохранённые контракты

- Current manifest writer и dataset schema не изменены.
- CLI, SQLite, export/state/incremental/media/discussion behavior не изменены.
- Legacy artifacts не мутируются.

## Проверки

- `python3 -m pytest tests/services/channel_export/test_channel_batch_update.py -q`: 9 passed.
- `ruff check ...`: passed.
- `ruff format --check ...`: выявил только formatting нового теста; `ruff format` применён.
- Повторный focused pytest: 9 passed.
- `python3 -m compileall tg_msg_manager`: passed.
- `make verify`: passed.
- `make pre-commit`: passed; 365 files unchanged, полный verify passed.
- `git diff --check`: passed.

## Skills

- `discussion-export-diagnoser`: applied from `.skills/discussion-export-diagnoser/SKILL.md`
- `bugfix-stage-writer`: applied from `.skills/bugfix-stage-writer/SKILL.md`
- `stage-reviewer`: applied from `.skills/stage-reviewer/SKILL.md`
- `architecture-guard`: applied from `.skills/architecture-guard/SKILL.md`
- `stage-completion-auditor`: applied from `.skills/stage-completion-auditor/SKILL.md`
