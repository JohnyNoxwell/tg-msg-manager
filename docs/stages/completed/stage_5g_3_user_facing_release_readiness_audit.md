# STAGE 5G.3 — User-Facing Release Readiness Audit

Status: active task
Stage: 5G.3
Type: docs audit
Depends on: completed 5F documentation/examples layer, current README/COMMANDS/development docs, current package metadata

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.
Use `stage-reviewer` before implementation, `architecture-guard` for release-boundary and post-processing/exporter boundary review, and `stage-completion-auditor` before claiming complete. If a skill is unavailable as a tool, read and apply the matching `.skills/<skill-name>/SKILL.md` file manually.

Do not execute any other 5G stage. This is not a release, tagging, packaging, or publishing stage.

## 1. PURPOSE

Audit whether the repository is understandable and safe for external users after the 5F block. Identify documentation, onboarding, privacy, example, limitation, and verification gaps. Do not publish or implement features.

Acceptable outcomes:

- `READINESS_AUDIT_COMPLETE_READY_FOR_LIMITED_EXTERNAL_USE`
- `READINESS_AUDIT_COMPLETE_DOC_GAPS_FOUND`
- `READINESS_AUDIT_COMPLETE_NOT_READY_FOR_EXTERNAL_USE`
- `BLOCKED_INSUFFICIENT_CONTEXT`

## 2. FILES TO INSPECT

Required reading:

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
- `docs/user/QUICKSTART.md`
- `docs/user/DATASET_DOCTOR_EXAMPLES.md`
- `docs/development/README.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- `docs/development/SAFE_FIRST_CHANNEL_EXPORT.md`
- `docs/development/CLI_CONTRACT.md`
- `docs/architecture/CURRENT_PROJECT_CONTEXT.md`
- `docs/architecture/README.md`
- `docs/architecture/POST_PROCESSING_BOUNDARY.md`
- `docs/architecture/STATIC_DATASET_SUMMARY_REPORT_DESIGN.md`
- `docs/stages/README.md`

If a listed file is absent, record the absence and continue.

Allowed docs-fix targets:

- `README.md`
- `COMMANDS.md`
- `docs/README.md`
- `docs/user/QUICKSTART.md`
- `docs/user/DATASET_DOCTOR_EXAMPLES.md`
- `docs/development/README.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- `docs/development/SAFE_FIRST_CHANNEL_EXPORT.md`
- `docs/architecture/README.md`
- `docs/architecture/POST_PROCESSING_BOUNDARY.md`
- `docs/architecture/STATIC_DATASET_SUMMARY_REPORT_DESIGN.md`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_5G_3_USER_FACING_RELEASE_READINESS_AUDIT_REPORT.md`
- lifecycle copy under `docs/stages/completed/`

## 3. HARD PROHIBITIONS

- Do not publish a release, create tags, bump versions, change `pyproject.toml` version, or add runtime `__version__`.
- Do not change package name, module root, console script, runtime code, CLI behavior, command names, flags, defaults, outputs, tests, SQLite, dataset format, storage contracts, exporter, validator, doctor, or post-processing implementation.
- Do not create GUI/Web/SaaS, analytics, OSINT, profiling, media analysis, OCR, STT, or LLM behavior.
- Do not read private artifacts or use real exports as examples.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Inspect required files; do not edit yet.
2. Audit project identity, installation/setup, first-run flow, command documentation, dataset examples, validation/doctor read-only boundary, privacy warnings, architecture boundaries, verification docs, and known limitations.
3. If small documentation inconsistencies are found and safe, make minimal docs-only fixes in allowed files.
4. Classify readiness as `READY_FOR_INTERNAL_USE`, `READY_FOR_LIMITED_EXTERNAL_USE`, `NOT_READY_FOR_EXTERNAL_USE`, or another explicit factual classification.
5. Create the required Russian factual report and then complete lifecycle cleanup according to `AGENTS.md`.

## 5. REQUIRED DOCS

Preferred output is audit report only. Docs fixes are allowed only when they are small, directly supported by inspected files, and do not change behavior or release posture.

Keep `COMMANDS.md` as the command reference. Keep release/publishing actions out of scope.

## 6. TESTS / VERIFICATION

Run:

```bash
git diff --check
```

If command examples are edited, verify against:

- `tg_msg_manager/cli_parser.py`
- `COMMANDS.md`
- `README.md`

If package identity docs are edited, verify against:

- `pyproject.toml`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`

If verification commands are referenced or changed, verify against:

- `Makefile`
- `README.md`
- `docs/development/README.md`

Do not claim checks passed unless actually run.

## 7. REPORT

Create `docs/stages/reports/STAGE_5G_3_USER_FACING_RELEASE_READINESS_AUDIT_REPORT.md` in Russian.

Include:

- status and outcome token;
- files inspected;
- readiness classification;
- blockers;
- non-blocking gaps;
- docs fixes made, if any;
- recommended next stages;
- checks run;
- confirmations: no release performed, no version changed, no runtime changed, no private artifacts read, no CLI/SQLite/dataset behavior changed;
- lifecycle notes.

## 8. COMPLETION CRITERIA

- Required audit areas are evaluated.
- Readiness classification is recorded.
- Only allowed docs/report/lifecycle files changed.
- Required report exists.
- Required checks are run or exact skip reasons are recorded.
- `stage-completion-auditor` is applied.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`, be under 1200 characters, and include only meaningful sections. Do not paste full diffs or broad summaries.
