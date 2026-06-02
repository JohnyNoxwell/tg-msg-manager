# Отчет Stage 5M.2 - Public Docs Feature Status Alignment

## Статус

Stage 5M.2 завершен.

## Итоговый вывод

PUBLIC_DOCS_FEATURE_STATUS_UPDATED_WITH_EXPORT_PM_CAVEAT

## Навыки

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`

## Проверенные файлы

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `README.md`
- `COMMANDS.md`
- `CHANGELOG.md`
- `docs/README.md`
- `docs/user/QUICKSTART.md`
- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md`
- `docs/architecture/PRIVATE_ARCHIVE_CONTRACT_DEFERRED_DECISION.md`
- `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md`
- `docs/development/RELEASE_CANDIDATE_DECISION.md`
- `docs/development/RELEASE_CHECKLIST_SCOPE.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `docs/stages/reports/STAGE_5J_3_RELEASE_READINESS_RECHECK_CHANGELOG_FINALIZATION_REPORT.md`
- `docs/stages/reports/STAGE_5L_1_RELEASE_CANDIDATE_DECISION_RECHECK_REPORT.md`
- `docs/stages/reports/STAGE_5M_0_EXTERNAL_RISK_AUDIT_VERIFICATION_REPORT.md`
- `docs/stages/README.md`

## Найденные расхождения

- `export-pm` был видим в README как feature и quick-reference команда, но `COMMANDS.md` не имел отдельной секции с caveat о deferred private archive contract.
- Contract docs и release/status docs уже фиксировали, что `export-pm` исключен из Non-Channel Export Contract V1.
- QUICKSTART уже направлял first-run пользователей к `export`, `db-export`, safe channel dataset, validation и command reference; отдельной правки не требовал.
- CHANGELOG `[Unreleased]` уже фиксировал deferred `export-pm` / private archive contract work; правка не требовалась.

## Измененные docs

- `README.md`: добавлены краткие caveats, что `export-pm` не входит в user/group `export` + `db-export` contract и private archive contract deferred.
- `COMMANDS.md`: добавлена минимальная секция `export-pm` с примером и deferred-contract caveat.
- `docs/README.md`: добавлена ссылка на deferred decision для private archive / `export-pm`.

## Проверки

- `git diff --check`: passed.

## Подтверждения

- Runtime behavior не менялся.
- CLI behavior не менялся.
- Tests, fixtures, SQLite schema, package metadata, release state и version не менялись.
- Private archive contract не реализован; `export-pm` не включен в Non-Channel Export Contract V1.

## Lifecycle

- Финальный отчет создан.
- Stage-файл перенесен из `docs/stages/active/` в `docs/stages/completed/`.
- `docs/stages/README.md` обновляется в рамках серии Stage 5M.
