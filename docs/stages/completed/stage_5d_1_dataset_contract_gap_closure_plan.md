# STAGE 5D.1 — DATASET CONTRACT GAP CLOSURE PLAN

Status: active task
Stage: 5D.1
Type: docs/planning
Depends on: `docs/architecture/DATASET_CONTRACT_COVERAGE_MATRIX.md`, current direct channel export implementation

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` first.
- Apply `stage-reviewer` before edits.
- Apply `architecture-guard` because this stage touches dataset contract boundaries.
- Write a plan with max 5 bullets before editing.
- Do not implement later 5D or 5E stages.

## 1. PURPOSE

Close the planning gap after Stage 5C.0 by converting the factual dataset contract coverage matrix into an executable closure plan.

This stage must decide only what later stages should prove or clarify. It must not change runtime behavior.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/architecture/DATASET_CONTRACT_COVERAGE_MATRIX.md`
- `docs/architecture/DATASET_CONTRACT_V1.md`
- `docs/architecture/DATASET_FORMAT.md`
- `tests/services/channel_export/test_channel_export_dataset_contracts.py`
- `tests/services/channel_export/test_channel_export_service.py`
- `tests/services/channel_export/test_channel_export_included_files_builder.py`
- `tests/services/dataset_validation/test_dataset_validation_contracts.py`
- `tg_msg_manager/services/channel_export/run_changelog.py`
- `tg_msg_manager/services/channel_export/included_files_builder.py`
- `tg_msg_manager/services/channel_export/payload_writer.py`
- `tg_msg_manager/services/channel_export/media_policy.py`
- `tg_msg_manager/services/channel_export/post_mapper.py`

## 3. HARD PROHIBITIONS

- Do not change Python runtime code.
- Do not change tests except to correct comments or references directly scoped by this stage.
- Do not change CLI commands, defaults, output filenames, dataset schema, SQLite schema, migrations, or `PRAGMA user_version`.
- Do not inspect ignored export directories, local databases, sessions, logs, or private artifacts.
- Do not read unrelated completed stages, reports, roadmap, or archive files.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Re-check each current matrix gap against the listed code/tests only.
2. Classify every gap as `test-only`, `docs-only`, `behavior-mismatch`, or `out-of-scope`.
3. Record the closure order:
   - 5D.2 run changelog key set tests.
   - 5D.3 TXT projection contract clarification.
   - 5D.4 channel export mode matrix tests.
   - 5D.5 safe first export guide.
4. Mark non-channel dataset families as out of Dataset Contract V1 unless a later stage explicitly scopes separate contracts.
5. Create the Stage 5D.1 report in Russian.

## 5. REQUIRED DOCS

- Update `docs/architecture/DATASET_CONTRACT_COVERAGE_MATRIX.md` only if the factual gap inventory or closure order is stale.
- Do not update user-facing docs in this stage.

## 6. TESTS / VERIFICATION

- `git diff --check`
- Code tests are not required unless this stage changes tests or Python code. If that happens, stop unless the change is a direct documentation-reference correction.

## 7. REPORT

Create `docs/stages/reports/STAGE_5D_1_DATASET_CONTRACT_GAP_CLOSURE_PLAN_REPORT.md` in Russian.

The report must include:

- inspected files;
- final gap classification;
- final 5D execution order;
- explicit note that no runtime behavior, CLI, dataset format, or SQLite behavior changed;
- skill lines:
  - `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
  - `architecture-guard: applied from .skills/architecture-guard/SKILL.md`

## 8. COMPLETION CRITERIA

- Gap closure plan is recorded.
- Required docs are updated or explicitly confirmed current in the report.
- Verification is run or documented as not applicable.
- `stage-completion-auditor` is applied after the report.
- Lifecycle cleanup is completed according to `AGENTS.md`; do not move unrelated later active files.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Do not continue to Stage 5D.2.
