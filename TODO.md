# TG_CLEANER TODO

## Operating Notes

- Live Telegram session from the project root may be used for validation.
- Live API requests are allowed for read/export and non-destructive chat inspection.
- Avoid ban-risk behavior: respect FloodWait, keep throttling conservative, do not brute-force retries.
- Store all live-test outputs in a separate temporary folder so they do not mix with working exports.
- Current live-test target:
  - `user_id`: `8603071440`
  - `chat_id`: `1274306614`

## Phase 0: Baseline

- [ ] Reproduce current test failures and classify them by root cause.
- [ ] Map all storage write call sites and all `sync_targets` schema usages.
- [ ] Define the target storage contract after refactor.
- [ ] Prepare an isolated live-test output directory convention.

## Phase 1: Storage Contract

- [ ] Convert `BaseStorage` write methods to the actual async contract.
- [ ] Update all write call sites to use `await`.
- [ ] Verify no un-awaited storage writes remain.
- [ ] Add storage contract tests for async single and batch writes.
- [ ] Validate queue drain and shutdown behavior.

## Phase 2: SQLite Schema And Migrations

- [ ] Add missing `last_sync_at` support to `sync_targets`.
- [ ] Audit all `sync_targets` queries against the real schema.
- [ ] Simplify migration flow for fresh and legacy databases.
- [ ] Add migration tests for clean and legacy DB states.
- [ ] Verify `get_outdated_chats` works on migrated databases.

## Phase 3: SQLite Storage Refactor

- [ ] Split schema, write-path, read-path, and sync-state responsibilities.
- [ ] Reduce `sqlite.py` complexity without changing external behavior.
- [ ] Re-check lock discipline and connection usage.

## Phase 4: Test Suite Repair

- [ ] Rewrite outdated config tests.
- [ ] Rewrite storage tests for async writes.
- [ ] Rewrite exporter/context tests for the current service API.
- [ ] Rewrite sync-system tests for the current method signatures.
- [ ] Replace process-signal tests with isolated handler tests.
- [ ] Establish a stable smoke suite.

## Phase 5: Config Semantics

- [ ] Define explicit precedence for init args, env, dotenv, and JSON config.
- [ ] Make env override behavior deterministic.
- [ ] Align legacy aliases with documented fields.
- [ ] Improve startup error clarity.

## Phase 6: Export-PM Gap

- [ ] Decide whether `export-pm` will really download media in this iteration.
- [ ] If yes: extend Telegram client interface with media download support.
- [ ] If yes: implement media download, routing, limits, and error handling.
- [ ] If no: correct CLI/docs/i18n claims immediately.

## Phase 7: Docs And UX Alignment

- [ ] Align README with actual behavior.
- [ ] Align CLI help and aliases with actual behavior.
- [ ] Align i18n strings with actual behavior.
- [ ] Add known limitations section.

## Phase 8: CI And Quality Gates

- [ ] Add lint/format/test validation commands.
- [ ] Add a minimal CI workflow.
- [ ] Exclude cache and transient artifacts from source control hygiene.
- [ ] Add a repeatable local verification checklist.

## Near-Term Execution Order

1. Baseline and isolated live-test setup.
2. Storage contract fix.
3. SQLite schema fix.
4. Test suite repair around the new contract.
5. Config semantics cleanup.
