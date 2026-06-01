# STAGE 5J.3 — RELEASE READINESS RECHECK / CHANGELOG FINALIZATION

Status: active task
Stage: 5J.3
Type: docs audit
Depends on: Stage 5J.1 and 5J.2 reports

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Apply these skills before implementation:

- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md` after checks/report/cleanup

If Stage 5J.1 or 5J.2 reports are missing, block or downgrade to pre-release precheck.

Do not perform an actual release.

## 1. PURPOSE

Recheck release-facing docs after Stage 5I and Stage 5J.1/5J.2 work.

Verify whether README, COMMANDS, docs indexes, changelog, contract docs, test plan, and reports present a coherent limited-use state.

Update `[Unreleased]` changelog entries and docs links only when necessary.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `CHANGELOG.md`
- `README.md`
- `COMMANDS.md`
- `docs/README.md`
- `docs/architecture/README.md`
- `docs/development/README.md`
- `docs/user/QUICKSTART.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- `docs/development/NON_CHANNEL_SYNTHETIC_FIXTURES_PLAN.md`
- `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md`
- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md`
- `docs/architecture/PRIVATE_ARCHIVE_CONTRACT_DEFERRED_DECISION.md`
- `docs/architecture/CURRENT_PROJECT_CONTEXT.md`
- `docs/stages/README.md`
- `pyproject.toml`
- `Makefile`
- `docs/stages/reports/STAGE_5G_3_USER_FACING_RELEASE_READINESS_AUDIT_REPORT.md`
- `docs/stages/reports/STAGE_5H_0_CHANGELOG_RELEASE_NOTES_REFRESH_PRECHECK_REPORT.md`
- `docs/stages/reports/STAGE_5I_1_USER_DB_EXPORT_SYNTHETIC_FIXTURE_IMPLEMENTATION_REPORT.md`
- `docs/stages/reports/STAGE_5I_2_NON_CHANNEL_CONTRACT_TEST_PLAN_REPORT.md`
- `docs/stages/reports/STAGE_5I_3_NON_CHANNEL_EXPORT_CONTRACT_V1_DRAFT_REPORT.md`
- `docs/stages/reports/STAGE_5J_1_NON_CHANNEL_CONTRACT_TESTS_IMPLEMENTATION_REPORT.md`
- `docs/stages/reports/STAGE_5J_2_FIXTURE_TO_CONTRACT_VERIFICATION_REPORT.md`

Writable paths:

- `CHANGELOG.md`
- `README.md`
- `COMMANDS.md`
- `docs/README.md`
- `docs/architecture/README.md`
- `docs/development/README.md`
- `docs/user/QUICKSTART.md`
- `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md`
- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md`
- `docs/stages/reports/STAGE_5J_3_RELEASE_READINESS_RECHECK_CHANGELOG_FINALIZATION_REPORT.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_5j_3_release_readiness_recheck_changelog_finalization.md`

## 3. HARD PROHIBITIONS

- Do not publish a release, create tags, bump versions, add runtime `__version__`, package artifacts, or upload artifacts.
- Do not change `pyproject.toml`.
- Do not change runtime behavior, CLI behavior, output formats, tests, fixtures, SQLite/storage/services, or private archive behavior.
- Do not claim release occurred.
- Do not claim broader readiness than evidence supports.
- Do not read private artifacts or real exports.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify Stage 5J.1 and 5J.2 reports exist; block or downgrade if missing.
2. Inspect release-facing docs and reports before editing.
3. Verify the readiness classification, `[Unreleased]` changelog accuracy, docs/index links, parser parity for command examples, and package version claims.
4. Preserve visible deferred areas: `export-pm`, raw JSON, exact rotation thresholds, `.export_state`, SQLite schema contract status, and live smoke checks.
5. Apply minimal changelog/docs-link fixes only when necessary.
6. Create the Stage 5J.3 report in Russian.
7. Complete lifecycle cleanup according to `AGENTS.md`.

## 5. REQUIRED DOCS

Update only release-facing docs or links that are inaccurate after Stage 5I/5J work.

Do not add release checklist execution, tag instructions as completed, or publish claims.

## 6. TESTS / VERIFICATION

Required:

```bash
git diff --check
```

If command examples change, verify them against:

- `tg_msg_manager/cli_parser.py`
- `README.md`
- `COMMANDS.md`

If version/package claims change, verify them against:

- `pyproject.toml`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`

If test coverage claims change, verify them against:

- `docs/stages/reports/STAGE_5J_1_NON_CHANNEL_CONTRACT_TESTS_IMPLEMENTATION_REPORT.md`
- `docs/stages/reports/STAGE_5J_2_FIXTURE_TO_CONTRACT_VERIFICATION_REPORT.md`

Runtime tests are not required unless documentation claims depend on them.

## 7. REPORT

Create `docs/stages/reports/STAGE_5J_3_RELEASE_READINESS_RECHECK_CHANGELOG_FINALIZATION_REPORT.md` in Russian.

Include:

- status and outcome token;
- files inspected;
- readiness classification;
- changelog changes;
- docs/index changes;
- blockers;
- non-blocking gaps;
- release boundary confirmation;
- version unchanged confirmation;
- checks run;
- no runtime/CLI/SQLite/output behavior changes confirmation;
- private artifact boundary confirmation;
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`;
- lifecycle notes.

Acceptable outcome tokens:

- `RELEASE_READINESS_RECHECK_COMPLETE_LIMITED_EXTERNAL_USE_CONFIRMED`
- `RELEASE_READINESS_RECHECK_COMPLETE_CHANGELOG_FINALIZED`
- `RELEASE_READINESS_RECHECK_BLOCKED_WAITING_FOR_5J1_5J2`
- `RELEASE_READINESS_RECHECK_FOUND_RELEASE_BLOCKERS`

## 8. COMPLETION CRITERIA

- Readiness classification is recorded and supported by evidence.
- Changelog/docs/index fixes, if needed, are complete.
- Release boundaries and version unchanged state are confirmed.
- Required checks are run or exact inability is recorded.
- No runtime/CLI/SQLite/output/test/fixture behavior changed.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md` final format.

Do not paste full diffs, large file excerpts, or broad summaries.
