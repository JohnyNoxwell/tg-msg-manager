# STAGE 4C.0C — TEST LAYOUT GROUPING

Status: active task
Stage: 4C.0C
Type: refactor / test organization
Depends on: Stage 4C.0B completion and current flat `tests/*.py` layout

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Execute only Stage 4C.0C after Stage 4C.0B is complete.

Goal: group tests by subsystem without changing assertions, test intent, CLI
behavior, runtime behavior, or dataset behavior.

## 1. PURPOSE

Move flat tests into subsystem directories so future focused checks are easier to
run and maintain.

## 2. FILES TO INSPECT

Required:

```text
tests/
pytest.ini
pyproject.toml
Makefile
.github/workflows/
docs/development/
```

May update only files that reference old flat test paths.

May create:

```text
docs/stages/reports/STAGE_4C_0C_TEST_LAYOUT_GROUPING_REPORT.md
```

## 3. HARD PROHIBITIONS

Do not change assertions, weaken tests, delete tests, hide coverage, change
runtime modules, change CLI behavior, change schemas, or change dataset formats.

Do not add features, dependencies, analytics, OCR, STT, GUI, web UI, or new
persistence.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Map current test files to subsystem directories.
2. Move tests in small batches.
3. Update only import paths, fixture paths, and configured test paths made stale
   by moves.
4. Preserve fixture access.
5. Run collection and full/focused verification.

## 5. REQUIRED DOCS

Create the stage report. Update `docs/development/`, `Makefile`, workflows, or
config only if old test paths become inaccurate.

## 6. TESTS / VERIFICATION

Run:

```bash
pytest --collect-only -q
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
pytest tests -q
```

If full tests fail due to unrelated baseline failures, record the failure and
run closest focused checks for moved files.

## 7. REPORT

Report in Russian:

```text
old path -> new path mapping
files changed
checks run
checks not run and why
baseline failures if any
```

## 8. COMPLETION CRITERIA

Stage 4C.0C is complete when tests collect from the new layout, required checks
are recorded, docs/config references are current, the report exists, and
lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Use `AGENTS.md` compact final response format. No full diffs.
