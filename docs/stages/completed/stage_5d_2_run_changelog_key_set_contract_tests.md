# STAGE 5D.2 — RUN CHANGELOG KEY SET CONTRACT TESTS

Status: active task
Stage: 5D.2
Type: tests/docs
Depends on: `docs/stages/reports/STAGE_5D_1_DATASET_CONTRACT_GAP_CLOSURE_PLAN_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` first.
- Read the Stage 5D.1 report before editing.
- Apply `stage-reviewer` before edits.
- Apply `architecture-guard` because this stage touches dataset contract tests.
- Write a plan with max 5 bullets before editing.
- Do not implement Stage 5D.3 or later.

## 1. PURPOSE

Add regression tests that assert the exact `run_changelog.jsonl` contract documented in Dataset Contract V1.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/reports/STAGE_5D_1_DATASET_CONTRACT_GAP_CLOSURE_PLAN_REPORT.md`
- `docs/architecture/DATASET_CONTRACT_V1.md`
- `docs/architecture/DATASET_FORMAT.md`
- `docs/architecture/DATASET_CONTRACT_COVERAGE_MATRIX.md`
- `tg_msg_manager/services/channel_export/run_changelog.py`
- `tg_msg_manager/services/channel_export/workflows/context.py`
- `tests/services/channel_export/test_channel_export_run_summary.py`
- `tests/services/channel_export/test_channel_export_dataset_contracts.py`
- `tests/services/channel_export/test_channel_export_service.py`
- `tests/fixtures/dataset_validation/valid_minimal_channel_dataset/run_changelog.jsonl`
- `tests/fixtures/dataset_validation/valid_discussion_dataset/run_changelog.jsonl`
- `tests/fixtures/dataset_validation/partial_discussion_dataset/run_changelog.jsonl`

## 3. HARD PROHIBITIONS

- Do not add product behavior.
- Do not change output filenames, JSON key names, run mode labels, CLI flags, or SQLite code.
- Do not store message text in `run_changelog.jsonl`.
- Do not change `ChannelExportService` except for mechanical wiring if an existing dependency injection path is broken.
- Do not inspect private export artifacts.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Define one expected top-level key set for `run_changelog.jsonl` in the relevant channel export contract test file.
2. Assert exact top-level keys for writer output.
3. Assert exact `artifact_paths` keys for writer output.
4. Assert no message text field exists in the changelog payload.
5. Assert fixture changelog rows match the same key set.
6. If current code differs from docs, stop and report the mismatch unless the fix is limited to a test fixture or docs typo.

## 5. REQUIRED DOCS

- Update `docs/architecture/DATASET_CONTRACT_COVERAGE_MATRIX.md` to mark the changelog key-set gap closed.
- Do not change `DATASET_CONTRACT_V1.md` or `DATASET_FORMAT.md` unless they are internally inconsistent with existing behavior.

## 6. TESTS / VERIFICATION

- `python3 -m pytest tests/services/channel_export/test_channel_export_run_summary.py tests/services/channel_export/test_channel_export_dataset_contracts.py -q`
- `python3 -m pytest tests/services/dataset_validation/test_dataset_validation_contracts.py -q`
- `git diff --check`

## 7. REPORT

Create `docs/stages/reports/STAGE_5D_2_RUN_CHANGELOG_KEY_SET_CONTRACT_TESTS_REPORT.md` in Russian.

The report must include:

- exact tests added or changed;
- whether fixtures were changed;
- verification results;
- confirmation that CLI, dataset filenames, SQLite, and runtime behavior were preserved;
- skill lines:
  - `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
  - `architecture-guard: applied from .skills/architecture-guard/SKILL.md`

## 8. COMPLETION CRITERIA

- Changelog top-level keys are covered by tests.
- Changelog `artifact_paths` keys are covered by tests.
- Matrix gap is updated.
- `stage-completion-auditor` is applied after the report.
- Lifecycle cleanup is completed according to `AGENTS.md`; do not move unrelated later active files.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Do not continue to Stage 5D.3.
