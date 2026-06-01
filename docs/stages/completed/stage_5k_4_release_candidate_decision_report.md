# STAGE 5K.4 — RELEASE CANDIDATE DECISION REPORT

Status: active task
Stage: 5K.4
Type: report
Depends on: Stage 5K.0, 5K.1, 5K.2, and 5K.3 reports

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Apply these skills before implementation:

- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md` after checks/report/cleanup

If required 5K reports are absent, block or downgrade to partial decision with exact missing reports.

Do not perform an actual release.

## 1. PURPOSE

Consolidate Stage 5K findings and decide whether a future actual release stage is safe to create.

This is a decision/report stage only.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/reports/STAGE_5K_0_RELEASE_CHECKLIST_SCOPE_NO_PUBLISH_BOUNDARY_REPORT.md`
- `docs/stages/reports/STAGE_5K_1_PACKAGING_METADATA_READINESS_AUDIT_REPORT.md`
- `docs/stages/reports/STAGE_5K_2_DOCUMENTATION_PRIVACY_CHANGELOG_RELEASE_AUDIT_REPORT.md`
- `docs/stages/reports/STAGE_5K_3_LOCAL_VERIFICATION_MATRIX_REPORT.md`
- `docs/development/RELEASE_CHECKLIST_SCOPE.md` if present
- `docs/development/LOCAL_VERIFICATION_MATRIX.md` if present
- `README.md`
- `COMMANDS.md`
- `CHANGELOG.md`
- `pyproject.toml`
- `Makefile`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md`
- `docs/stages/README.md`

Writable paths:

- `docs/stages/reports/STAGE_5K_4_RELEASE_CANDIDATE_DECISION_REPORT.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_5k_4_release_candidate_decision_report.md`
- `docs/development/RELEASE_CANDIDATE_DECISION.md` optional

## 3. HARD PROHIBITIONS

- Do not publish a release, create tags, bump version, change `pyproject.toml`, add runtime `__version__`, build/upload release artifacts, or claim a release occurred.
- Do not change runtime behavior, CLI behavior, tests, fixtures, docs/changelog except optional decision doc, SQLite/storage/services, or output formats.
- Do not read private artifacts or real exports.
- Do not rerun the full verification matrix unless explicitly re-scoped.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify required 5K reports exist; block or downgrade if evidence is missing.
2. Inspect 5K reports and release-facing evidence before editing.
3. Classify release candidate posture and record blockers, non-blocking gaps, required checks status from 5K.3, and whether a future actual release stage is safe to create.
4. Create optional `docs/development/RELEASE_CANDIDATE_DECISION.md` only if useful as a durable decision artifact.
5. Create the Stage 5K.4 report in Russian.
6. Complete lifecycle cleanup according to `AGENTS.md`.

## 5. REQUIRED DOCS

Default is report-only.

Do not edit release-facing docs/changelog in this stage. Recommend a follow-up stage for minor docs links.

## 6. TESTS / VERIFICATION

Required:

```bash
git diff --check
```

Do not rerun the full local verification matrix by default. Rely on Stage 5K.3 results and record whether they are sufficient.

## 7. REPORT

Create `docs/stages/reports/STAGE_5K_4_RELEASE_CANDIDATE_DECISION_REPORT.md` in Russian.

Include status/outcome token, files inspected, 5K report summary, readiness classification, blockers, non-blocking gaps, required checks status from 5K.3, whether future actual release stage is safe to create, recommended next stage, release boundary confirmation, version unchanged confirmation, no runtime/CLI/SQLite/output behavior changes confirmation, private artifact boundary confirmation, `architecture-guard: applied from .skills/architecture-guard/SKILL.md`, and lifecycle notes.

Acceptable outcome tokens:

- `READY_FOR_RELEASE_CANDIDATE_CHECKLIST`
- `READY_FOR_LIMITED_EXTERNAL_USE_ONLY`
- `BLOCKED_BY_TEST_FAILURES`
- `BLOCKED_BY_DOCS_OR_PRIVACY_GAPS`
- `BLOCKED_BY_PACKAGING_METADATA_GAPS`
- `BLOCKED_BY_MISSING_5K_EVIDENCE`

## 8. COMPLETION CRITERIA

- Decision is evidence-backed from 5K reports or blocked by exact missing evidence.
- Future release stage safety is explicitly classified.
- Required checks are run or exact inability is recorded.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md` final format.

Do not paste full diffs, large file excerpts, or broad summaries.
