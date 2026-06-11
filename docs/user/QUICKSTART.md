# Первый запуск / First Run

[Русский](#русский) | [English](#english)

Эта страница описывает установку и первый локальный запуск. Полный справочник
команд находится в [`../../COMMANDS.md`](../../COMMANDS.md).

This page covers installation and the first local run. The complete command
reference is [`../../COMMANDS.md`](../../COMMANDS.md).

<a id="русский"></a>
## Русский

### 1. Выберите способ установки

Для обычного использования рекомендуется PyPI:

```bash
python3 -m pip install tg-msg-manager
```

Windows PowerShell:

```powershell
py -m pip install tg-msg-manager
```

Для установки последней версии из репозитория:

```bash
git clone https://github.com/JohnyNoxwell/tg-msg-manager.git
cd tg-msg-manager
python3 -m pip install .
```

Для разработки используйте editable install:

```bash
python3 -m pip install -e ".[dev]"
```

### 2. Создайте конфигурацию

Запустите CLI один раз:

```bash
tg-msg-manager
```

CLI автоматически создаст безопасный базовый `config.json` в рабочей
директории и попросит указать `api_id` и `api_hash`. Существующий конфиг не
перезаписывается. Не публикуйте credentials, Telegram-сессии, базы, логи или
экспорты.

### 3. Запустите приложение

```bash
tg-msg-manager
```

Альтернативный Python entrypoint:

```bash
python3 -m tg_msg_manager.cli
```

В Windows замените `python3` на `py`.

### 4. Найдите рабочие файлы

Рабочая директория создаётся автоматически:

- macOS / Linux: `~/TG_MSG_MANAGER`
- Windows: `%USERPROFILE%\TG_MSG_MANAGER`

Основная структура:

```text
TG_MSG_MANAGER/
├── config.json
├── messages.db
├── tg_msg_manager.session
├── LOGS/
├── DB_EXPORTS/
├── PRIVAT_DIALOGS/
├── PUBLIC_GROUPS/
└── exports/
    └── channels/
```

Файл или каталог появляется только когда соответствующая функция впервые его
использует.

### 5. Обновите установленный пакет

```bash
python3 -m pip install --upgrade tg-msg-manager
```

В Windows замените `python3` на `py`.

Дальше используйте [`../../COMMANDS.md`](../../COMMANDS.md) для команд,
[`../development/SAFE_FIRST_CHANNEL_EXPORT.md`](../development/SAFE_FIRST_CHANNEL_EXPORT.md)
для первого безопасного channel export и
[`../development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`](../development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md)
для правил работы с приватными файлами.

<a id="english"></a>
## English

### 1. Choose an installation method

PyPI is recommended for normal use:

```bash
python3 -m pip install tg-msg-manager
```

Windows PowerShell:

```powershell
py -m pip install tg-msg-manager
```

To install the latest source from the repository:

```bash
git clone https://github.com/JohnyNoxwell/tg-msg-manager.git
cd tg-msg-manager
python3 -m pip install .
```

For development, use an editable install:

```bash
python3 -m pip install -e ".[dev]"
```

### 2. Create the configuration

Run the CLI once:

```bash
tg-msg-manager
```

The CLI automatically creates a safe base `config.json` in the working
directory and asks you to set `api_id` and `api_hash`. It never overwrites an
existing config. Do not publish credentials, Telegram sessions, databases,
logs, or exports.

### 3. Launch the application

```bash
tg-msg-manager
```

Alternative Python entrypoint:

```bash
python3 -m tg_msg_manager.cli
```

On Windows, replace `python3` with `py`.

### 4. Find the working files

The working directory is created automatically:

- macOS / Linux: `~/TG_MSG_MANAGER`
- Windows: `%USERPROFILE%\TG_MSG_MANAGER`

Main layout:

```text
TG_MSG_MANAGER/
├── config.json
├── messages.db
├── tg_msg_manager.session
├── LOGS/
├── DB_EXPORTS/
├── PRIVAT_DIALOGS/
├── PUBLIC_GROUPS/
└── exports/
    └── channels/
```

A file or directory appears only after the corresponding feature first uses
it.

### 5. Upgrade the installed package

```bash
python3 -m pip install --upgrade tg-msg-manager
```

On Windows, replace `python3` with `py`.

Continue with [`../../COMMANDS.md`](../../COMMANDS.md) for commands,
[`../development/SAFE_FIRST_CHANNEL_EXPORT.md`](../development/SAFE_FIRST_CHANNEL_EXPORT.md)
for the first safe channel export, and
[`../development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`](../development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md)
for private-file handling rules.
