# Stage 3D.0.6 - Root Docs Alignment Report

## 1. Summary

Root documentation was aligned with the reorganized docs tree and rewritten `AGENTS.md`.

No runtime code was changed. No CLI behavior was changed.

## 2. README changes

`README.md` remains user-facing.

Added compact links to:

- `docs/README.md`
- `COMMANDS.md`
- `AGENTS.md`

No feature descriptions or command behavior were changed.

## 3. COMMANDS changes

`COMMANDS.md` now links to:

- `docs/README.md`
- `AGENTS.md`

The existing `export-channel` command documentation was left behavior-stable. It already documented current media and discussion options, including:

- `--media none|metadata|full`
- default `metadata` media mode
- `--max-media-size`
- `--media-types`
- `--discussion none|full`
- `--max-comments-per-post`
- current discussion media limitation

## 4. CHANGELOG changes

Added `4.2.26` with a Stage 3D.0 docs/governance entry.

The entry states:

- documentation tree reorganized;
- stage docs separated into active/completed/reports/archive;
- `AGENTS.md` rewritten as repository agent contract;
- root docs aligned.

It does not claim runtime features were added.

## 5. Path references updated

Root `README.md` and `COMMANDS.md` now point to the current docs map.

Historical `docs/refactor` references remain in old changelog entries, reports, completed task files, and archive files as historical context.

## 6. Stale claims removed

No false current root-doc claims about Stage 3B/3C being unimplemented were found.

Remaining `not implemented yet` strings are historical Stage 3A/3B records or active stale-reference check commands. Current docs still correctly state that full media download for discussion comments is not implemented.

## 7. Runtime behavior statement

This stage did not change:

- source code under `tg_msg_manager/`;
- tests under `tests/`;
- CLI commands or flags;
- export, db-export, export-pm, export-channel, retry, report, clean, delete, schedule, or setup behavior;
- SQLite schema or migrations.

## 8. Remaining documentation risks

- Historical changelog and report entries still mention old paths as part of their original records.
- `docs/architecture/PROJECT_ARCHITECTURE_OVERVIEW.md` remains a dated architecture snapshot.
- Final Stage 3D.0 verification and governance report still need to be completed in Stage 3D.0.7.
