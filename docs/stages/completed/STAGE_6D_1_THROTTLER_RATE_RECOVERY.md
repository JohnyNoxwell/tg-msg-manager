# STAGE 6D.1 — THROTTLER RATE RECOVERY

Status: completed
Stage: 6D.1
Type: bugfix
Depends on: `tg_msg_manager/core/telegram/throttler.py` one-way `RateThrottler.adjust_rate()` slowdown after FloodWait

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Execute Stage 6D.1 — THROTTLER RATE RECOVERY.

Goal:
Fix one-way throttler slowdown after FloodWait with the smallest safe patch.

Do not start later stages.
Do not add new features.
Do not change public CLI behavior, output formats, SQLite schema, dataset formats, state files, or data flow except throttler recovery behavior required by this bug fix.

Use AGENTS.md compact output format.

## 1. SYMPTOM

`RateThrottler.adjust_rate()` only reduces `rps` after FloodWait and clamps it to `0.1`.

There is no gradual recovery toward the configured starting `rps`, so one incidental FloodWait can make the rest of a long export run unnecessarily slow.

## 2. REPRODUCTION / OBSERVED OUTPUT

No direct live Telegram reproduction command provided.

Use focused unit tests around `RateThrottler.adjust_rate()` and repeated `throttle()` calls to reproduce the old one-way slowdown.

## 3. LIKELY CAUSE

Likely cause:
- `RateThrottler` does not remember its configured starting rate.
- `throttle()` has no recovery step after prior slowdown.

## 4. FILES TO INSPECT

Required:
- `tg_msg_manager/core/telegram/throttler.py`
- `tg_msg_manager/core/telegram/client.py`
- `tests/core/telegram/test_telegram_core.py`
- `CHANGELOG.md`
- `docs/stages/README.md`

Referenced docs:
- `docs/architecture/README.md`

May create:
- `docs/stages/reports/STAGE_6D_1_THROTTLER_RATE_RECOVERY_REPORT.md`

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
Do not change Stage 6D.0 bounded FloodWait retry limits.

## 6. MINIMAL PATCH TASKS

1. Confirm the failing path.
   - inspect `RateThrottler.__init__()`, `adjust_rate()`, and `throttle()`
   - confirm `adjust_rate()` only slows down
   - do not edit unrelated methods

2. Patch throttler recovery narrowly.
   - store the configured starting `rps`
   - add gradual recovery toward the starting `rps` after throttled work continues
   - never recover above the configured starting `rps`
   - preserve token bucket burst behavior and existing slowdown clamp

3. Confirm caller compatibility.
   - inspect `TelethonClientWrapper` construction and FloodWait `adjust_rate()` callers
   - change `client.py` only if required for compatibility

4. Add regression coverage.
   - update focused throttler tests for recovery after slowdown
   - assert recovery is gradual and capped at the configured starting `rps`
   - preserve existing throttler limit test

5. Update lifecycle docs.
   - add bilingual Unreleased changelog entry
   - create the required factual report
   - complete lifecycle cleanup according to AGENTS.md

## 7. REGRESSION TESTS

Required:
- `pytest tests/core/telegram/test_telegram_core.py`

Tests must assert:
- `adjust_rate()` still slows down and clamps as before
- throttler gradually recovers after slowdown while `throttle()` continues
- recovery does not exceed configured starting `rps`

## 8. NON-REGRESSION CHECKS

Required:
- `python3 -m compileall tg_msg_manager/core/telegram`
- `ruff check tg_msg_manager/core/telegram/throttler.py tg_msg_manager/core/telegram/client.py tests/core/telegram/test_telegram_core.py`
- `git diff --check`

Must preserve:
- CLI surface
- SQLite schema
- dataset formats
- Stage 6D.0 bounded FloodWait retry limits
- token bucket burst behavior
- `max_requests_per_second` constructor alias

## 9. REQUIRED DOCS

Required:
- `CHANGELOG.md`
- `docs/stages/reports/STAGE_6D_1_THROTTLER_RATE_RECOVERY_REPORT.md`
- `docs/stages/README.md`

Do not update README, COMMANDS, architecture docs, or user examples unless they are made inaccurate by this fix.

## 10. REPORT

Create:
- `docs/stages/reports/STAGE_6D_1_THROTTLER_RATE_RECOVERY_REPORT.md`

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

- throttler slowdown can recover gradually toward its configured starting `rps`;
- recovery has regression coverage;
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
