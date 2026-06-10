# STAGE 5P.2 — TARGET IDENTITY HISTORY DUPLICATE OBSERVATION REMEDIATION

Status: completed
Stage: 5P.2
Type: bugfix
Depends on: failing Stage 5P `pytest` identity-history regression

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Fix the observed bug with the smallest safe patch.
Do not start later stages, add features, or change public CLI behavior, output
formats, SQLite schema, or data flow except as required by this bug fix.

## 1. SYMPTOM

`test_save_message_refreshes_target_current_author_name_and_history` sometimes
records the initial `Target User` identity twice before `Renamed User`.

## 2. REPRODUCTION / OBSERVED OUTPUT

```bash
pytest tests/infrastructure/storage/test_storage_sqlite.py::TestSQLiteStorage::test_save_message_refreshes_target_current_author_name_and_history
```

Expected names: `["Target User", "Renamed User"]`.
Observed names: `["Target User", "Target User", "Renamed User"]`.

## 3. LIKELY CAUSE

An initial target observation without username and the first message observation
with the same author name plus username can land in adjacent seconds and be
recorded as separate identity changes instead of one enriched observation.

## 4. FILES TO INSPECT

Required:

- `tg_msg_manager/infrastructure/storage/_sqlite_identity.py`
- `tests/infrastructure/storage/test_storage_sqlite.py`

May read: `AGENTS.md`, this stage file, and affected storage tests only.

## 5. HARD PROHIBITIONS

- No features, broad refactors, schema changes, CLI changes, or dependencies.
- Do not change unrelated source/tests/docs or protected files.
- Do not add analytics, OSINT, profiling, OCR/STT, media, or LLM behavior.

## 6. MINIMAL PATCH TASKS

1. Confirm the duplicate path without editing.
2. Merge compatible partial identity observations into the latest snapshot.
3. Strengthen the existing focused regression test.
4. Run focused and non-regression verification.

## 7. REGRESSION TESTS

- Existing failing identity-history test must pass and verify enrichment data.

## 8. NON-REGRESSION CHECKS

- Identity changes still create distinct snapshots.
- SQLite schema, CLI, dataset/export behavior, and public formats remain unchanged.

## 9. REQUIRED DOCS

Required report:
`docs/stages/reports/STAGE_5P_2_TARGET_IDENTITY_HISTORY_DUPLICATE_OBSERVATION_REMEDIATION_REPORT.md`.

## 10. REPORT

Record exact files changed, checks run, bug fixed, preserved behavior, and status.

## 11. COMPLETION CRITERIA

Minimal fix and regression coverage pass; report and lifecycle cleanup complete.

## 12. OUTPUT LIMITS

Use the compact `AGENTS.md` final response format.
