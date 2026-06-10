# STAGE 5Q.2 — PRIVACY / DEFERRED AREAS AUDIT

Status: active task
Stage: 5Q.2
Type: safety docs audit
Depends on: Stage 5P `PASSED`; Stage 5Q.0 `PASSED`; Stage 5Q.1 `PASSED` or non-blocking `PARTIAL`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply `.skills/stage-reviewer/SKILL.md`,
`.skills/architecture-guard/SKILL.md`, and
`.skills/stage-completion-auditor/SKILL.md` after report/cleanup.

Use names/categories only for ignored/private artifacts. Do not open contents.
Do not start Stage 5Q.3.

## 1. PURPOSE

Audit release privacy boundaries and ensure deferred areas are documented
without reading private artifacts or changing behavior.

## 2. FILES TO INSPECT

Required tracked files:

- `AGENTS.md`
- `.gitignore`
- `README.md`
- `COMMANDS.md`
- `CHANGELOG.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `docs/development/OPERATIONAL_RISKS_AND_LIMITS.md`
- `docs/architecture/PRIVATE_ARCHIVE_CONTRACT_DEFERRED_DECISION.md`
- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md`
- Stage 5P and Stage 5Q.0-5Q.1 reports
- `docs/stages/README.md`

Writable paths:

- the required tracked docs above, only for factual privacy/deferred-area correction
- `docs/stages/reports/STAGE_5Q_2_PRIVACY_DEFERRED_AREAS_AUDIT_REPORT.md`
- `docs/stages/README.md`
- lifecycle move of this stage file

## 3. HARD PROHIBITIONS

- Do not open/read private artifacts, sessions, credentials, `.env`, real
  exports/logs/screenshots/media/DB files, ignored artifact contents, or inject
  real Telegram IDs/usernames/message text.
- Do not change production code, tests, CLI contracts, SQLite schema,
  dataset/export contracts, versions, tags, package state, or dependencies.
- Do not add analytics, OSINT, profiling, identity claims, OCR/STT,
  media-analysis, GUI/SaaS, or LLM-dependent core behavior.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify prerequisite reports; inspect only tracked policy/docs files.
2. Run safe tracked/ignored name inventory without opening ignored contents.
3. Confirm docs explicitly cover: deferred 5N.2 chat/channel title history;
   private archive/`export-pm` contract deferral; optional separate live smoke
   checks; known limitations; stable release as a separate decision.
4. Apply only factual docs corrections in writable tracked files.
5. Create the Russian report, then complete lifecycle cleanup.

## 5. REQUIRED DOCS

Do not claim sensitive files are absent merely because they are ignored. Report
tracked release blockers separately from local ignored private categories.
Rollback: revert only inaccurate docs corrections.

## 6. TESTS / VERIFICATION

Required safe commands:

```bash
git ls-files
git status --ignored --short
git diff --check
```

Do not use commands that print private file contents.

## 7. REPORT

Create `docs/stages/reports/STAGE_5Q_2_PRIVACY_DEFERRED_AREAS_AUDIT_REPORT.md`
in Russian.

Include: `PASSED`, `FAILED`, or `PARTIAL`; commands/results; failures; tracked
blocker findings; commands not run and why; ignored/private categories by pattern only; deferred
areas status; files changed; private-content-not-read confirmation; no behavior/
CLI/SQLite/dataset change; final recommendation; applied skill paths; lifecycle notes.

## 8. COMPLETION CRITERIA

- No tracked release blocker is found, or exact blockers are listed.
- Deferred areas are factual and visible.
- Stage 5Q.3 is allowed only for `PASSED`, or `PARTIAL` with no blocking issue.
- Required report exists and lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`. Never include private names/content.
