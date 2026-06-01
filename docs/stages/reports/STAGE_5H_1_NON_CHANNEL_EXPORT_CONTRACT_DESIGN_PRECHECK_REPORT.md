# Отчет Stage 5H.1 - Non-Channel Export Contract Design Precheck

## Статус

Stage 5H.1 завершен.

## Итоговый вывод

NON_CHANNEL_CONTRACT_DESIGN_PRECHECK_COMPLETE_DESIGN_DOC_CREATED

## Проверенные файлы

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/reports/STAGE_5G_2_NON_CHANNEL_DATASET_CONTRACT_PRECHECK_REPORT.md`
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
- `docs/stages/README.md`
- `tg_msg_manager/cli_parser.py`
- `tg_msg_manager/cli/commands/export.py`
- `tg_msg_manager/cli/commands/db_export.py`
- `tg_msg_manager/cli/__init__.py`
- `tg_msg_manager/services/export/`
- `tg_msg_manager/services/db_export/`
- `tg_msg_manager/services/rendering/`
- `tg_msg_manager/services/context/`
- `tg_msg_manager/infrastructure/storage/read/`
- `tg_msg_manager/infrastructure/storage/write/`
- `tests/cli/`
- `tests/services/db_export/`
- `tests/services/rendering/`

## Contract boundary recommendation

- Следующий formal contract должен покрывать user/group `export` и `db-export` outputs under `DB_EXPORTS/`.
- `export-pm` не должен входить в этот contract.
- `.export_state/` можно описывать как DB export writer state после fixtures/tests.
- `.writer_state/` и part rotation лучше включать только после synthetic fixture coverage.
- Implementation details вроде exact rotation thresholds и full raw payload не должны становиться public contract сейчас.

## TXT projection recommendation

- `context-readable` должен быть primary TXT contract surface для user/group `export` и `db-export`.
- `legacy` следует описывать как explicit compatibility mode.
- `docs/architecture/TXT_RENDERING.md` достаточно как shared renderer boundary; final contract должен ссылаться на него и фиксировать markers/sections через fixtures, а не full golden snapshots.

## JSONL expectation recommendation

- Shared compact JSONL expectations можно документировать для default `ai` profile, где `export` и `db-export` используют общий DB export JSONL serializer.
- Stable candidates: `message_id`, `chat_id`, `user_id`, `author_name`, `timestamp`, `text`, reply fields, media/fwd/context/service fields и reactions.
- Omitted null/empty values должны быть частью compact JSONL expectation.
- Full raw payload должен остаться out of scope до отдельного stage.

## Fixtures/tests prerequisites

- Перед final contract нужен fixtures-first stage или минимум 5H.2 plan.
- Нужны synthetic fixtures для TXT context-readable/legacy, compact JSONL, part rotation, `.export_state`, `.writer_state`, skip/no-new-work behavior.
- Contract tests later должны проверять filenames, part paths, markers, JSONL key sets, state presence и privacy-safe examples.

## Design doc

- Создан `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_DESIGN.md`.
- Документ явно помечен как design/precheck, не final contract.
- Документ не создает runtime guarantees beyond current evidence.
- Документ не содержит private или real example data.
- Dataset Contract V1 boundary сохранен: current V1 остается direct channel export contract.

## Recommended next stage

- Следующий безопасный шаг: выполнить 5H.2 synthetic fixtures plan.
- Final `NON_CHANNEL_EXPORT_CONTRACT_V1.md` не создавать до synthetic fixtures и contract tests.

## Навыки

- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`

## Проверки

- `git diff --check`: passed.

## Подтверждения

- Runtime behavior не менялось.
- CLI behavior не менялось.
- SQLite schema и storage behavior не менялись.
- Dataset behavior не менялось.
- Output formats, TXT rendering, JSONL schema, exporter/db-export/private archive services, fixtures и tests не менялись.
- Private artifacts не читались.

## Lifecycle

- Финальный отчет создан.
- Stage-файл перенесен из `docs/stages/active/` в `docs/stages/completed/`.
- `docs/stages/README.md` обновлен.
