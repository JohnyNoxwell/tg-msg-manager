# STAGE 7A.2 — FIXTURE CONTRACT SNAPSHOT GATE

Status: active task
Stage: 7A.2
Type: implementation
Depends on: Stage 7A.1 completed with pytest as the authoritative `make test` runner

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Execute only Stage 7A.2.

Goal:
Add a mandatory fixture-backed contract snapshot gate for existing synthetic dataset/export fixtures.

Do not start Stage 7A.3.

Use AGENTS.md compact output format.

## 1. PURPOSE

Protect data pipeline output contracts with deterministic fixture expectations that run in `make verify`.

## 2. FILES TO INSPECT

Required:
- `AGENTS.md`
- `Makefile`
- `pyproject.toml`
- `tests/fixtures/`
- `tests/services/channel_export/`
- `tests/services/db_export/`
- `tests/services/rendering/`
- `tests/services/dataset_validation/`
- `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md`
- `docs/development/DEFERRED_CONTRACT_COVERAGE_PRIORITIZATION.md`
- `docs/development/LOCAL_VERIFICATION_MATRIX.md`
- `docs/stages/README.md`

May create or change only if required:
- focused tests under `tests/`
- fixture contract docs under `docs/development/`
- `docs/stages/reports/STAGE_7A_2_FIXTURE_CONTRACT_SNAPSHOT_GATE_REPORT.md`

Do not inspect or change:
- unrelated source modules;
- unrelated docs;
- `docs/archive`;
- existing `docs/stages/reports` files unrelated to this stage.

## 3. HARD PROHIBITIONS

Do not change fixture semantics to make tests pass.
Do not change product behavior.
Do not change CLI names, flags, defaults, outputs, or behavior.
Do not change SQLite schema or migrations.
Do not change dataset/export formats unless the stage is stopped as blocked.
Do not add runtime dependencies.
Do not add analytics, profiling, OSINT, OCR, STT, media analysis, or LLM-dependent logic.
Do not modify protected service facades or compatibility wrappers.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Inventory existing checked-in synthetic fixture contracts.
2. Add a narrow pytest contract/snapshot test or test group that fails on unexpected fixture output drift.
3. Wire the contract/snapshot group into `make verify` through the existing `make test` path.
4. Document the fixture contract gate and update any affected development docs.
5. Create a factual report and complete lifecycle cleanup if checks pass.

## 5. REQUIRED DOCS

Required:
- `docs/development/LOCAL_VERIFICATION_MATRIX.md`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_7A_2_FIXTURE_CONTRACT_SNAPSHOT_GATE_REPORT.md`

Update only if changed:
- `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md`
- `docs/development/DEFERRED_CONTRACT_COVERAGE_PRIORITIZATION.md`

## 6. TESTS / VERIFICATION

Required:

```bash
python3 -m pytest tests -q
make verify
git diff --check
make pre-commit
```

If `make pre-commit` would format unrelated pre-existing dirty files, stop and report the blocker instead of modifying them.

Do not claim checks passed unless actually run.

## 7. REPORT

Create:

```text
docs/stages/reports/STAGE_7A_2_FIXTURE_CONTRACT_SNAPSHOT_GATE_REPORT.md
```

The report must be factual and written in Russian.

Record:
- fixture contract scope;
- exact tests added or changed;
- exact checks run;
- files changed;
- preserved behavior/schema/CLI;
- completion status.

## 8. COMPLETION CRITERIA

This stage is complete when:

- fixture contract/snapshot gate runs through `make verify`;
- required docs and report exist;
- `make verify` passes after changes;
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must use AGENTS.md format.
Do not paste full diffs.
Do not include broad roadmap text.
Keep notes compact.
