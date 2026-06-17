# Stage 6G.1 — Internal Import Convergence Report

Дата: 2026-06-18

## Статус

- Stage 6G.1 выполнен.
- Stage 6G.2 не начинался.
- stage-reviewer: applied from .skills/stage-reviewer/SKILL.md
- architecture-guard: applied from .skills/architecture-guard/SKILL.md
- stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md

## Изменённые imports

- `tg_msg_manager/application/services.py`: `ExportService`, `DBExportService`, `PrivateArchiveService` переведены с compatibility/package re-export paths на canonical `.service` modules.
- `tg_msg_manager/testing/runtime.py`: те же service imports переведены на canonical `.service` modules.
- `tg_msg_manager/services/export/export_writer.py`: `DBExportService` переведён с `services.db_export` package re-export на `services.db_export.service`.
- `tg_msg_manager/cli/__init__.py`: internal CLI handlers импортируются из `tg_msg_manager.cli.commands`, не из `cli_commands.py`.
- `tg_msg_manager/cli_menu.py`: `_handle_export_channel_command` импортируется из `tg_msg_manager.cli.commands`, не из `cli_commands.py`.
- `tests/services/test_services.py`, `tests/services/sync/test_sync_system.py`, `tests/services/cleaner/test_cleaner.py`, `tests/services/db_export/test_db_export_components.py`, `tests/services/db_export/test_db_exporter.py`: non-compat test imports переведены на canonical modules.

## Сохранённые compatibility imports/tests

- `tg_msg_manager/services/exporter.py`, `context_engine.py`, `db_exporter.py`, `private_archive.py`, `core/models/service_payloads.py`, `cli_commands.py` не удалялись и не получали новую логику.
- Старые import paths сохраняются в `tests/architecture/test_compat_imports.py` и `tests/architecture/test_architecture_wrappers.py`.
- CLI compatibility imports в `tests/cli/test_channel_export_cli.py` и `tests/services/dataset_validation/test_dataset_validation_contracts.py` оставлены как test-side coverage, не production usage.

## Static guardrail changes

- `tests/architecture/test_static_boundaries.py` добавляет resolution relative imports и проверку, что production code не импортирует deprecated compatibility surfaces:
  `cli_commands`, `core.models.service_payloads`, `services.exporter`, `services.context_engine`, `services.db_exporter`, package re-export `services.db_export`, package re-export `services.private_archive`.

## Docs

- `docs/architecture/ARCHITECTURE_RULES.md` обновлён: internal production code должен импортировать canonical implementation modules, public compatibility imports остаются под compatibility tests.
- `docs/stages/README.md` обновлён в lifecycle cleanup.

## Сохранено без изменений

- CLI command names, flags, defaults, output formats и dispatch behavior не менялись.
- SQLite schema, dataset formats, manifests, state, incremental, force и no-new-work behavior не менялись.
- Public compatibility import behavior сохранён.

## Commands run

- `python3 -m pytest tests/architecture/test_static_boundaries.py -q`: failed before `tg_msg_manager/services/export/export_writer.py` import migration; 1 failed, 10 passed.
- `python3 -m pytest tests/architecture/test_architecture_wrappers.py tests/architecture/test_static_boundaries.py -q`: passed, 19 passed in 2.49s.
- `python3 -m pytest tests/services/test_services.py tests/services/sync/test_sync_system.py tests/cli/test_channel_export_cli.py tests/services/dataset_validation/test_dataset_validation_contracts.py -q`: passed, 123 passed in 7.62s.
- `python3 -m compileall tg_msg_manager`: passed.
- `make verify`: passed, 564 unittest tests OK.
- `make pre-commit`: passed, includes `ruff format`, `make verify`, 564 unittest tests OK.
- `git diff --check`: passed.

## Completion audit

- VERDICT: complete
- BLOCKERS: none
- SCOPE: pass; changes are import convergence, static guardrails, required docs/report, and lifecycle cleanup.
- CHECKS: pass; required focused checks, `make verify`, and `make pre-commit` passed.
- DOCS: pass; required report exists and architecture guidance updated for the new guardrail.
- LIFECYCLE: pass; Stage 6G.1 task moved from active to completed.
