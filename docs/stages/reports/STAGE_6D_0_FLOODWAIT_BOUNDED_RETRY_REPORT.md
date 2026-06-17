# STAGE 6D.0 — FLOODWAIT BOUNDED RETRY REPORT

Статус: complete

## Что изменено

- `tg_msg_manager/core/telegram/client.py`
  - `get_messages()` переведён с рекурсивного FloodWait retry на ограниченный итеративный цикл.
  - `download_media()` переведён с рекурсивного FloodWait retry на ограниченный итеративный цикл.
  - Внутренний лимит FloodWait retry: 3 повтора после первичной попытки.
- `tests/core/telegram/test_telegram_core.py`
  - Добавлена проверка остановки `get_messages()` после исчерпания FloodWait retry.
  - Добавлена проверка успешного FloodWait retry для `download_media()` с сохранением `file`.
  - Добавлена проверка остановки `download_media()` после исчерпания FloodWait retry.
- `CHANGELOG.md`
  - Добавлена bilingual Unreleased запись о FloodWait retry hardening.
- `docs/stages/completed/STAGE_6D_0_FLOODWAIT_BOUNDED_RETRY.md`
  - Stage task moved from active to completed.
- `docs/stages/README.md`
  - Stage index updated with report and completed prompt record.

## Что исправлено

- Убрана неограниченная рекурсия при повторяющемся `FloodWaitError` в `get_messages()` и `download_media()`.
- После исчерпания лимита `FloodWaitError` пробрасывается наружу вместо бесконечного сна и повторов.

## Что сохранено

- CLI surface не изменялся.
- SQLite schema не изменялась.
- Dataset, manifest, state и output layout не изменялись.
- Нормализация сообщений сохранена.
- `limit`, `message_ids` и `file` передаются в повторные вызовы без изменений.
- Throttling, FloodWait telemetry и generic non-FloodWait `download_media()` error handling сохранены.
- `delete_messages()` не изменялся.

## Проверки

- `python3 -m compileall tg_msg_manager/core/telegram`: passed
- `ruff check tg_msg_manager/core/telegram/client.py tests/core/telegram/test_telegram_core.py`: passed
- `pytest tests/core/telegram/test_telegram_core.py`: passed
- `git diff --check`: passed

## Skills

- `stage-writer`: applied from `/Users/maczone/.codex/skills/stage-writer/SKILL.md`
- `bugfix-stage-writer`: applied from `.skills/bugfix-stage-writer/SKILL.md`
- `stage-reviewer`: applied from `.skills/stage-reviewer/SKILL.md`; verdict pass
- `architecture-guard`: applied from `.skills/architecture-guard/SKILL.md`; violations none
- `stage-completion-auditor`: applied from `.skills/stage-completion-auditor/SKILL.md`; verdict complete

## Не запускалось

- `make test`: не запускался, stage required focused Telegram core checks.
- `make verify`: не запускался, stage required focused Telegram core checks.

## Завершение

- Implementation: complete.
- Required docs: complete.
- Lifecycle cleanup: complete.
