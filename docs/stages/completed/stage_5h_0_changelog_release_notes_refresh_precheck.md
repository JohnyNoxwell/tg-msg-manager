# STAGE 5H.0 — Changelog / Release Notes Refresh Precheck

Status: active task
Stage: 5H.0
Type: docs precheck
Depends on: completed 5F and 5G reports listed below; current release-facing docs

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.
Use `.skills/stage-reviewer/SKILL.md` before executing this stage.
Use `.skills/architecture-guard/SKILL.md` because this stage checks release and architecture boundary claims.
Use `.skills/stage-completion-auditor/SKILL.md` before claiming completion.
Do not execute any later stage.

## 1. PURPOSE

Audit whether `CHANGELOG.md` and release-facing docs are stale compared with completed 5F/5G history.
Produce a factual report.
Default to report-only.
Edit `CHANGELOG.md` only if the audit proves a docs-only unreleased entry is safe.

## 2. FILES TO INSPECT

Required:

```text
AGENTS.md
.skills/stage-reviewer/SKILL.md
.skills/architecture-guard/SKILL.md
.skills/stage-completion-auditor/SKILL.md
CHANGELOG.md
README.md
COMMANDS.md
docs/README.md
docs/user/QUICKSTART.md
docs/user/DATASET_DOCTOR_EXAMPLES.md
docs/architecture/CURRENT_PROJECT_CONTEXT.md
docs/architecture/README.md
docs/architecture/POST_PROCESSING_BOUNDARY.md
docs/architecture/STATIC_DATASET_SUMMARY_REPORT_DESIGN.md
docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md
docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md
docs/development/SAFE_FIRST_CHANNEL_EXPORT.md
docs/stages/README.md
pyproject.toml
```

Read if present; record missing reports and continue:

```text
docs/stages/reports/STAGE_5F_1_USER_DOCUMENTATION_NAVIGATION_AUDIT_QUICKSTART_CONSOLIDATION_REPORT.md
docs/stages/reports/STAGE_5F_2_SYNTHETIC_CHANNEL_DATASET_EXAMPLE_REPORT.md
docs/stages/reports/STAGE_5F_3_DATASET_DOCTOR_OUTPUT_EXAMPLES_REPORT.md
docs/stages/reports/STAGE_5F_4_POST_PROCESSING_EXAMPLE_CATALOGUE_REFINEMENT_REPORT.md
docs/stages/reports/STAGE_5F_5_STATIC_DATASET_SUMMARY_REPORT_DESIGN_REPORT.md
docs/stages/reports/STAGE_5G_0_POST_5F_DOCUMENTATION_EXAMPLES_CONSISTENCY_AUDIT_REPORT.md
docs/stages/reports/STAGE_5G_1_SYNTHETIC_EXAMPLES_REGRESSION_CHECK_REPORT.md
docs/stages/reports/STAGE_5G_2_NON_CHANNEL_DATASET_CONTRACT_PRECHECK_REPORT.md
docs/stages/reports/STAGE_5G_3_USER_FACING_RELEASE_READINESS_AUDIT_REPORT.md
```

Allowed to change:

```text
docs/stages/reports/STAGE_5H_0_CHANGELOG_RELEASE_NOTES_REFRESH_PRECHECK_REPORT.md
docs/stages/README.md
docs/stages/completed/stage_5h_0_changelog_release_notes_refresh_precheck.md
CHANGELOG.md
```

Do not inspect private artifacts, ignored exports, sessions, credentials, screenshots, logs, or local DB files.

## 3. HARD PROHIBITIONS

Do not publish a release, create tags, bump versions, change `pyproject.toml`, add runtime `__version__`, package/upload artifacts, or claim a release occurred.
Do not change runtime behavior, CLI behavior, tests, SQLite, dataset formats, exporter, validator, doctor, storage, services, command names, flags, defaults, or output semantics.
Do not claim unimplemented contracts, reports, or future stages are complete.
Do not use real exports or private artifacts as examples.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Inspect the required files and listed reports; do not edit yet.
2. Decide whether `CHANGELOG.md` is behind 5F/5G completed history.
3. Check whether 5F user docs/examples/design changes and 5G consistency/regression/precheck/readiness findings are represented accurately.
4. Decide whether the next action should be report-only precheck, docs-only changelog refresh, release-notes draft, release checklist, or no action.
5. If and only if safe, add a minimal unreleased docs-only `CHANGELOG.md` entry supported by current docs/reports.
6. Write the required report in Russian.
7. Complete lifecycle cleanup according to `AGENTS.md`.

## 5. REQUIRED DOCS

Always create:

```text
docs/stages/reports/STAGE_5H_0_CHANGELOG_RELEASE_NOTES_REFRESH_PRECHECK_REPORT.md
```

Update `docs/stages/README.md` during lifecycle cleanup.
Update `CHANGELOG.md` only under the conditions in section 4.
No other docs changes are allowed.

## 6. TESTS / VERIFICATION

Run:

```bash
git diff --check
```

If `CHANGELOG.md` is edited, verify in the report:

```text
no release/tag/published package is claimed
package version remains unchanged
all claims are supported by completed reports or current docs
no future work is described as complete
```

Do not claim checks passed unless they were run.
Runtime tests are not required for report-only or docs-only changelog work.

## 7. REPORT

Report must be factual and written in Russian.
Include:

```text
status and outcome token
files inspected
missing reports, if any
whether CHANGELOG.md is stale
whether changelog edits were made or deferred
proposed changelog/release-note bullets if deferred
release boundary confirmation
version unchanged confirmation
no runtime/CLI/SQLite/dataset behavior changes confirmation
checks run
lifecycle notes
architecture-guard: applied from .skills/architecture-guard/SKILL.md
stage-reviewer: applied from .skills/stage-reviewer/SKILL.md
stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md
```

Outcome token must be one of:

```text
CHANGELOG_REFRESH_PRECHECK_COMPLETE_REFRESH_RECOMMENDED
CHANGELOG_REFRESH_PRECHECK_COMPLETE_NO_CHANGE_NEEDED
CHANGELOG_REFRESH_PRECHECK_COMPLETE_CHANGELOG_UPDATED_DOCS_ONLY
BLOCKED_RELEASE_BOUNDARY_UNCLEAR
```

## 8. COMPLETION CRITERIA

Required report exists.
Any `CHANGELOG.md` edit is docs-only, unreleased, and evidence-backed.
No version, release, runtime, CLI, SQLite, dataset, service, or test behavior changed.
Required check is run or failure is recorded.
Lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`.
No full diffs.
No broad summaries.
No next-stage implementation.
End with `OUTPUT LIMITS`.
