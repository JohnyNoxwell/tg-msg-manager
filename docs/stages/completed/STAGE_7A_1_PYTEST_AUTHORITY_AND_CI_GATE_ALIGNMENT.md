# STAGE 7A.1 — PYTEST AUTHORITY AND CI GATE ALIGNMENT

Status: complete
Stage: 7A.1
Type: implementation
Depends on: `docs/stages/reports/STAGE_7A_0_TEST_INFRASTRUCTURE_BASELINE_AND_HARDENING_PLAN_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Execute only Stage 7A.1.

Goal:
Make pytest the authoritative test runner used by local `make test` and CI `make verify`, without changing product behavior.

Do not start Stage 7A.2 or 7A.3.

Use AGENTS.md compact output format.

## 1. PURPOSE

Align the declared dev dependency on pytest with the actual mandatory gate so future contract and snapshot tests can rely on pytest behavior.

## 2. FILES TO INSPECT

Required:
- `AGENTS.md`
- `Makefile`
- `.github/workflows/ci.yml`
- `pyproject.toml`
- `docs/development/README.md`
- `docs/development/LOCAL_VERIFICATION_MATRIX.md`
- `docs/development/PR_CHECKLIST.md`
- `docs/stages/README.md`

May inspect only if needed:
- `tests/`

May create:
- `docs/stages/reports/STAGE_7A_1_PYTEST_AUTHORITY_AND_CI_GATE_ALIGNMENT_REPORT.md`

Do not inspect or change:
- source modules;
- unrelated docs;
- `docs/archive`;
- existing `docs/stages/reports` files unrelated to this stage.

## 3. HARD PROHIBITIONS

Do not change product behavior.
Do not change CLI names, flags, defaults, outputs, or behavior.
Do not change SQLite schema or migrations.
Do not change dataset/export formats.
Do not rewrite tests unless pytest exposes a real incompatibility and the report justifies the minimal fix.
Do not add runtime dependencies.
Do not add mypy, pyright, coverage, snapshots, or integration matrix work in this stage.
Do not modify protected service facades or compatibility wrappers.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Confirm current `make test` uses `unittest discover` and CI calls `make verify`.
2. Change only the test runner wiring so `make test` runs pytest across `tests`.
3. Keep `make verify` as the CI-parity authoritative gate.
4. Update development docs/checklists that name routine test commands.
5. Create a factual report and complete lifecycle cleanup if checks pass.

## 5. REQUIRED DOCS

Required if `Makefile` changes:
- `docs/development/README.md`
- `docs/development/LOCAL_VERIFICATION_MATRIX.md`
- `docs/development/PR_CHECKLIST.md`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_7A_1_PYTEST_AUTHORITY_AND_CI_GATE_ALIGNMENT_REPORT.md`

Do not update user-facing product docs unless behavior changes; behavior changes are prohibited.

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
docs/stages/reports/STAGE_7A_1_PYTEST_AUTHORITY_AND_CI_GATE_ALIGNMENT_REPORT.md
```

The report must be factual and written in Russian.

Record:
- exact `make test` command after change;
- exact checks run;
- whether CI still runs `make verify`;
- files changed;
- what was not changed;
- completion status.

## 8. COMPLETION CRITERIA

This stage is complete when:

- `make test` uses pytest;
- `make verify` passes after the change;
- `make pre-commit` passes or the stage is left incomplete with exact blocker;
- required docs and report exist;
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must use AGENTS.md format.
Do not paste full diffs.
Do not include broad testing essays.
Keep notes compact.
