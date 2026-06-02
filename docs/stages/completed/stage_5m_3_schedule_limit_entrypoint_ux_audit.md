# STAGE 5M.3 — Schedule / Limit / Entrypoint UX Audit

Status: active task
Stage: 5M.3
Type: audit / docs-only
Depends on: docs/stages/reports/STAGE_5M_0_EXTERNAL_RISK_AUDIT_VERIFICATION_REPORT.md

---

## 0. CODEX ENTRY CONTRACT

1. Read `AGENTS.md` first.
2. Apply `.skills/stage-reviewer/SKILL.md` before implementation.
3. Apply `.skills/architecture-guard/SKILL.md` because this stage inspects CLI/parser and entrypoint boundaries.
4. Apply `.skills/stage-completion-auditor/SKILL.md` before claiming completion.
5. Do not change CLI/parser/runtime behavior, entrypoints, tests, or fixtures.

## 1. PURPOSE

Audit external UX clarity for:

```text
schedule command OS support
--limit semantics
entrypoints: run.py vs python3 -m tg_msg_manager.cli vs tg-msg-manager
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
docs/development/RELEASE_CANDIDATE_DECISION.md
pyproject.toml
run.py
tg_msg_manager/cli_parser.py
tg_msg_manager/cli/__init__.py
tg_msg_manager/cli/__main__.py
tg_msg_manager/__init__.py
tests/
docs/stages/reports/STAGE_5M_0_EXTERNAL_RISK_AUDIT_VERIFICATION_REPORT.md
docs/stages/README.md
```

May change only:

```text
README.md
COMMANDS.md
docs/user/QUICKSTART.md
docs/development/LOCAL_VERIFICATION_MATRIX.md
docs/stages/reports/STAGE_5M_3_SCHEDULE_LIMIT_ENTRYPOINT_UX_AUDIT_REPORT.md
docs/stages/README.md
docs/stages/completed/stage_5m_3_schedule_limit_entrypoint_ux_audit.md
```

## 3. HARD PROHIBITIONS

- Do not change CLI/parser/runtime behavior, package entrypoints, tests, fixtures, output formats, SQLite schema, package metadata, release state, or version.
- Do not add platform behavior, scheduler behavior, or new commands.
- Do not add tests in this stage; recommend follow-up tests if needed.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify whether `schedule` is public, macOS-only, and clearly documented for non-macOS behavior.
2. Verify whether `--limit` is per-dialog or global and whether docs say so wherever needed.
3. Verify `run.py`, `python3 -m tg_msg_manager.cli`, and console script alignment.
4. Make minimal docs-only corrections if evidence shows UX ambiguity.
5. Write the report and recommend separate follow-up tests only when needed.

## 5. REQUIRED DOCS

Create `docs/stages/reports/STAGE_5M_3_SCHEDULE_LIMIT_ENTRYPOINT_UX_AUDIT_REPORT.md` in Russian.

Update allowed docs only when verified ambiguity exists.

## 6. TESTS / VERIFICATION

Run:

```bash
git diff --check
```

If command examples change, verify them against parser, README, COMMANDS, pyproject, and `run.py`.

Do not claim checks passed unless actually run.

## 7. REPORT

Report must include:

- outcome token;
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`;
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`;
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`;
- files inspected;
- answers for schedule, `--limit`, and entrypoint questions;
- docs changed or explicit no-change reason;
- follow-up tests recommended, if any;
- confirmation that no CLI/runtime behavior changed.

Outcome token must be one of:

```text
SCHEDULE_LIMIT_ENTRYPOINT_UX_AUDIT_COMPLETE
SCHEDULE_LIMIT_ENTRYPOINT_DOCS_UPDATED
SCHEDULE_LIMIT_ENTRYPOINT_FOLLOWUP_TESTS_RECOMMENDED
SCHEDULE_LIMIT_ENTRYPOINT_BLOCKED_NEEDS_CODE_REVIEW
```

## 8. COMPLETION CRITERIA

- Schedule, `--limit`, and entrypoint UX questions are answered with evidence.
- Any docs change is minimal and evidence-backed.
- Report exists and is factual.
- Lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- No full diffs, broad summaries, or speculative UX redesign.
