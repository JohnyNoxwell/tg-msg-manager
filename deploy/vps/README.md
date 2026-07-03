# VPS Docker Compose deployment

Эта инструкция описывает ручной запуск `tg-msg-manager` на Ubuntu 24.04 VPS через Docker Compose. Контейнер запускает существующий CLI из текущего checkout и не должен содержать пользовательские секреты, Telegram sessions, SQLite базы, exports или logs.

## Требования

- Ubuntu 24.04 VPS.
- Установленные Docker Engine и Docker Compose plugin.
- Репозиторий клонирован в `/opt/tg-msg-manager`.
- Постоянное состояние хранится на хосте в `/opt/tg-msg-manager/state`.

## Подготовка VPS

```bash
sudo mkdir -p /opt/tg-msg-manager
sudo chown "$USER:$USER" /opt/tg-msg-manager
git clone https://github.com/JohnyNoxwell/tg-msg-manager.git /opt/tg-msg-manager
cd /opt/tg-msg-manager
mkdir -p state
docker compose build
```

Скопируйте или создайте `config.json` и Telegram session только внутри `/opt/tg-msg-manager/state`. Не добавляйте эти файлы в image, commits, issues или PR.

## Запуск

```bash
cd /opt/tg-msg-manager
docker compose run --rm tg-msg-manager --help
docker compose run --rm tg-msg-manager update
docker compose run --rm tg-msg-manager export --user-id 123456789 --chat-id 987654321 --json
```

Запуск без аргументов сохраняет интерактивный режим:

```bash
docker compose run --rm tg-msg-manager
```

## Shell helpers

```bash
cd /opt/tg-msg-manager
./deploy/vps/install-shell.sh
source /opt/tg-msg-manager/deploy/vps/tg-shell.sh
```

Доступные функции:

```bash
tg --help
tgu
tge 123456789
tgpm 123456789
tgh 123456789
tgr
tgd
```

Внимание: `tgd` запускает `clean --apply --yes`. Перед ним используйте `tgr`, чтобы проверить dry-run.

## Перенос состояния с Mac

На локальной машине остановите локальный запуск приложения перед push, чтобы не копировать состояние во время записи.

```bash
export TGMM_SSH_HOST=vps
export TGMM_LOCAL_STATE_DIR="$HOME/TG_MSG_MANAGER"
export TGMM_REMOTE_STATE_DIR=/opt/tg-msg-manager/state

./deploy/local/tg-state-sync.sh push --dry-run
./deploy/local/tg-state-sync.sh push --apply
./deploy/local/tg-state-sync.sh pull exports
./deploy/local/tg-state-sync.sh pull logs
./deploy/local/tg-state-sync.sh pull all
```

Sync helper использует `rsync` over SSH, `--partial` и `--info=progress2`. Он не использует `--delete`.
