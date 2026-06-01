# STAGE 5K.2 — DOCUMENTATION / PRIVACY / CHANGELOG RELEASE AUDIT

Status: active task
Stage: 5K.2
Type: docs audit
Depends on: Stage 5K.0 and 5K.1 reports; recent Stage 5J reports if present

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Apply these skills before implementation:

- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md` after checks/report/cleanup

Do not execute Stage 5K.3 or later.

## 1. PURPOSE

Audit release-facing docs for accuracy, privacy safety, changelog consistency, known limitations, and no-publish boundary compliance.

Make only minimal docs/changelog fixes supported by completed reports and current repository state.

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
- `docs/user/QUICKSTART.md`
- `docs/user/DATASET_DOCTOR_EXAMPLES.md`
- `docs/development/README.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- `docs/development/RELEASE_CHECKLIST_SCOPE.md` if present
- `docs/development/NON_CHANNEL_SYNTHETIC_FIXTURES_PLAN.md`
- `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md`
- `docs/architecture/README.md`
- `docs/architecture/CURRENT_PROJECT_CONTEXT.md`
- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md`
- `docs/architecture/PRIVATE_ARCHIVE_CONTRACT_DEFERRED_DECISION.md`
- `docs/architecture/POST_PROCESSING_BOUNDARY.md`
- `docs/stages/README.md`

Read if present:

- `docs/stages/reports/STAGE_5J_3_RELEASE_READINESS_RECHECK_CHANGELOG_FINALIZATION_REPORT.md`
- `docs/stages/reports/STAGE_5J_2_FIXTURE_TO_CONTRACT_VERIFICATION_REPORT.md`
- `docs/stages/reports/STAGE_5J_1_NON_CHANNEL_CONTRACT_TESTS_IMPLEMENTATION_REPORT.md`
- `docs/stages/reports/STAGE_5K_0_RELEASE_CHECKLIST_SCOPE_NO_PUBLISH_BOUNDARY_REPORT.md`
- `docs/stages/reports/STAGE_5K_1_PACKAGING_METADATA_READINESS_AUDIT_REPORT.md`

Writable paths:

- `CHANGELOG.md`
- `README.md`
- `COMMANDS.md`
- `docs/README.md`
- `docs/user/QUICKSTART.md`
- `docs/development/README.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `docs/development/RELEASE_CHECKLIST_SCOPE.md`
- `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md`
- `docs/architecture/README.md`
- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md`
- `docs/stages/reports/STAGE_5K_2_DOCUMENTATION_PRIVACY_CHANGELOG_RELEASE_AUDIT_REPORT.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_5k_2_documentation_privacy_changelog_release_audit.md`

## 3. HARD PROHIBITIONS

- Do not publish a release, create tags, bump version, change `pyproject.toml`, add runtime `__version__`, package/upload artifacts, or claim a release occurred.
- Do not change runtime behavior, CLI behavior, tests, fixtures, output formats, SQLite/storage/services, or package behavior.
- Do not claim unsupported test/contract coverage.
- Do not read private artifacts or real exports.
- Do not add OSINT, profiling, identity, analytics, LLM, OCR/STT, media recognition, GUI/Web/SaaS claims.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Inspect release-facing docs, privacy docs, changelog, contract docs, and recent reports before editing.
2. Audit `[Unreleased]`, non-channel fixture/test/contract claims, deferred areas, privacy warnings, docs links, known limitations, no-publish boundary, parser-aligned examples, and stale future-work references.
3. Apply minimal evidence-backed docs/changelog fixes only in allowed paths.
4. Create the Stage 5K.2 report in Russian.
5. Complete lifecycle cleanup according to `AGENTS.md`.

## 5. REQUIRED DOCS

Docs fixes must keep these deferred areas visible:

- `export-pm`;
- private archive contract;
- full raw JSON profile;
- exact rotation thresholds;
- `.export_state`;
- SQLite schema contract status;
- live Telegram smoke checks.

## 6. TESTS / VERIFICATION

Required:

```bash
git diff --check
```

If command examples change, verify them against:

- `tg_msg_manager/cli_parser.py`
- `README.md`
- `COMMANDS.md`

If changelog/test coverage claims change, verify them against recent stage reports.

If package/version claims change, verify them against:

- `pyproject.toml`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`

## 7. REPORT

Create `docs/stages/reports/STAGE_5K_2_DOCUMENTATION_PRIVACY_CHANGELOG_RELEASE_AUDIT_REPORT.md` in Russian.

Include status/outcome token, files inspected, docs/changelog/privacy findings, blockers, non-blocking gaps, docs fixes made, release boundary confirmation, version unchanged confirmation, checks run, no runtime/CLI/SQLite/output behavior changes confirmation, private artifact boundary confirmation, `architecture-guard: applied from .skills/architecture-guard/SKILL.md`, and lifecycle notes.

Acceptable outcome tokens:

- `DOCS_PRIVACY_CHANGELOG_RELEASE_AUDIT_COMPLETE`
- `DOCS_PRIVACY_CHANGELOG_RELEASE_AUDIT_COMPLETE_AFTER_DOC_FIXES`
- `DOCS_PRIVACY_CHANGELOG_RELEASE_AUDIT_FOUND_BLOCKERS`
- `BLOCKED_MISSING_RELEASE_SCOPE_OR_RECENT_REPORTS`

## 8. COMPLETION CRITERIA

- Docs/privacy/changelog release audit findings are recorded.
- Evidence-backed docs fixes, if any, are complete.
- Release boundary and version unchanged state are confirmed.
- Required checks are run or exact inability is recorded.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md` final format.

Do not paste full diffs, large file excerpts, or broad summaries.
