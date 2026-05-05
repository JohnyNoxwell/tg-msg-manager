# AGENTS.md

## 0. Purpose

This file defines the engineering rules for all AI agents and human contributors working on this repository.

The main goal is to preserve the architectural foundation of `tg-msg-manager` after refactoring and prevent future development from turning the project back into a set of large, fragile service files.

Every change must follow these rules unless a maintainer explicitly updates this document.

---

# 1. Core Principles

## 1.1. Preserve behavior first

Refactoring must not change user-visible behavior unless the task explicitly says so.

Do not change without explicit instruction:

- CLI command names;
- CLI arguments;
- default values;
- export formats;
- output filenames;
- output directory layout;
- database schema;
- incremental sync behavior;
- target attribution behavior;
- context depth behavior;
- retry behavior;
- report format.

If behavior must change, document it in `CHANGELOG.md`, tests, and architecture notes.

## 1.2. Small changes only

Prefer small, isolated changes.

Do not perform big-bang rewrites.

A valid change should normally fit one category:

- extract module;
- split responsibility;
- add test;
- fix bug;
- add internal helper;
- improve naming;
- update documentation;
- add compatibility wrapper;
- remove verified dead code.

Avoid mixing refactor, feature work, formatting, and behavioral changes in the same change.

## 1.3. Architecture over convenience

Do not place new logic in a file simply because it is convenient.

New functionality must go into the correct layer and module, even if that requires creating a new small module.

Bad:

```text
"Just add it to the existing service."
```

Good:

```text
"Create a dedicated component with one responsibility and inject it into the orchestrator."
```

## 1.4. Explicit boundaries

Each module must have a clear responsibility.

If a module needs the words "and also" to describe what it does, it probably has too many responsibilities.

---

# 2. Layering Rules

The project must preserve a layered architecture.

Expected direction of dependencies:

```text
CLI
  ↓
Application / Services
  ↓
Domain Models / Policies
  ↓
Infrastructure Interfaces / Contracts
  ↓
Infrastructure Implementations
```

## 2.1. CLI layer

CLI files must remain thin.

CLI may:

- parse command arguments;
- validate basic user input;
- call application/service layer;
- format high-level command result;
- exit with proper status code.

CLI must not:

- contain business logic;
- contain SQL;
- perform Telegram fetching directly;
- build context clusters;
- implement export formatting;
- write database records directly;
- decide target attribution;
- perform analytics.

If CLI code becomes complex, move logic into a service or command handler.

## 2.2. Service layer

Services coordinate use cases.

Services may:

- orchestrate components;
- call storage contracts;
- call adapters;
- call policies;
- call renderers/writers;
- emit events;
- return structured result objects.

Services must not:

- contain raw SQL;
- directly manipulate SQLite cursors;
- perform low-level filesystem formatting inline;
- become large algorithmic modules;
- contain unrelated use cases;
- import CLI modules;
- import concrete infrastructure when a contract is available.

A service should normally depend on narrow contracts, not broad storage objects.

## 2.3. Domain / core layer

Core/domain modules contain stable concepts.

They may contain:

- dataclasses;
- enums;
- value objects;
- policy objects;
- pure functions;
- domain-level validation.

They must not:

- import Telegram client code;
- import SQLite code;
- read/write files;
- depend on CLI;
- depend on concrete infrastructure.

Core logic should be easy to unit test without IO.

## 2.4. Infrastructure layer

Infrastructure contains concrete implementations.

It may contain:

- SQLite queries;
- file IO;
- Telegram adapter code;
- process locks;
- OS scheduler integration;
- logging sinks;
- retry persistence;
- concrete storage implementations.

Infrastructure must not:

- import CLI;
- decide business policy;
- perform user-facing orchestration;
- contain analytics decisions;
- format user-facing export text unless the module is explicitly a writer/renderer.

---

# 3. Hot-Path Protection

The following files or module types must not become large feature dumping grounds.

## 3.1. Protected hot-path files

Do not add new major logic to:

```text
tg_msg_manager/services/exporter.py
tg_msg_manager/services/context_engine.py
tg_msg_manager/services/db_exporter.py
tg_msg_manager/services/private_archive.py
tg_msg_manager/infrastructure/storage/interface.py
tg_msg_manager/core/models/service_payloads.py
```

These files should be compatibility wrappers, facades, or aggregators only.

If one of these files grows significantly, stop and create a dedicated module.

## 3.2. Protected service packages

Do not add unrelated logic to:

```text
tg_msg_manager/services/export/
tg_msg_manager/services/context/
tg_msg_manager/services/db_export/
tg_msg_manager/services/private_archive/
```

Each component inside these packages must keep one responsibility.

Examples:

```text
planner.py              -> planning only
source_loader.py        -> loading only
skip_policy.py          -> skip decision only
state_manager.py        -> state only
txt_renderer.py         -> TXT rendering only
jsonl_renderer.py       -> JSONL rendering only
event_emitter.py        -> events only
```

Do not merge these responsibilities back into a service facade.

---

# 4. Export Architecture Rules

## 4.1. Export service

Export orchestration must stay separated from:

- Telegram fetch;
- context resolution;
- target resolving;
- file rendering;
- checkpoint persistence;
- event emission.

The export service may coordinate these components, but it must not implement all of them inline.

## 4.2. DB export

DB export must be split by responsibility.

Expected components:

```text
services/db_export/service.py          -> orchestration facade
services/db_export/source_loader.py    -> load DB data
services/db_export/plan_builder.py     -> build export plan
services/db_export/skip_policy.py      -> unchanged/fingerprint decision
services/db_export/state_manager.py    -> export state
services/db_export/txt_renderer.py     -> TXT rendering
services/db_export/jsonl_renderer.py   -> JSONL rendering
services/db_export/payload_writer.py   -> file writing
services/db_export/event_emitter.py    -> events
services/db_export/models.py           -> DB export models
```

Do not put renderer, state, skip, and loading logic back into one class.

## 4.3. Export format stability

Existing export formats are contracts.

Before changing export rendering:

1. Add or update regression tests.
2. Compare fixture output before/after.
3. Document the change.
4. Update changelog.
5. Ensure the change is intentional.

If the task is refactor-only, export output must remain byte-for-byte stable where possible.

---

# 5. Context Architecture Rules

Context logic must stay modular.

Expected components:

```text
services/context/engine.py                    -> facade
services/context/reply_chain_resolver.py      -> reply-chain only
services/context/neighbor_window_resolver.py  -> before/after context only
services/context/cluster_builder.py           -> cluster construction only
services/context/deduplicator.py              -> deduplication only
services/context/scope_policy.py              -> context limits/policy only
```

## 5.1. Context engine

The context engine may coordinate context components.

It must not:

- contain raw SQL;
- perform Telegram fetch directly;
- format export text;
- write files;
- contain analytics;
- contain scoring;
- mutate storage directly.

## 5.2. Context policy

Context depth, before/after windows, reply depth, fallback behavior, and dedup rules must be explicit.

Do not scatter context constants across unrelated files.

## 5.3. Context relation tables

Context relation tables must have a documented status.

Any table such as:

```text
message_context_links
context_group_id
message_target_links
```

must be documented as one of:

- first-class source of truth;
- compatibility/legacy structure;
- migration candidate.

Do not build new features on ambiguous tables.

---

# 6. Storage Rules

## 6.1. No raw SQL in services

Raw SQL belongs in infrastructure/storage modules only.

Forbidden in service layer:

```python
cursor.execute(...)
connection.execute(...)
SELECT ...
INSERT ...
UPDATE ...
DELETE ...
```

If a service needs data, create or use a storage contract method.

## 6.2. Narrow contracts

Services must depend on narrow storage contracts.

Bad:

```python
def __init__(self, storage: Storage):
    self.storage = storage
```

Good:

```python
def __init__(self, storage: DBExportStorage):
    self.storage = storage
```

Each service should receive only the methods it actually needs.

## 6.3. Storage contract domains

Use separate contracts by use case:

```text
SyncStorage
ExportStorage
DBExportStorage
ContextStorage
PrivateArchiveStorage
ReportStorage
RetryStorage
AnalyticsStorage
```

Do not add unrelated methods to a contract because it is convenient.

## 6.4. Read-side / write-side separation

Read and write paths must stay separated.

Read modules may:

- perform SELECT queries;
- map rows to DTOs/models;
- return read-only projections.

Write modules may:

- insert;
- update;
- upsert;
- delete only if explicitly allowed;
- manage transactions through write infrastructure.

Read modules must not mutate state.

Write modules must not contain export/context business policy.

## 6.5. SQLite constraints

SQLite is the current local storage engine.

Do not replace it without explicit architectural decision.

When changing storage:

- preserve WAL/local assumptions unless instructed;
- avoid long write locks;
- batch writes when appropriate;
- preserve transaction safety;
- add tests for migrations/schema changes;
- document schema changes.

---

# 7. Payload / Model Rules

## 7.1. No DTO dumping ground

Do not add new models to a giant shared file if a domain-specific module exists.

Preferred structure:

```text
core/models/payloads/sync.py
core/models/payloads/export.py
core/models/payloads/db_export.py
core/models/payloads/context.py
core/models/payloads/private_archive.py
core/models/payloads/retry.py
core/models/payloads/report.py
core/models/payloads/telemetry.py
```

## 7.2. Compatibility aggregators

Files like:

```text
core/models/service_payloads.py
infrastructure/storage/interface.py
```

may exist as compatibility aggregators.

New code should import from domain-specific modules instead of aggregators.

## 7.3. Model rules

Models should be:

- explicit;
- typed;
- small;
- domain-specific;
- serializable where necessary;
- stable if used in exports or reports.

Avoid unstructured dicts for internal data passing unless the source is inherently dynamic.

---

# 8. Private Archive Rules

Private archive must not become a second independent pipeline duplicating sync/export logic.

Expected separation:

```text
services/private_archive/service.py          -> orchestration facade
services/private_archive/planner.py          -> scope planning
services/private_archive/source_resolver.py  -> private dialog/user resolving
services/private_archive/media_policy.py     -> media decision policy
services/private_archive/archive_writer.py   -> archive output writing
services/private_archive/state_manager.py    -> archive state/checkpoint
services/private_archive/event_emitter.py    -> archive events
```

Reuse shared components where possible:

- fetch orchestration;
- retry handling;
- checkpoint writers;
- file writers;
- storage contracts;
- event infrastructure.

Do not duplicate large blocks from export or sync code.

---

# 9. Analytics Boundary Rules

Analytics must be read-only unless a future architecture decision explicitly says otherwise.

Allowed future analytics examples:

- interaction counts;
- reply graph projections;
- user activity timelines;
- dataset projections;
- export-ready analytical views.

Forbidden:

- Telegram fetching inside analytics;
- writing sync/export state from analytics;
- adding analytics code to `ExportService`;
- adding analytics code to `DBExportService`;
- adding analytics code to `ContextEngine`;
- adding analytics SQL to service layer;
- mixing analytics with export rendering.

Expected location:

```text
tg_msg_manager/services/analytics/
tg_msg_manager/infrastructure/storage/read/analytics/
```

Analytics should read normalized storage data through read-only contracts.

---

# 10. Telegram Adapter Rules

Telegram API access must stay behind adapter/fetch layers.

Do not call Telethon or Telegram client methods from:

- CLI;
- renderers;
- storage;
- analytics;
- context cluster builder;
- DB export;
- report generation.

Telegram fetching belongs in dedicated adapter/fetch orchestration modules.

If a new feature needs Telegram data, add a method to the appropriate adapter/fetch layer and test it through that boundary.

---

# 11. File IO and Rendering Rules

## 11.1. File writing

File writing must be isolated in writer modules.

Services may call writers, but should not perform detailed file formatting inline.

## 11.2. Rendering

Rendering must be separate from writing.

Good split:

```text
txt_renderer.py      -> creates string/lines
jsonl_renderer.py    -> creates JSONL records/lines
payload_writer.py    -> writes rendered content to disk
```

## 11.3. Deterministic output

Export output should be deterministic.

Preserve:

- message ordering;
- timestamp formatting;
- author formatting;
- separator formatting;
- JSONL field order where relevant;
- stable filenames.

Any intentional change requires regression test updates and changelog entry.

---

# 12. Testing Rules

## 12.1. Run tests before and after refactor

Before changing a major area:

```bash
make test
make verify
```

or the current project-equivalent commands.

After changing a major area, run relevant tests again.

## 12.2. Required tests for refactor

If refactoring a component, add or preserve tests for:

- compatibility imports;
- public behavior;
- fixture output;
- edge cases;
- failure paths;
- no duplicate exports;
- checkpoint behavior;
- skip/fingerprint behavior where applicable.

## 12.3. Fixture regression

For export/context/db-export changes, compare fixture output before and after.

Refactor-only changes should not alter output.

## 12.4. CLI contract tests

CLI tests should protect:

- command availability;
- argument names;
- default values;
- basic help output;
- exit codes for known safe cases.

Do not assert full help text unless necessary; it is often too brittle.

## 12.5. Live smoke tests

Live Telegram tests should be manual or explicitly marked, not required in normal CI unless designed safely.

Maintain:

```text
docs/testing/LIVE_SMOKE_CHECKLIST.md
```

Use it when changing:

- Telegram fetch;
- sync;
- private archive;
- media handling;
- retry;
- checkpoint behavior.

---

# 13. Documentation Rules

Update documentation when architecture changes.

Relevant files may include:

```text
README.md
CHANGELOG.md
PROJECT_ARCHITECTURE_OVERVIEW.md
docs/ARCHITECTURE_RULES.md
docs/PR_CHECKLIST.md
docs/refactor/*.md
docs/testing/LIVE_SMOKE_CHECKLIST.md
```

Do not let docs claim that a refactor is complete if code still contradicts it.

If a file is kept only for compatibility, mark it clearly.

Example:

```python
# DEPRECATED: kept for backward-compatible imports.
# New code should import from tg_msg_manager.services.db_export.
```

---

# 14. Dependency Rules

## 14.1. Avoid circular imports

After moving modules, check imports.

Run a basic import smoke test:

```bash
python - <<'PY'
import tg_msg_manager
import tg_msg_manager.services.export
import tg_msg_manager.services.context
PY
```

Adapt imports to actual packages.

## 14.2. No upward imports

Infrastructure must not import services.

Core must not import infrastructure.

CLI must not be imported by service/core/infrastructure modules.

## 14.3. Prefer dependency injection

Do not instantiate concrete infrastructure deep inside business logic if it can be injected.

Bad:

```python
class SomeService:
    def run(self):
        storage = SQLiteStorage(...)
```

Good:

```python
class SomeService:
    def __init__(self, storage: SomeStorageContract):
        self.storage = storage
```

---

# 15. Error Handling Rules

Errors should be explicit and domain-appropriate.

Do not catch broad exceptions unless you add context and re-raise or convert to a structured result.

Bad:

```python
try:
    ...
except Exception:
    pass
```

Acceptable:

```python
try:
    ...
except TelegramFetchError as exc:
    return SyncResult.failed(reason=str(exc))
```

Do not hide failures that affect exported data, checkpoints, or storage state.

---

# 16. Logging / Telemetry Rules

Logging and telemetry must not contain business logic.

Event emitters may emit:

- start;
- progress;
- success;
- failure;
- skipped;
- retry scheduled.

Event emitters must not decide:

- what to export;
- what to fetch;
- what to skip;
- what to write.

Telemetry failure should not crash the main use case unless explicitly required.

---

# 17. Backward Compatibility Rules

Compatibility wrappers are allowed and preferred during refactor.

Examples:

```text
services/exporter.py
services/context_engine.py
services/db_exporter.py
services/private_archive.py
core/models/service_payloads.py
infrastructure/storage/interface.py
```

These files may re-export new implementations.

Do not remove them unless:

1. all imports are migrated;
2. tests confirm removal is safe;
3. changelog documents the break;
4. the change is explicitly approved.

---

# 18. Schema / Migration Rules

Do not change database schema casually.

Any schema change must include:

- reason;
- migration path;
- backward compatibility note;
- tests;
- updated architecture documentation;
- changelog entry.

For refactor-only tasks, schema should not change.

If a table is ambiguous or legacy, document its status before building on it.

---

# 19. Code Style Rules

Follow the existing project style.

Prefer:

- type hints;
- dataclasses for structured internal values;
- small modules;
- explicit names;
- pure functions where possible;
- narrow interfaces;
- deterministic behavior.

Avoid:

- global mutable state;
- untyped dict chains;
- large methods;
- hidden side effects;
- cross-layer imports;
- broad utility modules with unrelated functions;
- adding dependencies without need.

---

# 20. New Feature Rules

Before adding a feature, identify its proper layer.

Questions to answer:

1. Is this CLI surface?
2. Is this orchestration?
3. Is this domain policy?
4. Is this storage read/write?
5. Is this rendering?
6. Is this Telegram fetching?
7. Is this analytics?
8. Is this reporting?

Create new modules instead of expanding existing hot-path files.

Every new feature must include:

- tests;
- documentation if user-visible;
- architecture note if it adds a new subsystem;
- changelog entry if behavior changes.

---

# 21. Refactor Checklist

Before starting a refactor:

- [ ] Identify current behavior.
- [ ] Run relevant tests.
- [ ] Identify public contracts.
- [ ] Create split map if large module is affected.
- [ ] Plan compatibility wrappers.
- [ ] Avoid schema changes.
- [ ] Avoid CLI changes.

During refactor:

- [ ] Move one responsibility at a time.
- [ ] Keep old imports working.
- [ ] Add tests for extracted components.
- [ ] Run relevant tests after each logical step.
- [ ] Compare fixture output if export/context is affected.

After refactor:

- [ ] Run full tests.
- [ ] Run verification command if available.
- [ ] Run import smoke test.
- [ ] Update docs.
- [ ] Update changelog.
- [ ] Confirm no new product feature was added accidentally.

---

# 22. Definition of Done for Any Change

A change is done only if:

- [ ] tests pass;
- [ ] public behavior is preserved or documented;
- [ ] CLI contract is preserved if CLI touched;
- [ ] export output is preserved if export touched;
- [ ] no raw SQL added to service layer;
- [ ] no new logic added to compatibility wrappers;
- [ ] no broad storage contract expanded unnecessarily;
- [ ] no analytics added to hot-path services;
- [ ] no circular imports introduced;
- [ ] docs updated if architecture changed;
- [ ] changelog updated if behavior or architecture changed.

---

# 23. Absolute Prohibitions

Never do the following without explicit task instruction:

- rewrite the project from scratch;
- replace SQLite;
- change Telegram library;
- change CLI interface;
- change export format;
- add analytics to export/context/db-export services;
- put raw SQL in services;
- build new features on ambiguous legacy tables;
- remove compatibility wrappers blindly;
- hide exceptions with `except Exception: pass`;
- add large unrelated utility modules;
- merge multiple refactor stages into one uncontrolled change.

---

# 24. Preferred Development Pattern

Use this pattern:

```text
1. Understand current behavior.
2. Locate correct layer.
3. Create small dedicated module.
4. Move one responsibility.
5. Preserve compatibility import.
6. Add or update tests.
7. Run tests.
8. Update docs.
9. Stop.
```

Do not continue expanding scope after the requested task is complete.

---

# 25. Final Rule

The repository is a data pipeline with strict boundaries, not a collection of scripts.

Every change must make the codebase easier to extend, easier to test, and harder to accidentally break.

If a change makes future features faster to add but weakens boundaries, reject that change.
