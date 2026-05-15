# STAGE 4B.1 — DATASET INTEGRITY AUDIT ONLY

Status: completed  
Stage: 4B.1  
Type: factual audit stage  
Priority: after current active work  
Execution status: completed  
Depends on: current `export-channel`, `validate-dataset`, `inspect-dataset`, user/group `export`, and `db-export` behavior

---

## 0. CODEX ENTRY CONTRACT

This file has been executed and is now historical. It is not an active task.

The executed stage followed `AGENTS.md` and produced `docs/stages/reports/STAGE_4B_1_DATASET_INTEGRITY_AUDIT_REPORT.md`.

This stage is audit-only. Do not modify runtime behavior. Do not add features. Do not add new dataset artifacts. Do not change CLI defaults. Do not change tests unless the active-stage conversion explicitly scopes report-only or documentation verification.

The required output is a factual implementation-status report that separates implemented, partially implemented, missing, intentionally unsupported, and unsafe-to-change items.

---

## 1. PURPOSE

Create a factual baseline for the current export dataset pipeline before any dataset-integrity or AI-readiness hardening work begins.

The audit must answer whether the current implementation already supports, partially supports, or lacks the following capabilities:

- reliable incremental export;
- manifest per export;
- changelog or equivalent summary of newly exported messages;
- stable message IDs and stable media IDs;
- duplicate detection;
- message-ID gap detection;
- reply-link validation;
- media-link validation;
- separation of canonical raw JSON/JSONL and readable TXT/MD projections;
- AI-friendly output with chunks, context, metadata, authors, reply references, dates, and message IDs.

---

## 2. CURRENT SNAPSHOT TO VERIFY

Treat this snapshot as a hypothesis, not as truth. Verify it against code, docs, fixtures, and tests.

Expected mostly implemented:

- incremental channel export state/cursor behavior;
- manifest generation;
- stable Telegram `message_id` usage;
- stable media ID/path behavior;
- duplicate post validation;
- media manifest path/status validation;
- raw `messages.jsonl` plus readable `messages.txt` for channel export.

Expected partially implemented:

- new-message summary through run counters and append behavior, but no standalone per-run changelog artifact;
- reply IDs and readable reply markers, but no full dataset-level reply-chain validation;
- AI-friendly output for user/group DB export and context-readable TXT, but no complete chunked AI contract for channel export.

Expected missing or unclear:

- message-ID gap detection for channel datasets;
- Markdown projection as a formal dataset artifact;
- full reply-chain reconstruction or validation for exported datasets;
- stable validation-report contract with explicit warning/error codes for all integrity findings.

---

## 3. FILES TO INSPECT

Read only these files/directories unless the active stage explicitly adds more:

- `AGENTS.md`
- `COMMANDS.md`
- `README.md`
- `docs/architecture/README.md`
- `docs/architecture/DATASET_VALIDATION.md`
- `docs/architecture/DATASET_FORMAT.md`
- `tg_msg_manager/services/channel_export/`
- `tg_msg_manager/services/dataset_validation/`
- `tg_msg_manager/services/rendering/`
- `tg_msg_manager/services/db_export/`
- `tests/test_channel_export_*.py`
- `tests/test_dataset_validation_contracts.py`
- `tests/test_context_readable_txt_renderer.py`
- `tests/test_db_export_components.py`
- `tests/fixtures/dataset_validation/`

Do not inspect archive or completed stage files unless the active stage explicitly asks for historical comparison.

---

## 4. HARD PROHIBITIONS

- No runtime code changes.
- No SQLite schema changes.
- No new dataset artifacts.
- No validator rule changes.
- No CLI behavior changes.
- No analytics, OSINT, profiling, classification, OCR, speech-to-text, media analysis, or LLM report generation.
- No broad refactor of protected service facades.
- No formatting churn.
- No migration of legacy scripts.
- No inference-based claims in the report without pointing to exact files/tests/docs.

---

## 5. AUDIT TASKS

1. Read `AGENTS.md` and record the lifecycle rules that apply to this stage.
2. Inspect current dataset-producing flows:
   - channel export;
   - dataset validation;
   - dataset inspection;
   - user/group export;
   - DB export;
   - readable rendering.
3. Build a checklist table with one row per capability from section 1.
4. For each row, record:
   - status: implemented / partial / missing / intentionally unsupported / unsafe-to-change;
   - evidence files;
   - tests or fixtures that prove the behavior;
   - known gaps;
   - whether the item should be handled in Stage 4B.2, 4B.3, or 4B.4.
5. Identify current canonical artifacts and derived artifacts.
6. Identify current validation warnings/errors and whether they have stable codes.
7. Identify current append/incremental behavior and what evidence exists for newly exported messages.
8. Identify places where future work would require docs, fixtures, or compatibility notes.
9. Write the factual report.

---

## 6. REQUIRED REPORT

Create or update:

- `docs/stages/reports/STAGE_4B_1_DATASET_INTEGRITY_AUDIT_REPORT.md`

The report must be in Russian and include:

- stage scope;
- files inspected;
- checklist table with statuses;
- current artifact inventory;
- current validation behavior;
- current incremental behavior;
- current AI-friendly/readable behavior;
- items deferred to Stage 4B.2, 4B.3, and 4B.4;
- tests run and results;
- commands not run and exact reasons;
- SQLite/schema statement;
- known limitations;
- final recommendation: proceed / do not proceed to Stage 4B.2.

---

## 7. VERIFICATION

Run focused read-only checks where possible:

```bash
pytest tests/test_dataset_validation_contracts.py
pytest tests/test_channel_export_*.py
pytest tests/test_context_readable_txt_renderer.py
pytest tests/test_db_export_components.py
```

If test execution is not possible, record the exact command and reason in the report.

Do not run broad formatting tools unless the active stage explicitly allows them.

---

## 8. COMPLETION CRITERIA

The stage is complete only when:

- no runtime behavior was changed;
- the audit report exists;
- every capability from section 1 has a status and evidence;
- future work is assigned to Stage 4B.2, 4B.3, or 4B.4;
- tests run or non-run reasons are recorded;
- SQLite/schema statement is recorded;
- lifecycle cleanup follows `AGENTS.md`.

---

## 9. OUTPUT LIMITS

Agent final response must follow `AGENTS.md`.

Do not paste full diffs, full reports, or large file excerpts.
