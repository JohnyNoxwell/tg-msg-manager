# STAGE 5O.0 - Refactoring Guardrails Report

## Статус

Завершено.

`stage-reviewer`: applied from `.skills/stage-reviewer/SKILL.md`
`architecture-guard`: applied from `.skills/architecture-guard/SKILL.md`
`stage-completion-auditor`: applied from `.skills/stage-completion-auditor/SKILL.md`

## Измененные файлы

- `tests/architecture/test_static_boundaries.py`
- `docs/stages/reports/STAGE_5O_0_REFACTORING_GUARDRAILS_REPORT.md`
- `docs/stages/completed/stage_5o_0_refactoring_guardrails.md`
- `docs/stages/README.md`

## Добавленные guardrails

- Добавлен статический тест, который запрещает raw SQL и вызовы SQL execute вне `tg_msg_manager/infrastructure/storage/`.
- Добавлен статический тест, который запрещает импорты `tg_msg_manager.infrastructure` из `tg_msg_manager/core`.
- Добавлен статический тест, который запрещает импорты `tg_msg_manager.services` из `tg_msg_manager/infrastructure`.
- Добавлен статический тест, который запрещает импорты CLI-модулей из `core`, `services` и `infrastructure`.
- Добавлен статический тест, который запрещает новые импорты широкого compatibility-aggregator `tg_msg_manager.infrastructure.storage.interface`.

## Allowlist

- `tg_msg_manager/testing/fixtures.py` оставлен в allowlist для raw SQL, потому что это существующий тестовый helper внутри пакета, который напрямую подготавливает storage fixtures. Новые raw SQL-вхождения вне storage этим allowlist не разрешены.

## Проверки

- `pytest tests/architecture`: passed, 16 passed.
- `python3 -m compileall tg_msg_manager`: passed.
- `ruff check tests/architecture`: passed.

## Сохраненные контракты

- Runtime behavior: сохранено, runtime-код не менялся.
- CLI contracts: сохранены, CLI-код не менялся.
- SQLite schema: сохранена, storage/schema/runtime SQL не менялись.
- Export formats: сохранены, exporter/runtime-код не менялся.

## Lifecycle cleanup

- `docs/stages/active/stage_5o_0_refactoring_guardrails.md` перемещен в `docs/stages/completed/stage_5o_0_refactoring_guardrails.md`.
- `docs/stages/README.md` обновлен: stage 5O.0 убран из active и добавлен как completed с отчетом.
