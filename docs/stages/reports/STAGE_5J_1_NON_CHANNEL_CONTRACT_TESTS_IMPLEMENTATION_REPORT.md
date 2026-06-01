# Отчет Stage 5J.1 - Non-Channel Contract Tests Implementation

## Статус

Stage 5J.1 завершен.

## Итоговый вывод

NON_CHANNEL_CONTRACT_TESTS_IMPLEMENTED_WITH_DOC_LINKS

## Проверенные файлы

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/reports/STAGE_5J_0_POST_5I_CONSISTENCY_AUDIT_REPORT.md`
- Stage 5I.1/5I.2/5I.3 reports
- `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md`
- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md`
- `docs/architecture/TXT_RENDERING.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `README.md`
- `COMMANDS.md`
- `Makefile`
- `pyproject.toml`
- `docs/stages/README.md`
- `tests/fixtures/non_channel_export/`
- `tests/fixtures/db_export/`
- `tests/cli/`
- `tests/services/db_export/`
- `tests/services/rendering/`
- `tg_msg_manager/services/db_export/`
- `tg_msg_manager/services/rendering/`
- `tg_msg_manager/services/export/`
- `tg_msg_manager/infrastructure/storage/`
- `tg_msg_manager/cli_parser.py`

## Tests added

- `tests/services/rendering/test_non_channel_contract_fixtures.py`
- `tests/services/db_export/test_non_channel_contract_jsonl.py`
- `tests/cli/test_non_channel_contract_cli.py`

## Assertions covered

- Synthetic corpus JSONL parses into `MessageData`.
- `context-readable` renderer output matches non-channel golden fixture.
- DB `context-readable` fixture matches shared non-channel TXT fixture.
- `legacy` renderer output matches golden fixture.
- Fixture README privacy wording and `export-pm` / private archive exclusion are asserted.
- Fixture payload files are scanned for private artifact markers.
- Compact `ai` JSONL keys stay within the contract set and omit null/empty/list values.
- Reply, topic, media metadata, forwarding, edit date, context group, and reactions are asserted.
- DB export `ai` serializer output matches fixture JSONL.
- `.writer_state` fixture shape is limited to `current_part` and `current_count`.
- `.export_state` fixture remains absent/deferred.
- CLI scoped contract commands keep `context-readable` default and accept `legacy`.

## Deferred

- Exact rotation thresholds.
- Full raw JSON profile.
- Real Telegram smoke data.
- Private archive / `export-pm` contract tests.
- DB-backed generated no-new-work behavior beyond current fixture-state assertions.

## Docs updates

- Added implemented test locations to `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md`.
- Added implemented test locations to `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md`.

## Проверки

- `python3 -m unittest discover tests -p '*non_channel*contract*.py'`: passed, 14 tests.
- `ruff format --check tests/services/rendering/test_non_channel_contract_fixtures.py tests/services/db_export/test_non_channel_contract_jsonl.py tests/cli/test_non_channel_contract_cli.py`: passed.
- `git diff --check`: passed.
- `make test`: passed, 496 tests.

## Навыки

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`

## Подтверждения

- Runtime code не менялся.
- Fixtures and expected output files не менялись.
- CLI behavior не менялось.
- SQLite schema и storage behavior не менялись.
- TXT rendering, JSONL schema and output behavior не менялись.
- Private artifacts, real exports, sessions, credentials, ignored DB files, logs, screenshots, media and real Telegram data were not read.
- `export-pm` remains excluded from user/group + `db-export` contract tests.

## Lifecycle

- Финальный отчет создан.
- Stage-файл перенесен из `docs/stages/active/` в `docs/stages/completed/`.
- `docs/stages/README.md` обновлен.
