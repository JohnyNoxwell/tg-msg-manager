# 🧹 TG_MSG_MNGR: Advanced Telegram Suite

[🇷🇺 Русская версия](#русский) | [🇬🇧 English Version](#english)

---

<a id="русский"></a>
## 🇷🇺 Русский

**TG_MSG_MNGR** — это мощная экосистема для управления вашим цифровым следом в Telegram. Утилита представляет собой полноценное консольное приложение с интерактивным меню, фокусом на UX, скорость и надежность.

### Quick Reference

```bash
python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321 --depth 3 --json
python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321 --flat
python3 -m tg_msg_manager.cli db-export --user-id 123456789
python3 -m tg_msg_manager.cli export-pm --user-id 123456789
python3 -m tg_msg_manager.cli db-export --user-id 123456789 --json
python3 -m tg_msg_manager.cli export-channel --channel @example --limit 100 --media metadata
python3 -m tg_msg_manager.cli export-channel --channel @example --limit 10 --media metadata --discussion full --max-comments-per-post 100
python3 -m tg_msg_manager.cli update
python3 -m tg_msg_manager.cli retry --list
python3 -m tg_msg_manager.cli report
```

### Документация

- Полная карта документации: [`docs/README.md`](docs/README.md)
- Справочник команд: [`COMMANDS.md`](COMMANDS.md)
- Правила для coding agents: [`AGENTS.md`](AGENTS.md)

### 🚀 Быстрый старт

1. **Установка**:
   ```bash
   git clone https://github.com/JohnyNoxwell/tg-msg-manager.git
   cd tg-msg-manager
   pip install .
   ```

2. **Запуск интерактивного меню**:
   *   **Способ A (Самый быстрый)**: Из интерактивного терминала, находясь в корне проекта:
       ```bash
       python3 run.py
       ```
   *   **Способ B (После настройки)**: Введите `tg` в любом месте терминала (см. раздел [Алиасы](#алиасы)).

3. **Навигация**: Используйте двузначные коды меню: **01-10** для основных функций, **11** для `retry`, **12** для `report`, **98** — переключение языка, **00** — выход, **ESC** — возврат назад. Старые короткие вводы `1-9`, `R`, `P`, `L`, `0` сохранены для совместимости.

---

### 🌟 Основные функции

Основные возможности проекта:

* 🧹 **Глобальная очистка (`clean`)** — Удаляет **только ваши** сообщения из всех выбранных чатов. Поддерживает фильтры и безопасный режим (Dry Run).
* 📥 **Умный экспорт с контекстом (`export`)** — Собирает сообщения цели вместе с окружающим контекстом беседы, восстанавливая полную картину диалога.
* 💬 **Архив лички (`export-pm`)** — Текстовый бэкап приватного чата с подготовленной структурой папок под медиа.
* 🗄️ **SQLite База данных** — Все данные хранятся в структурированной базе `messages.db`. Это обеспечивает мгновенный поиск и отсутствие дубликатов.
* 📤 **Экспорт из БД** — Выгрузка накопленных данных из SQLite в JSON/Text. JSONL по умолчанию теперь компактный и ориентирован на анализ нейросетью.
* 📡 **Прямой экспорт канала (`export-channel`)** — Файловый dataset export постов Telegram-канала в `manifest.json`, `messages.jsonl`, `messages.txt`, `media_manifest.jsonl` и, при явном `--discussion full`, discussion dataset files.
* ♻️ **Retry Queue (`retry`)** — Управление повторными задачами для recoverable sync/archive ошибок без ручного вмешательства в БД.
* 📋 **Audit Report (`report`)** — Read-only диагностика локальной БД, retry-очереди, export artifacts и состояния tracked targets без доступа к Telegram.

---

### 🛠️ Продвинутое использование (CLI)

Для автоматизации и опытных пользователей доступны прямые команды:

> ⚠️ **Примечание**: Прямые команды `python3 -m ...` необходимо запускать из корня проекта.

*   **Экспорт сообщений**: 
    `python3 -m tg_msg_manager.cli export --user-id 123456789 --depth 3`
    `python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321 --depth 3 --json`
    `python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321 --flat`
    `--json` собирает итоговый JSONL-файл после синка; без `--json` итоговый файл будет TXT.
    По умолчанию Deep Mode использует `--depth 2`, если глубина явно не указана.
*   **Очистка (Боевой режим)**: 
    `python3 -m tg_msg_manager.cli clean --apply --yes`
*   **Обновление всех целей**: 
    `python3 -m tg_msg_manager.cli update`
    После прерванного большого экспорта `update` может некоторое время выглядеть "задумавшимся" до появления построчного прогресса: в этот момент сервис делает shared head prefetch для чата и готовит общий HEAD-срез для нескольких целей.
*   **Архив лички**:
    `python3 -m tg_msg_manager.cli export-pm --user-id 123456789`
*   **Экспорт из БД**:
    `python3 -m tg_msg_manager.cli db-export --user-id 123456789`
    `python3 -m tg_msg_manager.cli db-export --user-id 123456789 --json`
    Без `--json` команда пишет TXT; с `--json` — компактный AI-friendly JSONL.
*   **Прямой экспорт канала**:
    `python3 -m tg_msg_manager.cli export-channel --channel @example --limit 100 --media metadata`
    `python3 -m tg_msg_manager.cli export-channel --channel @example --limit 10 --media metadata --discussion full --max-comments-per-post 100`
    Команда создаёт файловый dataset в `exports/channels/`. Stage 3A/3A.1/3B/3C не делает analytics и не пишет channel posts или discussion comments в SQLite.
    Поддерживаются только broadcast-каналы; группы и супергруппы не входят в `export-channel`.
    После успешного запуска создаётся `channel_export_state.json`; повторный запуск без `--force` экспортирует только новые посты и дописывает dataset append-only.
    По умолчанию используется безопасный режим `--media metadata`.
    По умолчанию `--discussion none`: resolver обсуждений не запускается и discussion files не создаются.
    `--discussion full` пишет `discussion_comments.jsonl`, `discussion_comments.txt`, `discussion_threads.jsonl` и `discussion_export_state.json` только для постов, полученных в текущем run.
    Инкрементальный запуск экспортирует discussion comments только для новых постов; no-new-posts run не перечитывает старые threads и не меняет `discussion_export_state.json`.
    Для discussion comments не выполняется full media download, только metadata/empty media fields.
    Полная загрузка media требует явного `--media full`; для неё доступны `--max-media-size 50MB` по умолчанию и `--media-types photo,video,...`.
    В `full` режиме `media_manifest.jsonl` фиксирует итоговые статусы `downloaded`, `already_exists`, `skipped_by_size`, `skipped_by_type` и `failed`.
*   **Полное удаление локальных данных**:
    `python3 -m tg_msg_manager.cli delete --user-id 123456789`
*   **Планировщик (macOS)**:
    `python3 -m tg_msg_manager.cli schedule`
*   **Повтор задач retry-очереди**:
    `python3 -m tg_msg_manager.cli retry --list`
    `python3 -m tg_msg_manager.cli retry --limit 10`
    `python3 -m tg_msg_manager.cli retry --cleanup`
    `--list` печатает локальное состояние retry-очереди, обычный запуск исполняет due tasks, `--cleanup` удаляет terminal rows.
*   **Диагностический отчёт**:
    `python3 -m tg_msg_manager.cli report`
    `python3 -m tg_msg_manager.cli report --json`
    Команда работает только через SQLite/filesystem read-side и не требует Telegram credentials.
*   **Установка алиасов**:
    `python3 -m tg_msg_manager.cli setup`

### ✅ Локальная проверка

```bash
pip install -e .[dev]
make lint
make format-check
make test
make verify
```

Offline regression harness:

```bash
python3 -m unittest tests.test_fixture_e2e -q
```

Минимальный smoke-check с текущей Telegram-сессией:

```bash
python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321 --flat --limit 1
```

### ⚙️ Конфигурация

Приложение читает настройки из `config.json`, переменных окружения `TG_*`, `.env` и init args.

Базовый пример:

```json
{
  "api_id": 123456,
  "api_hash": "YOUR_API_HASH",
  "session_name": "tg_msg_manager",
  "db_path": "messages.db",
  "account_name": "Default Account",
  "whitelist_chats": [],
  "include_chats": [],
  "chats_to_search_user_msgs": [],
  "max_rps": 3.0,
  "log_level": "INFO",
  "lang": "ru"
}
```

Приоритет источников:
- init args;
- env vars `TG_*`;
- `config.json`;
- `.env`.

Legacy aliases still supported:
- `exclude_chats` -> `whitelist_chats`
- `language` / `ui_language` -> `lang`

### Known Limitations

* `--limit` ограничивает обработку в рамках одного `sync_chat`; при экспорте пользователя по нескольким диалогам лимит применяется к каждому диалогу отдельно.
* `export-pm` пишет текстовый лог и медиа-структуру, но не восстанавливает Telegram-специфичные сущности как полноценный replay архива.
* `export-channel` в Stage 3A/3A.1/3B/3C является filesystem-first dataset projection pipeline: channel posts и discussion comments не пишутся в SQLite, analytics не выполняется.
* Безопасный режим по умолчанию для `export-channel` — `--media metadata`; `--media full` работает только при явном указании и использует size/type guardrails.
* Discussion export выключен по умолчанию через `--discussion none`; `--discussion full` экспортирует только threads для постов текущего run.
* Старые discussion threads не refresh/backfill без `--force`; reply-tree reconstruction не выполняется, сохраняется только `reply_to_id`.
* Full media download для discussion comments не реализован.
* `export-channel` использует файловый `channel_export_state.json` и append-only incremental update для новых постов, но не делает partial rollback уже дописанных файлов при сбое посередине run.
* Переключение существующего metadata-only dataset на `--media full` без `--force` скачивает media только для новых постов текущего run; исторический backfill старых rows по-прежнему требует full re-export.
* Фоновая запись в SQLite остаётся чувствительной к очень большим deep-export проходам; основная оптимизация сейчас сделана на уровне пакетных сервисных вызовов.
* Планировщик `schedule` сейчас ориентирован на macOS `launchd`.
* `db-export --json` по умолчанию не включает полный `raw_payload`; если когда-нибудь понадобится полный Telethon-слепок, это потребует отдельного full-профиля экспорта.
* После прерванного `export/tge` команда `update/tgu` может иметь заметную подготовительную паузу перед первым видимым прогрессом, если системе нужно переиспользовать большой общий HEAD-срез чата.
* `retry` покрывает только типизированные recoverable tasks (`sync_target`, `archive_pm`); это не произвольная универсальная очередь задач.
* `report` — диагностический read-only срез состояния системы, а не аналитический слой с keyword/topic или graph intelligence.

### 🧪 Fixture-Based E2E

Начиная с foundation stages `3`–`5`, в репо есть автономная offline harness:
- `tests/fixtures/stage5/*.jsonl` — anonymized Telegram-like fixtures;
- `tg_msg_manager/testing/` — `FakeTelegramClient`, fixture loaders, temp runtime helpers;
- `tests/test_fixture_e2e.py` — end-to-end покрытие для `sync`, `context`, `db-export`, `retry`, `report`.

Эта harness не требует сети и используется как regression-опора для дальнейших refactor/change batches.

<a id="алиасы"></a>
#### 🚀 Быстрые Алиасы (Power User)
Выполните `python3 run.py setup`, чтобы создать короткие команды:
*   `tg` — Запуск главного меню.
*   `tgr` — Репетиция очистки в dry-run.
*   `tgd` — Мгновенная очистка всех ваших сообщений.
*   `tgu` — Автоматическое обновление всей базы.
*   `tge ID` — Быстрый экспорт конкретного пользователя.
*   `tgpm ID` — Быстрый архив лички по user ID.
*   `tgrt [args]` — Быстрый доступ к `retry`.
*   `tgrp [args]` — Быстрый доступ к `report`.

---
---

<a id="english"></a>
## 🇬🇧 English

**TG_MSG_MNGR** is a high-performance ecosystem for managing your digital footprint on Telegram. The utility features a robust, "app-like" terminal interface focusing on UX, speed, and deterministic data integrity.

### Quick Reference

```bash
python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321 --depth 3 --json
python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321 --flat
python3 -m tg_msg_manager.cli db-export --user-id 123456789
python3 -m tg_msg_manager.cli export-pm --user-id 123456789
python3 -m tg_msg_manager.cli db-export --user-id 123456789 --json
python3 -m tg_msg_manager.cli export-channel --channel @example --limit 100 --media metadata
python3 -m tg_msg_manager.cli export-channel --channel @example --limit 10 --media metadata --discussion full --max-comments-per-post 100
python3 -m tg_msg_manager.cli update
python3 -m tg_msg_manager.cli retry --list
python3 -m tg_msg_manager.cli report
```

### 🚀 Quick Start

1. **Installation**:
   ```bash
   git clone https://github.com/JohnyNoxwell/tg-msg-manager.git
   cd tg-msg-manager
   pip install .
   ```

2. **Launch Interactive Menu**:
   *   **Method A (Fastest)**: From an interactive terminal in the project root:
       ```bash
       python3 run.py
       ```
   *   **Method B (After setup)**: Type `tg` anywhere in your terminal (see [Aliases](#aliases)).

3. **Navigation**: Use two-digit menu codes: **01-10** for primary actions, **11** for `retry`, **12** for `report`, **98** for language toggle, **00** for exit, and **ESC** to go back/cancel. Legacy short inputs `1-9`, `R`, `P`, `L`, and `0` are still accepted for compatibility.

---

### 🌟 Core Features

Core system capabilities:

* 🧹 **Global Cleanup (`clean`)** — Removes **your own** messages from all selected chats. Supports whitelists and safe Dry Run mode.
* 📥 **Deep Context Export (`export`)** — Automatically retrieves target messages along with the "surrounding" conversation window.
* 💬 **PM Archive (`export-pm`)** — Text backup for private conversations with a prepared folder structure for media.
* 🗄️ **SQLite Storage** — All messages are stored in a structured `messages.db` for instant querying and zero duplicates.
* 📤 **Database Export** — Export collected SQLite records into JSON or Text. JSONL now defaults to a compact AI-friendly profile.
* 📡 **Direct Channel Export (`export-channel`)** — Filesystem-first dataset export of Telegram channel posts into `manifest.json`, `messages.jsonl`, `messages.txt`, `media_manifest.jsonl`, and optional discussion dataset files when `--discussion full` is explicit.
* ♻️ **Retry Queue (`retry`)** — Replays recoverable sync/archive failures through typed retry tasks instead of manual DB surgery.
* 📋 **Audit Report (`report`)** — Read-only diagnostics for local DB state, retry backlog, export artifacts, and tracked-target health without Telegram access.

---

### 📚 Documentation

- Full documentation map: [`docs/README.md`](docs/README.md)
- Command reference: [`COMMANDS.md`](COMMANDS.md)
- Coding-agent contract: [`AGENTS.md`](AGENTS.md)

---

### 🛠️ Advanced Usage (CLI)

Subcommands can be executed directly for automation:

> ⚠️ **Note**: Full `python3 -m ...` commands must be executed from the project root.

*   **Message Export**: 
    `python3 -m tg_msg_manager.cli export --user-id 123456789 --depth 3`
    `python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321 --depth 3 --json`
    `python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321 --flat`
    `--json` writes a final JSONL snapshot after sync; without `--json`, the final export is TXT.
    Deep Mode defaults to `--depth 2` when no explicit depth is provided.
*   **Global Cleanup (Apply)**: 
    `python3 -m tg_msg_manager.cli clean --apply --yes`
*   **Universal Update**: 
    `python3 -m tg_msg_manager.cli update`
    After a large interrupted export, `update` may appear idle before per-target progress starts; during that phase the service is building a shared head prefetch slice for the chat.
*   **PM Archive**:
    `python3 -m tg_msg_manager.cli export-pm --user-id 123456789`
*   **DB Export**:
    `python3 -m tg_msg_manager.cli db-export --user-id 123456789`
    `python3 -m tg_msg_manager.cli db-export --user-id 123456789 --json`
    Without `--json`, the command writes TXT; with `--json`, it writes compact AI-friendly JSONL.
*   **Direct Channel Export**:
    `python3 -m tg_msg_manager.cli export-channel --channel @example --limit 100 --media metadata`
    `python3 -m tg_msg_manager.cli export-channel --channel @example --limit 10 --media metadata --discussion full --max-comments-per-post 100`
    The command writes a filesystem dataset under `exports/channels/`. Stage 3A/3A.1/3B/3C does not perform analytics and does not persist channel posts or discussion comments into SQLite.
    Only broadcast channels are supported; groups and supergroups are out of scope for `export-channel`.
    Successful runs create `channel_export_state.json`; later runs without `--force` append only newly discovered posts to the dataset.
    The safe default remains `--media metadata`.
    The discussion default is `--discussion none`; no discussion resolver runs and no discussion files are created in that mode.
    `--discussion full` writes `discussion_comments.jsonl`, `discussion_comments.txt`, `discussion_threads.jsonl`, and `discussion_export_state.json` only for posts fetched in the current run.
    Incremental runs export discussion comments only for new posts; no-new-posts runs do not refetch old threads or mutate `discussion_export_state.json`.
    Discussion comment media is metadata-only; full media download for discussion comments is not implemented.
    Full media download requires explicit `--media full`; it supports `--max-media-size` with a `50MB` default and `--media-types photo,video,...`.
    In `full` mode, `media_manifest.jsonl` records final statuses such as `downloaded`, `already_exists`, `skipped_by_size`, `skipped_by_type`, and `failed`.
*   **Full Local Purge**:
    `python3 -m tg_msg_manager.cli delete --user-id 123456789`
*   **Scheduler (macOS)**:
    `python3 -m tg_msg_manager.cli schedule`
*   **Retry Queue Replay**:
    `python3 -m tg_msg_manager.cli retry --list`
    `python3 -m tg_msg_manager.cli retry --limit 10`
    `python3 -m tg_msg_manager.cli retry --cleanup`
    `--list` prints the local retry queue, plain execution runs due tasks, and `--cleanup` removes terminal rows.
*   **Diagnostic Report**:
    `python3 -m tg_msg_manager.cli report`
    `python3 -m tg_msg_manager.cli report --json`
    The command is fully read-only and works from SQLite/filesystem state without Telegram credentials.
*   **Alias Setup**:
    `python3 -m tg_msg_manager.cli setup`

### ✅ Local Verification

```bash
pip install -e .[dev]
make lint
make format-check
make test
make verify
```

Offline regression harness:

```bash
python3 -m unittest tests.test_fixture_e2e -q
```

Minimal live smoke-check with the current Telegram session:

```bash
python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321 --flat --limit 1
```

### ⚙️ Configuration

The app reads settings from `config.json`, `TG_*` environment variables, `.env`, and init args.

Minimal example:

```json
{
  "api_id": 123456,
  "api_hash": "YOUR_API_HASH",
  "session_name": "tg_msg_manager",
  "db_path": "messages.db",
  "account_name": "Default Account",
  "whitelist_chats": [],
  "include_chats": [],
  "chats_to_search_user_msgs": [],
  "max_rps": 3.0,
  "log_level": "INFO",
  "lang": "ru"
}
```

Source precedence:
- init args;
- `TG_*` env vars;
- `config.json`;
- `.env`.

Supported legacy aliases:
- `exclude_chats` -> `whitelist_chats`
- `language` / `ui_language` -> `lang`

### Known Limitations

* `--limit` caps work inside a single `sync_chat`; when exporting a user across multiple dialogs, the cap applies per dialog.
* `export-pm` produces a text-and-media archive, not a full Telegram-native replayable backup.
* `export-channel` in Stage 3A/3A.1/3B/3C is a filesystem-first dataset projection pipeline; channel posts and discussion comments are not written to SQLite, and analytics are not performed.
* The safe default for `export-channel` remains `--media metadata`; `--media full` works only when requested explicitly and runs through size/type guardrails.
* Discussion export is disabled by default with `--discussion none`; `--discussion full` exports only threads for posts fetched in the current run.
* Old discussion threads are not refreshed/backfilled without `--force`; reply-tree reconstruction is not implemented beyond preserving `reply_to_id`.
* Full media download for discussion comments is not implemented.
* `export-channel` now uses filesystem state plus append-only incremental updates for new posts, but it does not yet roll back already appended payload files if a run fails mid-write.
* Switching an existing metadata-only dataset to `--media full` without `--force` downloads media only for newly fetched posts in that run; historical backfill for old rows still requires a full re-export.
* SQLite background writing is still most sensitive during very large deep-export passes; the current optimization focus is batched service-level writes.
* The built-in `schedule` command currently targets macOS `launchd`.
* `db-export --json` no longer includes the full `raw_payload` by default; a future explicit full-export profile would be needed for raw Telethon dumps.
* After an interrupted `export/tge`, `update/tgu` may have a noticeable preparation pause before the first visible per-target progress if the service needs to rebuild a large shared chat-head slice.
* `retry` currently covers only typed recoverable tasks (`sync_target`, `archive_pm`); it is not a general-purpose task queue.
* `report` is an operational read-only diagnostic surface, not an analytics layer with keyword/topic or graph intelligence.

### 🧪 Fixture-Based E2E

Since foundation stages `3`–`5`, the repo ships an autonomous offline harness:
- `tests/fixtures/stage5/*.jsonl` — anonymized Telegram-like fixtures;
- `tg_msg_manager/testing/` — `FakeTelegramClient`, fixture loaders, and temporary runtime helpers;
- `tests/test_fixture_e2e.py` — end-to-end coverage for `sync`, `context`, `db-export`, `retry`, and `report`.

This harness requires no network access and acts as the regression baseline for future refactor and feature batches.

<a id="aliases"></a>
#### 🚀 Power User Aliases
Run `python3 run.py setup` to register short commands:
*   `tg` — Launch the main menu.
*   `tgr` — Dry-run cleanup rehearsal.
*   `tgd` — Instantly scan and delete your messages.
*   `tgu` — Progressively update all tracked targets.
*   `tge ID` — Quick export for a specific user.
*   `tgpm ID` — Quick PM archive by user ID.
*   `tgrt [args]` — Quick access to `retry`.
*   `tgrp [args]` — Quick access to `report`.
