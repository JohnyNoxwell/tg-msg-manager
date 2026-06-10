# STAGE 5U.7 — RC2 PACKAGE ARTIFACT VERIFICATION

Status: active task
Stage: 5U.7
Type: packaging verification
Depends on: `docs/stages/reports/STAGE_5U_6_CREATE_RC2_TAG_REPORT.md` with
`PASSED`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply stage-reviewer, architecture-guard, and
stage-completion-auditor from `.skills/`. Verify artifacts from exact
`v0.1.0-rc2`; do not install them or start Stage 5U.8.

## 1. PURPOSE

Build exact RC2 source in `/tmp`, run twine checks, inspect package metadata,
and record immutable artifact names/checksums without publishing.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_5U_6_CREATE_RC2_TAG_REPORT.md`
- `docs/stages/reports/STAGE_5U_4_LICENSE_METADATA_PACKAGE_VERIFICATION_REPORT.md`

Writable paths: `docs/stages/reports/STAGE_5U_7_RC2_PACKAGE_ARTIFACT_VERIFICATION_REPORT.md`,
`docs/stages/README.md`, lifecycle move of this stage file, and temporary files
only under `/tmp/tg-msg-manager-5u7-*`.

## 3. HARD PROHIBITIONS

- Do not edit repository source/tests/docs except required stage docs.
- Do not install built wheel, run CLI smoke, publish/upload, change/create/
  delete/push tags, create releases, or access credentials/private artifacts.
- Do not leave temporary/build artifacts in the repository or `/tmp`.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify prerequisite, clean state, and exact local/remote RC2 tag.
2. Export RC2 source into a fresh `/tmp` workspace and inspect metadata.
3. Build sdist/wheel, run twine check, inspect structured artifact metadata,
   and record SHA-256 checksums.
4. Write report draft, remove temp workspace, verify cleanup, finalize report,
   and complete lifecycle cleanup.

## 5. REQUIRED DOCS

Create only
`docs/stages/reports/STAGE_5U_7_RC2_PACKAGE_ARTIFACT_VERIFICATION_REPORT.md`;
update the stage index only for lifecycle state.

## 6. TESTS / VERIFICATION

Use `git archive`, isolated tooling venv, `python -m build`, `python -m twine
check`, structured wheel/sdist metadata readers, `shasum -a 256`, cleanup
checks, `git status --short`, and `git diff --check`.

## 7. REPORT

Write a Russian report with tag evidence, temp path, metadata, artifact names/
checksums, build/twine results, cleanup, no-publish/no-install confirmation,
preserved scope, applied skills, lifecycle notes, and recommendation
`Proceed to STAGE_5U_8_RC2_ISOLATED_INSTALL_SMOKE`.

## 8. COMPLETION CRITERIA

Complete only if exact RC2 artifacts build and pass twine/metadata checks,
checksums are recorded, cleanup passes, and report exists.
Lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Follow `AGENTS.md`; do not paste full build output or metadata dumps.
