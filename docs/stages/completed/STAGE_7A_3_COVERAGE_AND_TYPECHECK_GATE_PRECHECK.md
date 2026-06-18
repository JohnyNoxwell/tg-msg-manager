# STAGE 7A.3 — COVERAGE AND TYPECHECK GATE PRECHECK

Status: active task
Stage: 7A.3
Type: docs
Depends on: Stage 7A.2 completed with fixture contract snapshot gate in `make verify`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Execute only Stage 7A.3.

Goal:
Decide the narrowest coverage and type-check gate approach before adding mandatory tooling to the pipeline.

Use AGENTS.md compact output format.

## 1. PURPOSE

Avoid adding noisy or brittle quality gates without a baseline for current test coverage, typing debt, and supported Python versions.

## 2. FILES TO INSPECT

Required:
- `AGENTS.md`
- `Makefile`
- `.github/workflows/ci.yml`
- `pyproject.toml`
- `docs/development/LOCAL_VERIFICATION_MATRIX.md`
- `docs/development/PR_CHECKLIST.md`
- `docs/stages/README.md`
- `tests/`
- `tg_msg_manager/`

May create:
- `docs/development/TEST_INFRASTRUCTURE_HARDENING_PLAN.md`
- `docs/stages/reports/STAGE_7A_3_COVERAGE_AND_TYPECHECK_GATE_PRECHECK_REPORT.md`

Do not inspect or change:
- private exports, sessions, databases, logs, screenshots, or live Telegram data;
- unrelated docs;
- `docs/archive`;
- existing `docs/stages/reports` files unrelated to this stage.

## 3. HARD PROHIBITIONS

Do not add mandatory coverage or type-check dependencies in this precheck stage.
Do not change product code or tests.
Do not change CLI names, flags, defaults, outputs, or behavior.
Do not change SQLite schema or migrations.
Do not change dataset/export formats.
Do not add runtime dependencies.
Do not mark coverage or type-check gates as passed unless exact commands were run.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Inventory current absence or presence of coverage, mypy, pyright, and related config.
2. Compare supported Python versions in package metadata and CI matrix.
3. Draft a narrow follow-up recommendation for coverage gate and type-check gate sequencing.
4. Create the precheck report in Russian.
5. Update `docs/stages/README.md` only for lifecycle state.

## 5. REQUIRED DOCS

Required:
- `docs/stages/reports/STAGE_7A_3_COVERAGE_AND_TYPECHECK_GATE_PRECHECK_REPORT.md`
- `docs/stages/README.md`

Optional if a durable plan is useful:
- `docs/development/TEST_INFRASTRUCTURE_HARDENING_PLAN.md`

## 6. TESTS / VERIFICATION

Required:

```bash
python3 -m pytest tests -q
git diff --check
```

Do not run mutating format commands in this docs-only stage.
Do not claim checks passed unless actually run.

## 7. REPORT

Create:

```text
docs/stages/reports/STAGE_7A_3_COVERAGE_AND_TYPECHECK_GATE_PRECHECK_REPORT.md
```

The report must be factual and written in Russian.

Record:
- current coverage/type-check tooling state;
- recommended next stage split;
- exact checks run;
- files changed;
- what was deliberately not changed;
- completion status.

## 8. COMPLETION CRITERIA

This stage is complete when:

- coverage/type-check gate recommendation exists;
- mandatory tooling has not been added prematurely;
- required report exists;
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must use AGENTS.md format.
Do not paste full diffs.
Do not include broad roadmap text.
Keep notes compact.
