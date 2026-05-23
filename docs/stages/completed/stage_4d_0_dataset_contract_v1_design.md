# STAGE 4D.0 — DATASET CONTRACT V1 DESIGN

Status: active task
Stage: 4D.0
Type: docs / contract design
Depends on: Stage 4C.0 readiness decision

---

## 0. CODEX ENTRY CONTRACT

```text
Read AGENTS.md first.

Execute Stage 4D.0 — Dataset Contract V1 Design.

Goal:
Define a documented v1 filesystem dataset contract for exported Telegram datasets.

Do not modify runtime code.
Do not modify tests.
Do not change dataset formats.
Do not change CLI behavior.
Do not start implementation stages.

Use AGENTS.md compact output format.
```

---

## 1. PURPOSE

This stage creates the formal contract that future validator, inspector, doctor, and post-processing layers will rely on.

It must document existing behavior, not invent new runtime behavior.

The contract should cover channel export datasets first, and may reference group/db/private archive datasets only when existing docs/code already define their outputs clearly.

---

## 2. FILES TO INSPECT

Required:

```text
AGENTS.md
COMMANDS.md
README.md
tg_msg_manager/services/channel_export/
tg_msg_manager/services/channel_export/discussions/
tg_msg_manager/services/dataset_validation/
tests/services/channel_export/
tests/services/dataset_validation/
docs/architecture/
docs/development/
```

Optional only if directly relevant:

```text
tg_msg_manager/services/rendering/
tg_msg_manager/services/db_export/
tg_msg_manager/services/private_archive/
```

Do not inspect:

```text
docs/archive
unrelated roadmap files
old prompts
```

---

## 3. HARD PROHIBITIONS

Do not change:

```text
runtime code
tests
CLI behavior
output files
output directory layout
manifest format
state file format
JSONL schemas
TXT profiles
media behavior
discussion behavior
SQLite schema
```

Do not add:

```text
new commands
new validators
new doctor implementation
new post-processing implementation
new runtime dependencies
analytics
OSINT logic
profiling
LLM-dependent behavior
```

---

## 4. CONTRACT DESIGN TASKS

### 4.1 Inventory existing dataset files

Document existing channel export artifacts:

```text
manifest.json
messages.jsonl
messages.txt
media_manifest.jsonl
channel_export_state.json
discussion_threads.jsonl
discussion_comments.jsonl
discussion_export_state.json
run changelog files if present
```

For each artifact, record:

```text
when it is expected
which mode creates it
whether it is required or optional
whether it is append/overwrite/stateful
which command produces it
```

### 4.2 Define dataset modes matrix

Document current behavior for:

```text
media none / metadata / full
discussion none / metadata / full
force full vs incremental
include_jsonl / include_txt if present
no-new-work run
partial failure cases
```

### 4.3 Define contract status labels

Use deterministic labels:

```text
REQUIRED
OPTIONAL
CONDITIONAL
NOT_EXPECTED
LEGACY_COMPAT
UNKNOWN_NEEDS_CHECK
```

### 4.4 Define validation boundaries

Clarify:

```text
validate-dataset checks structure and consistency
inspect-dataset summarizes datasets
neither command performs analytics, OSINT, profiling, OCR, STT, or LLM analysis
```

### 4.5 Define extension boundary

Document the intended future pipeline:

```text
export -> validate/inspect -> dataset doctor -> post-processing -> optional LLM report
```

Clarify that post-processing reads datasets and must not be embedded inside exporter core.

---

## 5. REQUIRED DOCS

Create:

```text
docs/architecture/DATASET_CONTRACT_V1.md
docs/stages/reports/STAGE_4D_0_DATASET_CONTRACT_V1_DESIGN_REPORT.md
```

Conditional:

```text
docs/README.md only if new architecture doc must be indexed
COMMANDS.md only if it already contains inaccurate dataset contract wording
README.md only if it already contains inaccurate public output descriptions
```

Do not update docs just to restate the stage.

---

## 6. TESTS / VERIFICATION

Docs-only stage.

Run:

```bash
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
```

If not run, record exact reason.

Do not claim checks passed unless actually run.

---

## 7. REPORT

Create:

```text
docs/stages/reports/STAGE_4D_0_DATASET_CONTRACT_V1_DESIGN_REPORT.md
```

Report must record:

```text
contract doc created
source files/docs inspected
dataset artifacts covered
known gaps
runtime behavior unchanged
tests/checks run
completion status
```

---

## 8. COMPLETION CRITERIA

This stage is complete when:

```text
DATASET_CONTRACT_V1.md exists
contract documents existing behavior only
no runtime code changed
no tests changed
checks were run or inability documented
required report exists
lifecycle cleanup is completed according to AGENTS.md
```

---

## 9. OUTPUT LIMITS

Use AGENTS.md compact final response format.

Do not paste full docs.
Do not include broad future recommendations unless required by a real blocker.
