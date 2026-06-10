# STAGE 5P.1 — RUFF FORMATTING REMEDIATION

Status: active task
Stage: 5P.1
Type: bugfix
Depends on: `docs/stages/reports/STAGE_5P_POST_REFACTOR_FULL_VERIFICATION_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply `.skills/stage-reviewer/SKILL.md`,
`.skills/architecture-guard/SKILL.md`, and
`.skills/stage-completion-auditor/SKILL.md` after report/cleanup.

Fix only the observed Ruff formatting failure. Do not start Stage 5Q.

## 1. SYMPTOM

Stage 5P recorded that `ruff format --check tg_msg_manager tests` and
`make verify` fail because nine files require Ruff formatting.

## 2. REPRODUCTION / OBSERVED OUTPUT

`ruff format --check tg_msg_manager tests` reported exactly nine files that
would be reformatted, as recorded in the Stage 5P report.

## 3. LIKELY CAUSE

Likely cause:

- Stage 5N/5O changes were not formatted with the currently configured Ruff.

## 4. FILES TO INSPECT

Required and writable:

- `tests/architecture/test_static_boundaries.py`
- `tests/core/test_config.py`
- `tests/infrastructure/storage/test_target_names_history_storage.py`
- `tests/services/channel_export/discussions/test_channel_export_discussion_artifact_builder.py`
- `tg_msg_manager/cli/commands/target_names.py`
- `tg_msg_manager/infrastructure/storage/read/target_names.py`
- `tg_msg_manager/infrastructure/storage/records.py`
- `tg_msg_manager/services/channel_export/discussions/artifact_builder.py`
- `tg_msg_manager/services/dataset_validation/inspector.py`
- `docs/stages/reports/STAGE_5P_1_RUFF_FORMATTING_REMEDIATION_REPORT.md`
- `docs/stages/README.md`
- lifecycle move of this stage file

May read:

- `AGENTS.md`
- this stage file
- `docs/stages/reports/STAGE_5P_POST_REFACTOR_FULL_VERIFICATION_REPORT.md`

Do not read or change unrelated source, tests, docs, archives, or reports.

## 5. HARD PROHIBITIONS

- Do not add features, tests, dependencies, or broad refactors.
- Do not manually change logic; apply Ruff formatting only to the nine files.
- Do not change CLI behavior, output formats, SQLite schema, data flow, dataset
  contracts, versions, tags, or package state.
- Do not start Stage 5Q.

## 6. MINIMAL PATCH TASKS

1. Confirm the nine files match the Stage 5P failure.
2. Run Ruff formatter only on those nine files.
3. Inspect the resulting diff for formatting-only changes.
4. Run focused and full verification.
5. Create the Russian report and complete lifecycle cleanup.

## 7. REGRESSION TESTS

No new test is required because the defect is formatting-only. Existing focused
and full test suites must pass.

## 8. NON-REGRESSION CHECKS

Required:

```bash
git diff --check
ruff format --check tg_msg_manager tests
ruff check tg_msg_manager tests
pytest tests/architecture tests/core/test_config.py tests/infrastructure/storage/test_target_names_history_storage.py tests/services/channel_export/discussions/test_channel_export_discussion_artifact_builder.py
pytest
make verify
```

Do not claim a command passed unless it ran successfully.

## 9. REQUIRED DOCS

Required:

- `docs/stages/reports/STAGE_5P_1_RUFF_FORMATTING_REMEDIATION_REPORT.md`
- `docs/stages/README.md`

Do not update user-facing docs because behavior does not change.

## 10. REPORT

Record exact files changed, exact checks run, formatting defect fixed, behavior
preserved, commands not run and why, applied skill paths, and lifecycle notes.

## 11. COMPLETION CRITERIA

- Only the nine identified files receive formatting-only production/test edits.
- All required checks pass.
- Report exists and lifecycle cleanup is complete.
- Stage 5Q remains unstarted.

## 12. OUTPUT LIMITS

Use the compact `AGENTS.md` final format. Do not paste full diffs.
