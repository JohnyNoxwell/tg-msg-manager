# STAGE 5B.3 — DB Export Memory Boundaries

Status: completed
Stage: 5B.3
Type: implementation
Depends on: `tg_msg_manager/services/db_export/`; `tg_msg_manager/infrastructure/storage/read/exports.py`

---

## 0. CODEX ENTRY CONTRACT

1. Read `AGENTS.md`.
2. Read this stage file only.
3. Apply `stage-reviewer` before implementation. If no tool exists, read `.skills/stage-reviewer/SKILL.md`.
4. Apply `architecture-guard` because this touches DB export and storage read boundaries. If no tool exists, read `.skills/architecture-guard/SKILL.md`.
5. Do not start any other active 5B stage.

## 1. PURPOSE

Reduce DB export memory risk by replacing avoidable full-list materialization with existing iterator paths where output behavior can be preserved exactly.

Current risk to address:

- `load_export_source()` falls back to `get_user_messages()` or `get_user_export_rows()`.
- `DBExportPayloadWriter.write_payloads()` materializes context-readable TXT records.
- Some paths are streaming already; this stage must not regress them.

## 2. FILES TO INSPECT

Inspect only:

- `AGENTS.md`
- `docs/architecture/README.md`
- `docs/architecture/ARCHITECTURE_RULES.md`
- `docs/architecture/TXT_RENDERING.md`
- `docs/development/CLI_CONTRACT.md`
- `tg_msg_manager/services/db_export/summary.py`
- `tg_msg_manager/services/db_export/payload_writer.py`
- `tg_msg_manager/services/db_export/service.py`
- `tg_msg_manager/services/db_export/txt_renderer.py`
- `tg_msg_manager/services/db_export/jsonl_renderer.py`
- `tg_msg_manager/services/rendering/legacy_txt_renderer.py`
- `tg_msg_manager/services/rendering/context_readable_txt_renderer.py`
- `tg_msg_manager/services/rendering/models.py`
- `tg_msg_manager/infrastructure/storage/read/exports.py`
- `tg_msg_manager/infrastructure/storage/contracts/db_export_storage.py`
- `tests/services/db_export/test_db_export_components.py`
- `tests/services/db_export/test_db_exporter.py`
- `tests/services/db_export/test_export_txt_profile_integration.py`

May create:

- focused helper module under `tg_msg_manager/services/db_export/` if needed;
- focused tests under `tests/services/db_export/`;
- `docs/stages/reports/STAGE_5B_3_DB_EXPORT_MEMORY_BOUNDARIES_REPORT.md`.

## 3. HARD PROHIBITIONS

- Do not change CLI command names, flags, defaults, output paths, output filenames, or output formats.
- Do not change TXT profile semantics.
- Do not change JSONL profile semantics.
- Do not change SQLite schema or migrations.
- Do not add raw SQL to services.
- Do not add business logic to compatibility wrappers.
- Do not force streaming into `context_readable` if exact grouping/reply behavior would change.
- Do not add analytics, post-processing, LLM, or interpretation behavior.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Identify which DB export paths can use `iter_user_export_rows()` without changing output.
2. Preserve the current AI JSON streaming path.
3. For any exact-safe path, switch source loading/writing to iterator-based processing.
4. For any path that cannot be streamed exactly, leave behavior unchanged and record the reason in the report.
5. Add tests proving:
   - changed paths do not call full-list getters when iterator getters are available;
   - output bytes or parsed records match the previous behavior for representative fixtures;
   - context-readable TXT remains unchanged if left materialized.

## 5. REQUIRED DOCS

Update docs only if behavior, supported formats, or documented limitations change:

- `docs/architecture/TXT_RENDERING.md`
- `COMMANDS.md`

Always create:

- `docs/stages/reports/STAGE_5B_3_DB_EXPORT_MEMORY_BOUNDARIES_REPORT.md`

## 6. TESTS / VERIFICATION

Run:

- `pytest tests/services/db_export/test_db_export_components.py tests/services/db_export/test_db_exporter.py tests/services/db_export/test_export_txt_profile_integration.py`
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager tests`

If output equivalence is verified by a focused test, name that test in the report.

## 7. REPORT

Report in Russian:

- paths converted to iterator-based processing;
- paths intentionally left materialized and why;
- exact docs updated or why docs were not needed;
- checks run;
- `stage-reviewer` and `architecture-guard` application.

## 8. COMPLETION CRITERIA

- At least one avoidable full-list DB export path is removed, or the report proves none can be removed without behavior change.
- Existing export formats and profiles are preserved.
- Required tests pass or blockers are documented.
- No schema, CLI, or dataset contract changes.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md` final structure, be in Russian, and stay under 1200 characters.
