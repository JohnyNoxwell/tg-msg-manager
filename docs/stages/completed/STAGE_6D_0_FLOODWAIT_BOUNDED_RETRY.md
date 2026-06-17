# STAGE 6D.0 — FLOODWAIT BOUNDED RETRY

Status: completed
Stage: 6D.0
Type: bugfix
Depends on: `tg_msg_manager/core/telegram/client.py` recursive FloodWait handling in `get_messages()` and `download_media()`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Execute Stage 6D.0 — FLOODWAIT BOUNDED RETRY.

Goal:
Fix recursive unlimited FloodWait retry in the Telegram client wrapper with the smallest safe patch.

Do not start later stages.
Do not add new features.
Do not change public CLI behavior, output formats, SQLite schema, dataset formats, state files, or data flow except bounded retry failure behavior required by this bug fix.

Use AGENTS.md compact output format.

## 1. SYMPTOM

`TelethonClientWrapper.get_messages()` and `download_media()` catch `FloodWaitError`, slow the throttler, sleep `e.seconds`, and recursively call themselves without an attempt limit.

Repeated FloodWait responses can cause a very long stuck process, poor cancellation behavior, and theoretical recursive stack growth.

## 2. REPRODUCTION / OBSERVED OUTPUT

No direct live Telegram reproduction command provided.

Use focused unit tests with repeated `FloodWaitError` side effects to reproduce the old unlimited recursive retry path.

## 3. LIKELY CAUSE

Likely cause:
- FloodWait retry is implemented as self-recursion instead of an iterative bounded retry loop.
- There is no shared attempt limit for `get_messages()` and `download_media()`.

## 4. FILES TO INSPECT

Required:
- `tg_msg_manager/core/telegram/client.py`
- `tests/core/telegram/test_telegram_core.py`
- `CHANGELOG.md`
- `docs/stages/README.md`

Referenced docs:
- `docs/architecture/README.md`

May create:
- `docs/stages/reports/STAGE_6D_0_FLOODWAIT_BOUNDED_RETRY_REPORT.md`

May move after completion:
- this stage file to `docs/stages/completed/`

Do not read or change:
- unrelated source modules
- unrelated docs
- `docs/archive/`
- completed stages except the final lifecycle target path
- existing `docs/stages/reports/` files unrelated to this stage

## 5. HARD PROHIBITIONS

Do not add features.
Do not perform broad refactors.
Do not change command names, CLI flags, defaults, output files, output directory layout, SQLite schema, dataset formats, manifest/state formats, or export data flow.
Do not add analytics, OSINT logic, profiling, fingerprinting, OCR, STT, media recognition, or LLM-dependent behavior.
Do not add new runtime dependencies.
Do not modify protected service facades or compatibility wrappers.
Do not change `delete_messages()` retry behavior in this stage.

## 6. MINIMAL PATCH TASKS

1. Confirm the failing path.
   - inspect `get_messages()` and `download_media()` FloodWait branches
   - confirm recursive retry and current telemetry/throttling behavior
   - do not edit unrelated methods

2. Patch `get_messages()` narrowly.
   - replace recursive FloodWait retry with an iterative loop
   - preserve throttling, telemetry, message normalization, and `limit` / `message_ids` forwarding
   - enforce a small internal maximum retry count

3. Patch `download_media()` narrowly.
   - replace recursive FloodWait retry with an iterative loop
   - preserve throttling, telemetry, file argument forwarding, generic error handling, and `None` return for non-FloodWait download failures
   - enforce the same internal maximum retry count

4. Add regression coverage.
   - update focused tests for successful retry without recursion
   - add tests for repeated FloodWait exhaustion
   - add media download retry/exhaustion coverage

5. Update lifecycle docs.
   - add bilingual Unreleased changelog entry
   - create the required factual report
   - complete lifecycle cleanup according to AGENTS.md

## 7. REGRESSION TESTS

Required:
- `pytest tests/core/telegram/test_telegram_core.py`

Tests must assert:
- successful `get_messages()` retry preserves `limit`
- repeated FloodWait in `get_messages()` stops after the bounded attempts
- successful `download_media()` retry preserves `file`
- repeated FloodWait in `download_media()` stops after the bounded attempts

## 8. NON-REGRESSION CHECKS

Required:
- `python3 -m compileall tg_msg_manager/core/telegram`
- `ruff check tg_msg_manager/core/telegram/client.py tests/core/telegram/test_telegram_core.py`

Must preserve:
- CLI surface
- SQLite schema
- dataset formats
- message normalization
- download media non-FloodWait error handling
- `delete_messages()` behavior

## 9. REQUIRED DOCS

Required:
- `CHANGELOG.md`
- `docs/stages/reports/STAGE_6D_0_FLOODWAIT_BOUNDED_RETRY_REPORT.md`
- `docs/stages/README.md`

Do not update README, COMMANDS, architecture docs, or user examples unless they are made inaccurate by this fix.

## 10. REPORT

Create:
- `docs/stages/reports/STAGE_6D_0_FLOODWAIT_BOUNDED_RETRY_REPORT.md`

Report must record:
- exact files changed
- exact checks run
- bug fixed
- behavior unchanged
- skills applied manually from `.skills/`
- what was not run and why
- completion status

## 11. COMPLETION CRITERIA

This stage is complete when:

- recursive unlimited FloodWait retry is removed from `get_messages()` and `download_media()`;
- bounded retry exhaustion has regression coverage;
- prohibited behavior remains unchanged;
- changelog and report exist;
- required checks are recorded;
- lifecycle cleanup is completed according to AGENTS.md.

## 12. OUTPUT LIMITS

Use AGENTS.md compact final response format.

Final response must contain only:

DONE:
- ...

CHANGED:
- ...

CHECKS:
- ...

PRESERVED:
- behavior: yes/no
- CLI: yes/no
- SQLite: yes/no
- scope: yes/no

NOTES:
- ...

STAGE:
- complete/incomplete: <reason if incomplete>

Do not paste full diffs.
Do not explain the task back to the user.
Do not include broad summaries.
Do not include future recommendations unless required by a real blocker.
