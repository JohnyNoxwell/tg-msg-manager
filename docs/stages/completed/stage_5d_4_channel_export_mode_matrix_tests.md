# STAGE 5D.4 — CHANNEL EXPORT MODE MATRIX TESTS

Status: active task
Stage: 5D.4
Type: tests/behavior-fix-if-required
Depends on: `docs/stages/reports/STAGE_5D_1_DATASET_CONTRACT_GAP_CLOSURE_PLAN_REPORT.md`, `docs/stages/reports/STAGE_5D_2_RUN_CHANGELOG_KEY_SET_CONTRACT_TESTS_REPORT.md`, `docs/stages/reports/STAGE_5D_3_TXT_PROJECTION_CONTRACT_CLARIFICATION_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` first.
- Read Stage 5D.1, 5D.2, and 5D.3 reports before editing.
- Apply `stage-reviewer` before edits.
- Apply `architecture-guard` because this stage touches channel export services and dataset contracts.
- Write a plan with max 5 bullets before editing.
- Do not implement Stage 5D.5 or any 5E stage.

## 1. PURPOSE

Add focused runtime regression coverage for documented channel export mode matrix behavior.

The target matrix is:

- media modes: `none`, `metadata`, `full`;
- discussion modes: `none`, `metadata`, `full`;
- output toggles: `include_jsonl=False`, `include_txt=False`;
- run modes: full, force full, incremental, no-new-posts.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/reports/STAGE_5D_1_DATASET_CONTRACT_GAP_CLOSURE_PLAN_REPORT.md`
- `docs/stages/reports/STAGE_5D_2_RUN_CHANGELOG_KEY_SET_CONTRACT_TESTS_REPORT.md`
- `docs/stages/reports/STAGE_5D_3_TXT_PROJECTION_CONTRACT_CLARIFICATION_REPORT.md`
- `docs/architecture/DATASET_CONTRACT_V1.md`
- `docs/architecture/DATASET_FORMAT.md`
- `docs/architecture/DATASET_CONTRACT_COVERAGE_MATRIX.md`
- `tg_msg_manager/services/channel_export/models.py`
- `tg_msg_manager/services/channel_export/media_policy.py`
- `tg_msg_manager/services/channel_export/post_mapper.py`
- `tg_msg_manager/services/channel_export/payload_writer.py`
- `tg_msg_manager/services/channel_export/included_files_builder.py`
- `tg_msg_manager/services/channel_export/manifest_coordinator.py`
- `tg_msg_manager/services/channel_export/workflows/full_export.py`
- `tg_msg_manager/services/channel_export/workflows/incremental_export.py`
- `tg_msg_manager/services/channel_export/workflows/no_new_posts.py`
- `tests/services/channel_export/test_channel_export_service.py`
- `tests/services/channel_export/test_channel_export_included_files_builder.py`
- `tests/services/channel_export/test_channel_export_dataset_contracts.py`

## 3. HARD PROHIBITIONS

- Do not change CLI flags, defaults, command output, or interactive prompts.
- Do not change dataset filenames or JSON key names except to fix a documented behavior mismatch found by these tests.
- Do not modify SQLite code or schema.
- Do not add feature logic to `tg_msg_manager/services/channel_export/service.py`; only mechanical wiring is allowed if unavoidable.
- Do not add analytics, profiling, OSINT, OCR, STT, LLM, or media analysis.
- Do not inspect private exports.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Add or tighten tests for `media_mode="none"`:
   - no media download calls;
   - `media_manifest.jsonl` remains in included files;
   - `media/` is not listed in manifest included files.
2. Add or tighten tests for `include_jsonl=False`:
   - `messages.jsonl` is not listed in manifest included files;
   - disabled payload file is not created for that run.
3. Add or tighten tests for `include_txt=False`:
   - `messages.txt` is not listed in manifest included files;
   - disabled payload file is not created for that run.
4. Add one compact mode matrix test or subtests for discussion `none`, `metadata`, and `full` included-file behavior.
5. Add one compact run-mode test or subtests for full, force full, incremental, and no-new-posts changelog/state write behavior if not already covered by existing tests.
6. If a new test exposes a behavior mismatch, fix only the smallest focused module that owns that behavior.

## 5. REQUIRED DOCS

- Update `docs/architecture/DATASET_CONTRACT_COVERAGE_MATRIX.md` to mark closed gaps.
- Update `docs/architecture/DATASET_CONTRACT_V1.md` or `docs/architecture/DATASET_FORMAT.md` only if tests prove the docs are stale.
- Do not update user-facing docs unless public behavior changes.

## 6. TESTS / VERIFICATION

- `python3 -m pytest tests/services/channel_export/test_channel_export_service.py tests/services/channel_export/test_channel_export_included_files_builder.py tests/services/channel_export/test_channel_export_dataset_contracts.py -q`
- `python3 -m pytest tests/services/dataset_validation/test_dataset_validation_contracts.py -q`
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager tests`
- `git diff --check`

## 7. REPORT

Create `docs/stages/reports/STAGE_5D_4_CHANNEL_EXPORT_MODE_MATRIX_TESTS_REPORT.md` in Russian.

The report must include:

- matrix rows covered;
- tests added or changed;
- any behavior fix and exact owner module;
- verification results;
- confirmation that CLI and SQLite behavior were preserved;
- skill lines:
  - `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
  - `architecture-guard: applied from .skills/architecture-guard/SKILL.md`

## 8. COMPLETION CRITERIA

- The mode matrix gaps from Stage 5D.1 are covered or explicitly deferred with reason.
- Any behavior mismatch found by tests is fixed in focused channel export modules.
- Docs and coverage matrix match final behavior.
- `stage-completion-auditor` is applied after the report.
- Lifecycle cleanup is completed according to `AGENTS.md`; do not move unrelated later active files.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Do not continue to Stage 5D.5.
