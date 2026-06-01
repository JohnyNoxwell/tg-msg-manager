# Отчет Stage 5H.3 - Private Archive Contract Deferred Decision

## Статус

Stage 5H.3 завершен.

## Итоговый вывод

PRIVATE_ARCHIVE_CONTRACT_DEFERRED_DECISION_RECORDED

## Проверенные файлы

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/reports/STAGE_5G_2_NON_CHANNEL_DATASET_CONTRACT_PRECHECK_REPORT.md`
- `docs/architecture/CURRENT_PROJECT_CONTEXT.md`
- `docs/architecture/README.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `README.md`
- `COMMANDS.md`
- `docs/stages/README.md`
- `tg_msg_manager/cli_parser.py`
- `tg_msg_manager/cli/commands/`
- `tg_msg_manager/services/private_archive/`
- `tg_msg_manager/services/rendering/`
- `tg_msg_manager/infrastructure/storage/`
- `tests/services/private_archive/`

## Current understanding of export-pm output family

- CLI command: `export-pm --user-id`.
- Default base directory: `PRIVAT_DIALOGS/`.
- User directory: safe display name plus user id.
- Main log: `chat_log.txt` with file rotation through `FileRotateWriter`.
- Media folders: `media/photos/`, `media/videos/`, `media/voices/`, `media/documents/`.
- Media target path currently uses message id as filename.
- Service writes messages to SQLite and updates private archive sync state after flush.
- Tests cover deterministic folder/log paths, media categories, PM log formatting, flush-before-mark ordering, no mark on stream failure, media skip/download behavior.

## Decision

- `export-pm` remains deferred.
- `export-pm` is an archive-contract candidate, not a user/group plus DB export dataset contract candidate.
- It must stay outside non-channel user/group + `db-export` contract work because it mixes text log output, media folders, SQLite side effects, sync state, media transfer policy, retry behavior, and private dialog privacy constraints.

## Future prerequisites

- Finish or at least stabilize user/group + DB export contract fixtures first.
- Add a later private archive precheck before any final contract.
- Define privacy-safe synthetic private archive fixture policy.
- Clarify whether media filename/extension policy is stable enough to document.
- Decide whether SQLite side effects are public contract surface or implementation detail.

## Privacy constraints

- Future examples must use obviously synthetic names, ids, timestamps, paths and neutral text.
- Real private dialogs, Telegram exports, sessions, credentials, logs, screenshots, local DB files, media and ignored artifacts remain forbidden.
- Future examples should avoid realistic private conversation content.

## Decision doc

- Создан `docs/architecture/PRIVATE_ARCHIVE_CONTRACT_DEFERRED_DECISION.md`.
- Документ явно помечен как deferred decision, not final contract.
- Документ не создает runtime guarantees.
- Документ не содержит private или realistic example data.
- Документ явно оставляет `export-pm` вне user/group + DB export contract work.

## Проверки

- `git diff --check`: passed.

## Навыки

- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`

## Подтверждения

- Runtime behavior не менялось.
- CLI behavior не менялось.
- SQLite schema и behavior не менялись.
- Media behavior не менялось.
- Sync state behavior не менялось.
- Service behavior, fixtures и tests не менялись.
- Private artifacts не читались.

## Lifecycle

- Финальный отчет создан.
- Stage-файл перенесен из `docs/stages/active/` в `docs/stages/completed/`.
- `docs/stages/README.md` обновлен.
