# Отчет Stage 5G.2 - Non-Channel Dataset Contract Precheck

## Статус

Stage 5G.2 завершен.

## Итоговый вывод

PRECHECK_COMPLETE_SEPARATE_CONTRACTS_RECOMMENDED

## Recommendation tokens

- SEPARATE_CONTRACTS_RECOMMENDED
- CONTRACT_STAGE_NEEDED
- EXPORT_PM_DEFERRED

## Проверенные файлы

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/architecture/CURRENT_PROJECT_CONTEXT.md`
- `docs/architecture/DATASET_CONTRACT_V1.md`
- `docs/architecture/DATASET_FORMAT.md`
- `docs/architecture/TXT_RENDERING.md`
- `docs/architecture/README.md`
- `README.md`
- `COMMANDS.md`
- `docs/user/QUICKSTART.md`
- `docs/development/README.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `docs/stages/reports/STAGE_5D_3_TXT_PROJECTION_CONTRACT_CLARIFICATION_REPORT.md`
- `docs/stages/reports/STAGE_4A_7_DB_EXPORT_TXT_PROFILE_PARITY_REPORT.md`
- `tg_msg_manager/cli_parser.py`
- `tg_msg_manager/cli/commands/export.py`
- `tg_msg_manager/cli/commands/db_export.py`
- `tg_msg_manager/cli/__init__.py`
- `tg_msg_manager/cli_support.py`
- `tg_msg_manager/core/runtime.py`
- `tg_msg_manager/services/export/`
- `tg_msg_manager/services/db_export/`
- `tg_msg_manager/services/private_archive/`
- `tg_msg_manager/services/rendering/`
- `tests/cli/test_txt_profile_cli.py`
- `tests/cli/test_cli.py`
- `tests/services/db_export/test_db_export_components.py`
- `tests/services/rendering/test_context_readable_txt_renderer.py`
- `tests/services/private_archive/test_private_archive_components.py`

## User/group `export`

- CLI принимает `--user-id`, optional `--chat-id`, sync/context options, `--json`, `--txt-profile context-readable|legacy`.
- После sync команда вызывает `DBExportService.export_user_messages(..., include_date=False)`.
- Default TXT output пишется через shared TXT renderer profile `context-readable`.
- `--txt-profile legacy` включает старый flat log-style TXT renderer.
- `--json` пишет JSONL вместо TXT; `txt_profile` не влияет на JSONL schema.
- Output filename формируется как `<safe_author>_<user_id>.txt` или `.jsonl` в `DB_EXPORTS/`, с part-файлами `<name>_partN.<ext>` при rotation.
- Canonical data остаются SQLite records и JSONL; TXT является projection.

## `db-export`

- CLI принимает `--user-id`, `--json`, `--txt-profile context-readable|legacy`.
- Default output dir: `DB_EXPORTS/`.
- TXT default: `context-readable`; `legacy` доступен явно.
- JSONL default profile: compact AI-friendly `ai`; full raw payload по умолчанию не включается.
- Service хранит writer state under `.writer_state/` и export manifest under `.export_state/<user_id>.json`.
- Skip/no-new-work логика использует fingerprint: counts, first/last message id, timestamps, output mode, JSON profile, TXT profile.
- Тесты покрывают parser defaults/rejection, direct/menu plumbing, DB export planning, skip policy, JSON/TXT rendering markers, and Stage 4A.7 parity.
- Gaps: нет формального non-channel contract doc, нет synthetic public fixtures for complete user/group and db-export outputs, нет отдельной contract matrix для DB_EXPORTS artifacts.

## `export-pm`

- CLI принимает только `--user-id`.
- Output family: private archive, not Dataset Contract V1 dataset.
- Default base dir: `PRIVAT_DIALOGS/`.
- User folder: `<safe_name>_<user_id>/`.
- Files/directories: `chat_log.txt` with rotation parts through `FileRotateWriter`, `media/photos/`, `media/videos/`, `media/voices/`, `media/documents/`.
- Media filenames use message id without extension in current policy.
- Service also saves messages to SQLite and updates private archive sync state.
- Tests cover deterministic folder/log paths, media categories, log formatting, flush-before-mark, failure handling, and media skip/download behavior.
- Gaps: contract status is not stable enough for a formal dataset contract; it needs a separate archive contract later if desired.

## Cross-cutting findings

- One combined `NON_CHANNEL_DATASET_CONTRACT_V1.md` is not recommended now.
- User/group `export` and `db-export` should share a TXT projection contract and can share JSONL expectations where outputs are identical.
- `export-pm` should be deferred into a separate private archive contract because it mixes text log, media folders, SQLite side effects, and sync state.
- Future contract work needs synthetic fixtures for `export`, `db-export`, and `export-pm`, plus contract tests for output filenames, part rotation, `.export_state`, `.writer_state`, TXT profiles, compact JSONL keys, and privacy-safe examples.
- Current docs are enough for user operation, but not enough for a formal non-channel contract.
- `docs/architecture/NON_CHANNEL_DATASET_CONTRACT_PRECHECK.md` was not created; this report is sufficient as the precheck record.

## Проверки

- `git diff --check`: passed.
- Runtime tests not required: report-only stage, command examples were not changed.

## Навыки

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`

## Подтверждения

- Runtime behavior не менялось.
- CLI behavior не менялось.
- SQLite schema и storage behavior не менялись.
- Output formats, TXT rendering, JSONL schema, exporter/db-export/private archive services и tests не менялись.
- Private artifacts, sessions, credentials, logs, screenshots, DB files, ignored private exports и archive docs не читались.

## Lifecycle

- Финальный отчет создан.
- Stage-файл перенесен из `docs/stages/active/` в `docs/stages/completed/`.
- `docs/stages/README.md` обновлен.
