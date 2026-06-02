# Отчет Stage 5M.6 - Operational Risk Notes

## Статус

Stage 5M.6 завершен.

## Итоговый вывод

OPERATIONAL_RISK_DOCS_UPDATED

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
- `docs/user/QUICKSTART.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `docs/development/RELEASE_CHECKLIST_SCOPE.md`
- `docs/development/LOCAL_VERIFICATION_MATRIX.md`
- `docs/development/RELEASE_CANDIDATE_DECISION.md`
- `docs/development/README.md`
- `docs/stages/reports/STAGE_5M_0_EXTERNAL_RISK_AUDIT_VERIFICATION_REPORT.md`
- `tg_msg_manager/core/config.py`
- `tg_msg_manager/core/telegram/client.py`
- `tg_msg_manager/core/telegram/throttler.py`
- `tg_msg_manager/infrastructure/storage/sqlite.py`
- `tg_msg_manager/infrastructure/storage/write/connection.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py`
- `tg_msg_manager/services/scheduler.py`
- `tg_msg_manager/cli_support.py`
- `tests/core/telegram/test_telegram_core.py`
- `tests/core/test_concurrency.py`
- `tests/services/scheduler/test_scheduler.py`
- `docs/stages/README.md`

## Ответы аудита

- Session sensitivity уже описана в privacy doc; recovery/re-auth guidance была неканонической.
- FloodWait handling существует для части Telethon wrapper paths; `max_rps` есть в config, но Telegram limits остаются внешними и нестабильными.
- SQLite использует WAL для main write connection и background write queue, но concurrent long writers могут привести к lock/busy рискам.
- `schedule` является macOS launchd/launchctl path; scheduled runs требуют той же local session/config/DB среды.
- Live smoke checks уже отделены от offline verification в release docs; canonical operational page добавляет прямую caveat.

## Измененные docs

- `docs/development/OPERATIONAL_RISKS_AND_LIMITS.md`: создана canonical страница operational caveats.
- `docs/development/README.md`: добавлена ссылка на operational risks page.
- `docs/user/QUICKSTART.md`: добавлена ссылка на operational caveats.
- `README.md`: добавлена ссылка на operational risks page.

## Проверки

- `git diff --check`: passed.

## Подтверждения

- Runtime behavior, CLI behavior, SQLite schema, storage logic, scheduler behavior, tests, fixtures, output formats и live checks не менялись.
- Sessions, DB contents, real exports, media, logs, screenshots и private artifacts не читались.

## Lifecycle

- Финальный отчет создан.
- Stage-файл перенесен из `docs/stages/active/` в `docs/stages/completed/`.
- `docs/stages/README.md` обновляется в рамках серии Stage 5M.
