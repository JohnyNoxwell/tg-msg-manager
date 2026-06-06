# Stage 5O.8 — Discussion Builder Split Report

Дата: 2026-06-05

## Итог

Stage 5O.8 выполнен: чистая сборка discussion thread/metadata артефактов вынесена из `ChannelDiscussionExporter` в `ChannelDiscussionArtifactBuilder`.

## Изменения

- Добавлен `tg_msg_manager/services/channel_export/discussions/artifact_builder.py`.
- `ChannelDiscussionExporter` оставлен orchestration/fetch/write координатором и делегирует builder-решения.
- Добавлены чистые unit-тесты builder на synthetic records.
- Формат discussion JSONL/TXT/state, имена файлов, статусы и порядок записи не менялись.

## Навыки

- stage-reviewer: applied from .skills/stage-reviewer/SKILL.md; verdict pass.
- architecture-guard: applied from .skills/architecture-guard/SKILL.md; violations none.
- stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md; verdict complete.

## Проверки

- `pytest tests/services/channel_export/discussions`: passed.
- `pytest tests/services/channel_export/test_channel_export_service.py`: passed.
- `python3 -m compileall tg_msg_manager`: passed.
- `ruff check tg_msg_manager/services/channel_export tests/services/channel_export`: passed.
- `git diff --check`: passed.

## Сохранено

- CLI: без изменений.
- SQLite: без изменений.
- Dataset contract: без изменений.
- Discussion fetch/retry/media/state/incremental/force/no-new-work поведение: без изменений.

## Lifecycle

- Task file moved to `docs/stages/completed/stage_5o_8_discussion_builder_split.md`.
- `docs/stages/README.md` обновлен: Stage 5O.8 убран из active и добавлен в completed/report records.
- `docs/stages/active/` содержит только незавершенные следующие stage task files.

## Отложено

- Дополнительная cleanup-декомпозиция discussion exporter вне scope Stage 5O.8 не выполнялась.
