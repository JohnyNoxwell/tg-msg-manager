# STAGE 6A.5 — CLIContext Adapter Shrink Report

Дата: 2026-06-17
Статус: completed
Тип: implementation

## Выполнено

- `CLIContext` оставлен совместимым адаптером над `ApplicationSession`: runtime/settings/paths/session и публичные compatibility attributes сохранены.
- Прямая сборка runtime resources и service constructors внутри `CLIContext` не используется; добавлено regression coverage против возврата такой сборки.
- Compatibility attributes `pm`, `storage`, `client`, `exporter`, `cleaner`, `db_exporter`, `private_archive`, `channel_exporter`, `retry_worker`, `alias_manager` синхронизируются из session.
- `active_uid` и emergency JSON export callback сохранены без изменения поведения.
- Добавлен regression guard, запрещающий прямую сборку process manager, storage, Telegram client и service constructors внутри `CLIContext`.

## Измененные файлы

- `tests/cli/test_cli.py`
- `tests/architecture/test_static_boundaries.py`
- `docs/stages/reports/STAGE_6A_5_CLI_CONTEXT_ADAPTER_SHRINK_REPORT.md`
- `docs/stages/completed/stage_6a_5_cli_context_adapter_shrink.md`
- `docs/stages/README.md`

## Проверки

- `pytest tests/cli`: passed, 95 passed.
- `pytest tests/architecture`: passed, 21 passed.
- `python3 -m compileall tg_msg_manager`: passed.
- `ruff check tg_msg_manager tests/cli tests/architecture`: passed.
- `git diff --check`: passed.

## Сохранено

- CLI commands, flags, prompts, output routing и exit codes не менялись.
- No-client path сохраняет отсутствие Telegram client construction.
- Login error rendering, lock failure handling и lifecycle messages сохранены.
- SQLite schema/storage SQL не менялись.
- Dataset/export formats, retry, scheduler, media/discussion behavior не менялись.

## Skill notes

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`

## Architecture guard

- Нарушений нет: `CLIContext` не содержит прямой сборки extracted runtime/service classes.
- `ApplicationSession` владеет lifecycle construction; CLI остается адаптером и renderer/callback holder.
- Protected service facades, compatibility wrappers, storage SQL и package metadata не менялись.

## Lifecycle

- Stage file перемещен из `docs/stages/active/` в `docs/stages/completed/`.
- `docs/stages/README.md` обновлен: Stage 6A.5 убран из active и добавлена ссылка на report.
