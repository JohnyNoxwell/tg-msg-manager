# Stage 5O.6 — DB Export Run Coordinator Extraction

## Статус

Завершено.

## Навыки

- stage-reviewer: applied from .skills/stage-reviewer/SKILL.md
- architecture-guard: applied from .skills/architecture-guard/SKILL.md
- stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md

## Изменения

- Добавлен `tg_msg_manager/services/db_export/run_coordinator.py`.
- `DBExportFullRunCoordinator` вынес последовательность полного DB export run.
- `DBExportUpdateRunCoordinator` вынес последовательность incremental update run.
- `DBExportRunProgress` вынес общий учет обработанных сообщений и последнего timestamp для failure bookkeeping.
- `tg_msg_manager/services/db_export/service.py` оставлен public facade: создает collaborators, сохраняет compatibility helpers и делегирует public run methods.
- `tests/services/db_export/test_db_exporter.py` обновлен для инъекции writer failure через `payload_writer`, так как private facade method больше не является hot path.
- `docs/development/FACADE_SIZE_BASELINE.md` обновлен: `db_export/service.py` уменьшен до 358 строк.
- `docs/stages/README.md` обновлен для Stage 5O.6 lifecycle.
- Stage file перенесен из `docs/stages/active/stage_5o_6_db_export_run_coordinator_extraction.md` в `docs/stages/completed/stage_5o_6_db_export_run_coordinator_extraction.md`.

## Protected facade

- `tg_msg_manager/services/db_export/service.py` изменен только для механической wiring/delegation.
- Public method names, параметры, defaults и return values сохранены.
- Existing private compatibility helpers сохранены для тестов и legacy callers.

## Проверки

- `pytest tests/services/db_export`: passed
- `pytest tests/services/test_services.py`: passed
- `python3 -m compileall tg_msg_manager`: passed
- `ruff check tg_msg_manager/services/db_export tests/services/db_export`: passed

## Подтверждения

- CLI behavior: unchanged.
- SQLite schema/contracts: unchanged.
- DB export output filenames, formats, state, incremental/update, force/no-new-work paths: unchanged.
- Raw SQL в services не добавлялся.
- Analytics/OSINT/profiling/LLM logic не добавлялись.
- Scope ограничен Stage 5O.6.
