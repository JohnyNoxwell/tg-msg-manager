# Отчет Stage 5P.2 — Target Identity History Duplicate Observation Remediation

Статус: complete

## Исправление

- Совместимое частичное identity-наблюдение теперь обогащает последний snapshot
  вместо создания дубликата.
- Реальное изменение имени или username продолжает создавать новый snapshot.
- Регрессионный тест дополнительно проверяет username и source message первого
  snapshot.

## Измененные файлы

- `tg_msg_manager/infrastructure/storage/_sqlite_identity.py`
- `tests/infrastructure/storage/test_storage_sqlite.py`
- stage/report/lifecycle docs Stage 5P.2 и обновление Stage 5P.

## Проверки

- focused identity-history pytest: passed, 7 tests.
- focused `ruff check`: passed.
- focused `ruff format --check`: passed.
- focused `python3 -m compileall`: passed.
- `git diff --check`: passed.
- Полный Stage 5P повторно не запускался по прямому указанию пользователя;
  принята delta-verification исправленного единственного сбоя.

## Сохраненные границы

- CLI, SQLite schema, dataset/export contracts и зависимости не изменены.
- `architecture-guard`: applied from `.skills/architecture-guard/SKILL.md`.
- `stage-completion-auditor`: applied from `.skills/stage-completion-auditor/SKILL.md`.
- Stage 5P.2 перемещен в `completed/`; Stage 5Q не запускался.
