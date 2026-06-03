# User Quickstart

This page is a navigation guide for a first local run. It does not replace the
command reference in [`../../COMMANDS.md`](../../COMMANDS.md).

## Start Here

1. Install the package, launch the interactive menu, and review configuration in
   [`../../README.md`](../../README.md).
2. For the full list of commands, flags, defaults, and notes, use
   [`../../COMMANDS.md`](../../COMMANDS.md).
3. Keep private exports, sessions, databases, logs, screenshots, and media local
   by default. Agent and sharing rules are documented in
   [`../development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`](../development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md).
4. Review local operational caveats for sessions, FloodWait/rate limits, SQLite
   concurrency, scheduler runs, and live smoke checks in
   [`../development/OPERATIONAL_RISKS_AND_LIMITS.md`](../development/OPERATIONAL_RISKS_AND_LIMITS.md).

## First User Or Group Export

- Use the `export` command reference:
  [`../../COMMANDS.md#export`](../../COMMANDS.md#export).
- Use the interactive menu reference:
  [`../../COMMANDS.md#interactive-menu`](../../COMMANDS.md#interactive-menu).
- Treat TXT output as a projection. JSONL and SQLite records remain canonical.

## First DB Export

- Use the `db-export` command reference:
  [`../../COMMANDS.md#db-export`](../../COMMANDS.md#db-export).
- Use `README.md` for configuration source order before relying on cached local
  SQLite data.

## First Channel Dataset

- Start with the safe metadata-only channel guide:
  [`../development/SAFE_FIRST_CHANNEL_EXPORT.md`](../development/SAFE_FIRST_CHANNEL_EXPORT.md).
- Use the full `export-channel` command reference only when you need exact flags:
  [`../../COMMANDS.md#export-channel`](../../COMMANDS.md#export-channel).

## Validate And Inspect

- Validate the local channel dataset:
  [`../../COMMANDS.md#validate-dataset`](../../COMMANDS.md#validate-dataset).
- Inspect deterministic counts and statuses:
  [`../../COMMANDS.md#inspect-dataset`](../../COMMANDS.md#inspect-dataset).
- Use doctor mode only for read-only diagnostic findings and suggested actions.
  It does not repair, migrate, fetch from Telegram, rewrite datasets, write
  SQLite data, or analyze message meaning.

## Local Target Name History

- Use `target names` to inspect locally stored metadata only:
  [`../../COMMANDS.md#target-names`](../../COMMANDS.md#target-names).
- The command does not refresh Telegram metadata and can be incomplete when a
  target was not observed before.
- It reports stored name facts only; it is not identity or profiling analysis.

## Documentation Map

- Main documentation index: [`../README.md`](../README.md).
- Architecture boundary index: [`../architecture/README.md`](../architecture/README.md).
- Development and testing index: [`../development/README.md`](../development/README.md).
