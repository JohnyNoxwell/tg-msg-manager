# STAGE 5K.0 — RELEASE CHECKLIST SCOPE / NO-PUBLISH BOUNDARY

Status: active task
Stage: 5K.0
Type: docs audit
Depends on: Stage 5J reports if present; current release-facing docs and package metadata

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Apply these skills before implementation:

- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md` after checks/report/cleanup

Do not execute Stage 5K.1 or later.

If `docs/stages/reports/STAGE_5J_3_RELEASE_READINESS_RECHECK_CHANGELOG_FINALIZATION_REPORT.md` is absent, record that the boundary can still be drafted but later decision stages must account for missing 5J completion.

## 1. PURPOSE

Define release-checklist scope and no-publish boundaries for the 5K block.

Create either a report-only decision or a durable docs-only release checklist scope document.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `README.md`
- `COMMANDS.md`
- `CHANGELOG.md`
- `pyproject.toml`
- `Makefile`
- `docs/README.md`
- `docs/development/README.md`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `docs/architecture/CURRENT_PROJECT_CONTEXT.md`
- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md`
- `docs/architecture/PRIVATE_ARCHIVE_CONTRACT_DEFERRED_DECISION.md`
- `docs/stages/README.md`

Read if present:

- `docs/stages/reports/STAGE_5J_3_RELEASE_READINESS_RECHECK_CHANGELOG_FINALIZATION_REPORT.md`
- `docs/stages/reports/STAGE_5J_2_FIXTURE_TO_CONTRACT_VERIFICATION_REPORT.md`
- `docs/stages/reports/STAGE_5J_1_NON_CHANNEL_CONTRACT_TESTS_IMPLEMENTATION_REPORT.md`
- `docs/stages/reports/STAGE_5H_0_CHANGELOG_RELEASE_NOTES_REFRESH_PRECHECK_REPORT.md`
- `docs/stages/reports/STAGE_5G_3_USER_FACING_RELEASE_READINESS_AUDIT_REPORT.md`

Writable paths:

- `docs/stages/reports/STAGE_5K_0_RELEASE_CHECKLIST_SCOPE_NO_PUBLISH_BOUNDARY_REPORT.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_5k_0_release_checklist_scope_no_publish_boundary.md`
- `docs/development/RELEASE_CHECKLIST_SCOPE.md` optional
- `docs/development/README.md` link-only if scope doc is created

## 3. HARD PROHIBITIONS

- Do not publish a release, create tags, bump version, change `pyproject.toml`, add runtime `__version__`, build release artifacts, upload artifacts, or claim a release occurred.
- Do not change runtime behavior, CLI behavior, output formats, tests, fixtures, SQLite/storage/services, or package behavior.
- Do not read private artifacts or real exports.
- Do not run live Telegram smoke checks requiring credentials.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Inspect required release-facing docs, package metadata, and recent reports before editing.
2. Define actual release actions and which are forbidden in 5K.
3. Define allowed checklist inspections, editable docs, safe local checks, optional/manual checks, and evidence needed before a future actual release stage.
4. Create `docs/development/RELEASE_CHECKLIST_SCOPE.md` only if a durable boundary doc is useful; otherwise keep report-only.
5. Create the Stage 5K.0 report in Russian.
6. Complete lifecycle cleanup according to `AGENTS.md`.

## 5. REQUIRED DOCS

If `docs/development/RELEASE_CHECKLIST_SCOPE.md` is created, ensure it is checklist-only, no-publish, and does not authorize version bump, tag creation, package build/upload, private data access, credentials, or real exports.

## 6. TESTS / VERIFICATION

Required:

```bash
git diff --check
```

Do not run publish/upload/build release commands.

## 7. REPORT

Create `docs/stages/reports/STAGE_5K_0_RELEASE_CHECKLIST_SCOPE_NO_PUBLISH_BOUNDARY_REPORT.md` in Russian.

Include status/outcome token, files inspected, forbidden release actions, allowed checklist actions, optional/manual actions, whether a durable boundary doc was created, checks run, version unchanged confirmation, no release/tag/publish confirmation, no runtime/CLI/SQLite/output behavior changes confirmation, private artifact boundary confirmation, `architecture-guard: applied from .skills/architecture-guard/SKILL.md`, and lifecycle notes.

Acceptable outcome tokens:

- `RELEASE_CHECKLIST_SCOPE_RECORDED_DOC_CREATED`
- `RELEASE_CHECKLIST_SCOPE_RECORDED_REPORT_ONLY`
- `BLOCKED_RELEASE_BOUNDARY_UNCLEAR`

## 8. COMPLETION CRITERIA

- Release checklist, release candidate decision, and actual release boundaries are separated.
- Forbidden release actions and safe checklist actions are recorded.
- Required checks are run or exact inability is recorded.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md` final format.

Do not paste full diffs, large file excerpts, or broad summaries.
