# Stage 0: Refactor Baseline Before Feature Expansion

## 0. Purpose

This stage is a safety baseline before adding larger features such as graph analytics, OSINT-style reporting, linguistic analysis, interaction mapping, temporal statistics, or expanded export modes.

The goal is **not** to rewrite the project. The goal is to stabilize the current architecture, reduce future change risk, and prevent new functionality from being added directly into already large hot-path files.

Current project state is already usable and architecturally meaningful. It has layered structure, SQLite persistence, Telegram abstraction, runtime bootstrap, service events, telemetry, tests, and multiple CLI workflows. Therefore this stage must be treated as a **targeted refactor-gate**, not as a global redesign.

## 1. Non-Negotiable Rules

### 1.1 Preserve Current Behavior

The agent must not intentionally change public behavior during this stage.

Public behavior includes:

- CLI command names.
- CLI arguments and flags.
- Help output semantics.
- Interactive menu behavior.
- Output file formats.
- Export folder structure.
- Database schema behavior, unless explicitly covered by a safe migration.
- Existing config keys and legacy aliases.
- Existing retry/report/update/export semantics.
- Existing tests, except where tests are adjusted only to reflect moved internal code.

### 1.2 Refactor Only by Extraction and Boundary Clarification

Allowed changes:

- Move functions/classes into smaller modules.
- Extract pure helpers.
- Extract command handlers.
- Extract read-side query groups.
- Extract writer/export format components.
- Add typed DTOs where they clarify existing contracts.
- Add tests around existing behavior before moving code.
- Add architecture documentation.
- Mark legacy scripts as deprecated if they are not compatible with current package structure.

Disallowed changes:

- Rewriting the storage model.
- Replacing SQLite.
- Introducing an ORM.
- Replacing argparse with Click/Typer.
- Replacing unittest with another test framework.
- Changing Telethon interaction semantics.
- Changing default export format.
- Changing checkpoint logic without explicit tests proving equivalence.
- Adding new product features during this stage.

### 1.3 Work in Small Commits

Each logical extraction must be independently testable.

Recommended commit sequence:

1. Add/strengthen tests.
2. Extract module or function.
3. Update imports.
4. Run tests.
5. Commit.

Do not batch unrelated refactors into one large patch.

## 2. Success Criteria

Stage 0 is complete only when all conditions below are true:

- Full test suite passes.
- Smoke scenarios are documented and runnable manually.
- Public CLI behavior is unchanged.
- `ExportService` is smaller and has clearer subcomponents.
- `ContextEngine` / `DeepModeEngine` responsibilities are split into smaller modules.
- `DBExportService` is split by export responsibilities.
- SQLite read-side is split by query responsibility.
- Legacy scripts are either updated, deleted, or clearly marked as historical/unsupported.
- Architecture rules are documented so future agents do not add features into hot-path files.
- No new large feature has been added as part of this stage.

## 3. Current Hot-Path Files

Treat these files as controlled-risk zones:

- `tg_msg_manager/cli.py`
- `tg_msg_manager/services/exporter.py`
- `tg_msg_manager/services/context_engine.py`
- `tg_msg_manager/services/db_exporter.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_read_path.py`

New feature logic must not be added directly into these files unless the change is a small compatibility wrapper around extracted functionality.

## 4. Task Block A: Freeze Current Tests and Smoke Scenarios

### A.1 Establish Test Baseline

#### A.1.1 Run existing tests

Atomic tasks:

- Run `python3 -m unittest discover -s tests -q`.
- Record number of tests executed.
- Record pass/fail status.
- If tests fail before refactor, stop and create a `BASELINE_FAILURES.md` note.
- Do not refactor on top of failing baseline unless the failure is unrelated and explicitly documented.

#### A.1.2 Run existing project verification command if available

Atomic tasks:

- Check whether `Makefile` contains `test`, `verify`, or equivalent commands.
- If available, run `make test`.
- If available, run `make verify`.
- Record results in `docs/refactor/STAGE_0_BASELINE.md`.

#### A.1.3 Confirm import health

Atomic tasks:

- Run `python3 -m tg_msg_manager.cli --help`.
- Confirm command exits successfully.
- Confirm help output lists expected major commands.
- Record command output or a short summary in baseline notes.

### A.2 Define Manual Smoke Scenarios

Create file:

```text
docs/refactor/STAGE_0_SMOKE_SCENARIOS.md
```

Smoke scenarios must be written as manual verification steps, not as vague descriptions.

#### A.2.1 CLI smoke scenarios

Atomic tasks:

- Document smoke check for `python3 -m tg_msg_manager.cli --help`.
- Document smoke check for `python3 -m tg_msg_manager.cli export --help`.
- Document smoke check for `python3 -m tg_msg_manager.cli update --help`.
- Document smoke check for `python3 -m tg_msg_manager.cli db-export --help`.
- Document smoke check for `python3 -m tg_msg_manager.cli retry --help`.
- Document smoke check for `python3 -m tg_msg_manager.cli report --help`.
- Document smoke check for `python3 -m tg_msg_manager.cli clean --help`.
- Document smoke check for `python3 -m tg_msg_manager.cli delete --help`.
- Document smoke check for `python3 -m tg_msg_manager.cli schedule --help`.
- Document smoke check for `python3 -m tg_msg_manager.cli setup --help`.

#### A.2.2 Offline fixture smoke scenarios

Atomic tasks:

- Locate existing offline fixture-based test harness.
- Document how to run it.
- Document expected success condition.
- If no single command exists, document which test files cover fixture-backed scenarios.

#### A.2.3 Database smoke scenarios

Atomic tasks:

- Document how to create or use a temporary test database.
- Document expected tables.
- Document expected storage sanity checks.
- Do not require live Telegram access for this smoke group.

#### A.2.4 Export smoke scenarios

Atomic tasks:

- Document TXT export smoke check using existing test fixtures or test DB.
- Document JSONL export smoke check using existing test fixtures or test DB.
- Document expected output existence check.
- Document expected non-empty output check.
- Document expected repeated export skip behavior if manifest/fingerprint exists.

### A.3 Add Regression Tests Before Extraction

#### A.3.1 Identify fragile behavior

Atomic tasks:

- List behavior in `ExportService` that must not change.
- List behavior in `DeepModeEngine` that must not change.
- List behavior in `DBExportService` that must not change.
- List behavior in `_sqlite_read_path.py` that must not change.
- Link each behavior to existing tests if present.
- Mark missing test coverage explicitly.

#### A.3.2 Add missing tests only where necessary

Atomic tasks:

- Add tests for any untested extraction target before moving it.
- Prefer small unit tests over broad integration tests.
- Use mocks/fixtures already present in the project.
- Avoid live Telegram tests.
- Avoid adding flaky time-dependent tests.

## 5. Task Block B: Preserve Public CLI Behavior

### B.1 Create CLI Surface Inventory

Create file:

```text
docs/refactor/STAGE_0_CLI_SURFACE.md
```

#### B.1.1 Inventory commands

Atomic tasks:

- List every top-level command.
- For each command, list current arguments.
- For each command, list current flags.
- For each command, list default values if visible from parser configuration.
- For each command, list whether it requires Telegram client.
- For each command, list whether it reads DB only.
- For each command, list whether it mutates Telegram.
- For each command, list whether it mutates local DB/files.

#### B.1.2 Inventory interactive menu entry points

Atomic tasks:

- Identify menu entry function(s).
- List menu actions.
- List hotkeys.
- List back/cancel behavior.
- List which menu flows call which services.

#### B.1.3 Inventory output-sensitive behavior

Atomic tasks:

- Identify messages likely asserted by tests.
- Identify progress rendering paths.
- Identify summary rendering paths.
- Identify error rendering paths.
- Do not change these unless tests are updated for strictly internal reasons.

### B.2 Extract CLI Internals Without Changing Surface

Target principle:

`cli.py` may remain the composition entry point, but it should not keep growing with command-specific implementation logic.

Proposed target structure:

```text
tg_msg_manager/cli/
    __init__.py
    parser.py
    handlers.py
    menu.py
    renderers.py
    command_registry.py
```

Use this structure only if it fits current package constraints. Do not force it if it creates circular imports.

#### B.2.1 Extract parser construction

Atomic tasks:

- Locate argparse parser construction code.
- Move parser construction to `tg_msg_manager/cli/parser.py` or equivalent.
- Keep command names identical.
- Keep argument names identical.
- Keep defaults identical.
- Keep help text semantically equivalent.
- Update imports in original `cli.py`.
- Run CLI help smoke checks.

#### B.2.2 Extract command handlers

Atomic tasks:

- Identify command dispatch function.
- Extract handler functions by command.
- Preserve async/sync boundaries.
- Preserve runtime context creation behavior.
- Preserve exception handling.
- Preserve signal handling interaction.
- Keep `cli.py` as a thin entry point.
- Run test suite.

#### B.2.3 Extract rendering-only helpers

Atomic tasks:

- Identify functions that only render output.
- Move rendering helpers to renderer module if not already in `cli_io.py` or UI utilities.
- Ensure services still do not print directly.
- Preserve service-event rendering behavior.
- Run progress/event related tests.

## 6. Task Block C: Reduce ExportService Complexity

### C.1 Define ExportService Responsibility Boundary

`ExportService` should coordinate sync workflows, but should not own all implementation details.

Allowed responsibilities after refactor:

- Coordinate Telegram client, storage, and context engine.
- Select high-level sync mode.
- Emit service events.
- Call extracted scan/checkpoint/target helpers.

Responsibilities to extract:

- Scan range construction.
- Checkpoint transition calculations.
- Target grouping/discovery helpers.
- Shared head prefetch planning.
- Sync result aggregation.
- Progress payload construction if currently embedded.

### C.2 Extract Scan Range Logic

Proposed module:

```text
tg_msg_manager/services/sync/ranges.py
```

#### C.2.1 Locate scan range model and builder logic

Atomic tasks:

- Find `_ScanRange` or equivalent internal scan range structure.
- Find first-sync range planning logic.
- Find update HEAD-range planning logic.
- Find resume TAIL-range planning logic.
- Find logic that protects tail checkpoint from false completion.

#### C.2.2 Add or confirm tests

Atomic tasks:

- Test first full scan range construction.
- Test update-only HEAD range construction.
- Test interrupted/resume range construction.
- Test multiple descending tail ranges.
- Test that tail checkpoint does not skip unprocessed middle range.

#### C.2.3 Extract implementation

Atomic tasks:

- Move scan range dataclass/model if appropriate.
- Move pure range builder functions.
- Keep public behavior identical.
- Ensure no storage or Telegram dependency enters range builder module unless already unavoidable.
- Import extracted builder into `ExportService`.
- Run sync tests.

### C.3 Extract Checkpoint Logic

Proposed module:

```text
tg_msg_manager/services/sync/checkpoints.py
```

#### C.3.1 Locate checkpoint update rules

Atomic tasks:

- Find `last_msg_id` update logic.
- Find `tail_msg_id` update logic.
- Find `is_complete` transition logic.
- Find per-target sync timestamp update logic.
- Find special whole-chat target handling if present.

#### C.3.2 Add or confirm tests

Atomic tasks:

- Test HEAD checkpoint advances on new messages.
- Test TAIL checkpoint advances only after safe completed range.
- Test `is_complete` transition after full history pass.
- Test checkpoint behavior when no new messages exist.
- Test checkpoint behavior after partial failure.

#### C.3.3 Extract pure decision logic

Atomic tasks:

- Separate calculation from storage mutation.
- Create small typed result object if needed.
- Keep storage write in service/storage layer.
- Use extracted function inside `ExportService`.
- Run storage and sync tests.

### C.4 Extract Target Grouping and Shared Head Prefetch Planning

Proposed module:

```text
tg_msg_manager/services/sync/planner.py
```

#### C.4.1 Locate target grouping logic

Atomic tasks:

- Find logic that groups tracked targets by chat.
- Find logic that determines outdated targets.
- Find logic that decides shared head prefetch scope.
- Find logic that reuses a shared top slice for multiple targets.

#### C.4.2 Add or confirm tests

Atomic tasks:

- Test multiple targets in one chat are grouped.
- Test targets from different chats are separated.
- Test shared prefetch is selected only when valid.
- Test no target is dropped from update plan.

#### C.4.3 Extract planning logic

Atomic tasks:

- Move grouping helpers to planner module.
- Keep Telegram calls outside planner if possible.
- Planner should produce a plan, not execute it.
- Update `ExportService` to consume plan.
- Run tests.

### C.5 Keep ExportService as Orchestrator

Atomic tasks:

- After extraction, review `ExportService` public methods.
- Ensure `sync_chat()` remains readable.
- Ensure `sync_all_dialogs_for_user()` remains readable.
- Ensure `sync_all_outdated()` remains readable.
- Ensure `sync_all_tracked()` remains readable.
- Remove dead helper functions from original file.
- Add module docstrings explaining boundaries.

## 7. Task Block D: Reduce ContextEngine / DeepModeEngine Complexity

### D.1 Define Context Engine Boundary

The context engine should build context clusters around target messages. It should prefer Telegram structural relations over naive time windows.

Responsibilities to isolate:

- Reply-chain traversal.
- Children/replied-by discovery.
- Topic/thread relation handling.
- Local cache lookup.
- Live missing-message fetch strategy.
- Time-window fallback.
- Cluster assembly.
- Context link persistence decisions if currently mixed.

### D.2 Extract Graph Traversal Logic

Proposed module:

```text
tg_msg_manager/services/context/graph.py
```

#### D.2.1 Locate structural traversal rules

Atomic tasks:

- Find parent lookup by `reply_to_id`.
- Find child/replied-by lookup.
- Find recursive traversal depth behavior.
- Find depth 1/2/3 differences.
- Find topic/thread handling.
- Find cycle/deduplication protection.

#### D.2.2 Add or confirm tests

Atomic tasks:

- Test parent message is included when target replies to someone.
- Test child replies to target are included.
- Test recursive traversal stops at configured depth.
- Test duplicates are not emitted twice.
- Test missing parent does not crash context construction.
- Test topic/thread relationship if currently supported.

#### D.2.3 Extract traversal into pure or near-pure component

Atomic tasks:

- Move graph traversal helpers to context graph module.
- Keep storage/live-fetch boundaries explicit.
- Use typed input/output collections.
- Preserve ordering of resulting messages.
- Run context tests.

### D.3 Extract Local Cache Strategy

Proposed module:

```text
tg_msg_manager/services/context/cache.py
```

#### D.3.1 Locate local-first lookup behavior

Atomic tasks:

- Find local lookup for parent messages.
- Find local lookup for ranges.
- Find local lookup for replies/children.
- Find local lookup for existing context group messages.

#### D.3.2 Extract cache adapter

Atomic tasks:

- Create small class/function group wrapping storage reads needed by context engine.
- Do not move raw SQL here; use storage interface/read-side functions.
- Keep return types consistent with existing engine expectations.
- Add tests using fake storage where possible.

### D.4 Extract Live Fetch Strategy

Proposed module:

```text
tg_msg_manager/services/context/fetch_strategy.py
```

#### D.4.1 Locate missing-message fetch behavior

Atomic tasks:

- Find selective fill by exact message IDs.
- Find compact fill by small range.
- Find full scan range fallback.
- Find conditions selecting one strategy over another.
- Find FloodWait/throttling assumptions delegated to Telegram adapter.

#### D.4.2 Add or confirm tests

Atomic tasks:

- Test exact-ID fetch strategy selection.
- Test compact-range fetch strategy selection.
- Test full-range fallback selection.
- Test no live fetch when cache already has required messages.

#### D.4.3 Extract strategy selection

Atomic tasks:

- Separate strategy decision from actual Telegram calls if possible.
- Represent selected strategy as typed object or enum if useful.
- Keep execution path equivalent.
- Run context and Telegram adapter tests.

### D.5 Extract Cluster Assembly

Proposed module:

```text
tg_msg_manager/services/context/clusters.py
```

#### D.5.1 Locate cluster assembly logic

Atomic tasks:

- Find context group ID assignment.
- Find message ordering logic inside cluster.
- Find target/context attribution logic.
- Find duplicate elimination logic.
- Find fallback time-window grouping logic.

#### D.5.2 Add or confirm tests

Atomic tasks:

- Test stable cluster group creation.
- Test target message stays present in cluster.
- Test parent/child/context messages are ordered consistently.
- Test duplicate messages collapse to one instance.
- Test context group ID is stable if currently expected.

#### D.5.3 Extract assembly implementation

Atomic tasks:

- Move cluster assembly helpers to dedicated module.
- Keep persistence outside assembly if possible.
- Ensure output is deterministic.
- Run tests.

### D.6 Decide Status of `message_context_links`

The current architecture indicates this table may be underused compared to `reply_to_id`, `context_group_id`, and `message_target_links`.

#### D.6.1 Audit usage

Atomic tasks:

- Search all references to `message_context_links`.
- Classify each usage as write, read, migration/schema, test, or dead reference.
- Determine whether any current behavior depends on it as source of truth.

#### D.6.2 Document decision

Create section in:

```text
docs/refactor/STAGE_0_STORAGE_DECISIONS.md
```

Decision options:

- Keep as active normalized context relation table.
- Keep as legacy compatibility table.
- Deprecate but do not remove yet.
- Remove only in a later migration stage, not Stage 0.

Atomic tasks:

- Do not drop table in Stage 0 unless project already has explicit migration/test coverage for it.
- Document current role precisely.
- Document future recommendation.

## 8. Task Block E: Reduce DBExportService Complexity

### E.1 Define DB Export Boundary

`DBExportService` should coordinate exporting accumulated local history from SQLite. It should not directly own all details of TXT formatting, JSONL formatting, fingerprinting, manifest checks, and file rotation.

Responsibilities to extract:

- Fingerprint/manifest logic.
- TXT formatting/writing.
- JSONL formatting/writing.
- Export summary construction.
- Streaming iterator adapter.

### E.2 Extract Manifest and Fingerprint Logic

Proposed module:

```text
tg_msg_manager/services/export_manifest.py
```

or:

```text
tg_msg_manager/services/db_export/manifest.py
```

#### E.2.1 Locate manifest/fingerprint code

Atomic tasks:

- Find fingerprint calculation.
- Find manifest path calculation.
- Find export skip condition.
- Find validation that all export parts still exist.
- Find manifest write/update logic.

#### E.2.2 Add or confirm tests

Atomic tasks:

- Test same input produces same fingerprint.
- Test changed message count changes fingerprint.
- Test changed timestamp range changes fingerprint.
- Test changed format changes fingerprint.
- Test missing export part disables skip.
- Test existing valid manifest enables skip.

#### E.2.3 Extract implementation

Atomic tasks:

- Move fingerprint data model if useful.
- Move manifest read/write helpers.
- Keep file paths explicit and testable.
- Update `DBExportService` to call manifest helper.
- Run db-export tests.

### E.3 Extract TXT Export Formatting

Proposed module:

```text
tg_msg_manager/services/db_export/txt_writer.py
```

#### E.3.1 Locate TXT-specific logic

Atomic tasks:

- Find human-readable grouping by date.
- Find author grouping logic.
- Find reply-context insertion logic.
- Find file rotation interaction.
- Find text escaping/sanitization rules.

#### E.3.2 Add or confirm tests

Atomic tasks:

- Test TXT output contains expected date grouping.
- Test TXT output contains expected author display.
- Test reply context appears when expected.
- Test empty message handling.
- Test media/service message handling if supported.

#### E.3.3 Extract TXT writer

Atomic tasks:

- Move TXT formatting to writer module.
- Keep writer independent of Telegram client.
- Keep storage reads outside writer if possible.
- Preserve output format exactly.
- Run export tests.

### E.4 Extract JSONL Export Formatting

Proposed module:

```text
tg_msg_manager/services/db_export/jsonl_writer.py
```

#### E.4.1 Locate JSONL-specific logic

Atomic tasks:

- Find compact AI profile formatting.
- Find full profile logic if present.
- Find raw payload inclusion/exclusion logic.
- Find JSON serialization rules.
- Find streaming write path.

#### E.4.2 Add or confirm tests

Atomic tasks:

- Test one message becomes one JSONL line.
- Test compact profile excludes heavy raw payload by default.
- Test reply metadata is preserved.
- Test context metadata is preserved.
- Test Unicode text is preserved.
- Test output is valid JSON per line.

#### E.4.3 Extract JSONL writer

Atomic tasks:

- Move JSONL formatting to writer module.
- Keep streaming behavior intact.
- Avoid materializing full export in memory if current path streams.
- Preserve CLI default profile behavior.
- Run db-export tests.

### E.5 Extract Export Summary Construction

Proposed module:

```text
tg_msg_manager/services/db_export/summary.py
```

Atomic tasks:

- Find result/summary object construction.
- Move summary DTO or helper if currently embedded.
- Preserve service event payloads.
- Preserve CLI rendering compatibility.
- Add tests if summary is asserted.

## 9. Task Block F: Split SQLite Read-Side

### F.1 Define Read-Side Boundaries

Current `_sqlite_read_path.py` should be split by query responsibility. Avoid one large file collecting every SELECT query.

Proposed structure:

```text
tg_msg_manager/infrastructure/storage/read/
    __init__.py
    messages.py
    targets.py
    context.py
    reporting.py
    exports.py
```

Alternative structure is acceptable if it avoids circular imports and preserves mixin composition.

### F.2 Inventory Existing Read Methods

Create file:

```text
docs/refactor/STAGE_0_SQLITE_READ_INVENTORY.md
```

Atomic tasks:

- List all public read methods from `_sqlite_read_path.py`.
- List all private helper methods from `_sqlite_read_path.py`.
- For each method, classify responsibility:
  - message retrieval;
  - target retrieval;
  - context retrieval;
  - reporting/audit;
  - export iteration;
  - retry-related read;
  - miscellaneous.
- For each method, list known callers.
- For each method, list existing tests if known.

### F.3 Extract Message Read Queries

Target module:

```text
tg_msg_manager/infrastructure/storage/read/messages.py
```

Atomic tasks:

- Move message-by-id read helpers.
- Move message range read helpers.
- Move message iterator helpers if not export-specific.
- Preserve connection handling semantics.
- Preserve returned record types.
- Run storage tests.

### F.4 Extract Target Read Queries

Target module:

```text
tg_msg_manager/infrastructure/storage/read/targets.py
```

Atomic tasks:

- Move sync target listing methods.
- Move tracked target lookup methods.
- Move outdated target read methods.
- Move author-name lookup if target-specific.
- Preserve whole-chat target behavior.
- Run sync/storage tests.

### F.5 Extract Context Read Queries

Target module:

```text
tg_msg_manager/infrastructure/storage/read/context.py
```

Atomic tasks:

- Move reply-to lookup queries.
- Move replied-by/children queries.
- Move context group queries.
- Move context links queries if active.
- Preserve ordering.
- Preserve deduplication behavior.
- Run context tests.

### F.6 Extract Reporting Read Queries

Target module:

```text
tg_msg_manager/infrastructure/storage/read/reporting.py
```

Atomic tasks:

- Move read-only diagnostics queries.
- Move report summary queries.
- Move audit/status queries.
- Preserve typed reporting DTOs.
- Run reporting tests.

### F.7 Extract Export Read Queries

Target module:

```text
tg_msg_manager/infrastructure/storage/read/exports.py
```

Atomic tasks:

- Move DB export summary queries.
- Move streaming export iterator if currently in read path.
- Move first/last/count fingerprint queries if export-specific.
- Preserve streaming behavior.
- Run db-export tests.

### F.8 Preserve Mixin Composition

Atomic tasks:

- Ensure `SQLiteStorage` still exposes the same public methods.
- Re-export or inherit extracted read mixins as needed.
- Avoid changing storage interface unless strictly necessary.
- Avoid changing call sites where possible.
- Run full test suite.

## 10. Task Block G: Legacy Scripts Audit

### G.1 Inventory Scripts

Create file:

```text
docs/refactor/STAGE_0_SCRIPT_AUDIT.md
```

Atomic tasks:

- List every file under `scripts/`.
- For each script, identify purpose.
- For each script, check whether imports match current package structure.
- For each script, check whether it is documented in README/COMMANDS/TODO.
- For each script, classify as active, ad-hoc, legacy, broken, or unknown.

### G.2 Validate Active Scripts

Atomic tasks:

- For each active script, run `python3 scripts/<name>.py --help` if supported.
- If no help exists, inspect import-only behavior.
- Ensure active scripts do not crash on import.
- Add minimal documentation for active scripts.

### G.3 Mark Legacy Scripts

Atomic tasks:

- For scripts that are historical but retained, add header comment:

```python
# LEGACY / HISTORICAL SCRIPT
# This script is not part of the supported Stage 0 runtime path.
# Do not use as a source of truth without validating against current package structure.
```

- Move legacy scripts to `scripts/legacy/` only if imports/docs/tests will not break.
- If moved, update references.
- If not moved, add deprecation note in audit doc.

### G.4 Remove Only If Safe

Atomic tasks:

- Do not delete scripts unless they are definitely unused and broken.
- If deleting, mention reason in changelog/refactor note.
- Prefer marking over deleting during Stage 0.

## 11. Task Block H: Architecture Rules for Future Features

### H.1 Create Architecture Rules Document

Create file:

```text
docs/ARCHITECTURE_RULES.md
```

### H.2 Add Rule: No New Features in Hot-Path Files

Atomic tasks:

- Document hot-path files.
- State that new feature logic must go into dedicated modules.
- Allow only thin wrappers/adapters in hot-path files.
- Require tests for new module boundaries.

Recommended wording:

```text
New product features must not be implemented directly inside `cli.py`, `ExportService`, `ContextEngine`, `DBExportService`, or SQLite read/write mega-modules. These files may coordinate extracted components, but they must not accumulate new domain logic.
```

### H.3 Add Rule: Ingestion and Analysis Must Stay Separate

Atomic tasks:

- Define ingestion as Telegram sync/archive/update/clean operations.
- Define analysis as read-only processing over stored local data.
- State that graph analytics, linguistic profiling, temporal stats, and profile reports must read from storage/read-side, not directly from live Telegram client.
- State that analysis modules must not mutate Telegram.

Recommended target structure:

```text
tg_msg_manager/analysis/
    graph_builder.py
    interaction_metrics.py
    temporal_activity.py
    linguistic_stats.py
    reports.py
```

### H.4 Add Rule: CLI Is Presentation and Dispatch Only

Atomic tasks:

- Document that CLI must parse commands, create runtime context, call services, and render results.
- CLI must not contain business logic.
- CLI must not contain SQL.
- CLI must not contain Telegram traversal logic.
- CLI must not contain export formatting logic.

### H.5 Add Rule: Storage Interface Owns Persistence Boundaries

Atomic tasks:

- Document that services should use storage interface/read-side methods.
- Services should not embed raw SQL.
- Analysis modules should not open SQLite directly unless explicitly designed as storage-layer components.
- New SQL queries must be placed in correct read/write module group.

### H.6 Add Rule: Every New Feature Needs a Test Boundary

Atomic tasks:

- Require at least one unit test for pure logic.
- Require at least one integration/fixture test if feature crosses storage boundary.
- Require no live Telegram dependency in standard test suite.
- Require CLI smoke check if feature adds command surface.

### H.7 Add Rule: Documentation Must Be Updated With Architecture Changes

Atomic tasks:

- Update README only for user-facing behavior.
- Update COMMANDS only for command surface changes.
- Update architecture docs for internal boundaries.
- Update TODO/ROADMAP only if priorities change.
- Do not let architecture snapshot become the only source of truth.

## 12. Task Block I: Final Verification

### I.1 Run Full Test Suite

Atomic tasks:

- Run `python3 -m unittest discover -s tests -q`.
- Run `make test` if available.
- Run `make verify` if available.
- Record final result in `docs/refactor/STAGE_0_FINAL_REPORT.md`.

### I.2 Run Smoke Scenarios

Atomic tasks:

- Run all CLI help smoke checks documented in `STAGE_0_SMOKE_SCENARIOS.md`.
- Run offline fixture smoke check if available.
- Run DB/export smoke checks if available without live Telegram.
- Record pass/fail status.

### I.3 Compare CLI Surface

Atomic tasks:

- Compare before/after command inventory.
- Confirm no command was removed.
- Confirm no flag was renamed.
- Confirm no default was changed intentionally.
- Document any accidental diff and fix it before completing Stage 0.

### I.4 Review Hot-Path File Size and Responsibility

Atomic tasks:

- Record line counts for hot-path files before and after if baseline exists.
- Confirm extracted modules have clear names and narrow responsibilities.
- Confirm hot-path files still coordinate behavior but do not own all details.
- Confirm no new feature was added during refactor.

### I.5 Update Changelog or Refactor Report

Atomic tasks:

- Add concise entry describing Stage 0 refactor baseline.
- Mention behavior-preserving nature.
- Mention extracted modules.
- Mention tests/smoke checks passed.
- Mention any known remaining hotspots.

## 13. Expected Final File/Module Layout Changes

The exact layout may vary, but the end state should resemble this direction:

```text
tg_msg_manager/
    cli.py                         # thin entry point / compatibility layer
    cli/
        parser.py                  # argparse construction
        handlers.py                # command handlers
        menu.py                    # interactive menu flows
        renderers.py               # CLI rendering helpers

    services/
        exporter.py                # orchestrator only
        sync/
            ranges.py              # scan range planning
            checkpoints.py         # checkpoint transition logic
            planner.py             # target grouping / shared prefetch plan

        context_engine.py          # orchestrator only
        context/
            graph.py               # reply/thread traversal
            cache.py               # local-first lookup helpers
            fetch_strategy.py      # live missing-message strategy
            clusters.py            # cluster assembly

        db_exporter.py             # orchestrator only
        db_export/
            manifest.py            # fingerprint/manifest
            txt_writer.py          # TXT formatting/writing
            jsonl_writer.py        # JSONL formatting/writing
            summary.py             # export summary

    infrastructure/
        storage/
            _sqlite_read_path.py   # compatibility mixin / aggregator only
            read/
                messages.py
                targets.py
                context.py
                reporting.py
                exports.py

scripts/
    legacy/                        # optional; only if safe

docs/
    ARCHITECTURE_RULES.md
    refactor/
        STAGE_0_BASELINE.md
        STAGE_0_SMOKE_SCENARIOS.md
        STAGE_0_CLI_SURFACE.md
        STAGE_0_SQLITE_READ_INVENTORY.md
        STAGE_0_SCRIPT_AUDIT.md
        STAGE_0_STORAGE_DECISIONS.md
        STAGE_0_FINAL_REPORT.md
```

## 14. Agent Execution Order

The agent must execute in this order:

1. Build baseline and smoke documentation.
2. Inventory CLI and storage read-side.
3. Add missing regression tests around extraction targets.
4. Refactor CLI internals if safe.
5. Refactor `ExportService` scan/checkpoint/planner logic.
6. Refactor `ContextEngine` graph/cache/fetch/cluster logic.
7. Refactor `DBExportService` manifest/TXT/JSONL/summary logic.
8. Split SQLite read-side modules.
9. Audit and mark legacy scripts.
10. Add architecture rules.
11. Run full verification.
12. Produce final report.

Do not start with the largest file blindly. Start with tests and inventory.

## 15. Definition of Done

Stage 0 is done when:

- Tests pass.
- Smoke scenarios are documented.
- Public CLI surface is preserved.
- Hot-path files are reduced or converted into orchestrators.
- Read-side storage is split by responsibility.
- Legacy scripts are classified.
- Future architecture rules are documented.
- No unrelated product feature was added.
- Final report exists and clearly states what changed and what did not change.

## 16. Explicit Non-Goals

Do not do these in Stage 0:

- Do not add graph analytics.
- Do not add psychological/user profiling reports.
- Do not add linguistic fingerprinting.
- Do not add temporal intelligence dashboards.
- Do not add multi-account support.
- Do not replace SQLite.
- Do not introduce a web UI.
- Do not change export semantics.
- Do not change Telegram deletion semantics.
- Do not change scheduler behavior.
- Do not add background daemon architecture.

These belong to later stages after the baseline is stable.

