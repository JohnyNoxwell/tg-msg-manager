# STAGE 6A.6 — Headless Runtime Contract Report

Дата: 2026-06-17
Статус: completed
Тип: implementation/docs

## Выполнено

- Стабильный non-CLI entrypoint зафиксирован как `tg_msg_manager.application.ApplicationSession`.
- Поддерживающие runtime exports остаются доступны через `tg_msg_manager.application`: `RuntimeResourceFactory`, `ServiceBundle`, `create_service_bundle`.
- Добавлен architecture smoke test, который в отдельном Python-процессе импортирует `tg_msg_manager.application` и подтверждает, что CLI modules не загружаются.
- Добавлен no-client smoke test: `ApplicationSession(needs_client=False)` собирает storage и local services без создания `TelethonClientWrapper`.
- Architecture/development docs обновлены: CLI описан как adapter поверх application runtime boundary.

## Измененные файлы

- `tests/architecture/test_application_runtime_contract.py`
- `docs/architecture/README.md`
- `docs/architecture/ARCHITECTURE_RULES.md`
- `docs/development/CLI_CONTRACT.md`
- `docs/stages/reports/STAGE_6A_6_HEADLESS_RUNTIME_CONTRACT_REPORT.md`
- `docs/stages/completed/stage_6a_6_headless_runtime_contract.md`
- `docs/stages/README.md`

## Проверки

- `pytest tests/architecture/test_application_runtime_contract.py`: passed, 2 passed.
- `pytest tests/architecture`: passed, 23 passed.
- `pytest tests/cli`: passed, 95 passed.
- `python3 -m compileall tg_msg_manager`: passed.
- `ruff check tg_msg_manager tests/architecture tests/cli`: passed.
- `git diff --check`: passed.

## Сохранено

- CLI commands, flags, defaults, prompts, output, exit codes и routing не менялись.
- SQLite schema, storage SQL, dataset/export formats, state files, retry и scheduler behavior не менялись.
- Daemon mode, GUI, web UI, SaaS/product behavior, analytics, OSINT/profiling, OCR/STT/media analysis и LLM behavior не добавлялись.
- Services, core и infrastructure не импортируют CLI modules.

## Skill notes

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`

## Architecture guard

- Нарушений нет: runtime/session boundary остается в `tg_msg_manager/application/`.
- Protected service facades, compatibility wrappers, storage SQL и package metadata не менялись.
- `ApplicationSession(needs_client=False)` подтверждает local/headless assembly без Telegram client construction.

## Lifecycle

- Stage report создан до cleanup.
- Stage file перемещен из `docs/stages/active/` в `docs/stages/completed/`.
- `docs/stages/README.md` обновлен: Stage 6A.6 убран из active и добавлена ссылка на report.
