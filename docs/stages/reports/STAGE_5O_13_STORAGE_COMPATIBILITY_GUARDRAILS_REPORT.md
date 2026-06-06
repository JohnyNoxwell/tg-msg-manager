# Отчет по этапу 5O.13 — Storage Compatibility Guardrails

Статус: завершен.

## Выполнено

- Добавлена архитектурная проверка, запрещающая сервисам зависеть от
  `BaseStorage` и legacy-агрегатора `storage.interface`.
- Добавлена проверка, запрещающая storage compatibility surfaces импортировать
  сервисы или CLI.
- В split-map документах зафиксированы сохраняемые compatibility surfaces:
  `BaseStorage`, публичные реэкспорты, write/state wrappers и record DTO.

## Измененные файлы

- `tests/architecture/test_static_boundaries.py`
- `docs/architecture/STORAGE_CONTRACT_SPLIT_MAP.md`
- `docs/architecture/SQLITE_WRITE_PATH_SPLIT_MAP.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_5o_13_storage_compatibility_guardrails.md`
- `docs/stages/reports/STAGE_5O_13_STORAGE_COMPATIBILITY_GUARDRAILS_REPORT.md`

## Проверки

- `pytest tests/architecture -q`: пройдено, 18 tests и 4 subtests.
- `pytest tests/infrastructure/storage -q`: пройдено, 49 tests.
- `python3 -m compileall tg_msg_manager`: пройдено.
- `ruff check tests/architecture tests/infrastructure/storage`: пройдено.

## Сохраненные границы

- SQLite schema, migrations, SQL text/order и `user_version` не изменялись.
- Storage behavior, exported records и публичные import paths не изменялись.
- `BaseStorage` сохранен как compatibility umbrella для `SQLiteStorage`.
- `stage-reviewer`: applied from `.skills/stage-reviewer/SKILL.md`.
- `architecture-guard`: applied from `.skills/architecture-guard/SKILL.md`.
- `stage-completion-auditor`: applied from
  `.skills/stage-completion-auditor/SKILL.md`; blockers не обнаружены.
