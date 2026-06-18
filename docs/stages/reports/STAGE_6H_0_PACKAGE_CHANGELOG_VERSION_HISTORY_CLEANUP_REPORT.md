# STAGE 6H.0 - PACKAGE CHANGELOG VERSION HISTORY CLEANUP REPORT

Статус: complete
Дата: 2026-06-18

## Scope

- Выполнена docs-only правка истории версий.
- `pyproject.toml` оставлен на package version `0.1.2`.
- Runtime code, tests, CLI behavior, package metadata, SQLite schema, dataset formats и release tags не изменялись.

## Changed files

- `CHANGELOG.md`
- `docs/archive/legacy_notes/PRE_PACKAGE_INTERNAL_CHANGELOG_4X.md`
- `docs/stages/completed/STAGE_6H_0_PACKAGE_CHANGELOG_VERSION_HISTORY_CLEANUP.md`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_6H_0_PACKAGE_CHANGELOG_VERSION_HISTORY_CLEANUP_REPORT.md`

## What changed

- Root `CHANGELOG.md` теперь явно описан как changelog публичных package semver releases.
- Исторические internal/stage-numbered записи `4.x` и `3.x` перенесены в archive legacy note.
- Архивный файл явно помечает перенесённые записи как исторические project notes, не package releases.

## Verification

- `rg -n "^version = \"0\.1\.2\"$" pyproject.toml`: passed, found `version = "0.1.2"`.
- `rg -n "^## \[(4|3)\." CHANGELOG.md`: passed, no matches; command exited `1` as expected for no matches.
- `rg -n "^## \[(4|3)\." docs/archive/legacy_notes/PRE_PACKAGE_INTERNAL_CHANGELOG_4X.md`: passed, archived matches found from `4.2.33` through `3.5.0`.
- `rg --files docs/stages/active`: passed, no active stage files; command exited `1` as expected for no matches.
- `test -f docs/stages/completed/STAGE_6H_0_PACKAGE_CHANGELOG_VERSION_HISTORY_CLEANUP.md`: passed.
- `test -f docs/stages/reports/STAGE_6H_0_PACKAGE_CHANGELOG_VERSION_HISTORY_CLEANUP_REPORT.md`: passed.
- `python3 -m compileall tg_msg_manager`: not run, docs-only stage with no code/test changes.

## Preservation

- behavior: yes
- CLI: yes
- SQLite: yes
- scope: yes

## Skill application

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`

## Notes

- Existing unrelated worktree changes were preserved and not reverted.
- Lifecycle cleanup moved the stage file to `docs/stages/completed/` and updated `docs/stages/README.md`.
