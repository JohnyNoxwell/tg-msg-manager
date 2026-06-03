# Stage 5N.0 Report — Target Names History Read Model

## Статус

COMPLETED

## Измененные файлы

Добавлены:

- `tg_msg_manager/infrastructure/storage/contracts/target_names_storage.py`
- `tg_msg_manager/infrastructure/storage/read/target_names.py`
- `tg_msg_manager/services/target_names/__init__.py`
- `tg_msg_manager/services/target_names/models.py`
- `tg_msg_manager/services/target_names/query.py`
- `tests/infrastructure/storage/test_target_names_history_storage.py`
- `tests/services/target_names/test_target_names_query.py`

Изменены:

- `tg_msg_manager/infrastructure/storage/_sqlite_read_path.py`
- `tg_msg_manager/infrastructure/storage/contracts/__init__.py`
- `tg_msg_manager/infrastructure/storage/read/__init__.py`
- `tg_msg_manager/infrastructure/storage/records.py`

Удалены: нет.

## Найденные storage-факты

- `user_identity_history` содержит `observed_at`, `author_name`, `username`, `chat_id`, `source_message_id`.
- `users` содержит текущие `username` и `current_author_name`.
- `sync_targets` содержит текущий tracked target context и timestamps `added_at`, `last_sync_at`.
- `chats` содержит только текущие `title` и `type`; истории title для chat/channel в текущей схеме нет.

## Что добавлено

- Read-only target-name storage contract и DTO.
- Локальное разрешение target по numeric id и локально сохраненному username.
- Явные состояния `found`, `not_found`, `ambiguous`.
- Read-only service/query слой для нормализации snapshots в `username`, `display_name`, `title`.
- Derive `old_value` из предыдущего observed value, фильтрация consecutive duplicate values, сортировка ascending.
- Для chat/channel title history возвращается пустая история с текущим title, без синтетических изменений.

## Границы

- SQLite schema changed: no.
- `PRAGMA user_version`, migrations, indexes changed: no.
- Telegram calls added: no.
- SQLite writes in new query path: no.
- Private artifacts read: no.

## Тесты

Добавлены:

- storage tests для numeric user, username lookup, ambiguity, chat title gap, unknown target.
- service tests для old_value derivation, field filtering, empty chat title history, unknown/ambiguous states.

## Verification

- `python3 -m unittest tests.infrastructure.storage.test_target_names_history_storage -q`: passed.
- `python3 -m unittest tests.services.target_names.test_target_names_query -q`: passed.
- `python3 -m unittest tests.infrastructure.storage.test_storage_sqlite -q`: passed.
- `git diff --check`: passed.

Не запускались:

- `make test`: deferred until full 5N workflow.
- `make verify`: deferred until full 5N workflow.

## Deferred

- CLI command, formatters, user docs: Stage 5N.1.
- Chat/channel title history persistence: Stage 5N.2.

## Skills

- stage-reviewer: applied from .skills/stage-reviewer/SKILL.md
- architecture-guard: applied from .skills/architecture-guard/SKILL.md
- stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md
