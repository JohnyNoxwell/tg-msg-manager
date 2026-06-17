# STAGE 6G.0 — Compatibility Surface Baseline

Status: active task
Stage: 6G.0
Type: report
Depends on: current compatibility wrappers, aggregators, and architecture guardrails

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` first.
- Apply `stage-reviewer` before executing this stage.
- Apply `architecture-guard` because this stage audits compatibility wrappers, storage, CLI, and service boundaries.
- This is an audit/report stage only; do not edit runtime code.
- Do not start Stage 6G.1.

## 1. PURPOSE

Create a factual baseline for compatibility-wrapper architecture debt and classify each surface as:

- keep as public compatibility import;
- migrate internal production imports away from it;
- shrink because it still contains non-thin implementation logic;
- defer removal because deletion would break public compatibility.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `docs/stages/README.md`
- `docs/architecture/ARCHITECTURE_RULES.md`
- `docs/architecture/PROJECT_ARCHITECTURE_OVERVIEW.md`
- `docs/architecture/EXPORT_SERVICE_SPLIT_MAP.md`
- `docs/architecture/CONTEXT_ENGINE_SPLIT_MAP.md`
- `docs/architecture/DB_EXPORT_ENTRYPOINT_AUDIT.md`
- `docs/architecture/PRIVATE_ARCHIVE_IMPORT_RESOLUTION.md`
- `docs/architecture/SQLITE_WRITE_PATH_SPLIT_MAP.md`
- `docs/architecture/STORAGE_CONTRACT_SPLIT_MAP.md`
- `tg_msg_manager/services/exporter.py`
- `tg_msg_manager/services/context_engine.py`
- `tg_msg_manager/services/db_exporter.py`
- `tg_msg_manager/services/private_archive.py`
- `tg_msg_manager/core/models/service_payloads.py`
- `tg_msg_manager/infrastructure/storage/interface.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_sync_state.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_read_path.py`
- `tg_msg_manager/cli_commands.py`
- `tests/architecture/test_architecture_wrappers.py`
- `tests/architecture/test_static_boundaries.py`
- `docs/stages/reports/STAGE_6G_0_COMPATIBILITY_SURFACE_BASELINE_REPORT.md` may be created.

## 3. HARD PROHIBITIONS

- Do not change Python runtime code.
- Do not delete compatibility imports.
- Do not change CLI commands, flags, defaults, output formats, dataset formats, state files, retry behavior, or SQLite schema.
- Do not inspect archive or completed stage files unless a listed current doc explicitly requires it.
- Do not edit existing `docs/stages/reports` files unrelated to this stage.

## 4. ATOMIC IMPLEMENTATION TASKS

1. List every current compatibility wrapper, aggregator, and package-level re-export surface from the inspected files.
2. Find production and test imports of those surfaces with `rg`.
3. Classify each surface by risk and next action.
4. Identify exact candidate files for Stage 6G.1 and Stage 6G.2.
5. Write the factual report only.

## 5. REQUIRED DOCS

- Create `docs/stages/reports/STAGE_6G_0_COMPATIBILITY_SURFACE_BASELINE_REPORT.md`.
- Update no public docs unless the audit proves current architecture docs are stale.

## 6. TESTS / VERIFICATION

Run:

```bash
python3 -m pytest tests/architecture/test_architecture_wrappers.py tests/architecture/test_static_boundaries.py -q
```

Docs-only stage: `make verify` is not required unless code or tests change.

## 7. REPORT

The report must be in Russian and include:

- inspected files;
- compatibility surface inventory;
- import usage findings;
- risk classification;
- recommended next stage order;
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`;
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`;
- commands run and results.

## 8. COMPLETION CRITERIA

- Required report exists.
- No runtime code changed.
- Verification is run or documented as not run with reason.
- Stage 6G.1 and 6G.2 remain unstarted.
- Lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must use the `AGENTS.md` final format.
- Maximum 1200 characters.
- No full diffs.
- No broad summaries.
