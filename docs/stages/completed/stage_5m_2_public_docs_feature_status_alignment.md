# STAGE 5M.2 — Public Docs Feature Status Alignment

Status: active task
Stage: 5M.2
Type: docs-only
Depends on: docs/stages/reports/STAGE_5M_0_EXTERNAL_RISK_AUDIT_VERIFICATION_REPORT.md

---

## 0. CODEX ENTRY CONTRACT

1. Read `AGENTS.md` first.
2. Apply `.skills/stage-reviewer/SKILL.md` before implementation.
3. Apply `.skills/architecture-guard/SKILL.md` because this stage touches public docs, contract boundaries, and `export-pm` status.
4. Apply `.skills/stage-completion-auditor/SKILL.md` before claiming completion.
5. Preserve public CLI behavior and do not implement deferred contracts.

## 1. PURPOSE

Align public-facing docs with engineering status for:

```text
export-pm / private archive deferred contract
limited external use
release-candidate checklist status
deferred contract coverage
focused non-channel contract tests
known limitations
```

Do not hide features; make status clear.

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
docs/README.md
docs/user/QUICKSTART.md
docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md
docs/architecture/PRIVATE_ARCHIVE_CONTRACT_DEFERRED_DECISION.md
docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md
docs/development/RELEASE_CANDIDATE_DECISION.md
docs/development/RELEASE_CHECKLIST_SCOPE.md
docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md
docs/stages/reports/STAGE_5J_3_RELEASE_READINESS_RECHECK_CHANGELOG_FINALIZATION_REPORT.md
docs/stages/reports/STAGE_5L_1_RELEASE_CANDIDATE_DECISION_RECHECK_REPORT.md
docs/stages/reports/STAGE_5M_0_EXTERNAL_RISK_AUDIT_VERIFICATION_REPORT.md
docs/stages/README.md
```

May change only:

```text
README.md
COMMANDS.md
CHANGELOG.md
docs/README.md
docs/user/QUICKSTART.md
docs/architecture/PRIVATE_ARCHIVE_CONTRACT_DEFERRED_DECISION.md
docs/development/RELEASE_CANDIDATE_DECISION.md
docs/stages/reports/STAGE_5M_2_PUBLIC_DOCS_FEATURE_STATUS_ALIGNMENT_REPORT.md
docs/stages/README.md
docs/stages/completed/stage_5m_2_public_docs_feature_status_alignment.md
```

## 3. HARD PROHIBITIONS

- Do not change runtime, CLI, tests, fixtures, output formats, SQLite schema, package metadata, release state, or version.
- Do not implement private archive contract or include `export-pm` in the non-channel contract.
- Do not overstate coverage for generated filenames, `_partN`, DB-backed no-new-work, `.export_state`, raw JSON, SQLite schema, live smoke checks, or private archive.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify whether public docs present `export-pm` as stable/core while its contract is deferred.
2. Verify whether caveats are visible where users encounter the feature.
3. Verify deferred areas and focused contract test coverage are described accurately.
4. Verify QUICKSTART points users toward stable/contract-backed flows first and CHANGELOG `[Unreleased]` remains accurate.
5. Make minimal docs-only corrections if evidence shows mismatch, then write the report.

## 5. REQUIRED DOCS

Create `docs/stages/reports/STAGE_5M_2_PUBLIC_DOCS_FEATURE_STATUS_ALIGNMENT_REPORT.md` in Russian.

Update allowed docs only to align stated status with verified repository evidence.

## 6. TESTS / VERIFICATION

Run:

```bash
git diff --check
```

If command examples change, verify them against:

```text
tg_msg_manager/cli_parser.py
README.md
COMMANDS.md
```

Do not claim checks passed unless actually run.

## 7. REPORT

Report must include:

- outcome token;
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`;
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`;
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`;
- files inspected;
- public-doc status mismatches found or explicit no-change reason;
- docs changed;
- confirmation that no runtime behavior changed.

Outcome token must be one of:

```text
PUBLIC_DOCS_FEATURE_STATUS_ALIGNED
PUBLIC_DOCS_FEATURE_STATUS_ALREADY_ALIGNED
PUBLIC_DOCS_FEATURE_STATUS_UPDATED_WITH_EXPORT_PM_CAVEAT
PUBLIC_DOCS_FEATURE_STATUS_BLOCKED_UNCLEAR_FEATURE_STATUS
```

## 8. COMPLETION CRITERIA

- Public docs no longer overstate feature or coverage status.
- Any docs change is minimal and evidence-backed.
- Report exists and is factual.
- Lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- No full diffs, broad summaries, or speculative roadmap language.
