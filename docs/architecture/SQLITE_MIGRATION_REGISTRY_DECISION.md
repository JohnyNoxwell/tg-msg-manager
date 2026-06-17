# SQLite Migration Registry Decision

Status: deferred.
Date: 2026-06-18.

## Decision

Keep the current ordered `run_migrations()` implementation with the Stage 6F.0
startup guardrails and the Stage 6F.1 startup path split. Do not implement a
SQLite migration registry in the current architecture state.

This decision does not authorize SQLite schema changes, new migrations, new
tables, new indexes, `PRAGMA user_version` changes, CLI changes, service
changes, dataset changes, analytics, or post-processing behavior.

## Options Compared

Option 1: keep the current ordered migration coordinator.

- `schema/migrations.py::run_migrations()` keeps the linear `PRAGMA
  user_version` sequence from 2 through 14.
- Migration behavior remains explicit in one storage infrastructure module.
- Stage 6F.0 contract tests cover fresh bootstrap, representative legacy
  versions, data preservation, final version 14, and idempotent repeated
  startup.
- Stage 6F.1 keeps `_init_db()` as phase orchestration and preserves the
  startup order before current migrations run.

Option 2: implement a small registry with version, name, precheck, postcheck,
and idempotency metadata.

- A registry would make migration metadata more uniform.
- It would also add runtime migration surface without a current failing
  migration path or an active schema change that needs registry metadata.
- It would require new regression coverage for registry ordering, metadata
  dispatch, precheck/postcheck execution, and idempotency behavior.

## Rationale

The remaining risk after Stage 6F.0 and Stage 6F.1 is not high enough to justify
a registry now. The current risk is concentrated in preserving the existing
startup and legacy migration sequence, and the active guardrails already test
that sequence directly.

Stage 6F.0 established a startup safety baseline without runtime changes:
fresh database bootstrap reaches `PRAGMA user_version = 14`, required tables,
columns, primary keys, and indexes exist, selected legacy versions migrate to
version 14 while preserving data, and repeated startup is idempotent.

Stage 6F.1 split startup orchestration without changing SQL semantics:
`SQLiteSchemaMixin._init_db()` delegates current schema creation, compatibility
column ensures, index creation, legacy migrations, and final commit through
named startup phases. The migration coordinator remains under
`tg_msg_manager/infrastructure/storage/schema/migrations.py`.

The registry option is reasonable later, but implementing it before the next
schema migration would add abstraction around stable behavior rather than
removing an observed defect.

## Reopen Threshold

Reopen migration registry work only when at least one of these conditions is
true:

- an active stage explicitly scopes a new SQLite schema migration after
  `PRAGMA user_version = 14`;
- a migration needs explicit precheck/postcheck/idempotency metadata that cannot
  be represented clearly by the current ordered branches and focused tests;
- startup or legacy migration guardrails expose an ordering or idempotency
  defect that requires metadata-driven coordination rather than a narrow fix.

Until that threshold is met, new work should keep storage schema behavior
covered by focused regression tests and avoid adding registry runtime code.
