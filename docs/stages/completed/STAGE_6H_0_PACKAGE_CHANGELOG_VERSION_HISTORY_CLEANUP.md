# STAGE 6H.0 - PACKAGE CHANGELOG VERSION HISTORY CLEANUP

Status: completed
Stage: 6H.0
Type: docs
Depends on: `pyproject.toml` package version `0.1.2`, root `CHANGELOG.md`, `docs/archive/README.md`, `docs/stages/README.md`

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` first.
- Apply `stage-reviewer` before executing this stage.
- Execute only this docs-only stage.
- Use `stage-completion-auditor` after the stage is claimed complete.

## 1. PURPOSE

Resolve confusing external version history by making `CHANGELOG.md` package-semver-only for `tg-msg-manager` releases and moving old `4.x` internal/stage history to an archive file with an explicit non-package-release label.

## 2. FILES TO INSPECT

- `pyproject.toml`
- `CHANGELOG.md`
- `docs/archive/README.md`
- `docs/stages/README.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`

## 3. HARD PROHIBITIONS

- Do not change `pyproject.toml` version.
- Do not change runtime code, tests, CLI behavior, package metadata, SQLite schema, dataset formats, or release tags.
- Do not delete old `4.x` or `3.x` history; preserve it under `docs/archive/legacy_notes/`.
- Do not edit unrelated docs, completed stage files, existing unrelated reports, or archive content not created by this stage.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Confirm `pyproject.toml` currently declares package version `0.1.2`.
2. Create `docs/archive/legacy_notes/PRE_PACKAGE_INTERNAL_CHANGELOG_4X.md` and move all root `CHANGELOG.md` entries from `4.2.33` through `3.5.0` there.
3. Add a short note in `CHANGELOG.md` stating it tracks public package semver releases only, and link to the archived internal history.
4. Keep `CHANGELOG.md` entries for `Unreleased`, `0.1.2`, and `0.1.1` intact except for the new explanatory note.
5. Create the factual stage report, then perform lifecycle cleanup according to `AGENTS.md`.

## 5. REQUIRED DOCS

- Update `CHANGELOG.md`.
- Create `docs/archive/legacy_notes/PRE_PACKAGE_INTERNAL_CHANGELOG_4X.md`.
- Update `docs/stages/README.md` after report creation and cleanup.

## 6. TESTS / VERIFICATION

- `rg -n "^## \\[(4|3)\\." CHANGELOG.md`: must return no matches.
- `rg -n "^## \\[(4|3)\\." docs/archive/legacy_notes/PRE_PACKAGE_INTERNAL_CHANGELOG_4X.md`: must return archived matches.
- `python3 -m compileall tg_msg_manager`: not required; docs-only, no code/test changes.
- Do not claim checks passed unless actually run.

## 7. REPORT

Create `docs/stages/reports/STAGE_6H_0_PACKAGE_CHANGELOG_VERSION_HISTORY_CLEANUP_REPORT.md` in Russian with:

- scope;
- changed files;
- verification results;
- preservation notes;
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`;
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`.

## 8. COMPLETION CRITERIA

- Root changelog no longer presents `4.x` or `3.x` entries as package versions.
- Archived internal history exists and clearly says it is not package release history.
- `pyproject.toml` remains `0.1.2`.
- Required verification is recorded.
- Final report exists.
- Lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- No full diffs.
- No broad summary.
