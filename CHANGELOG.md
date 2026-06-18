All notable changes to this project will be documented in this file in both English and Russian.
Все значимые изменения проекта фиксируются в этом файле на английском и русском языках.

Note: This changelog tracks public package semantic-version releases for `tg-msg-manager`. Older internal/stage-numbered `4.x` and `3.x` history was moved to [`docs/archive/legacy_notes/PRE_PACKAGE_INTERNAL_CHANGELOG_4X.md`](docs/archive/legacy_notes/PRE_PACKAGE_INTERNAL_CHANGELOG_4X.md); those entries are historical project notes, not package releases.

## [Unreleased]

### Fixed (EN)
- **Direct Export Exit Codes**: Direct `export` and `export-pm` commands now exit non-zero when the current network/archive operation fails, while preserving existing error logging and PM retry enqueue behavior.
- **FloodWait retry hardening**: Telegram `get_messages()` and `download_media()` FloodWait handling now uses bounded iterative retries instead of unlimited recursion, preserving throttling and request arguments.
- **Throttler rate recovery**: Telegram request throttling now gradually recovers toward the configured starting RPS after FloodWait slowdown instead of staying permanently reduced for the rest of a long run.
- **SQLite writer flush reliability**: Background writer batch commit failures now unblock `flush()` and surface the failed write instead of leaving the write queue join waiting forever.

### Added (EN)
- **Stage 6A Application Runtime Boundary**: Added `tg_msg_manager.application` runtime assembly with `ApplicationSession`, `RuntimeResourceFactory`, and `create_service_bundle` as stable non-CLI entrypoints, including `needs_client=False` support for headless local runtime setup.

### Changed (EN)
- **CLI Runtime Assembly**: `CLIContext` now delegates process, storage, Telegram client, and service lifecycle wiring to `ApplicationSession` while preserving existing CLI behavior and lifecycle messages.
- **Architecture Guardrails**: Added static boundary coverage and docs for the application runtime layer so CLI modules remain adapters and non-CLI integrations do not import CLI runtime code.

### Добавлено (RU)
- **Stage 6A application runtime boundary**: Добавлен runtime assembly слой `tg_msg_manager.application` со стабильными non-CLI entrypoints `ApplicationSession`, `RuntimeResourceFactory` и `create_service_bundle`, включая `needs_client=False` для headless local runtime setup.

### Изменения (RU)
- **CLI runtime assembly**: `CLIContext` теперь делегирует wiring process, storage, Telegram client и service lifecycle в `ApplicationSession`, сохраняя существующее CLI behavior и lifecycle messages.
- **Architecture guardrails**: Добавлены static boundary tests и docs для application runtime layer, чтобы CLI modules оставались adapters, а non-CLI integrations не импортировали CLI runtime code.

### Исправлено (RU)
- **Exit codes прямого export**: Прямые команды `export` и `export-pm` теперь завершаются с ненулевым кодом, если текущая network/archive операция падает; существующее error logging и enqueue retry для PM сохранены.
- **Защита FloodWait retry**: Обработка FloodWait в Telegram `get_messages()` и `download_media()` теперь использует ограниченные итеративные повторы вместо бесконечной рекурсии, сохраняя throttling и аргументы запроса.
- **Восстановление скорости throttler**: Telegram request throttling теперь постепенно восстанавливается к настроенному начальному RPS после FloodWait slowdown, а не остаётся навсегда замедленным до конца долгого run.
- **Надёжность flush в SQLite writer**: Ошибки batch commit в background writer теперь разблокируют `flush()` и возвращают ошибку записи вместо вечного ожидания write queue join.

## [0.1.2] - 2026-06-11

### Fixed (EN)
- **First-run configuration**: The CLI now creates a safe base `config.json` in the application working directory when it is missing, never overwrites an existing config, and clearly asks for Telegram API credentials before network commands.

### Исправлено (RU)
- **Конфигурация первого запуска**: CLI теперь создаёт безопасный базовый `config.json` в рабочей директории приложения, если файл отсутствует, никогда не перезаписывает существующий конфиг и явно просит указать Telegram API credentials перед сетевыми командами.

## [0.1.1] - 2026-06-11

### Changed (EN)
- **Stable PyPI Runtime Home**: Installed CLI runs now use the visible `~/TG_MSG_MANAGER` directory instead of the shell working directory, with `TG_HOME` available as an override. Runtime directories, logs, relative database paths, and relative Telegram session paths are resolved under that stable application home.
- **Installation Documentation**: Added mirrored Russian and English instructions for PyPI, repository, developer, upgrade, first-run configuration, and cross-platform working-directory paths.

### Изменения (RU)
- **Стабильный runtime-каталог для PyPI**: Установленный CLI теперь использует видимую директорию `~/TG_MSG_MANAGER` вместо текущей директории shell; путь можно переопределить через `TG_HOME`. Runtime-каталоги, логи, относительные пути базы и Telegram-сессии разрешаются внутри стабильного каталога приложения.
- **Документация установки**: Добавлены зеркальные русские и английские инструкции для установки из PyPI и репозитория, developer install, обновления, первой настройки и cross-platform рабочей директории.
