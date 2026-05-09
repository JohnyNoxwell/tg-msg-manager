# Architecture Guard

## Purpose

Detect architecture violations in proposed or completed changes to `tg-msg-manager`.

Use this skill to block architecture creep, service bloat, boundary violations, hidden analytics, and unsafe schema/storage changes.

This skill reviews architecture. It does not implement fixes unless explicitly requested.

## When To Use

Use for:

```text
feature stages
refactor stages
bugfixes touching services/storage/CLI
changes touching protected files
changes involving exporter boundaries
```

Do not use for pure prose review unless architecture boundaries are relevant.

## Inputs

Required:

```text
AGENTS.md
active stage file or task
changed files list or diff summary
```

Optional:

```text
docs/architecture/README.md
docs/architecture/PROJECT_ARCHITECTURE_OVERVIEW.md
changed file contents
```

Do not inspect unrelated files.

## Architecture Rules

### CLI Boundary

CLI may:

```text
parse args
validate basic input
call services
render high-level results
```

CLI must not contain:

```text
export algorithms
raw SQL
storage logic
dataset transformation logic
analytics
profiling
OSINT logic
LLM-dependent logic
```

### Service Boundary

Services orchestrate.

Services must not contain:

```text
raw SQL
large feature algorithms
analytics/profiling/OSINT/LLM logic
storage implementation details
```

Protected service facades:

```text
tg_msg_manager/services/export/service.py
tg_msg_manager/services/db_export/service.py
tg_msg_manager/services/private_archive/service.py
tg_msg_manager/services/context/engine.py
tg_msg_manager/services/channel_export/service.py
```

Allowed in protected service facades only when scoped:

```text
mechanical wiring
delegation to focused modules
passing options/config through
small orchestration adjustments
```

### Compatibility Wrappers

No business logic in:

```text
tg_msg_manager/services/exporter.py
tg_msg_manager/services/context_engine.py
tg_msg_manager/services/db_exporter.py
tg_msg_manager/services/private_archive.py
tg_msg_manager/core/models/service_payloads.py
tg_msg_manager/infrastructure/storage/interface.py
```

Allowed:

```text
backward-compatible delegation
thin adapter behavior
deprecation forwarding
```

### Storage Boundary

Rules:

```text
SQL belongs under tg_msg_manager/infrastructure/storage/
core/domain must not import infrastructure
infrastructure must not import services
service/core/infrastructure must not import CLI
```

### Exporter Boundary

Exporter prepares datasets.

Do not add into exporter core:

```text
analytics
OSINT interpretation
sentiment analysis
bot detection
user profiling
fingerprinting
OCR
STT
media recognition
LLM-dependent behavior
identity claims
```

Allowed pipeline:

```text
export -> validate/inspect -> post-processing -> optional LLM report
```

### Schema Boundary

SQLite schema changes are forbidden unless the active stage explicitly scopes them.

Dataset format changes require:

```text
explicit stage scope
regression tests
documentation updates
```

## Output Format

Return only:

```text
VERDICT:
- pass/fail

VIOLATIONS:
- file: <path>
  rule: <short rule>
  evidence: <short evidence>
  fix: <minimal correction>

RISK:
- low/medium/high

NOTES:
- <real caveat or none>
```

If no violations:

```text
VIOLATIONS:
- none
```

## Rules

Do not suggest unrelated refactors.

Do not paste full diffs.

Keep evidence short and specific.

Treat architecture creep as a blocker.

If evidence is insufficient, state the missing input.

## Example

Input issue:

```text
tg_msg_manager/services/export/service.py adds sqlite3 query logic.
```

Output:

```text
VERDICT:
- fail

VIOLATIONS:
- file: tg_msg_manager/services/export/service.py
  rule: services must not contain raw SQL
  evidence: sqlite3 query logic added to protected service facade
  fix: move SQL to tg_msg_manager/infrastructure/storage/ and keep service as orchestration only

RISK:
- high

NOTES:
- protected file may receive delegation only
```
