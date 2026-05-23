---
name: architecture-guard
description: Detect architecture violations in proposed or completed tg-msg-manager changes. Use when changes touch CLI, services, storage, protected files, compatibility wrappers, channel export, dataset validation/inspection/doctor boundaries, post-processing boundaries, schema or dataset formats, or architecture-sensitive feature/refactor/bugfix stages.
---

# Architecture Guard

## Purpose

Detect architecture violations in proposed or completed changes.

Block architecture creep, service bloat, boundary violations, unsafe schema/storage changes, and exporter-core analytics pollution.

Do not implement fixes unless explicitly requested.

## When To Use

Use for:

```text
feature stages
refactor stages
bugfixes touching services/storage/CLI
changes touching protected files
changes involving exporter boundaries
changes involving dataset validation/inspection/doctor boundaries
changes involving post-processing boundary
```

Do not use for:

```text
pure prose review unless architecture boundaries are relevant
simple translation or formatting tasks
```

## Inputs

Request these inputs when available:

```text
AGENTS.md
active stage file or task
changed files list
diff summary
specific changed file contents
architecture docs when relevant
test/check output if architecture claim depends on tests
```

Do not require a full diff unless necessary.

## Architecture Rules

### CLI Boundary

CLI may:

```text
parse args
validate basic input
call services
render high-level results
dispatch commands
```

CLI must not contain:

```text
export algorithms
raw SQL
storage implementation
dataset transformation logic
Telegram traversal logic
analytics
profiling
OSINT logic
LLM-dependent logic
```

### Service Boundary

Services may orchestrate.

Services must not contain:

```text
raw SQL
large feature algorithms inside facades
analytics/profiling/OSINT/LLM logic
storage implementation details
```

Feature logic must live in focused modules with one responsibility.

### Protected Files

Protected service facades:

```text
tg_msg_manager/services/export/service.py
tg_msg_manager/services/db_export/service.py
tg_msg_manager/services/private_archive/service.py
tg_msg_manager/services/context/engine.py
tg_msg_manager/services/channel_export/service.py
```

Allowed only when scoped:

```text
mechanical wiring
delegation
small orchestration adjustments
option/config pass-through
```

Forbidden:

```text
new feature logic
large algorithms
analytics
raw SQL
schema changes
format changes
```

### Compatibility Wrappers

Compatibility wrappers / aggregators:

```text
tg_msg_manager/services/exporter.py
tg_msg_manager/services/context_engine.py
tg_msg_manager/services/db_exporter.py
tg_msg_manager/services/private_archive.py
tg_msg_manager/core/models/service_payloads.py
tg_msg_manager/infrastructure/storage/interface.py
tg_msg_manager/cli_commands.py
```

Allowed:

```text
backward-compatible delegation
thin adapter behavior
re-exporting stable names
deprecation forwarding
```

Forbidden:

```text
business logic
new product behavior
storage logic
analytics
```

### Storage Boundary

Rules:

```text
SQL belongs under tg_msg_manager/infrastructure/storage/
core/domain must not import infrastructure
infrastructure must not import services
service/core/infrastructure must not import CLI
SQLite schema changes require explicit stage scope
```

### Channel Export Boundary

Rules:

```text
channel export logic lives under tg_msg_manager/services/channel_export/
discussion logic lives under tg_msg_manager/services/channel_export/discussions/
media logic lives in media-specific channel export modules
ChannelExportService remains orchestration-only
workflow modules own workflow-specific run paths
ChannelExportWorkflowContext is wiring/helper context, not product logic container
```

Do not add to exporter core:

```text
analytics
OSINT interpretation
profiling
fingerprinting
identity claims
sentiment analysis
narrative classification
OCR
STT
media recognition
LLM-dependent behavior
```

### Dataset Validation / Doctor Boundary

Rules:

```text
validate-dataset checks deterministic structure and consistency
inspect-dataset summarizes datasets
doctor diagnoses validation findings and suggests actions
validation/inspection/doctor must be read-only
doctor must not repair, migrate, fetch, mutate, or rewrite datasets
```

Forbidden inside validation/inspection/doctor:

```text
analytics
OSINT interpretation
profiling
fingerprinting
OCR
STT
media recognition
LLM-dependent behavior
Telegram network access
dataset repair unless explicitly scoped as a separate repair tool
```

### Post-Processing Boundary

Rules:

```text
post-processing is outside exporter core
post-processing reads exported datasets
post-processing outputs separate artifacts
source datasets must not be mutated by default
LLM reports are optional downstream outputs, not exporter behavior
```

Do not embed post-processing in:

```text
channel export
DB export
context engine
private archive
storage write paths
validation
doctor
CLI command handlers beyond dispatch to explicitly scoped external post-processing tools
```

### Schema And Dataset Format Boundary

Rules:

```text
SQLite schema changes require explicit stage scope
dataset format changes require explicit stage scope
manifest/state/JSONL/TXT/media layout changes require tests and docs
state/incremental/force/no-new-work behavior must be preserved unless explicitly scoped
```

## Output Format

Return exactly:

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

If there are no violations:

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

Prefer minimal boundary-preserving fixes.

Do not approve changes that mix refactor, feature work, formatting churn, and behavior changes unless explicitly scoped.

## Example

Input issue:

```text
tg_msg_manager/services/channel_export/service.py adds analytics classification during export.
```

Expected output:

```text
VERDICT:
- fail

VIOLATIONS:
- file: tg_msg_manager/services/channel_export/service.py
  rule: exporter core must not contain analytics/profiling/OSINT/LLM logic
  evidence: analytics classification added during export path
  fix: move analysis to external post-processing layer; keep exporter producing dataset only

RISK:
- high

NOTES:
- ChannelExportService is protected and must remain orchestration-only
```
