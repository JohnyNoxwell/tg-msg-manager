# STAGE 5M.6 — Operational Risk Notes

Status: active task
Stage: 5M.6
Type: audit / docs-only
Depends on: docs/stages/reports/STAGE_5M_0_EXTERNAL_RISK_AUDIT_VERIFICATION_REPORT.md

---

## 0. CODEX ENTRY CONTRACT

1. Read `AGENTS.md` first.
2. Apply `.skills/stage-reviewer/SKILL.md` before implementation.
3. Apply `.skills/architecture-guard/SKILL.md` because this stage inspects runtime, SQLite, scheduler, and operational boundaries.
4. Apply `.skills/stage-completion-auditor/SKILL.md` before claiming completion.
5. Do not implement behavior changes or run live checks.

## 1. PURPOSE

Verify and document operational risks:

```text
Telethon session loss/corruption/re-authentication
FloodWait / rate limiting expectations
SQLite concurrent access / SQLITE_BUSY risk
scheduled/background command caveats
manual live smoke checks
```

## 2. FILES TO INSPECT

Read:

```text
AGENTS.md
.skills/stage-reviewer/SKILL.md
.skills/architecture-guard/SKILL.md
.skills/stage-completion-auditor/SKILL.md
README.md
COMMANDS.md
docs/user/QUICKSTART.md
docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md
docs/development/RELEASE_CHECKLIST_SCOPE.md
docs/development/LOCAL_VERIFICATION_MATRIX.md
docs/development/RELEASE_CANDIDATE_DECISION.md
docs/stages/reports/STAGE_5M_0_EXTERNAL_RISK_AUDIT_VERIFICATION_REPORT.md
tg_msg_manager/
tests/
docs/stages/README.md
```

Inspect code only enough to identify existing handling and docs references.

May change only:

```text
README.md
COMMANDS.md
docs/user/QUICKSTART.md
docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md
docs/development/LOCAL_VERIFICATION_MATRIX.md
docs/development/OPERATIONAL_RISKS_AND_LIMITS.md
docs/development/README.md
docs/stages/reports/STAGE_5M_6_OPERATIONAL_RISK_NOTES_REPORT.md
docs/stages/README.md
docs/stages/completed/stage_5m_6_operational_risk_notes.md
```

## 3. HARD PROHIBITIONS

- Do not read sessions, DB contents, real exports, media, logs, screenshots, or private artifacts.
- Do not implement session recovery, FloodWait handling, rate-limit changes, SQLite concurrency changes, scheduler changes, runtime/CLI/output changes, tests, fixtures, or live checks.
- Do not overstate operational guarantees that Telegram, OS schedulers, or SQLite do not provide.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify whether session sensitivity, recovery, and re-authentication guidance exists.
2. Verify FloodWait/rate-limit documentation, including `max_rps` if present and the instability of Telegram limits.
3. Verify SQLite concurrent-run and `SQLITE_BUSY` caveats where applicable.
4. Verify scheduled/background caveats and separation of live smoke checks from offline release checks.
5. Make minimal docs-only corrections if evidence shows gaps, then write the report.

## 5. REQUIRED DOCS

Create `docs/stages/reports/STAGE_5M_6_OPERATIONAL_RISK_NOTES_REPORT.md` in Russian.

Create or update `docs/development/OPERATIONAL_RISKS_AND_LIMITS.md` only if operational guidance is missing or scattered enough to need one canonical page.

## 6. TESTS / VERIFICATION

Run:

```bash
git diff --check
```

If command examples change, verify them against CLI parser and COMMANDS.

Do not claim checks passed unless actually run.

## 7. REPORT

Report must include:

- outcome token;
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`;
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`;
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`;
- files inspected;
- answers for session, FloodWait/rate limit, SQLite concurrency, scheduler, and live-smoke-check questions;
- docs changed or explicit no-change reason;
- confirmation that no runtime behavior or live checks changed.

Outcome token must be one of:

```text
OPERATIONAL_RISK_NOTES_CONFIRMED
OPERATIONAL_RISK_DOCS_UPDATED
OPERATIONAL_RISK_FOLLOWUPS_RECOMMENDED
OPERATIONAL_RISK_BLOCKED_NEEDS_SOURCE_REVIEW
```

## 8. COMPLETION CRITERIA

- Operational risk questions are answered with evidence.
- Any docs change is minimal and evidence-backed.
- Report exists and is factual.
- Lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- No full diffs, broad summaries, live-check output, or private artifact content.
