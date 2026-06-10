# STAGE 5Q.0 — PUBLIC DOCS / CLI ALIGNMENT

Status: active task
Stage: 5Q.0
Type: docs audit
Depends on: `docs/stages/reports/STAGE_5P_POST_REFACTOR_FULL_VERIFICATION_REPORT.md` with `PASSED`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply `.skills/stage-reviewer/SKILL.md`,
`.skills/architecture-guard/SKILL.md`, and
`.skills/stage-completion-auditor/SKILL.md` after report/cleanup.

Stop if Stage 5P is absent or not `PASSED`. Do not start Stage 5Q.1.

## 1. PURPOSE

Audit and minimally align public documentation with the implemented CLI. This
stage covers docs/CLI truth only; packaging, privacy, and release decisions are later.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `README.md`
- `COMMANDS.md`
- `docs/development/CLI_CONTRACT.md`
- `docs/user/QUICKSTART.md`
- `docs/development/OPERATIONAL_RISKS_AND_LIMITS.md`
- `docs/stages/reports/STAGE_5P_POST_REFACTOR_FULL_VERIFICATION_REPORT.md`
- `docs/stages/reports/STAGE_5N_1_TARGET_NAMES_HISTORY_CLI_REPORT.md`
- `docs/stages/README.md`

Inspect only as needed to verify help:

- `tg_msg_manager/cli_parser.py`
- `tg_msg_manager/cli/`

Writable paths:

- `README.md`
- `COMMANDS.md`
- `docs/development/CLI_CONTRACT.md`
- `docs/user/QUICKSTART.md`
- `docs/stages/reports/STAGE_5Q_0_PUBLIC_DOCS_CLI_ALIGNMENT_REPORT.md`
- `docs/stages/README.md`
- lifecycle move of this stage file

## 3. HARD PROHIBITIONS

- Do not change production code, tests, CLI names/flags/defaults/stdout/stderr,
  SQLite schema, dataset/export contracts, versions, tags, package state, or dependencies.
- Do not edit docs to promise unsupported behavior or stable release readiness.
- Do not read private artifacts, sessions, credentials, real exports/logs/media/
  screenshots/DB files, or inject real Telegram data.
- Do not add analytics, OSINT, profiling, identity claims, OCR/STT,
  media-analysis, GUI/SaaS, or LLM-dependent core behavior.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Confirm Stage 5P is `PASSED`; inspect docs before editing.
2. Compare documented public commands and entrypoints with safe help output.
3. Verify `target names <target> [--field ...] [--format ...]`, limitations,
   local-only behavior, installation path, project identity, and quickstart flow.
4. Apply only factual docs corrections in writable paths.
5. Create the Russian report, then complete lifecycle cleanup.

## 5. REQUIRED DOCS

README must state what the project is/is not, local/privacy limits, basic
installation/usage, and avoid OSINT/profiling/identity guarantees. Missing
required files must be reported, not invented.

Rollback: revert only inaccurate docs edits; no runtime rollback applies.

## 6. TESTS / VERIFICATION

Required:

```bash
python3 -m tg_msg_manager.cli --help
python3 -m tg_msg_manager.cli target --help
python3 -m tg_msg_manager.cli target names --help
git diff --check
```

Do not initialize Telegram or use real data.

## 7. REPORT

Create `docs/stages/reports/STAGE_5Q_0_PUBLIC_DOCS_CLI_ALIGNMENT_REPORT.md` in Russian.

Include: `PASSED`, `FAILED`, or `PARTIAL`; commands/results; failures;
commands not run and why; files changed; documented CLI mismatches and corrections;
confirmation that production/CLI/SQLite/dataset behavior was not intentionally
changed; final recommendation; applied skill paths; lifecycle notes.

## 8. COMPLETION CRITERIA

- Public docs and current safe help output are aligned or exact blockers are listed.
- Stage 5Q.1 is allowed only when status is `PASSED`.
- Required report exists and lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`. Do not paste full diffs or large help output.
