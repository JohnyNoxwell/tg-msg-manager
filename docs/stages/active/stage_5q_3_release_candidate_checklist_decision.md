# STAGE 5Q.3 — RELEASE CANDIDATE CHECKLIST DECISION

Status: active task
Stage: 5Q.3
Type: decision / release-notes draft
Depends on: Stage 5P `PASSED`; Stage 5Q.0-5Q.2 reports without blockers

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply `.skills/stage-reviewer/SKILL.md`,
`.skills/architecture-guard/SKILL.md`, and
`.skills/stage-completion-auditor/SKILL.md` after report/cleanup.

This consolidates 5Q evidence. Do not repeat audits or start Stage 5R.

## 1. PURPOSE

Decide whether the repository may proceed to package build dry-run and create a
conservative release-candidate notes draft.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `CHANGELOG.md`
- `docs/development/RELEASE_CHECKLIST_SCOPE.md`
- `docs/development/RELEASE_CANDIDATE_DECISION.md`
- Stage 5P report
- Stage 5Q.0, 5Q.1, and 5Q.2 reports
- `docs/stages/README.md`

Writable paths:

- `docs/stages/reports/STAGE_5Q_RELEASE_CANDIDATE_NOTES_DRAFT.md`
- `docs/stages/reports/STAGE_5Q_RELEASE_CANDIDATE_CHECKLIST_REPORT.md`
- `docs/stages/README.md`
- lifecycle move of this stage file

## 3. HARD PROHIBITIONS

- Do not change production code, tests, public docs, changelog, CLI contracts,
  SQLite schema, dataset/export contracts, package metadata, version, tags,
  artifacts, or publish state.
- Do not claim stable readiness or that a release/tag/build/publish occurred.
- Do not read private artifacts, sessions, credentials, real exports/logs/media/
  screenshots/DB files, or inject real Telegram data.
- Do not add analytics, OSINT, profiling, identity/media analysis, GUI/SaaS,
  or LLM-dependent core behavior.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify all prerequisite reports and classify missing/failed evidence.
2. Consolidate docs, CLI, packaging, privacy, and deferred-area findings.
3. Create a factual conservative RC notes draft from existing evidence only.
4. Decide whether Stage 5R.0 may run.
5. Create the Russian checklist report, then complete lifecycle cleanup.

## 5. REQUIRED DOCS

The RC notes draft must distinguish implemented behavior, known limitations,
deferred areas, and checks still pending. It must not claim stable release.
Rollback: remove or correct the draft/report only; no runtime rollback applies.

## 6. TESTS / VERIFICATION

Required:

```bash
git diff --check
```

Do not rerun full verification or build/install packages.

## 7. REPORT

Create:

- `docs/stages/reports/STAGE_5Q_RELEASE_CANDIDATE_NOTES_DRAFT.md`
- `docs/stages/reports/STAGE_5Q_RELEASE_CANDIDATE_CHECKLIST_REPORT.md`

The Russian checklist report must include: `PASSED`, `FAILED`, or `PARTIAL`;
prerequisite evidence; blockers/non-blocking gaps; commands/results; failures;
commands not run and why;
files changed; notes-draft path; confirmation of no intentional behavior/CLI/
SQLite/dataset/package/release change; final recommendation; applied skill
paths; lifecycle notes.

## 8. COMPLETION CRITERIA

- `PASSED` or non-blocking `PARTIAL` explicitly authorizes only Stage 5R.0.
- Blocking evidence produces `FAILED` and names the next isolated fix stage.
- Notes draft and checklist report exist.
- Lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`. Do not paste full report bodies.
