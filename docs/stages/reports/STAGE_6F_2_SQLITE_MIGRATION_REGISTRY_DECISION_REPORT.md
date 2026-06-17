# Stage 6F.2 — SQLite migration registry decision report

Статус: complete.

## Решение

- Финальное решение: defer; registry implementation не создается.
- Текущий ordered `run_migrations()` остается достаточным вместе с guardrails из
  Stage 6F.0 и startup path split из Stage 6F.1.
- Follow-up active stages не создаются.

## Обоснование

- Stage 6F.0 добавил startup guardrails без runtime-изменений: свежий bootstrap,
  legacy версии 0, 5, 9, 10, 12 и 13, сохранение данных, финальный
  `PRAGMA user_version = 14` и идемпотентность повторного startup.
- Stage 6F.1 разделил startup phases без изменения SQL semantics: current schema
  creation, compatibility column ensures, index creation, legacy migrations и
  final commit остались в прежнем порядке.
- Registry добавил бы новую runtime migration surface без текущего дефекта или
  новой schema migration, требующей metadata-driven coordination.

## Файлы

- Создан `docs/architecture/SQLITE_MIGRATION_REGISTRY_DECISION.md`.
- Обновлен `docs/architecture/README.md`.
- Создан `docs/stages/reports/STAGE_6F_2_SQLITE_MIGRATION_REGISTRY_DECISION_REPORT.md`.
- Обновлен `docs/stages/README.md` в рамках lifecycle cleanup.
- Перемещен `docs/stages/active/stage_6f_2_sqlite_migration_registry_decision.md` в `docs/stages/completed/`.
- Runtime code и tests в рамках 6F.2 не редактировались; рабочее дерево уже
  содержало незакоммиченные изменения 6F.0/6F.1 до начала 6F.2.

## Проверки

- `git diff --check`: passed.
- `python3 -m compileall tg_msg_manager`: passed.
- Полные storage tests не запускались: stage docs-only, runtime code и tests не изменялись в рамках 6F.2.

## Skills

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`
