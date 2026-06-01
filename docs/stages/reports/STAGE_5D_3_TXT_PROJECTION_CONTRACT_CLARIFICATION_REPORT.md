# Отчет Stage 5D.3 - TXT Projection Contract Clarification

## Статус

Stage 5D.3 завершен.

## Измененные файлы

- `docs/architecture/TXT_RENDERING.md`
- `docs/architecture/DATASET_FORMAT.md`
- `docs/architecture/DATASET_CONTRACT_V1.md`
- `docs/architecture/DATASET_CONTRACT_COVERAGE_MATRIX.md`
- `docs/stages/reports/STAGE_5D_3_TXT_PROJECTION_CONTRACT_CLARIFICATION_REPORT.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_5d_3_txt_projection_contract_clarification.md`
- `docs/stages/active/stage_5d_3_txt_projection_contract_clarification.md` moved to completed.

## Подтвержденный channel TXT contract

- `messages.txt` и `discussion_comments.txt` являются direct channel export human-readable projections.
- Эти TXT files не являются canonical schema и не используют user/group `--txt-profile` profiles.
- Контракт тестов для channel TXT остается smoke/marker: message ids, timestamps, author/channel context, media sections, comment text.
- Full golden snapshots для полного TXT output не добавлялись.

## Подтвержденные TXT profile defaults

- `DEFAULT_TXT_PROFILE` в `tg_msg_manager/services/rendering/txt_profiles.py` равен `context-readable`.
- `export` default TXT profile подтвержден тестом `test_export_parser_default_txt_profile_is_context_readable`.
- `db-export` default TXT profile подтвержден тестом `test_db_export_parser_default_txt_profile_is_context_readable`.
- `legacy` остается доступным явно для `export` и `db-export`.

## Проверки

- `python3 -m pytest tests/services/channel_export/test_channel_export_renderers.py tests/services/channel_export/test_channel_export_dataset_contracts.py tests/cli/test_txt_profile_cli.py -q`: passed, `23 passed, 3 subtests passed`.
- `git diff --check`: passed.

## Сохранено

- Runtime behavior: preserved.
- CLI: preserved.
- Dataset JSON files: preserved.
- SQLite behavior and schema: preserved.

## Lifecycle cleanup

- Active task file moved to `docs/stages/completed/`.
- `docs/stages/README.md` updated.
- Later active stages were not moved.

## Skills

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`
