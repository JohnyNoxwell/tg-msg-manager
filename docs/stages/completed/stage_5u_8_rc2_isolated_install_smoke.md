# STAGE 5U.8 — RC2 ISOLATED INSTALL SMOKE

Status: completed
Stage: 5U.8
Type: release verification
Depends on:
`docs/stages/reports/STAGE_5U_7_RC2_PACKAGE_ARTIFACT_VERIFICATION_REPORT.md`
with `PASSED`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply stage-reviewer, architecture-guard, and
stage-completion-auditor from `.skills/`. Run only isolated install/help smoke
from exact RC2 source; do not publish or start Stage 5V.1.

## 1. PURPOSE

Confirm an exact RC2 wheel installs in a fresh venv and preserves scoped public
help entrypoints.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_5U_7_RC2_PACKAGE_ARTIFACT_VERIFICATION_REPORT.md`
- `docs/stages/reports/STAGE_5U_1_POST_RC_TAG_SMOKE_FROM_TAG_REPORT.md`

Writable paths: `docs/stages/reports/STAGE_5U_8_RC2_ISOLATED_INSTALL_SMOKE_REPORT.md`,
`docs/stages/README.md`, lifecycle move of this stage file, and temporary files
only under `/tmp/tg-msg-manager-5u8-*`.

## 3. HARD PROHIBITIONS

- Do not edit source/tests/package metadata or unrelated docs.
- Do not run Telegram/live/runtime data commands, publish/upload, access
  credentials/private artifacts, or change/create/delete/push tags/releases.
- Do not leave temporary/build/install artifacts.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify prerequisite, clean state, and exact RC2 tag.
2. Export/build RC2 wheel under `/tmp` and install it into a fresh venv.
3. Run only the four help commands established by Stage 5U.1.
4. Write report draft, clean temp workspace, verify cleanup, finalize report,
   and complete lifecycle cleanup.

## 5. REQUIRED DOCS

Create only `docs/stages/reports/STAGE_5U_8_RC2_ISOLATED_INSTALL_SMOKE_REPORT.md`;
update the stage index only for lifecycle state.

## 6. TESTS / VERIFICATION

Verify local/remote tag; run `tg-msg-manager --help`, `tg-msg-manager target
--help`, `tg-msg-manager target names --help`, and `python -m
tg_msg_manager.cli --help` only; verify cleanup/status/diff.

## 7. REPORT

Write a Russian report with exact tag/source evidence, install and help-smoke
results, cleanup, prohibited commands not run, preserved scope, applied skills,
lifecycle notes, and recommendation
`Proceed to STAGE_5V_1_TESTPYPI_NAME_AUTH_PREPARATION`.

## 8. COMPLETION CRITERIA

Complete only if isolated install and all scoped help commands pass, cleanup
passes, no forbidden action occurred, and report exists.
Lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Follow `AGENTS.md`; do not paste full help/build output.
