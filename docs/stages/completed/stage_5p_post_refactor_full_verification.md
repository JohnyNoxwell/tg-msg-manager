# STAGE 5P — POST-REFACTOR FULL VERIFICATION

Status: active task
Stage: 5P
Type: verification
Depends on: completed Stage 5N.0-5N.1 and Stage 5O.0-5O.14 reports

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply `.skills/stage-reviewer/SKILL.md`,
`.skills/architecture-guard/SKILL.md`, and
`.skills/stage-completion-auditor/SKILL.md` after report/cleanup.

Run this stage before every Stage 5Q task. Do not fix failures or start 5Q.

## 1. PURPOSE

Verify the complete offline project after the 5N/5O changes. This is
verification-only; the only deliverable is factual evidence.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `Makefile`
- `pyproject.toml`
- `docs/development/LOCAL_VERIFICATION_MATRIX.md`
- `docs/development/RELEASE_CANDIDATE_DECISION.md`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_5N_0_TARGET_NAMES_HISTORY_READ_MODEL_REPORT.md`
- `docs/stages/reports/STAGE_5N_1_TARGET_NAMES_HISTORY_CLI_REPORT.md`
- every tracked report matching `docs/stages/reports/STAGE_5O_*_REPORT.md`

If a required report is missing, record the exact path; do not invent evidence.

Writable paths:

- `docs/stages/reports/STAGE_5P_POST_REFACTOR_FULL_VERIFICATION_REPORT.md`
- `docs/stages/README.md`
- lifecycle move of this stage file

## 3. HARD PROHIBITIONS

- Do not change production code, tests, fixtures, docs except a typo that blocks
  verification clarity, CLI contracts, SQLite schema/migrations/`user_version`,
  dataset/export contracts, versions, tags, package state, or dependencies.
- Do not mix fixes, refactoring, features, release work, or publishing into this stage.
- Do not read private artifacts, sessions, credentials, real exports, logs,
  screenshots, media, real/local DB files, or inject real Telegram data.
- Do not add analytics, OSINT, profiling, identity claims, OCR/STT,
  media-analysis, GUI/SaaS, or LLM-dependent core behavior.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Confirm every required report exists; record missing paths before checks.
2. Run each required and focused command exactly once from the repository root.
3. Run optional Make targets only when available; record exact skip reasons.
4. Classify failures without editing code/tests/docs to hide them.
5. Create the Russian report, then complete lifecycle cleanup.

## 5. REQUIRED DOCS

Report-only. A blocking typo fix requires exact justification in the report.
No runtime rollback applies; revert only an allowed typo if it was incorrect.

## 6. TESTS / VERIFICATION

Required:

```bash
git diff --check
python3 -m compileall tg_msg_manager
pytest
pytest tests/architecture
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
python3 -m unittest discover tests -p '*target*names*.py'
python3 -m unittest discover tests -p '*target*history*.py'
python3 -m unittest discover tests -p '*non_channel*contract*.py'
python3 -m unittest tests.e2e.test_fixture_e2e -q
```

Also run when available:

```bash
make test
make verify
```

Do not claim a command passed unless it ran successfully.

## 7. REPORT

Create `docs/stages/reports/STAGE_5P_POST_REFACTOR_FULL_VERIFICATION_REPORT.md`
in Russian.

Include: `PASSED`, `FAILED`, or `PARTIAL`; files/reports inspected; commands run
and results; failures; commands not run and why; files changed; confirmation
that production/CLI/SQLite/dataset behavior was not intentionally changed;
missing evidence; suspected failure area; recommended isolated fix stage;
final recommendation; applied skill paths; lifecycle notes.

Expected output: one evidence report. Do not create a fix stage in this stage.

## 8. COMPLETION CRITERIA

- `PASSED` only when all required commands pass and required evidence exists.
- `PARTIAL` or `FAILED` must block Stage 5Q and name the next isolated fix stage.
- No production behavior, release state, tag, version, or package state changed.
- Required report exists and lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`. Do not paste full diffs, large outputs,
private artifact names/content, or release claims.
