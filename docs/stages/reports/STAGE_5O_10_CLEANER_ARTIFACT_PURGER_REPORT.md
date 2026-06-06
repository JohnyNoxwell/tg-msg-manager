# STAGE 5O.10 — отчет по выделению очистки артефактов

## Статус

Завершено.

`stage-reviewer`: applied from `.skills/stage-reviewer/SKILL.md`
`architecture-guard`: applied from `.skills/architecture-guard/SKILL.md`
`stage-completion-auditor`: applied from `.skills/stage-completion-auditor/SKILL.md`

## Изменения

- Файловое удаление выделено из `CleanerService.purge_user_data` в `purge_user_artifacts`, принимающий явные корни и ID пользователя.
- `CleanerService` оставлен оркестратором удаления записей storage и файловых артефактов.
- Добавлены tempfile-тесты границ корней, совпадений файлов и директорий, несовпадающих имен, отсутствующих корней и DB sidecar-файлов.
- CLI-документация не менялась: существующий контракт `delete` соответствует сохраненному поведению.

## Измененные файлы

- `tg_msg_manager/services/artifact_purger.py`
- `tg_msg_manager/services/cleaner.py`
- `tests/services/cleaner/test_artifact_purger.py`
- `tests/services/cleaner/test_cleaner.py`
- `docs/stages/reports/STAGE_5O_10_CLEANER_ARTIFACT_PURGER_REPORT.md`
- `docs/stages/completed/stage_5o_10_cleaner_artifact_purger.md`
- `docs/stages/README.md`

## Проверки

- `pytest tests/services/cleaner -q`: passed, 13 passed.
- `pytest tests/services -k cleaner`: passed, 13 passed.
- `pytest tests/cli -k delete`: passed, 1 passed.
- `pytest tests/architecture -q`: passed, 16 passed, 4 subtests passed.
- `python3 -m compileall -q tg_msg_manager`: passed.
- `ruff check tg_msg_manager/services/cleaner.py tg_msg_manager/services/artifact_purger.py tests/services/cleaner tests/cli`: passed.
- `ruff format --check tg_msg_manager/services/cleaner.py tg_msg_manager/services/artifact_purger.py tests/services/cleaner/test_cleaner.py tests/services/cleaner/test_artifact_purger.py`: passed.
- `git diff --check -- tg_msg_manager/services/cleaner.py tg_msg_manager/services/artifact_purger.py tests/services/cleaner/test_cleaner.py tests/services/cleaner/test_artifact_purger.py`: passed.

## Сохраненные контракты

- CLI-команда, аргументы, подтверждение и итоговый вывод не менялись.
- Возвращаемая сводка `purge_user_data` и обработка ошибок удаления сохранены.
- Состав удаляемых записей и SQLite-схема не менялись.
- Удаление ограничено прежними явными корнями и прежним совпадением `_<user_id>`.

## Lifecycle cleanup

- Задача перемещена из `docs/stages/active/` в `docs/stages/completed/`.
- `docs/stages/README.md` обновлен.
