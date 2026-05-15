# STAGE 4B.3 — RUN CHANGELOG ARTIFACT

Status: completed  
Stage: 4B.3  
Type: incremental export artifact hardening stage  
Priority: after Stage 4B.2 validation hardening  
Execution status: completed  
Depends on: completed Stage 4B.1 audit and Stage 4B.2 validation hardening

---

## 0. CODEX ENTRY CONTRACT

This file has been executed and is now historical.

The executed stage followed `AGENTS.md` and produced `docs/stages/reports/STAGE_4B_3_RUN_CHANGELOG_ARTIFACT_REPORT.md`.

Do not start this stage unless Stage 4B.1 and Stage 4B.2 reports exist.

This stage is limited to producing a per-run changelog or documenting and testing an existing equivalent artifact. It must not introduce AI chunks, analytics, OSINT, profiling, or new persistence.

---

## 1. PURPOSE

Make incremental exports auditable by recording what changed during each export run.

The user must be able to answer:

- how many messages/posts were newly exported in this run;
- which message IDs were added;
- what timestamp range was added;
- what export state/cursor existed before and after the run;
- whether the run appended, skipped, retried, or produced no changes;
- where the canonical data and derived readable artifacts are located.

---

## 2. ARTIFACT CONTRACT

Preferred artifact name:

- `run_changelog.jsonl`

Optional readable projection if useful and explicitly scoped during active-stage conversion:

- `run_changelog.md`

Each changelog entry should be derived from already available export data and state. Do not add DB persistence.

Minimum JSONL fields, if implemented:

- `run_id`;
- `export_target_type`;
- `export_target_id`;
- `export_target_name` if available;
- `started_at`;
- `finished_at` if available;
- `previous_cursor` or equivalent previous state;
- `new_cursor` or equivalent new state;
- `new_message_count`;
- `first_new_message_id`;
- `last_new_message_id`;
- `first_new_message_date`;
- `last_new_message_date`;
- `artifact_paths`;
- `warnings` if produced by the run.

If the current implementation already has an equivalent artifact, document the equivalence instead of adding a new file.

---

## 3. FILES TO INSPECT

Read only these files/directories unless the active stage adds more:

- `AGENTS.md`
- `COMMANDS.md`
- `README.md`
- `docs/architecture/DATASET_FORMAT.md`
- `docs/stages/reports/STAGE_4B_1_DATASET_INTEGRITY_AUDIT_REPORT.md`
- `docs/stages/reports/STAGE_4B_2_DATASET_VALIDATION_HARDENING_REPORT.md`
- `tg_msg_manager/services/channel_export/`
- `tg_msg_manager/services/db_export/`
- `tg_msg_manager/services/export/`
- `tests/test_channel_export_*.py`
- `tests/test_db_export_components.py`

Do not inspect archive or completed stage files unless the active stage explicitly asks for historical comparison.

---

## 4. HARD PROHIBITIONS

- No SQLite schema changes.
- No DB persistence for changelog rows.
- No validation-rule work except compatibility updates required by the changelog artifact.
- No AI-friendly chunk generation.
- No analytics, OSINT, profiling, classification, OCR, speech-to-text, media analysis, or LLM report generation.
- No change to canonical JSONL unless explicitly scoped with fixtures, docs, and compatibility notes.
- No change to existing CLI defaults unless explicitly documented and covered by tests.
- No broad refactor of protected service facades.

---

## 5. ATOMIC IMPLEMENTATION TASKS

1. Read Stage 4B.1 and 4B.2 reports and extract incremental/changelog-related findings.
2. Identify current run counters, append behavior, state/cursor logic, and manifest fields.
3. Decide whether current artifacts are sufficient or whether `run_changelog.jsonl` is required.
4. If current artifacts are sufficient, document the contract and add tests proving equivalence.
5. If `run_changelog.jsonl` is required, define the minimal schema and keep it derived from existing run data.
6. Implement changelog writing in the narrowest existing export boundary that already knows run state and new records.
7. Ensure no-op runs are represented clearly or explicitly documented as not producing entries.
8. Ensure retry/partial-run behavior is documented and tested where current architecture supports it.
9. Add focused tests for first run, append run, no-new-message run, and warning/partial cases where feasible.
10. Update `README.md`, `COMMANDS.md`, and `DATASET_FORMAT.md` with the artifact contract.
11. Write the stage report.

---

## 6. REQUIRED DOCS

Update when behavior changes:

- `README.md`
- `COMMANDS.md`
- `docs/architecture/DATASET_FORMAT.md`
- `docs/architecture/DATASET_VALIDATION.md` only if validators reference changelog state
- `docs/development/LIVE_SMOKE_CHECKLIST.md` only if smoke procedure changes

Add a factual report under:

- `docs/stages/reports/STAGE_4B_3_RUN_CHANGELOG_ARTIFACT_REPORT.md`

---

## 7. TESTS / VERIFICATION

Run focused tests first:

```bash
pytest tests/test_channel_export_*.py
pytest tests/test_db_export_components.py
```

Then run broader checks if dataset contracts or CLI behavior changed:

```bash
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
make verify
```

If a command cannot be run, record the exact reason in the report.

---

## 8. REPORT

The report must be in Russian and include:

- whether a new changelog artifact was added or existing artifacts were documented as sufficient;
- exact changelog schema if added;
- files changed;
- tests run and results;
- behavior preserved or intentionally changed;
- SQLite/schema statement;
- known limitations, especially retry/no-op/partial-run behavior.

---

## 9. COMPLETION CRITERIA

The stage is complete only when:

- changelog behavior is explicit and tested;
- docs match runtime behavior;
- no DB persistence was added;
- no AI chunking or analytics was added;
- report exists;
- lifecycle cleanup is completed according to `AGENTS.md`.

---

## 10. OUTPUT LIMITS

Agent final response must follow `AGENTS.md`.

Do not paste full diffs, full reports, or large file excerpts.
