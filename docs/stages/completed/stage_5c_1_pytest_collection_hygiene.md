# STAGE 5C.1 — PYTEST COLLECTION HYGIENE

Status: completed
Stage: 5C.1
Type: test hygiene
Depends on: current pytest collection including `scratch/test_whitelist.py`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Execute Stage 5C.1 only.

Goal:
Make pytest collection match the tracked regression test tree without collecting ignored scratch files.

Do not start Stage 5C.0 or later stages.
Do not change runtime behavior, CLI behavior, SQLite schema, dataset formats, or test assertions unrelated to collection.
Use `AGENTS.md` compact output format.

## 1. PURPOSE

Pytest currently collects at least one ignored scratch test path. This stage limits pytest discovery to intended tests and records the result.

## 2. FILES TO INSPECT

Required:
- `AGENTS.md`
- this stage file
- `pyproject.toml`
- `Makefile`
- `.gitignore`
- `scratch/test_whitelist.py`
- `tests/`

May change:
- `pyproject.toml`
- `docs/stages/reports/STAGE_5C_1_PYTEST_COLLECTION_HYGIENE_REPORT.md`
- `docs/stages/README.md`
- this stage file location during lifecycle cleanup

Do not read or change:
- ignored artifact contents under `DB_EXPORTS/`, `exports/`, `PRIVAT_DIALOGS/`, `PUBLIC_GROUPS/`
- local credentials, sessions, or databases
- unrelated source modules
- unrelated docs, archive files, or completed stage files

## 3. HARD PROHIBITIONS

- Do not delete or edit `scratch/` files.
- Do not modify runtime package code.
- Do not change `Makefile` unless `pyproject.toml` cannot express the collection boundary.
- Do not change test semantics to make failures disappear.
- Do not add dependencies.
- Do not change command names, CLI flags, defaults, output files, dataset layouts, or SQLite schema.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Confirm current collection.
   - Run `python3 -m pytest --collect-only -q -p no:cacheprovider`.
   - Record any collected path outside `tests/`.
   - Do not edit yet.

2. Add the narrow collection boundary.
   - Prefer `pyproject.toml` pytest configuration that sets collection to `tests`.
   - Keep existing build/project metadata unchanged.
   - Do not add warnings filters or unrelated pytest options.

3. Re-check collection.
   - Run the same collect-only command.
   - Confirm no `scratch/` node is collected.

4. Run non-regression checks.
   - Run the commands listed in section 6.
   - Record exact results in the report.

5. Write the report and perform lifecycle cleanup.
   - Create the report in Russian.
   - Move this task file to `docs/stages/completed/` only after report and checks are done.
   - Update `docs/stages/README.md`.

## 5. REQUIRED DOCS

Required:
- `docs/stages/reports/STAGE_5C_1_PYTEST_COLLECTION_HYGIENE_REPORT.md`
- `docs/stages/README.md` during lifecycle cleanup

Do not update user-facing docs unless the pytest command contract changes.

## 6. TESTS / VERIFICATION

Run:
- `python3 -m pytest --collect-only -q -p no:cacheprovider`
- `python3 -m unittest discover -s tests -q`
- `python3 -m compileall tg_msg_manager tests`
- `ruff check tg_msg_manager tests`
- `git diff --check`

Do not claim checks passed unless they were run.

## 7. REPORT

Create `docs/stages/reports/STAGE_5C_1_PYTEST_COLLECTION_HYGIENE_REPORT.md` in Russian.

Include:
- exact collection issue observed before the change;
- exact changed files;
- exact checks and results;
- confirmation that runtime code, CLI behavior, dataset formats, and SQLite schema were unchanged;
- lifecycle status.

## 8. COMPLETION CRITERIA

- Pytest collect-only does not collect `scratch/`.
- `unittest discover -s tests` still passes or any failure is recorded as a blocker.
- Runtime behavior is unchanged.
- Required report exists.
- lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- No full diffs.
- No markdown tables in the final response.
- Mention only changed files, checks, preserved behavior, notes, and stage status.
