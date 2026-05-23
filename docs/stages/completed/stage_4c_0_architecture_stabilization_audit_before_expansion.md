# STAGE 4C.0 — ARCHITECTURE STABILIZATION AUDIT BEFORE EXPANSION

Status: active task
Stage: 4C.0
Type: audit / architecture readiness
Depends on: current CLI decomposition, channel export workflows, tests layout, AGENTS.md rules

---

## 0. CODEX ENTRY CONTRACT

```text
Read AGENTS.md first.

Execute Stage 4C.0 — Architecture Stabilization Audit Before Expansion.

Goal:
Audit current architecture readiness before new expansion layers.

Do not modify runtime code.
Do not modify AGENTS.md.
Do not modify docs except the required factual stage report.
Do not start later stages.

Use AGENTS.md compact output format.
```

---

## 1. PURPOSE

This is a read-only stabilization audit.

The project already appears to have completed major decomposition:

```text
cli_commands.py -> tg_msg_manager/cli/commands/*
ChannelExportService -> tg_msg_manager/services/channel_export/workflows/*
tests/*.py -> tests/<subsystem>/*
```

This stage verifies whether that decomposition is stable enough for future expansion.

The output must determine whether new refactor work is actually needed or whether the project is ready to move toward dataset-contract and external post-processing layers.

---

## 2. FILES TO INSPECT

Required:

```text
AGENTS.md
tg_msg_manager/cli_commands.py
tg_msg_manager/cli/
tg_msg_manager/cli/commands/
tg_msg_manager/services/channel_export/service.py
tg_msg_manager/services/channel_export/workflows/
tg_msg_manager/services/channel_export/discussions/
tests/
pyproject.toml
Makefile
.github/workflows/
README.md
COMMANDS.md
docs/README.md
docs/architecture/
docs/development/
docs/stages/README.md
```

Optional only if directly referenced:

```text
docs/stages/active/
recent docs/stages/reports/ relevant to CLI/channel/test decomposition
```

Do not inspect:

```text
docs/archive
unrelated roadmap files
old prompts
unrelated runtime modules
```

---

## 3. HARD PROHIBITIONS

Do not change:

```text
runtime code
tests
AGENTS.md
README.md
COMMANDS.md
architecture docs
development docs
CLI behavior
channel export behavior
dataset validation behavior
SQLite schema
dataset formats
output files
```

Do not add:

```text
new features
new commands
new runtime dependencies
new docs except the required report
analytics
OSINT logic
profiling
fingerprinting
LLM-dependent behavior
post-processing implementation
```

---

## 4. AUDIT TASKS

### 4.1 CLI decomposition audit

Verify:

```text
tg_msg_manager/cli_commands.py is only a compatibility aggregator
tg_msg_manager/cli/commands/* contains focused command handlers
old imports remain compatible
CLI handlers do not contain service-layer business logic
CLI remains thin
README.md and COMMANDS.md match current CLI command surface
```

Flag:

```text
business logic inside CLI handlers
duplicated command handlers
stale docs references
broken compatibility imports
overly broad CLI command modules
```

### 4.2 Channel export workflow audit

Verify:

```text
ChannelExportService remains orchestration-only
workflow modules exist and own full/incremental/no-new-work paths
workflow modules reuse existing focused components
discussion logic remains under channel_export/discussions/
media logic remains in media-specific modules
state/manifest/result handling is not duplicated dangerously
```

Flag:

```text
feature logic added back into ChannelExportService
workflow context acting as hidden god object
full/incremental workflow duplication that should be extracted later
discussion/media behavior mixed into wrong layer
state or manifest behavior changes without tests/docs
```

### 4.3 Tests layout audit

Verify:

```text
tests are grouped by subsystem
pytest collection still works according to project config
Makefile and GitHub Actions reference valid test paths
docs/development test commands do not point to old flat paths
fixtures remain accessible from moved tests
```

Flag:

```text
stale flat test paths
broken test collection assumptions
docs or CI still referencing old paths
```

### 4.4 AGENTS.md architecture rule audit

Evaluate whether `AGENTS.md` needs new rules.

Check if current `AGENTS.md` already covers:

```text
CLI thin boundary
service orchestration-only boundary
protected service facades
compatibility wrappers
storage SQL boundary
channel export service boundary
discussion/media module ownership
skill selection
stage lifecycle
output discipline
```

If no update is needed, state:

```text
AGENTS.md update not needed.
```

If update is needed, do not edit `AGENTS.md` in this stage. Instead, propose exact minimal patches for Stage 4C.1.

### 4.5 Expansion readiness decision

Classify readiness:

```text
READY_FOR_DATASET_CONTRACT
READY_AFTER_DOC_SYNC
NEEDS_TARGETED_REFACTOR_FIRST
NOT_READY
```

Give exact blockers if not ready.

---

## 5. REQUIRED DOCS

Required:

```text
docs/stages/reports/STAGE_4C_0_ARCHITECTURE_STABILIZATION_AUDIT_BEFORE_EXPANSION_REPORT.md
```

Do not update other docs in this stage.

Report must record:

```text
CLI decomposition status
ChannelExportService/workflow status
tests layout status
AGENTS.md rule status
docs/CI/test command status
risks found
whether Stage 4C.1 is needed
expansion readiness decision
recommended next stage
```

---

## 6. TESTS / VERIFICATION

This is read-only.

Run or inspect where available:

```bash
python3 -m compileall tg_msg_manager
pytest --collect-only -q
ruff check tg_msg_manager tests
```

If commands cannot be run, record exact reason.

Do not claim checks passed unless actually run.

---

## 7. COMPLETION CRITERIA

This stage is complete when:

```text
required architecture areas were inspected
AGENTS.md need/no-need decision is recorded
expansion readiness decision is recorded
required report exists
checks were run or inability was documented
no runtime files were modified
lifecycle cleanup is completed according to AGENTS.md
```

---

## 8. OUTPUT LIMITS

Use AGENTS.md compact final response format.

Do not paste full diffs.
Do not include broad summaries.
Do not include future recommendations unless required by a real blocker.
