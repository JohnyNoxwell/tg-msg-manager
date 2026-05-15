# STAGE 4B.2 — DATASET VALIDATION HARDENING

Status: completed  
Stage: 4B.2  
Type: validation hardening stage  
Priority: after Stage 4B.1 audit  
Execution status: completed  
Depends on: completed `STAGE_4B_1_DATASET_INTEGRITY_AUDIT_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

This file has been executed and is now historical.

The executed stage followed `AGENTS.md` and produced `docs/stages/reports/STAGE_4B_2_DATASET_VALIDATION_HARDENING_REPORT.md`.

Do not start this stage unless Stage 4B.1 has produced a factual audit report and that report recommends proceeding.

This stage is limited to dataset validation hardening. It must not introduce AI chunks, changelog artifacts, analytics, OSINT, profiling, or new persistence.

---

## 1. PURPOSE

Harden local validation of exported Telegram datasets so integrity issues are detected, classified, and reported without mutating exported data.

This stage focuses on:

- duplicate detection;
- message-ID gap detection;
- reply-link validation;
- discussion reply-link validation where supported by current exported records;
- media-link validation;
- stable validation warning/error codes;
- validation report documentation and fixtures.

---

## 2. DATASET CONTRACT RULES

- Canonical JSONL remains the source of truth.
- Validation must never mutate exported data.
- Validation findings must be emitted as stable warning/error codes.
- Validation must distinguish warnings from errors.
- Gaps must default to warnings unless exporter data loss is proven.
- Missing reply parents must distinguish, where possible:
  - parent is outside export scope;
  - parent was deleted or unavailable;
  - parent is missing despite being expected in the exported range;
  - validation cannot determine the cause.
- Media-link validation must check exported metadata against available manifest/path/status information without downloading media.
- No validator rule may silently reinterpret canonical dataset format.

---

## 3. FILES TO INSPECT

Read only these files/directories unless the active stage adds more:

- `AGENTS.md`
- `COMMANDS.md`
- `README.md`
- `docs/architecture/DATASET_VALIDATION.md`
- `docs/architecture/DATASET_FORMAT.md`
- `docs/stages/reports/STAGE_4B_1_DATASET_INTEGRITY_AUDIT_REPORT.md`
- `tg_msg_manager/services/dataset_validation/`
- `tg_msg_manager/services/channel_export/`
- `tests/test_dataset_validation_contracts.py`
- `tests/test_channel_export_*.py`
- `tests/fixtures/dataset_validation/`

Do not inspect archive or completed stage files unless the active stage explicitly asks for historical comparison.

---

## 4. HARD PROHIBITIONS

- No SQLite schema changes.
- No DB persistence for validation results.
- No changelog artifact work.
- No AI-friendly chunk generation.
- No analytics, OSINT, profiling, classification, OCR, speech-to-text, media analysis, or LLM report generation.
- No external services.
- No destructive repair of exported data.
- No change to existing CLI defaults unless explicitly documented and covered by tests.
- No broad refactor of protected service facades.
- No dataset format change without fixtures, docs, and compatibility notes.

---

## 5. ATOMIC IMPLEMENTATION TASKS

1. Read the Stage 4B.1 audit report and extract validation-related missing/partial items.
2. Confirm the current canonical dataset fields used for message identity, reply references, media references, and export scope.
3. Define stable validation codes for new or clarified findings.
4. Add or harden duplicate detection only if the audit shows it is missing or incomplete.
5. Add message-ID gap detection with warning-level findings by default.
6. Ensure gap detection avoids false certainty where Telegram-deleted or unavailable messages cannot be distinguished from exporter loss.
7. Add reply-link validation for `reply_to_id` when the parent should be available in the exported dataset.
8. Add discussion reply-link validation only for relationships represented in current exported records.
9. Add explicit findings for reply parents outside scope, missing, unavailable, or indeterminate where the data supports that distinction.
10. Harden media-link validation against manifest/path/status data already produced by current export flows.
11. Add or update fixtures for each new validation finding.
12. Add or update focused tests for every new warning/error code.
13. Update dataset validation docs with codes, severity, meaning, and expected remediation.
14. Update command docs only if user-visible validation output changes.
15. Write the stage report.

---

## 6. REQUIRED DOCS

Update when behavior changes:

- `README.md`
- `COMMANDS.md`
- `docs/architecture/DATASET_VALIDATION.md`
- `docs/architecture/DATASET_FORMAT.md` if canonical assumptions or documented fields change
- `docs/development/LIVE_SMOKE_CHECKLIST.md` only if smoke procedure changes

Add a factual report under:

- `docs/stages/reports/STAGE_4B_2_DATASET_VALIDATION_HARDENING_REPORT.md`

---

## 7. TESTS / VERIFICATION

Run focused tests first:

```bash
pytest tests/test_dataset_validation_contracts.py
pytest tests/test_channel_export_*.py
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

- final status for each validation item;
- validation codes added or changed;
- severity of each finding;
- files changed;
- fixtures added or changed;
- tests run and results;
- behavior preserved or intentionally changed;
- SQLite/schema statement;
- known limitations.

---

## 9. COMPLETION CRITERIA

The stage is complete only when:

- Stage 4B.1 audit findings were used as input;
- validation changes are covered by fixtures and tests;
- docs match runtime behavior;
- no exported data is mutated by validation;
- report exists;
- lifecycle cleanup is completed according to `AGENTS.md`.

---

## 10. OUTPUT LIMITS

Agent final response must follow `AGENTS.md`.

Do not paste full diffs, full reports, or large file excerpts.
