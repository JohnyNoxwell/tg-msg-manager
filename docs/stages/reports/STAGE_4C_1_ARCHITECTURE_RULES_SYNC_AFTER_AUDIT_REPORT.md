# STAGE 4C.1 — ARCHITECTURE RULES SYNC AFTER AUDIT REPORT

## Статус

- Stage 4C.1 завершён.
- Выполнена только docs-sync работа, требуемая Stage 4C.0.
- Runtime code, tests, CLI behavior, channel export behavior, dataset behavior, SQLite schema и output formats не менялись.

## Требовалась ли синхронизация

- Да.
- Stage 4C.0 зафиксировал `READY_AFTER_DOC_SYNC`.
- Причины:
  - stale flat test path references после группировки тестов;
  - необходимость коротко зафиксировать boundary `ChannelExportWorkflowContext`;
  - README содержал старую E2E unittest command и старый путь fixture E2E файла.

## Изменённые файлы

- `README.md`
- `docs/architecture/README.md`
- `docs/architecture/PRIVATE_ARCHIVE_ENTRYPOINT_AUDIT.md`
- `docs/architecture/DB_EXPORT_ENTRYPOINT_AUDIT.md`
- `docs/architecture/PRIVATE_ARCHIVE_IMPORT_RESOLUTION.md`
- `docs/architecture/PROJECT_ARCHITECTURE_OVERVIEW.md`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_4C_1_ARCHITECTURE_RULES_SYNC_AFTER_AUDIT_REPORT.md`
- `docs/stages/completed/stage_4c_1_architecture_rules_sync_after_audit.md`

## Обновлённые правила и docs

- `README.md`:
  - `python3 -m unittest tests.test_fixture_e2e -q` заменено на `python3 -m unittest tests.e2e.test_fixture_e2e -q`;
  - `tests/test_fixture_e2e.py` заменено на `tests/e2e/test_fixture_e2e.py`.
- Architecture docs:
  - old flat test paths заменены на grouped layout paths.
  - `ChannelExportWorkflowContext` описан как workflow wiring/helper context; новая product/dataset logic должна оставаться в focused channel export modules.
- `docs/stages/README.md` обновлён только в рамках lifecycle cleanup.

## Что намеренно не менялось

- `AGENTS.md`: Stage 4C.0 прямо зафиксировал, что update не нужен.
- Runtime source и tests: Stage 4C.1 запрещает такие изменения.
- `COMMANDS.md`, `Makefile`, `.github/workflows/`: Stage 4C.0 не нашёл требуемых изменений.
- Root pytest `scratch/test_whitelist.py` collection risk: зафиксирован как deferred hygiene risk. CI использует `make verify`, а текущий stage не меняет pytest config и не удаляет scratch files.

## Проверки

- `python3 -m compileall tg_msg_manager`: passed.
- `ruff check tg_msg_manager tests`: passed.
- `python3 -m unittest tests.e2e.test_fixture_e2e -q`: passed, 4 tests.
- `rg` stale path consistency check across `README.md`, `docs/architecture`, `docs/development`, `docs/stages/README.md`: passed; old flat references from Stage 4C.0 report are gone.

## Не выполнялось

- `make test`: not run; docs-only stage required compileall/ruff, and changed README E2E command was verified directly.
- `stage-completion-auditor`: not run; no such skill/tool is available in this session.
- `architecture-guard`: not run; no such skill/tool is available in this session.

## Completion status

- Stage 4C.0 findings followed exactly: yes.
- AGENTS/docs updated only where required: yes.
- No runtime code changed: yes.
- Required report exists: yes.
- Lifecycle cleanup completed: yes.
