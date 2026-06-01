# STAGE 5C.0 — DATASET CONTRACT COVERAGE MATRIX

Status: completed
Stage: 5C.0
Type: documentation / test coverage audit
Depends on: Stage 5C.1 complete; `docs/architecture/DATASET_CONTRACT_V1.md`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Execute Stage 5C.0 only.

Goal:
Create a coverage matrix that maps Dataset Contract V1 requirements to current docs, tests, fixtures, and gaps.

Do not start Stage 5C.2 or later stages.
Do not change exporter behavior, validation behavior, dataset formats, CLI behavior, or SQLite schema.
Use `AGENTS.md` compact output format.

## 1. PURPOSE

Make dataset contract coverage explicit before further expansion. The output is a factual matrix, not a new dataset contract and not permission to change behavior.

## 2. FILES TO INSPECT

Required:
- `AGENTS.md`
- this stage file
- `docs/architecture/DATASET_CONTRACT_V1.md`
- `docs/architecture/DATASET_FORMAT.md`
- `docs/architecture/DATASET_VALIDATION.md`
- `tests/services/channel_export/test_channel_export_dataset_contracts.py`
- `tests/services/dataset_validation/test_dataset_validation_contracts.py`
- `tests/fixtures/dataset_validation/`

May change:
- `docs/architecture/DATASET_CONTRACT_COVERAGE_MATRIX.md`
- `docs/architecture/README.md`
- `docs/stages/reports/STAGE_5C_0_DATASET_CONTRACT_COVERAGE_MATRIX_REPORT.md`
- `docs/stages/README.md`
- this stage file location during lifecycle cleanup

Do not read or change:
- runtime channel export implementation unless a test/doc reference cannot be understood without one exact file;
- ignored local export artifacts;
- unrelated docs, archive files, or completed stage files.

## 3. HARD PROHIBITIONS

- Do not change dataset JSONL, TXT, manifest, state, media, discussion, or changelog behavior.
- Do not change validators, inspector, doctor, or CLI handlers.
- Do not add tests unless a matrix assertion needs a small docs-only fixture reference test; prefer no code changes.
- Do not add analytics, OSINT, profiling, classification, OCR, STT, media recognition, or LLM-dependent logic.
- Do not change SQLite schema or persistence.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Inventory contract rows.
   - List artifacts and modes from `DATASET_CONTRACT_V1.md`.
   - Include files, key sets, status labels, mode matrix, failure contract, validation boundary, and non-channel dataset status.
   - Do not edit yet.

2. Map coverage.
   - For each row, record coverage source: architecture doc, unit test, fixture, validator test, or gap.
   - Use `UNKNOWN_NEEDS_CHECK` only when current docs/tests do not prove coverage.

3. Write the matrix doc.
   - Create `docs/architecture/DATASET_CONTRACT_COVERAGE_MATRIX.md`.
   - A compact Markdown table is allowed in this matrix doc.
   - Each row must include: contract area, expected status, current coverage, gap or next stage.

4. Index the doc.
   - Add the matrix to `docs/architecture/README.md`.
   - Do not duplicate the matrix elsewhere.

5. Verify and report.
   - Run section 6 checks.
   - Create the Russian report.
   - Perform lifecycle cleanup only after the report exists.

## 5. REQUIRED DOCS

Required:
- `docs/architecture/DATASET_CONTRACT_COVERAGE_MATRIX.md`
- `docs/architecture/README.md`
- `docs/stages/reports/STAGE_5C_0_DATASET_CONTRACT_COVERAGE_MATRIX_REPORT.md`
- `docs/stages/README.md` during lifecycle cleanup

No README/COMMANDS changes unless the matrix discovers stale user-facing behavior documentation and the correction is strictly factual.

## 6. TESTS / VERIFICATION

Run:
- `python3 -m pytest tests/services/channel_export/test_channel_export_dataset_contracts.py tests/services/dataset_validation/test_dataset_validation_contracts.py -q`
- `python3 -m compileall tg_msg_manager`
- `git diff --check`

If docs-only changes make the focused pytest command unnecessary, still run it because the matrix depends on those tests.

## 7. REPORT

Create `docs/stages/reports/STAGE_5C_0_DATASET_CONTRACT_COVERAGE_MATRIX_REPORT.md` in Russian.

Include:
- files inspected;
- matrix file created;
- coverage gaps found;
- checks run;
- confirmation that runtime, CLI, dataset formats, and SQLite schema were unchanged;
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`.

## 8. COMPLETION CRITERIA

- Matrix exists and is indexed.
- Matrix does not redefine behavior beyond current contract/docs/tests.
- Gaps are recorded as gaps, not silently implemented.
- Required checks are run or exact blockers are recorded.
- lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- No full diffs.
- No broad summaries.
- No markdown tables in the final response.
