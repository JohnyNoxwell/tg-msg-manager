# TG_MSG_MNGR: Local Telegram Export/Data CLI

[🇷🇺 Русская версия](#русский) | [🇬🇧 English Version](#english)

---

<a id="русский"></a>
## 🇷🇺 Русский

**TG_MSG_MNGR** — это локальная CLI-утилита и data pipeline для Telegram exports, SQLite-backed sync, очистки собственных сообщений, channel datasets и read-only validation.

Проект не является SaaS-мониторингом, analytics/OSINT-платформой, системой
профилирования или GUI dashboard.

### Quick Reference

```bash
python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321 --depth 3 --json
python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321 --flat
python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321 --txt-profile legacy
python3 -m tg_msg_manager.cli db-export --user-id 123456789
python3 -m tg_msg_manager.cli export-pm --user-id 123456789
python3 -m tg_msg_manager.cli db-export --user-id 123456789 --json
python3 -m tg_msg_manager.cli export-channel --channel @example --limit 100 --media metadata
python3 -m tg_msg_manager.cli export-channel --channel @example --limit 10 --media metadata --discussion full --max-comments-per-post 100
python3 -m tg_msg_manager.cli validate-dataset --path exports/channels/example
python3 -m tg_msg_manager.cli inspect-dataset --path exports/channels/example
python3 -m tg_msg_manager.cli target names 123456789
python3 -m tg_msg_manager.cli update
python3 -m tg_msg_manager.cli retry --list
python3 -m tg_msg_manager.cli report
```

### Документация

- Быстрый путь первого запуска: [`docs/user/QUICKSTART.md`](docs/user/QUICKSTART.md)
- Примеры dataset doctor output: [`docs/user/DATASET_DOCTOR_EXAMPLES.md`](docs/user/DATASET_DOCTOR_EXAMPLES.md)
- Полная карта документации: [`docs/README.md`](docs/README.md)
- Справочник команд: [`COMMANDS.md`](COMMANDS.md)
- Privacy / sensitive artifacts: [`docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`](docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md)
- Operational risks / local limits: [`docs/development/OPERATIONAL_RISKS_AND_LIMITS.md`](docs/development/OPERATIONAL_RISKS_AND_LIMITS.md)
- Package identity / version policy: [`docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`](docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md)
- Правила для coding agents: [`AGENTS.md`](AGENTS.md)

### 🚀 Быстрый старт

#### Рекомендуется: установка из PyPI

macOS / Linux:

```bash
python3 -m pip install tg-msg-manager
tg-msg-manager
```

Windows PowerShell:

```powershell
py -m pip install tg-msg-manager
tg-msg-manager
```

#### Установка последней версии из репозитория

```bash
git clone https://github.com/JohnyNoxwell/tg-msg-manager.git
cd tg-msg-manager
python3 -m pip install .
tg-msg-manager
```

В Windows замените `python3` на `py`.

#### Установка для разработки

```bash
git clone https://github.com/JohnyNoxwell/tg-msg-manager.git
cd tg-msg-manager
python3 -m pip install -e ".[dev]"
```

#### Обновление PyPI-версии

```bash
python3 -m pip install --upgrade tg-msg-manager
```

В Windows замените `python3` на `py`.

После установки доступен console script `tg-msg-manager`. При первом запуске
он автоматически создаёт безопасный базовый `config.json` в рабочей директории.
Укажите в нём свои `api_id` и `api_hash`. Пошаговая настройка:
[`docs/user/QUICKSTART.md`](docs/user/QUICKSTART.md).

Рабочая директория создаётся автоматически:

- macOS / Linux: `~/TG_MSG_MANAGER`
- Windows: `%USERPROFILE%\TG_MSG_MANAGER`

Запустите интерактивное меню командой `tg-msg-manager`. Используйте двузначные
коды меню: **01-10** для основных функций, **11** для `retry`, **12** для
`report`, **98** — переключение языка, **00** — выход, **ESC** — возврат назад.

---

### 🌟 Основные функции

Основные возможности проекта:

* 🧹 **Глобальная очистка (`clean`)** — Удаляет **только ваши** сообщения из всех выбранных чатов. Поддерживает фильтры и безопасный режим (Dry Run).
* 📥 **Умный экспорт с контекстом (`export`)** — Собирает сообщения цели вместе с окружающим контекстом беседы, восстанавливая полную картину диалога.
* 💬 **Архив лички (`export-pm`)** — Текстовый бэкап приватного чата с подготовленной структурой папок под медиа; отдельный public contract для private archive пока deferred.
* 🗄️ **SQLite База данных** — Все данные хранятся в структурированной базе `messages.db`. Это обеспечивает мгновенный поиск и отсутствие дубликатов.
* 📤 **Экспорт из БД** — Выгрузка накопленных данных из SQLite в JSON/Text. JSONL по умолчанию теперь компактный и ориентирован на анализ нейросетью.
* 📡 **Прямой экспорт канала (`export-channel`)** — Файловый dataset export постов Telegram-канала в `manifest.json`, `messages.jsonl`, `messages.txt`, `media_manifest.jsonl`, `run_changelog.jsonl` и, при явном `--discussion full`, discussion dataset files.
* ✅ **Dataset validation / inspection** — `validate-dataset` проверяет структуру channel dataset, `inspect-dataset` показывает deterministic counts/statuses, а `inspect-dataset --doctor` даёт read-only diagnostic findings без Telegram access, repair/migration или analytics.
* ♻️ **Retry Queue (`retry`)** — Управление повторными задачами для recoverable sync/archive ошибок без ручного вмешательства в БД.
* 📋 **Audit Report (`report`)** — Read-only диагностика локальной БД, retry-очереди, export artifacts и состояния tracked targets без доступа к Telegram.

---

### 🛠️ Продвинутое использование (CLI)

Для автоматизации и опытных пользователей доступны прямые команды:

> ⚠️ **Примечание**: В source checkout сначала выполните установку выше.
> После установки используйте `tg-msg-manager ...` или
> `python3 -m tg_msg_manager.cli ...` из активного Python-окружения.

*   **Экспорт сообщений**: 
    `python3 -m tg_msg_manager.cli export --user-id 123456789 --depth 3`
    `python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321 --depth 3 --json`
    `python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321 --flat`
    `python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321 --txt-profile legacy`
    `--json` собирает итоговый JSONL-файл после синка; без `--json` итоговый файл будет TXT. TXT-профиль по умолчанию для `export` — `context-readable`: он группирует вывод в `CONTEXT BLOCK` с секциями `[REPLIED MESSAGE]`, `[CONTEXT BEFORE]`, `[TARGET MESSAGE]` / `[TARGET MESSAGES]`, `[CONTEXT AFTER]`. `--txt-profile legacy` сохраняет старый плоский log-style TXT. TXT — только projection; JSONL/SQLite остаются canonical data.
    По умолчанию Deep Mode использует `--depth 2`, если глубина явно не указана.
*   **Очистка (Боевой режим)**: 
    `python3 -m tg_msg_manager.cli clean --apply --yes`
*   **Обновление всех целей**: 
    `python3 -m tg_msg_manager.cli update`
    После прерванного большого экспорта `update` может некоторое время выглядеть "задумавшимся" до появления построчного прогресса: в этот момент сервис делает shared head prefetch для чата и готовит общий HEAD-срез для нескольких целей.
*   **Архив лички**:
    `python3 -m tg_msg_manager.cli export-pm --user-id 123456789`
    `export-pm` остается отдельным archive workflow: он не входит в Non-Channel Export Contract V1 для `export` / `db-export`, а private archive contract пока deferred.
*   **Экспорт из БД**:
    `python3 -m tg_msg_manager.cli db-export --user-id 123456789`
    `python3 -m tg_msg_manager.cli db-export --user-id 123456789 --txt-profile legacy`
    `python3 -m tg_msg_manager.cli db-export --user-id 123456789 --json`
    Без `--json` команда пишет TXT; с `--json` — компактный AI-friendly JSONL. TXT-профиль по умолчанию — `context-readable`; `--txt-profile legacy` сохраняет старый плоский формат.
*   **Прямой экспорт канала**:
    `python3 -m tg_msg_manager.cli export-channel --channel @example --limit 100 --media metadata`
    `python3 -m tg_msg_manager.cli export-channel --channel @example --limit 10 --media metadata --discussion full --max-comments-per-post 100`
    Команда создаёт файловый dataset в `exports/channels/`. Stage 3A/3A.1/3B/3C не делает analytics и не пишет channel posts или discussion comments в SQLite.
    Поддерживаются только broadcast-каналы; группы и супергруппы не входят в `export-channel`.
    После успешного запуска создаётся `channel_export_state.json`; повторный запуск без `--force` экспортирует только новые посты и дописывает dataset через temp-file copy/append/replace.
    По умолчанию используется безопасный режим `--media metadata`.
    По умолчанию `--discussion none`: resolver обсуждений не запускается, комментарии не скачиваются и discussion files не создаются.
    `--discussion metadata` пишет компактный `discussion_metadata.jsonl` из `raw_payload.replies` и не скачивает комментарии.
    `--discussion full` — явный heavy mode: пишет `discussion_comments.jsonl`, `discussion_comments.txt`, `discussion_threads.jsonl` и `discussion_export_state.json` только для постов, полученных в текущем run. Для больших каналов он может создать миллионы records и multi-gigabyte datasets; для broad archives используйте `metadata`.
    Discussion resolver использует linked discussion metadata канала и fallback из Telegram metadata конкретного поста (`raw_payload.replies.channel_id`), если channel-level link недоступен.
    Инкрементальный запуск экспортирует discussion comments только для новых постов; no-new-posts run не перечитывает старые threads и не меняет `discussion_export_state.json`.
    Если старый dataset уже был создан без discussion comments, перезапустите экспорт с `--force --discussion full` или в чистую output directory, чтобы перечитать старые threads.
    Для discussion comments не выполняется full media download, только metadata/empty media fields.
    Полная загрузка media требует явного `--media full`; для неё доступны `--max-media-size 50MB` по умолчанию и `--media-types photo,video,...`.
    Имена media-файлов и итоговые media-подпапки выбираются из безопасного Telegram original filename, затем MIME type, затем лёгких magic bytes; `.bin` остаётся fallback только для неизвестного типа.
    `media_manifest.jsonl` фиксирует итоговый путь media. OCR, speech-to-text, media analysis, transcoding и ffmpeg processing не выполняются.
    В `full` режиме `media_manifest.jsonl` фиксирует итоговые статусы `downloaded`, `already_exists`, `skipped_by_size`, `skipped_by_type` и `failed`.
    `run_changelog.jsonl` получает одну строку на каждый завершенный запуск с предыдущим/новым cursor, run mode, списком новых message IDs и artifact paths; no-new-posts run пишет строку с `new_message_count: 0`.
    Интерактивный пункт меню `10` теперь запрашивает discussion mode, max comments per post, force, output directory, max media size и media types; пустой ввод сохраняет defaults прямой CLI-команды.
*   **Проверка / инспекция channel dataset**:
    `python3 -m tg_msg_manager.cli validate-dataset --path exports/channels/example`
    `python3 -m tg_msg_manager.cli validate-dataset --path exports/channels/example --json`
    `python3 -m tg_msg_manager.cli inspect-dataset --path exports/channels/example`
    `python3 -m tg_msg_manager.cli inspect-dataset --path exports/channels/example --json`
    `python3 -m tg_msg_manager.cli inspect-dataset --path exports/channels/example --doctor`
    Команды read-only, не требуют Telegram credentials, не чинят и не мигрируют dataset, не выполняют analytics/OCR/STT/media processing. Doctor mode добавляет severity, artifact path и suggested next action для validation findings.
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
*   **Локальная история имён цели**:
    `python3 -m tg_msg_manager.cli target names 123456789`
    `python3 -m tg_msg_manager.cli target names 123456789 --field username --format json`
    Команда читает только локальные SQLite metadata, не подключается к Telegram
    и не выполняет identity/profiling/OSINT-анализ.
*   **Установка алиасов**:
    `python3 -m tg_msg_manager.cli setup`

### ✅ Локальная проверка

```bash
pip install -e .[dev]
make lint
make format-check
make test
make verify
make pre-commit
```

Перед коммитом запускайте `make pre-commit`: он применяет `ruff format`, затем выполняет полный `make verify`.

Offline regression harness:

```bash
python3 -m unittest tests.e2e.test_fixture_e2e -q
```

Минимальный smoke-check с текущей Telegram-сессией:

```bash
python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321 --flat --limit 1
```

### ⚙️ Конфигурация

После установки из PyPI приложение использует постоянный рабочий каталог
`~/TG_MSG_MANAGER`. При первом запуске автоматически создаются каталоги для
базы, логов и экспортов. Путь можно переопределить через `TG_HOME`.

Приложение читает настройки из `~/TG_MSG_MANAGER/config.json`, переменных
окружения `TG_*`, `.env` и init args. Относительные пути базы и Telegram-сессии
разрешаются внутри рабочего каталога, а не внутри текущей директории shell.

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
* `export-pm` пишет текстовый лог и медиа-структуру, но не восстанавливает Telegram-специфичные сущности как полноценный replay архива; private archive contract пока deferred и не входит в user/group `export` + `db-export` contract.
* `export-channel` в Stage 3A/3A.1/3B/3C является filesystem-first dataset projection pipeline: channel posts и discussion comments не пишутся в SQLite, analytics не выполняется.
* `validate-dataset` и `inspect-dataset` проверяют только структуру, deterministic counts/statuses и связи файлов; validation также предупреждает о message-id gaps, missing reply parents и media linkage drift, но не анализирует содержание сообщений и не проверяет SHA-256 media по умолчанию.
* Безопасный режим по умолчанию для `export-channel` — `--media metadata`; `--media full` работает только при явном указании и использует size/type guardrails.
* Discussion export выключен по умолчанию через `--discussion none`; `--discussion metadata` сохраняет только компактный `discussion_metadata.jsonl`, а `--discussion full` экспортирует comments/threads только для постов текущего run и является heavy mode для малых scoped runs.
* Discussion resolver сначала использует linked discussion metadata канала, затем fallback из Telegram metadata поста (`raw_payload.replies.channel_id`), если channel-level link недоступен.
* Старые discussion threads не refresh/backfill без `--force`; reply-tree reconstruction не выполняется, сохраняется только `reply_to_id`.
* Full media download для discussion comments не реализован.
* `export-channel` использует файловый `channel_export_state.json`; channel/discussion payload writes проходят через temp-file replace, поэтому сбой write-session не дописывает частичные rows в финальные payload files. Это не полноценная multi-file ACID-транзакция и не откатывает уже скачанные media files.
* Переключение существующего metadata-only dataset на `--media full` без `--force` скачивает media только для новых постов текущего run; исторический backfill старых rows по-прежнему требует full re-export.
* Фоновая запись в SQLite остаётся чувствительной к очень большим deep-export проходам; основная оптимизация сейчас сделана на уровне пакетных сервисных вызовов.
* Планировщик `schedule` сейчас ориентирован на macOS `launchd`.
* `db-export --json` по умолчанию не включает полный `raw_payload`; если когда-нибудь понадобится полный Telethon-слепок, это потребует отдельного full-профиля экспорта.
* `context-readable` меняет только TXT-представление user/group export. Он не меняет Telegram fetching, context extraction, JSONL schema, dataset/state schema или SQLite schema; missing replies отображаются компактно как `↪ missing reply #id`.
* После прерванного `export/tge` команда `update/tgu` может иметь заметную подготовительную паузу перед первым видимым прогрессом, если системе нужно переиспользовать большой общий HEAD-срез чата.
* `retry` покрывает только типизированные recoverable tasks (`sync_target`, `archive_pm`); это не произвольная универсальная очередь задач.
* `report` — диагностический read-only срез состояния системы, а не аналитический слой с keyword/topic или graph intelligence.

### 🧪 Fixture-Based E2E

Начиная с foundation stages `3`–`5`, в репо есть автономная offline harness:
- `tests/fixtures/stage5/*.jsonl` — anonymized Telegram-like fixtures;
- `tg_msg_manager/testing/` — `FakeTelegramClient`, fixture loaders, temp runtime helpers;
- `tests/e2e/test_fixture_e2e.py` — end-to-end покрытие для `sync`, `context`, `db-export`, `retry`, `report`.

Эта harness не требует сети и используется как regression-опора для дальнейших refactor/change batches.

### License

MIT License. See [LICENSE](LICENSE).

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

**TG_MSG_MNGR** is a local CLI utility and data pipeline for Telegram exports, SQLite-backed sync, self-message cleanup, channel datasets, and read-only validation.

It is not a SaaS monitoring, analytics/OSINT, profiling, or GUI dashboard
platform.

### Quick Reference

```bash
python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321 --depth 3 --json
python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321 --flat
python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321 --txt-profile legacy
python3 -m tg_msg_manager.cli db-export --user-id 123456789
python3 -m tg_msg_manager.cli export-pm --user-id 123456789
python3 -m tg_msg_manager.cli db-export --user-id 123456789 --json
python3 -m tg_msg_manager.cli export-channel --channel @example --limit 100 --media metadata
python3 -m tg_msg_manager.cli export-channel --channel @example --limit 10 --media metadata --discussion full --max-comments-per-post 100
python3 -m tg_msg_manager.cli validate-dataset --path exports/channels/example
python3 -m tg_msg_manager.cli inspect-dataset --path exports/channels/example
python3 -m tg_msg_manager.cli target names 123456789
python3 -m tg_msg_manager.cli update
python3 -m tg_msg_manager.cli retry --list
python3 -m tg_msg_manager.cli report
```

### 🚀 Quick Start

#### Recommended: install from PyPI

macOS / Linux:

```bash
python3 -m pip install tg-msg-manager
tg-msg-manager
```

Windows PowerShell:

```powershell
py -m pip install tg-msg-manager
tg-msg-manager
```

#### Install the latest source from the repository

```bash
git clone https://github.com/JohnyNoxwell/tg-msg-manager.git
cd tg-msg-manager
python3 -m pip install .
tg-msg-manager
```

On Windows, replace `python3` with `py`.

#### Development installation

```bash
git clone https://github.com/JohnyNoxwell/tg-msg-manager.git
cd tg-msg-manager
python3 -m pip install -e ".[dev]"
```

#### Upgrade the PyPI installation

```bash
python3 -m pip install --upgrade tg-msg-manager
```

On Windows, replace `python3` with `py`.

The installed console script is `tg-msg-manager`. On first run it automatically
creates a safe base `config.json` in the working directory. Set your `api_id`
and `api_hash` there. See the step-by-step guide:
[`docs/user/QUICKSTART.md`](docs/user/QUICKSTART.md).

The working directory is created automatically:

- macOS / Linux: `~/TG_MSG_MANAGER`
- Windows: `%USERPROFILE%\TG_MSG_MANAGER`

Launch the interactive menu with `tg-msg-manager`. Use two-digit menu codes:
**01-10** for primary actions, **11** for `retry`, **12** for `report`, **98**
for language toggle, **00** for exit, and **ESC** to go back.

---

### 🌟 Core Features

Core system capabilities:

* 🧹 **Global Cleanup (`clean`)** — Removes **your own** messages from all selected chats. Supports whitelists and safe Dry Run mode.
* 📥 **Deep Context Export (`export`)** — Automatically retrieves target messages along with the "surrounding" conversation window.
* 💬 **PM Archive (`export-pm`)** — Text backup for private conversations with a prepared folder structure for media; a separate public private-archive contract is still deferred.
* 🗄️ **SQLite Storage** — All messages are stored in a structured `messages.db` for instant querying and zero duplicates.
* 📤 **Database Export** — Export collected SQLite records into JSON or Text. JSONL now defaults to a compact AI-friendly profile.
* 📡 **Direct Channel Export (`export-channel`)** — Filesystem-first dataset export of Telegram channel posts into `manifest.json`, `messages.jsonl`, `messages.txt`, `media_manifest.jsonl`, `run_changelog.jsonl`, and optional discussion dataset files when `--discussion full` is explicit.
* ✅ **Dataset Validation / Inspection** — `validate-dataset` checks channel dataset structure, `inspect-dataset` reports deterministic counts/statuses, and `inspect-dataset --doctor` emits read-only diagnostic findings without Telegram access, repair/migration, or analytics.
* ♻️ **Retry Queue (`retry`)** — Replays recoverable sync/archive failures through typed retry tasks instead of manual DB surgery.
* 📋 **Audit Report (`report`)** — Read-only diagnostics for local DB state, retry backlog, export artifacts, and tracked-target health without Telegram access.

---

### 📚 Documentation

- First-run navigation: [`docs/user/QUICKSTART.md`](docs/user/QUICKSTART.md)
- Dataset doctor output examples: [`docs/user/DATASET_DOCTOR_EXAMPLES.md`](docs/user/DATASET_DOCTOR_EXAMPLES.md)
- Full documentation map: [`docs/README.md`](docs/README.md)
- Command reference: [`COMMANDS.md`](COMMANDS.md)
- Privacy / sensitive artifacts: [`docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`](docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md)
- Operational risks / local limits: [`docs/development/OPERATIONAL_RISKS_AND_LIMITS.md`](docs/development/OPERATIONAL_RISKS_AND_LIMITS.md)
- Package identity / version policy: [`docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`](docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md)
- Coding-agent contract: [`AGENTS.md`](AGENTS.md)

---

### 🛠️ Advanced Usage (CLI)

Subcommands can be executed directly for automation:

> ⚠️ **Note**: In a source checkout, complete the installation step above first.
> After installation, use `tg-msg-manager ...` or
> `python3 -m tg_msg_manager.cli ...` from the active Python environment.

*   **Message Export**: 
    `python3 -m tg_msg_manager.cli export --user-id 123456789 --depth 3`
    `python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321 --depth 3 --json`
    `python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321 --flat`
    `python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321 --txt-profile legacy`
    `--json` writes a final JSONL snapshot after sync; without `--json`, the final export is TXT. The default TXT profile for `export` is `context-readable`: it groups output into `CONTEXT BLOCK` sections with `[REPLIED MESSAGE]`, `[CONTEXT BEFORE]`, `[TARGET MESSAGE]` / `[TARGET MESSAGES]`, and `[CONTEXT AFTER]`. Use `--txt-profile legacy` for the old flat log-style TXT. TXT is a projection only; JSONL/SQLite records remain canonical.
    Deep Mode defaults to `--depth 2` when no explicit depth is provided.
*   **Global Cleanup (Apply)**: 
    `python3 -m tg_msg_manager.cli clean --apply --yes`
*   **Universal Update**: 
    `python3 -m tg_msg_manager.cli update`
    After a large interrupted export, `update` may appear idle before per-target progress starts; during that phase the service is building a shared head prefetch slice for the chat.
*   **PM Archive**:
    `python3 -m tg_msg_manager.cli export-pm --user-id 123456789`
    `export-pm` remains a separate archive workflow: it is not part of Non-Channel Export Contract V1 for `export` / `db-export`, and the private archive contract remains deferred.
*   **DB Export**:
    `python3 -m tg_msg_manager.cli db-export --user-id 123456789`
    `python3 -m tg_msg_manager.cli db-export --user-id 123456789 --txt-profile legacy`
    `python3 -m tg_msg_manager.cli db-export --user-id 123456789 --json`
    Without `--json`, the command writes TXT; with `--json`, it writes compact AI-friendly JSONL. The default TXT profile is `context-readable`; `--txt-profile legacy` keeps the old flat format.
*   **Direct Channel Export**:
    `python3 -m tg_msg_manager.cli export-channel --channel @example --limit 100 --media metadata`
    `python3 -m tg_msg_manager.cli export-channel --channel @example --limit 10 --media metadata --discussion full --max-comments-per-post 100`
    The command writes a filesystem dataset under `exports/channels/`. Stage 3A/3A.1/3B/3C does not perform analytics and does not persist channel posts or discussion comments into SQLite.
    Only broadcast channels are supported; groups and supergroups are out of scope for `export-channel`.
    Successful runs create `channel_export_state.json`; later runs without `--force` append only newly discovered posts through temp-file copy/append/replace.
    The safe default remains `--media metadata`.
    The discussion default is `--discussion none`; no discussion resolver runs, no comments are fetched, and no discussion files are created in that mode.
    `--discussion metadata` writes compact `discussion_metadata.jsonl` records from `raw_payload.replies` and does not fetch comments.
    `--discussion full` is explicit heavy mode: it writes `discussion_comments.jsonl`, `discussion_comments.txt`, `discussion_threads.jsonl`, and `discussion_export_state.json` only for posts fetched in the current run. For large channels it can produce millions of records and multi-gigabyte datasets; use `metadata` for broad archives.
    The discussion resolver uses channel linked-discussion metadata and falls back to per-post Telegram metadata (`raw_payload.replies.channel_id`) when the channel-level link is unavailable.
    Incremental runs export discussion comments only for new posts; no-new-posts runs do not refetch old threads or mutate `discussion_export_state.json`.
    If an existing dataset was created without discussion comments, rerun with `--force --discussion full` or use a clean output directory to reprocess old threads.
    Discussion comment media is metadata-only; full media download for discussion comments is not implemented.
    Full media download requires explicit `--media full`; it supports `--max-media-size` with a `50MB` default and `--media-types photo,video,...`.
    Media filenames and final media subdirectories are resolved from a safe Telegram original filename, then MIME type, then lightweight magic bytes; `.bin` remains the fallback only for unknown types.
    `media_manifest.jsonl` records the final media path. OCR, speech-to-text, media analysis, transcoding, and ffmpeg processing are not performed.
    In `full` mode, `media_manifest.jsonl` records final statuses such as `downloaded`, `already_exists`, `skipped_by_size`, `skipped_by_type`, and `failed`.
    `run_changelog.jsonl` gets one row per completed run with previous/new cursor, run mode, new message IDs, and artifact paths; no-new-posts runs write a row with `new_message_count: 0`.
    Interactive menu item `10` now prompts for discussion mode, max comments per post, force, output directory, max media size, and media types; empty input preserves the direct CLI defaults.
*   **Channel Dataset Validation / Inspection**:
    `python3 -m tg_msg_manager.cli validate-dataset --path exports/channels/example`
    `python3 -m tg_msg_manager.cli validate-dataset --path exports/channels/example --json`
    `python3 -m tg_msg_manager.cli inspect-dataset --path exports/channels/example`
    `python3 -m tg_msg_manager.cli inspect-dataset --path exports/channels/example --json`
    `python3 -m tg_msg_manager.cli inspect-dataset --path exports/channels/example --doctor`
    These commands are read-only, require no Telegram credentials, do not repair or migrate datasets, and do not perform analytics/OCR/STT/media processing. Doctor mode adds severity, artifact path, and suggested next action for validation findings.
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
*   **Local Target Name History**:
    `python3 -m tg_msg_manager.cli target names 123456789`
    `python3 -m tg_msg_manager.cli target names 123456789 --field username --format json`
    The command reads local SQLite metadata only, does not connect to Telegram,
    and does not perform identity, profiling, or OSINT analysis.
*   **Alias Setup**:
    `python3 -m tg_msg_manager.cli setup`

### ✅ Local Verification

```bash
pip install -e .[dev]
make lint
make format-check
make test
make verify
make pre-commit
```

Before committing, run `make pre-commit`: it applies `ruff format`, then runs the full `make verify`.

Offline regression harness:

```bash
python3 -m unittest tests.e2e.test_fixture_e2e -q
```

Minimal live smoke-check with the current Telegram session:

```bash
python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321 --flat --limit 1
```

### ⚙️ Configuration

After installation from PyPI, the app uses `~/TG_MSG_MANAGER` as its stable
working directory. Database, log, and export directories are created
automatically on first run. Override the location with `TG_HOME`.

The app reads settings from `~/TG_MSG_MANAGER/config.json`, `TG_*` environment
variables, `.env`, and init args. Relative database and Telegram session paths
are resolved inside the working directory instead of the shell's current
directory.

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
* `export-pm` produces a text-and-media archive, not a full Telegram-native replayable backup; its private archive contract remains deferred and is not part of the user/group `export` + `db-export` contract.
* `export-channel` in Stage 3A/3A.1/3B/3C is a filesystem-first dataset projection pipeline; channel posts and discussion comments are not written to SQLite, and analytics are not performed.
* `validate-dataset` and `inspect-dataset` check only structure, deterministic counts/statuses, and file relationships; validation also warns about message-id gaps, missing reply parents, and media linkage drift, but does not analyze message content or verify media SHA-256 by default.
* The safe default for `export-channel` remains `--media metadata`; `--media full` works only when requested explicitly and runs through size/type guardrails.
* Discussion export is disabled by default with `--discussion none`; `--discussion metadata` saves only compact `discussion_metadata.jsonl`, while `--discussion full` exports comments/threads only for posts fetched in the current run and is heavy mode for small scoped runs.
* Discussion resolution uses channel linked-discussion metadata first, then per-post Telegram metadata (`raw_payload.replies.channel_id`) when the channel-level link is unavailable.
* Old discussion threads are not refreshed/backfilled without `--force`; reply-tree reconstruction is not implemented beyond preserving `reply_to_id`.
* Full media download for discussion comments is not implemented.
* `export-channel` uses filesystem state; channel/discussion payload writes go through temp-file replace, so write-session failures do not append partial rows to final payload files. This is not a full multi-file ACID transaction and does not roll back media files already downloaded.
* Switching an existing metadata-only dataset to `--media full` without `--force` downloads media only for newly fetched posts in that run; historical backfill for old rows still requires a full re-export.
* SQLite background writing is still most sensitive during very large deep-export passes; the current optimization focus is batched service-level writes.
* The built-in `schedule` command currently targets macOS `launchd`.
* `db-export --json` no longer includes the full `raw_payload` by default; a future explicit full-export profile would be needed for raw Telethon dumps.
* `context-readable` changes only the user/group export TXT projection. It does not change Telegram fetching, context extraction, JSONL schema, dataset/state schema, or SQLite schema; missing replies render compactly as `↪ missing reply #id`.
* After an interrupted `export/tge`, `update/tgu` may have a noticeable preparation pause before the first visible per-target progress if the service needs to rebuild a large shared chat-head slice.
* `retry` currently covers only typed recoverable tasks (`sync_target`, `archive_pm`); it is not a general-purpose task queue.
* `report` is an operational read-only diagnostic surface, not an analytics layer with keyword/topic or graph intelligence.

### 🧪 Fixture-Based E2E

Since foundation stages `3`–`5`, the repo ships an autonomous offline harness:
- `tests/fixtures/stage5/*.jsonl` — anonymized Telegram-like fixtures;
- `tg_msg_manager/testing/` — `FakeTelegramClient`, fixture loaders, and temporary runtime helpers;
- `tests/e2e/test_fixture_e2e.py` — end-to-end coverage for `sync`, `context`, `db-export`, `retry`, and `report`.

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
