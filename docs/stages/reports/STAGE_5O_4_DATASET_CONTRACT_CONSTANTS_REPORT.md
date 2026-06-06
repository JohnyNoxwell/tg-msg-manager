# STAGE 5O.4 — Dataset Contract Constants Report

Дата: 2026-06-05

## Итог

- Выполнено: контрактные имена датасета централизованы без изменения формата экспорта и валидации.
- `stage-reviewer`: applied from `.skills/stage-reviewer/SKILL.md`.
- `architecture-guard`: applied from `.skills/architecture-guard/SKILL.md`.
- `stage-completion-auditor`: applied from `.skills/stage-completion-auditor/SKILL.md`.

## Централизованные константы

- Добавлен нейтральный модуль `tg_msg_manager/core/models/dataset_contracts.py`.
- Централизованы имена файлов датасета: `manifest.json`, `messages.jsonl`, `messages.txt`, `media_manifest.jsonl`, `run_changelog.jsonl`, `channel_export_state.json`, discussion-артефакты и `media/`.
- Централизованы `dataset_type`, `schema_version` и ключи `artifact_paths` для run changelog.
- Экспорт и валидация теперь используют общий модуль только для имен/ключей; IO, форматирование, проверка и бизнес-логика в `core` не добавлялись.

## Измененные файлы

- `tg_msg_manager/core/models/dataset_contracts.py`
- `tg_msg_manager/services/channel_export/plan_builder.py`
- `tg_msg_manager/services/channel_export/included_files_builder.py`
- `tg_msg_manager/services/channel_export/run_changelog.py`
- `tg_msg_manager/services/channel_export/workflows/context.py`
- `tg_msg_manager/services/channel_export/manifest_writer.py`
- `tg_msg_manager/services/channel_export/state_manager.py`
- `tg_msg_manager/services/channel_export/discussions/manifest_summary.py`
- `tg_msg_manager/services/channel_export/discussions/state_manager.py`
- `tg_msg_manager/services/dataset_validation/contract_validator.py`
- `tg_msg_manager/services/dataset_validation/manifest_validator.py`
- `tg_msg_manager/services/dataset_validation/jsonl_validator.py`
- `tg_msg_manager/services/dataset_validation/media_validator.py`
- `tg_msg_manager/services/dataset_validation/discussion_validator.py`
- `tg_msg_manager/services/dataset_validation/inspector.py`
- `tg_msg_manager/services/dataset_validation/state_validator.py`
- `tests/services/channel_export/test_channel_export_dataset_contracts.py`
- `tests/services/dataset_validation/test_dataset_validation_contracts.py`
- `docs/stages/README.md`
- `docs/stages/completed/stage_5o_4_dataset_contract_constants.md`
- `docs/stages/reports/STAGE_5O_4_DATASET_CONTRACT_CONSTANTS_REPORT.md`

## Оставленные литералы

- Тексты диагностик в валидаторах оставлены строками, потому что это пользовательские сообщения, а не точки формирования путей или ключей.
- Ожидаемые строковые значения в тестах сохранены там, где они проверяют публичный контракт вывода.
- Константы статусов медиа, режимов discussion и ключей JSON-объектов не менялись: это отдельные контракты вне цели этапа.

## Проверки

- `pytest tests/services/dataset_validation tests/services/channel_export`: passed, 229 passed.
- `python3 -m compileall tg_msg_manager`: passed.
- `ruff check tg_msg_manager tests/services/dataset_validation tests/services/channel_export`: passed.

## Подтверждение сохранения

- Формат датасета сохранен: имена файлов, ключи `artifact_paths`, `dataset_type` и `schema_version` не изменены.
- CLI не менялся.
- SQLite не менялся.
- Импорты остаются архитектурно допустимыми: `services` импортируют нейтральные `core.models`, обратных импортов нет.
- Статус этапа: complete.
