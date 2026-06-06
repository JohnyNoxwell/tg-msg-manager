# Stage 5O.1 — Config Loading Source Cleanup

## Статус

- Выполнено.
- `stage-reviewer`: applied from `.skills/stage-reviewer/SKILL.md`.
- `stage-completion-auditor`: applied from `.skills/stage-completion-auditor/SKILL.md`.

## Изменения

- `tg_msg_manager/core/config.py`: удалена временная запись синтетических `TG_*` ключей в `os.environ`; значения из `config.json` теперь передаются локально в `Settings`.
- `tests/core/test_config.py`: добавлены проверки приоритета explicit init, process env, config file и defaults; добавлена проверка отсутствия утечки синтетических `TG_*` ключей после успешной загрузки и ошибки валидации.
- `docs/stages/completed/stage_5o_1_config_loading_source_cleanup.md`: stage-файл перенесен из active в completed.
- `docs/stages/README.md`: обновлены active/completed списки и ссылка на отчет Stage 5O.1.
- `docs/stages/reports/STAGE_5O_1_CONFIG_LOADING_SOURCE_CLEANUP_REPORT.md`: создан текущий отчет.

## Поведение

- Имена настроек, env-префикс `TG_`, алиасы, defaults и порядок приоритета сохранены: explicit init > process env > config file > defaults.
- `load_settings(path)` и `load_settings(path, require_api_credentials=False)` сохранены.
- Реальные `config.json`, `.env`, credentials, sessions, exports, logs, screenshots, media и локальные БД не читались.
- CLI, SQLite, экспортные форматы и runtime paths не изменялись.

## Проверки

- `pytest tests/core/test_config.py`: passed, `10 passed`.
- `python3 -m compileall tg_msg_manager`: passed.
- `ruff check tg_msg_manager/core tests/core/test_config.py`: passed.

## Lifecycle

- Stage-файл перенесен из `docs/stages/active/` в `docs/stages/completed/`.
- `docs/stages/README.md` обновлен.
