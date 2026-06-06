# STAGE 5O.2 - I18N Parity Guard Report

## Статус

Завершено.

`stage-reviewer`: applied from `.skills/stage-reviewer/SKILL.md`
`stage-completion-auditor`: applied from `.skills/stage-completion-auditor/SKILL.md`

## Измененные файлы

- `tests/core/test_i18n.py`
- `tg_msg_manager/i18n.py`
- `docs/stages/reports/STAGE_5O_2_I18N_PARITY_GUARD_REPORT.md`
- `docs/stages/completed/stage_5o_2_i18n_parity_guard.md`
- `docs/stages/README.md`

## Добавленные проверки

- Добавлен тест, который проверяет одинаковый набор translation keys для всех поддерживаемых локалей.
- Добавлен тест, который проверяет совпадение named format placeholders с fallback-локалью.

## Исправления переводов

- В `ru` добавлены отсутствовавшие help-ключи, которые уже существовали в `en`.
- Placeholder mismatch не найден.

## Проверки

- `pytest tests/core`: passed, 30 passed.
- `python3 -m compileall tg_msg_manager`: passed.
- `ruff check tg_msg_manager/i18n.py tests/core`: passed.

## Сохраненные контракты

- CLI behavior: сохранено, команды, флаги и defaults не менялись.
- SQLite schema: сохранена, storage/schema не менялись.
- Runtime helper API: сохранен, публичные i18n helper imports не менялись.

## Lifecycle cleanup

- `docs/stages/active/stage_5o_2_i18n_parity_guard.md` перемещен в `docs/stages/completed/stage_5o_2_i18n_parity_guard.md`.
- `docs/stages/README.md` обновлен: stage 5O.2 убран из active и добавлен как completed с отчетом.
