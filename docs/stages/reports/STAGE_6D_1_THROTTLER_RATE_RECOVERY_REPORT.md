# STAGE 6D.1 — THROTTLER RATE RECOVERY REPORT

Статус: complete

## Что изменено

- `tg_msg_manager/core/telegram/throttler.py`
  - `RateThrottler` теперь сохраняет настроенный начальный `rps`.
  - После slowdown throttler постепенно восстанавливает `rps` при последующих `throttle()` вызовах.
  - Recovery ограничен начальным `rps` и не повышает скорость выше него.
- `tests/core/telegram/test_telegram_core.py`
  - Добавлен тест сохранения minimum clamp в `adjust_rate()`.
  - Добавлен тест постепенного восстановления после slowdown и ограничения recovery начальным `rps`.
- `CHANGELOG.md`
  - Добавлена bilingual Unreleased запись о throttler rate recovery.
- `docs/stages/completed/STAGE_6D_1_THROTTLER_RATE_RECOVERY.md`
  - Stage task moved from active to completed.
- `docs/stages/README.md`
  - Stage index updated with report and completed prompt record.

## Что исправлено

- Убрано постоянное замедление throttler после единичного FloodWait в долгом процессе.
- `adjust_rate()` по-прежнему снижает `rps` и сохраняет minimum clamp `0.1`.

## Что сохранено

- CLI surface не изменялся.
- SQLite schema не изменялась.
- Dataset, manifest, state и output layout не изменялись.
- Stage 6D.0 bounded FloodWait retry limits не изменялись.
- Token bucket burst behavior сохранён.
- `max_requests_per_second` constructor alias сохранён.
- Protected service facades и compatibility wrappers не изменялись.

## Проверки

- `python3 -m compileall tg_msg_manager/core/telegram`: passed
- `ruff check tg_msg_manager/core/telegram/throttler.py tg_msg_manager/core/telegram/client.py tests/core/telegram/test_telegram_core.py`: passed
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
