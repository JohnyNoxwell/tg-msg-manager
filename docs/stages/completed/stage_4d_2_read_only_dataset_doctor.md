# STAGE 4D.2 — READ-ONLY DATASET DOCTOR

Status: active task
Stage: 4D.2
Type: feature / read-only inspection
Depends on: Stage 4D.0 Dataset Contract V1 and Stage 4D.1 validation alignment

---

## 0. CODEX ENTRY CONTRACT

```text
Read AGENTS.md first.

Execute Stage 4D.2 — Read-Only Dataset Doctor.

Goal:
Add a read-only dataset doctor/report layer that diagnoses dataset integrity issues without modifying datasets.

Do not repair datasets.
Do not modify exported files.
Do not add analytics or content interpretation.
Do not change export behavior.
Do not change existing validate-dataset or inspect-dataset contracts unless explicitly scoped.

Use AGENTS.md compact output format.
```

---

## 1. PURPOSE

This stage adds a separate diagnostic layer after validation.

The dataset doctor should answer:

```text
what is wrong
where it is wrong
how severe it is
what command/user action may fix it
```

It must not edit dataset files.

---

## 2. FILES TO INSPECT

Required:

```text
AGENTS.md
docs/architecture/DATASET_CONTRACT_V1.md
tg_msg_manager/services/dataset_validation/
tg_msg_manager/cli/commands/dataset.py
tg_msg_manager/cli_parser.py
tests/services/dataset_validation/
tests/cli/
COMMANDS.md
```

Optional only if needed:

```text
README.md
docs/development/
```

Do not inspect unrelated services.

---

## 3. HARD PROHIBITIONS

Do not change:

```text
export behavior
dataset output formats
state files
manifest files
JSONL files
media files
SQLite schema
existing command behavior unless explicitly scoped
```

Do not add:

```text
write/repair behavior
analytics
OSINT logic
profiling
fingerprinting
OCR
STT
media recognition
LLM-dependent behavior
new runtime dependencies
```

Doctor must be read-only.

---

## 4. ATOMIC IMPLEMENTATION TASKS

### 4.1 Decide command surface

Prefer one of:

```text
inspect-dataset --doctor
```

or:

```text
doctor-dataset
```

Choose the option that best fits current CLI style and minimizes CLI churn.

Record the reason in the report.

### 4.2 Define doctor result model

Create focused model(s) for:

```text
issue code
severity
artifact path
message
suggested next action
```

Severity:

```text
INFO
WARNING
ERROR
```

Do not include analytics labels.

### 4.3 Implement read-only doctor service

The service may reuse validators.

It must:

```text
read dataset artifacts
aggregate validation/consistency issues
produce deterministic report
avoid modifying files
```

### 4.4 Add CLI output

CLI output must be concise.

If JSON output exists in current style, support it only if consistent with existing patterns.

Do not add complex formatting.

### 4.5 Add focused tests

Tests must verify:

```text
doctor does not write files
missing required file produces ERROR
optional missing file does not produce ERROR
invalid JSONL produces ERROR
healthy dataset produces no ERROR
CLI command/flag works
```

---

## 5. REQUIRED DOCS

Required:

```text
docs/stages/reports/STAGE_4D_2_READ_ONLY_DATASET_DOCTOR_REPORT.md
COMMANDS.md
```

Conditional:

```text
README.md only if command overview needs update
docs/development/ only if test/dev workflow changes
docs/architecture/DATASET_CONTRACT_V1.md only if contract needs a doctor boundary note
```

---

## 6. TESTS / VERIFICATION

Run:

```bash
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
pytest tests -q -k "dataset or doctor or validate or inspect"
```

If filter is too broad, run closest focused tests and record exact command.

Do not claim checks passed unless actually run.

---

## 7. REPORT

Create:

```text
docs/stages/reports/STAGE_4D_2_READ_ONLY_DATASET_DOCTOR_REPORT.md
```

Report must record:

```text
chosen command surface
files changed
doctor checks implemented
read-only guarantee
tests added/updated
docs updated
checks run
completion status
```

---

## 8. COMPLETION CRITERIA

This stage is complete when:

```text
doctor functionality exists
doctor is read-only
focused tests cover read-only behavior
docs describe command/flag
export behavior is unchanged
required report exists
lifecycle cleanup is completed according to AGENTS.md
```

---

## 9. OUTPUT LIMITS

Use AGENTS.md compact final response format.

Do not paste full diffs.
