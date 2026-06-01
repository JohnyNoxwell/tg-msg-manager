# Отчет Stage 5I.2 - Non-Channel Contract Test Plan

## Статус

Stage 5I.2 завершен.

## Итоговый вывод

CONTRACT_TEST_PLAN_COMPLETE_DOC_CREATED

## Проверенные файлы

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/reports/STAGE_5H_1_NON_CHANNEL_EXPORT_CONTRACT_DESIGN_PRECHECK_REPORT.md`
- `docs/stages/reports/STAGE_5H_2_USER_DB_EXPORT_SYNTHETIC_FIXTURES_PLAN_REPORT.md`
- `docs/stages/reports/STAGE_5I_1_USER_DB_EXPORT_SYNTHETIC_FIXTURE_IMPLEMENTATION_REPORT.md`
- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_DESIGN.md`
- `docs/development/NON_CHANNEL_SYNTHETIC_FIXTURES_PLAN.md`
- `docs/architecture/TXT_RENDERING.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `README.md`
- `COMMANDS.md`
- `Makefile`
- `pyproject.toml`
- `docs/stages/README.md`
- `tests/`
- `tests/fixtures/`
- `tests/cli/`
- `tests/services/db_export/`
- `tests/services/rendering/`
- `tests/services/private_archive/`
- `tg_msg_manager/services/export/`
- `tg_msg_manager/services/db_export/`
- `tg_msg_manager/services/rendering/`
- `tg_msg_manager/infrastructure/storage/`

## Fixture prerequisite

- 5I.1 report exists.
- `tests/fixtures/non_channel_export/` exists.
- `tests/fixtures/db_export/` exists.
- Plan continues from 5I.1 fixtures.

## Test plan

- Created `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md`.
- The document is marked as plan only and does not claim tests exist.
- Future tests should use both golden-file comparisons and generated-output comparisons.

## Recommended future locations

- `tests/services/rendering/test_non_channel_context_readable_contract.py`
- `tests/services/rendering/test_non_channel_legacy_txt_contract.py`
- `tests/services/db_export/test_non_channel_ai_jsonl_contract.py`
- `tests/services/db_export/test_non_channel_db_export_state_contract.py`
- `tests/cli/test_non_channel_contract_cli.py`

## Assertion categories

- Filenames, extensions, `DB_EXPORTS/` layout, `_partN` part paths.
- TXT profile headers, context markers, reply-present, reply-missing, target sections and legacy lines.
- Compact JSONL key sets, omitted null/empty values, reply fields, media metadata-only fields, edit date, forwarding id, context group id, service marker and reactions.
- `.writer_state` current part/current count shape.
- `.export_state` legacy manifest fallback deferred unless future scope explicitly restores it as test surface.
- Synthetic-data scanning and `export-pm` exclusion.

## Tests deferred

- Test implementation.
- Final contract assertions.
- Private archive / `export-pm` contract tests.
- Full raw JSON profile.
- Exact rotation thresholds.
- SQLite schema contract status.
- Real Telegram smoke data.

## Проверки

- `git diff --check`: passed.

## Навыки

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`

## Подтверждения

- Runtime behavior не менялось.
- Tests and fixtures не менялись в рамках 5I.2.
- CLI behavior не менялось.
- SQLite schema и storage behavior не менялись.
- Output formats, TXT rendering and JSONL schema не менялись.
- Private artifacts, real exports, sessions, credentials, ignored DB files, logs, screenshots and media were not read.
- Future test plan requires offline synthetic fixtures only and excludes `export-pm`.

## Lifecycle

- Финальный отчет создан.
- Stage-файл перенесен из `docs/stages/active/` в `docs/stages/completed/`.
- `docs/stages/README.md` обновлен.
