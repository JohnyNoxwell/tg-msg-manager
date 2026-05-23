# STAGE 4D.1 — DATASET VALIDATION CONTRACT ALIGNMENT

Status: active task
Stage: 4D.1
Type: implementation / validation hardening
Depends on: Stage 4D.0 Dataset Contract V1

---

## 0. CODEX ENTRY CONTRACT

```text
Read AGENTS.md first.

Execute Stage 4D.1 — Dataset Validation Contract Alignment.

Goal:
Align validate-dataset and inspect-dataset behavior with DATASET_CONTRACT_V1 without changing export behavior.

Do not change export behavior.
Do not change dataset formats.
Do not change CLI command names, flags, or defaults unless explicitly required by the contract and documented.
Do not add analytics, OSINT, profiling, OCR, STT, media recognition, or LLM logic.

Use AGENTS.md compact output format.
```

---

## 1. PURPOSE

This stage turns the documented dataset contract into stronger deterministic validation and inspection checks.

It must remain read-only with respect to exported datasets.

It must not modify datasets, repair files, or perform content analytics.

---

## 2. FILES TO INSPECT

Required:

```text
AGENTS.md
docs/architecture/DATASET_CONTRACT_V1.md
tg_msg_manager/services/dataset_validation/
tg_msg_manager/cli/commands/dataset.py
tg_msg_manager/cli_commands.py
tests/services/dataset_validation/
tests/cli/
COMMANDS.md
```

Optional only if directly needed:

```text
tg_msg_manager/services/channel_export/
tests/services/channel_export/
```

Do not inspect:

```text
docs/archive
unrelated services
post-processing code
```

---

## 3. HARD PROHIBITIONS

Do not change:

```text
export behavior
channel export behavior
media behavior
discussion export behavior
dataset output formats
manifest formats
state formats
SQLite schema
CLI command names
CLI defaults
output directory layout
```

Do not add:

```text
repair/write behavior
analytics
OSINT interpretation
profiling
fingerprinting
OCR
STT
media recognition
LLM-dependent behavior
new runtime dependencies
```

Validation and inspection must remain read-only.

---

## 4. ATOMIC IMPLEMENTATION TASKS

### 4.1 Map current validators to contract

- Inspect current dataset validators.
- Map each validator to `DATASET_CONTRACT_V1.md`.
- Identify missing checks.
- Do not edit yet.

### 4.2 Add missing deterministic checks

Add only checks that are directly supported by the contract.

Candidate checks:

```text
required/conditional artifact presence
mode-specific expected files
manifest counters vs files where already supported
discussion metadata/full consistency
media manifest presence by mode
state file consistency
invalid JSONL rows
empty required files
unexpected files only if contract defines them
```

### 4.3 Keep output stable unless scoped

If validation output changes, ensure:

```text
tests cover it
COMMANDS.md documents it if user-visible
report records it
```

### 4.4 Add or update focused tests

Tests must cover:

```text
valid contract-conforming dataset
missing required artifact
mode-specific conditional artifact
discussion metadata/full expectation
invalid JSONL or inconsistent counters if implemented
```

### 4.5 Verify read-only behavior

Ensure validators/inspectors do not write to dataset directories.

---

## 5. REQUIRED DOCS

Required:

```text
docs/stages/reports/STAGE_4D_1_DATASET_VALIDATION_CONTRACT_ALIGNMENT_REPORT.md
```

Conditional:

```text
COMMANDS.md if validate/inspect output or documented behavior changed
docs/architecture/DATASET_CONTRACT_V1.md only if Stage 4D.0 missed an existing behavior
docs/development/ only if test commands changed
```

Do not update docs just to restate the stage.

---

## 6. TESTS / VERIFICATION

Run:

```bash
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
pytest tests -q -k "dataset_validation or validate_dataset or inspect_dataset"
```

If filter is too broad or matches no tests, run closest focused dataset validation tests and record exact command.

Do not claim checks passed unless actually run.

---

## 7. REPORT

Create:

```text
docs/stages/reports/STAGE_4D_1_DATASET_VALIDATION_CONTRACT_ALIGNMENT_REPORT.md
```

Report must record:

```text
validators changed
checks added
tests added/updated
docs updated or not needed
read-only behavior preserved
export behavior unchanged
checks run
completion status
```

---

## 8. COMPLETION CRITERIA

This stage is complete when:

```text
validate/inspect behavior aligns with DATASET_CONTRACT_V1
read-only behavior is preserved
export behavior is unchanged
focused tests exist
docs updated only if required
required report exists
lifecycle cleanup is completed according to AGENTS.md
```

---

## 9. OUTPUT LIMITS

Use AGENTS.md compact final response format.

Do not paste full diffs.
