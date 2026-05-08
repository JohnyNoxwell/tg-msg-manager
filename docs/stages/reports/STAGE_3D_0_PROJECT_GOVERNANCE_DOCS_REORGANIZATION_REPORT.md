# Stage 3D.0 - Project Governance / Documentation Reorganization Report

## 1. Summary

Stage 3D.0 reorganized project governance and documentation.

Completed:

- documentation tree reorganized under `docs/`;
- architecture, development, stages, roadmap, and archive docs separated;
- active, completed, and report stage files separated;
- `AGENTS.md` rewritten as the concise repository-level agent contract;
- root `README.md`, `COMMANDS.md`, and `CHANGELOG.md` aligned with the new docs map;
- final verification completed.

No product feature was added.
No SQLite schema change was made.
No legacy CLI behavior was changed.

## 2. Final documentation structure

Current top-level docs structure:

```text
docs/
  README.md
  architecture/
  development/
  stages/
    active/
    completed/
    reports/
  roadmap/
  archive/
    legacy_notes/
    old_prompts/
    deprecated_stage_files/
```

Index files:

- `docs/README.md`
- `docs/architecture/README.md`
- `docs/development/README.md`
- `docs/stages/README.md`
- `docs/roadmap/README.md`
- `docs/archive/README.md`

## 3. AGENTS.md contract

`AGENTS.md` is the repository-level agent contract.

It now defines:

- mandatory first-step workflow;
- project identity;
- architecture rules;
- protected files and boundaries;
- documentation map;
- relevant-doc selection policy;
- stage workflow;
- coding rules;
- testing policy;
- documentation policy;
- forbidden behavior;
- stop-and-report conditions;
- final response expectations.

It explicitly says not to read the whole docs tree by default and not to use archive files as current instructions unless explicitly asked.

## 4. Stage documentation lifecycle

Active stage files live under:

```text
docs/stages/active/
```

Completed task files are historical and live under:

```text
docs/stages/completed/
```

Reports are factual records and live under:

```text
docs/stages/reports/
```

Stage lifecycle:

```text
active task -> implementation -> tests/checks -> report -> completed task history
```

## 5. Architecture/development docs separation

Current architecture guidance lives under `docs/architecture/`.

Current development guidance lives under `docs/development/`.

Stage task files do not replace architecture docs. Reports record historical facts and may contain time-bound claims.

## 6. Archive policy

Archive is not current guidance.

Archived files live under:

- `docs/archive/legacy_notes/`
- `docs/archive/old_prompts/`
- `docs/archive/deprecated_stage_files/`

Agents should not read or execute archived files unless the user explicitly asks.

## 7. Root docs alignment

`README.md` remains user-facing and now links to:

- `docs/README.md`
- `COMMANDS.md`
- `AGENTS.md`

`COMMANDS.md` now links to:

- `docs/README.md`
- `AGENTS.md`

`CHANGELOG.md` includes the Stage 3D.0 docs/governance entry without claiming runtime feature additions.

## 8. Verification results

| Command | Result |
| --- | --- |
| `find docs -maxdepth 3 -type d | sort` | passed; expected docs directories present |
| `find docs -maxdepth 4 -type f | sort` | passed; docs tree listed |
| `grep -n "docs/stages/active" AGENTS.md` | passed |
| `grep -n "Do not read" AGENTS.md` | passed |
| `grep -n "archive" AGENTS.md` | passed |
| `grep -n "SQLite" AGENTS.md` | passed |
| `grep -n "Protected" AGENTS.md` | passed |
| `grep -R "not implemented yet" -n README.md COMMANDS.md docs || true` | completed; remaining matches are historical completed-stage/report lines or active stale-reference check commands |
| `grep -R "docs/refactor" -n README.md COMMANDS.md docs || true` | completed; remaining matches are historical archive/completed/report lines or active stale-reference check commands |
| `grep -R "old_prompts" -n README.md COMMANDS.md docs || true` | completed; matches are archive/index/stage-governance references |
| `python3 -m compileall tg_msg_manager` | passed |
| `python3 -m tg_msg_manager.cli --help` | passed |
| `python3 -m tg_msg_manager.cli export-channel --help` | passed |
| `pytest tests/test_channel_export_*.py` | passed, 130 tests |
| `ruff check tg_msg_manager tests` | passed |
| `ruff format --check tg_msg_manager tests` | passed, 238 files already formatted |

## 9. Runtime behavior statement

Runtime behavior was preserved.

This stage did not change:

- source code under `tg_msg_manager/`;
- tests under `tests/`;
- CLI command names or flags;
- export behavior;
- `db-export` behavior;
- `export-pm` behavior;
- `export-channel` behavior;
- retry/report/clean/delete/schedule/setup behavior;
- SQLite schema;
- migrations.

## 10. Remaining documentation limitations

- Historical reports and completed task files still contain old paths such as `docs/refactor/`; those are historical records, not current guidance.
- Historical Stage 3A/3B records still contain time-bound `not implemented yet` statements; current root docs and command docs do not present those as current behavior.
- `docs/architecture/PROJECT_ARCHITECTURE_OVERVIEW.md` remains a dated architecture snapshot and should be refreshed in a future architecture-specific task if needed.
- `.DS_Store` files still exist under `docs/`; they were not removed because cleanup was outside the stage scope.

## 11. Rules for future stages

- Read `AGENTS.md` first.
- Read the active task file under `docs/stages/active/`.
- Read only referenced architecture/development docs.
- Do not use completed tasks, reports, roadmap files, or archive files as implementation permission.
- Keep documentation updated with behavior, format, architecture, workflow, and testing changes.
- Do not claim a stage is complete while required docs are stale.

## 12. Status

Stage 3D.0.1: complete.
Stage 3D.0.2: complete.
Stage 3D.0.3: complete.
Stage 3D.0.4: complete.
Stage 3D.0.5: complete.
Stage 3D.0.6: complete.
Stage 3D.0.7: complete.

Stage 3D.0: complete.
