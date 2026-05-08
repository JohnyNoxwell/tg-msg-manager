# STAGE 5 — Fixture And E2E Hardening

## Цель этапа

Закрепить foundation backlog полноценной автономной test harness без сети, чтобы дальнейшее расширение проекта не приводило к каскадным регрессиям.

Этап завершает foundation-first программу.

## Статус выполнения

Обновлено: `2026-05-04`

- [x] `5.1` Fixture format
- [x] `5.2` Fake Telegram surface
- [x] `5.3` Fixture loaders and runtime helpers
- [x] `5.4` E2E suites
- [x] `5.5` Final verification

Закрыто в текущем проходе:
- добавлен автономный testing surface в `tg_msg_manager/testing/`;
- описан anonymized JSONL fixture format в `tests/fixtures/stage5/README.md`;
- реализован `FakeTelegramClient` с поддержкой:
  - `iter_messages`;
  - `get_messages`;
  - `get_entity`;
  - `get_dialogs`;
  - `delete_messages`;
  - `download_media`;
  - deleted/missing states;
  - deterministic failure injection;
  - call history для assertions;
- добавлены fixture loaders, export normalization helpers и temp runtime для реальных service/storage e2e прогонов;
- добавлены fixture datasets для:
  - missing-parent/context extraction;
  - duplicate messages;
  - edited payload revision;
  - retryable tracked-sync failure;
- добавлен fixture-backed e2e suite для:
  - sync;
  - context;
  - export;
  - retry;
  - report;
- edge coverage подтверждена сценариями:
  - interrupted sync;
  - missing parents;
  - duplicate messages;
  - edited payloads;
  - retryable failures;
  - missing export state / stale report diagnostics;
- harness не требует Telegram API и не добавляет новый product surface.

Текущая верификация:
- `python3 -m unittest tests.test_fixture_e2e -q` -> `4 tests`, `OK`
- `python3 -m unittest tests.test_fixture_e2e tests.test_reporting tests.test_retry_worker tests.test_services tests.test_sync_system -q` -> `62 tests`, `OK`
- `make test` -> `144 tests`, `OK`
- `ruff check .` -> `OK`
- `ruff format --check .` -> `OK`

Test matrix и границы fixture-backed coverage:
- `group_sync_context.jsonl` проверяет deep sync, missing-parent recovery, duplicate message idempotency и export/report integration;
- `group_sync_context_edited.jsonl` проверяет replacement edited payload без раздувания target-linked state;
- `tracked_retry.jsonl` проверяет tracked sync retry enqueue, due-task replay, missing export warning и stale sync diagnostics;
- interrupted sync покрывается через cooperative stop на первом persistence-шаге поверх fixture runtime, без сети и без Telethon.

Итог этапа:
- `Stage 5` завершён;
- foundation backlog теперь имеет автономную fixture-based harness;
- ключевые pipeline paths `sync/context/export/retry/report` воспроизводимы локально без Telegram API;
- будущие refactor/change batches получили устойчивую e2e опору против частичных регрессий.

## Что делаем

- определяем устойчивый fixture format для Telegram-like данных;
- реализуем `FakeTelegramClient`;
- добавляем fixture loader helpers;
- строим e2e tests для:
  - sync;
  - context;
  - export;
  - retry;
  - report;
- добавляем edge fixtures для проблемных сценариев.

## Что не делаем

- не используем реальные Telegram данные;
- не требуем сеть;
- не делаем новый product surface;
- не расширяем analytics scope;
- не внедряем избыточную симуляцию Telethon, которая не нужна для тестируемых сценариев.

## Входные инварианты

- Stage 0–4 завершены и имеют стабильные contracts;
- fake client должен моделировать только те Telegram behaviors, которые нужны проекту;
- fixtures обязаны быть обезличены и безопасны для хранения в репо;
- e2e tests должны проверять pipeline behavior, а не внутренние приватные helper details.

## Исполняемая очередь

### Блок 5.1 — Fixture format

- описать JSONL fixture format и допустимые дополнительные поля;
- явно запретить реальные user/chat identifiers и приватные payloads;
- зафиксировать правила для deleted/missing/fetch-error cases.

### Блок 5.2 — Fake Telegram surface

- реализовать `FakeTelegramClient` с поддержкой:
  - `iter_messages`;
  - fetch by message id;
  - range fetch;
  - sender filter;
  - deleted/missing messages;
  - controlled failure simulation там, где это нужно для retry/report coverage;
- вести call history для assertions.

### Блок 5.3 — Fixture loaders and runtime helpers

- добавить helpers для загрузки fixtures, seed storage и подготовки temp runtime;
- убрать boilerplate из будущих e2e tests;
- обеспечить сравнение export outputs без нестабильных полей.

### Блок 5.4 — E2E suites

- покрыть end-to-end сценарии для sync/context/export/retry/report;
- включить edge fixtures:
  - interrupted sync;
  - missing parents;
  - duplicate messages;
  - edited payloads;
  - retryable failures;
  - stale export/report situations.

### Блок 5.5 — Final verification

- убедиться, что e2e tests не ходят в сеть;
- прогнать полный suite;
- зафиксировать test matrix и границы того, что считается fixture-backed coverage.

## Definition of Done

- в репо есть автономная fixture-based test harness;
- foundation pipeline можно проверять без Telegram API;
- e2e tests покрывают ключевые сценарии sync/context/export/retry/report;
- fixtures обезличены и пригодны для долгой поддержки;
- этап снижает риск частичных поломок при последующих изменениях.

Статус:
- `Done` on `2026-05-04`.
