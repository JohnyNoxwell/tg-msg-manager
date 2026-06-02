# STAGE 5M.0 — External Risk Audit Verification

Status: active task
Stage: 5M.0
Type: audit / report-only
Depends on: AGENTS.md, docs/stages/README.md, post-5L.1 repository state

---

## 0. CODEX ENTRY CONTRACT

1. Read `AGENTS.md` first.
2. Apply `.skills/stage-reviewer/SKILL.md` before implementation.
3. Apply `.skills/architecture-guard/SKILL.md` because this audit covers CLI, services, storage, CI, privacy, and contract boundaries.
4. Apply `.skills/stage-completion-auditor/SKILL.md` before claiming completion.
5. Do not fix broad issues in this stage; collect evidence and write the report.

## 1. PURPOSE

Verify external audit findings against repository evidence and classify each point as:

```text
confirmed issue
partially confirmed
already handled
false / not applicable
missing evidence
needs follow-up stage
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
CHANGELOG.md
pyproject.toml
Makefile
.gitignore
docs/README.md
docs/development/README.md
docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md
docs/development/RELEASE_CHECKLIST_SCOPE.md
docs/development/LOCAL_VERIFICATION_MATRIX.md
docs/development/RELEASE_CANDIDATE_DECISION.md
docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md
docs/architecture/PRIVATE_ARCHIVE_CONTRACT_DEFERRED_DECISION.md
docs/architecture/CURRENT_PROJECT_CONTEXT.md
docs/stages/README.md
docs/stages/reports/STAGE_5L_1_RELEASE_CANDIDATE_DECISION_RECHECK_REPORT.md
docs/stages/reports/STAGE_5K_4_RELEASE_CANDIDATE_DECISION_REPORT.md
docs/stages/reports/STAGE_5J_2_FIXTURE_TO_CONTRACT_VERIFICATION_REPORT.md
docs/stages/reports/STAGE_5J_3_RELEASE_READINESS_RECHECK_CHANGELOG_FINALIZATION_REPORT.md
```

Inspect if present:

```text
.github/workflows/
backlog/
config.example.json
run.py
tg_msg_manager/cli_parser.py
tg_msg_manager/cli/
tg_msg_manager/services/
tg_msg_manager/infrastructure/storage/
tests/
```

May change only:

```text
docs/stages/reports/STAGE_5M_0_EXTERNAL_RISK_AUDIT_VERIFICATION_REPORT.md
docs/stages/README.md
docs/stages/completed/stage_5m_0_external_risk_audit_verification.md
```

Do not read private artifacts, real exports, sessions, local DB contents, logs, screenshots, or media.

## 3. HARD PROHIBITIONS

- Do not change runtime, CLI, tests, fixtures, output formats, SQLite/storage/services, `.gitignore`, README, COMMANDS, CHANGELOG, CI, release metadata, or versioning.
- Do not publish, tag, build/upload packages, or add `__version__`.
- Do not add analytics, OSINT interpretation, profiling, media analysis, OCR, STT, or LLM-dependent core behavior.
- Do not silently expand `export-pm` into the user/group + `db-export` non-channel contract.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Inspect the required files and record exactly which paths were inspected.
2. Verify deferred coverage: generated-output filenames, `_partN`, DB-backed no-new-work / skip behavior, `.export_state`, and `export-pm`.
3. Verify `schedule` OS support docs/tests, `config.json` and secret protection, privacy warnings, `run.py` entrypoint alignment, CI status, `--limit` semantics, public `backlog/` risk, and Telethon/FloodWait/SQLite concurrency notes.
4. Classify each point with evidence, severity, and follow-up recommendation.
5. Write the report and update stage lifecycle docs only as allowed.

## 5. REQUIRED DOCS

Create `docs/stages/reports/STAGE_5M_0_EXTERNAL_RISK_AUDIT_VERIFICATION_REPORT.md` in Russian.

Do not update user-facing docs in this stage.

## 6. TESTS / VERIFICATION

Run:

```bash
git diff --check
```

Do not claim checks passed unless actually run.

## 7. REPORT

Report must include:

- outcome token;
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`;
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`;
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`;
- files inspected;
- audit point / evidence / classification / severity / follow-up;
- confirmed issues;
- already-handled points;
- false/not-applicable points;
- missing evidence;
- recommended follow-up order;
- no behavior changes confirmation.

Outcome token must be one of:

```text
EXTERNAL_RISK_AUDIT_VERIFIED_WITH_FOLLOWUPS
EXTERNAL_RISK_AUDIT_REPORT_ONLY_NO_CONFIRMED_BLOCKERS
EXTERNAL_RISK_AUDIT_BLOCKED_MISSING_REPOSITORY_EVIDENCE
```

## 8. COMPLETION CRITERIA

- Every verification point is classified with cited repository evidence or marked missing evidence.
- No forbidden file or private artifact was read.
- Report exists and is factual.
- Allowed stage lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- No full diffs, large code blocks, broad summaries, or speculation.
