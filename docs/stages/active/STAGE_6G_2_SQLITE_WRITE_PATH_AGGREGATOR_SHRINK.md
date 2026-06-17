# STAGE 6G.2 — SQLite Write Path Aggregator Shrink

Status: active task
Stage: 6G.2
Type: implementation
Depends on: `docs/stages/reports/STAGE_6G_1_INTERNAL_IMPORT_CONVERGENCE_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` first.
- Read the Stage 6G.0 and 6G.1 reports before editing.
- Apply `stage-reviewer` before executing this stage.
- Apply `architecture-guard` because this stage touches storage compatibility surfaces.
- Preserve SQLite behavior exactly.
- Do not start any later stage.

## 1. PURPOSE

Shrink `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py` from a deprecated compatibility aggregator with active write-path logic into a thin delegating mixin over focused storage write modules.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `docs/stages/reports/STAGE_6G_0_COMPATIBILITY_SURFACE_BASELINE_REPORT.md`
- `docs/stages/reports/STAGE_6G_1_INTERNAL_IMPORT_CONVERGENCE_REPORT.md`
- `docs/architecture/ARCHITECTURE_RULES.md`
- `docs/architecture/SQLITE_WRITE_PATH_SPLIT_MAP.md`
- `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py`
- `tg_msg_manager/infrastructure/storage/sqlite.py`
- `tg_msg_manager/infrastructure/storage/write/__init__.py`
- `tg_msg_manager/infrastructure/storage/write/message_writer.py`
- `tg_msg_manager/infrastructure/storage/write/checkpoint_writer.py`
- `tg_msg_manager/infrastructure/storage/write/context_writer.py`
- `tg_msg_manager/infrastructure/storage/write/target_link_writer.py`
- `tg_msg_manager/infrastructure/storage/write/user_writer.py`
- New focused module under `tg_msg_manager/infrastructure/storage/write/` if needed.
- `tests/infrastructure/storage/test_storage_sqlite.py`
- `tests/architecture/test_architecture_wrappers.py`
- `tests/architecture/test_static_boundaries.py`
- Directly affected storage tests identified by changes.
- `docs/stages/reports/STAGE_6G_2_SQLITE_WRITE_PATH_AGGREGATOR_SHRINK_REPORT.md` may be created.

## 3. HARD PROHIBITIONS

- Do not change SQLite schema or migrations.
- Do not change message row contents, payload serialization, target links, sync state updates, queue flush semantics, background writer failure behavior, telemetry names, or close/start behavior.
- Do not move storage logic into services, core, CLI, or compatibility service wrappers.
- Do not add raw SQL outside `tg_msg_manager/infrastructure/storage/`.
- Do not broaden `SQLiteStorage` responsibilities.
- Do not perform unrelated storage refactors or formatting churn.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Move queue/background writer implementation from `_sqlite_write_path.py` into a focused write module.
2. Move `_upsert_message_row_in_conn` SQL into `write/message_writer.py` or a focused sibling module.
3. Leave `_sqlite_write_path.py` as method-level delegation only, preserving method names used by `SQLiteStorage` and tests.
4. Add or adjust tests that prove delegated methods preserve write behavior and the compatibility mixin stays thin.
5. Update architecture docs only where the split map or guardrails become stale.

## 5. REQUIRED DOCS

- Create `docs/stages/reports/STAGE_6G_2_SQLITE_WRITE_PATH_AGGREGATOR_SHRINK_REPORT.md`.
- Update `docs/architecture/SQLITE_WRITE_PATH_SPLIT_MAP.md` if ownership changed.
- Update `docs/architecture/ARCHITECTURE_RULES.md` only if guardrail wording changes.

## 6. TESTS / VERIFICATION

Run focused checks first:

```bash
python3 -m pytest tests/infrastructure/storage/test_storage_sqlite.py tests/architecture/test_architecture_wrappers.py tests/architecture/test_static_boundaries.py -q
python3 -m compileall tg_msg_manager
```

Then run completion gates:

```bash
make verify
make pre-commit
```

Do not claim completion if `make verify` cannot run.

## 7. REPORT

The report must be in Russian and include:

- exact logic moved out of `_sqlite_write_path.py`;
- preserved storage behavior notes;
- docs changed or reason none were needed;
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`;
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`;
- commands run and results.

## 8. COMPLETION CRITERIA

- `_sqlite_write_path.py` contains compatibility delegation only.
- SQLite schema and persisted data formats are unchanged.
- Required focused tests and completion gates pass.
- Required report exists.
- Lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must use the `AGENTS.md` final format.
- Maximum 1200 characters.
- No full diffs.
- No broad summaries.
