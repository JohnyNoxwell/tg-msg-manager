# STAGE 4A.4 — CONTRACT FIXTURES / DOCS / FINAL REPORT

Status: active task  
Stage: 4A.4  
Type: contract tests, documentation, lifecycle cleanup  
Depends on: Stage 4A.0, 4A.1, 4A.2, 4A.3

---

## 0. CODEX ENTRY CONTRACT

```text
Read AGENTS.md first.

Execute Stage 4A.4 — Contract Fixtures / Docs / Final Report.

Finish Stage 4A by adding realistic fixture coverage, documentation, verification, report, and lifecycle cleanup.
Do not implement new features beyond validation/inspection.
Do not start Stage 4B.
```

---

## 1. PURPOSE

Close Stage 4A properly:

```text
- dataset validation/inspection tests are stable
- docs explain the commands and boundary
- stage report records actual verification
- stage files move through lifecycle correctly
```

---

## 2. FIXTURE STRATEGY

Create small local test fixtures under tests, for example:

```text
tests/fixtures/dataset_validation/
  valid_minimal_channel_dataset/
  invalid_duplicate_messages/
  invalid_missing_media_file/
  invalid_bad_jsonl/
  valid_discussion_dataset/
```

Keep fixtures tiny.

Do not store real Telegram data.

Use synthetic records only.

---

## 3. REQUIRED FIXTURE CASES

### A. Valid minimal channel dataset

Contains:

```text
manifest.json
messages.jsonl
messages.txt
media_manifest.jsonl
channel_export_state.json
```

Expected:

```text
validate-dataset -> ok
inspect-dataset -> counts visible
```

### B. Duplicate messages

Contains duplicate `message_id`.

Expected:

```text
validate-dataset -> errors
issue code duplicate_message_id
```

### C. Invalid JSONL

Contains malformed JSONL line.

Expected:

```text
validate-dataset -> errors
line number present
```

### D. Missing downloaded media file

Contains media row with status `downloaded` or `already_exists` referencing missing file.

Expected:

```text
validate-dataset -> errors
issue code media_file_missing
```

### E. Valid discussion dataset

Contains discussion comments and threads linked to channel posts.

Expected:

```text
validate-dataset -> ok or warnings-free if schema supports it
inspect-dataset -> discussion counts visible
```

### F. Partial discussion dataset

Discussion JSONL exists but state missing.

Expected:

```text
validate-dataset -> warnings
```

---

## 4. CONTRACT TESTS

Create / consolidate:

```text
tests/test_dataset_validation_contracts.py
```

Tasks:

- [ ] Validate every fixture path.
- [ ] Assert expected status.
- [ ] Assert key issue codes.
- [ ] Assert JSON renderer output is stable enough for tests.
- [ ] Assert Markdown renderer includes required sections.
- [ ] Assert inspection output includes deterministic summary.
- [ ] Assert no test requires network/Telegram.

Do not make tests brittle on irrelevant field ordering except where JSON determinism is intentional.

---

## 5. DOCUMENTATION TASKS

Update or create:

```text
docs/architecture/DATASET_VALIDATION.md
COMMANDS.md
README.md
docs/README.md
docs/stages/README.md
CHANGELOG.md
```

### A. `docs/architecture/DATASET_VALIDATION.md`

Required sections:

```text
# Dataset Validation / Inspection

## Purpose
## Commands
## Read-only boundary
## Validation status
## What is checked
## What is not checked
## Known limitations
```

Must state:

```text
Stage 4A validates dataset structure and relationships.
Stage 4A does not analyze content.
Stage 4A does not repair datasets.
Stage 4A does not call Telegram.
```

### B. COMMANDS.md

Add command examples:

```bash
python3 -m tg_msg_manager.cli validate-dataset --path exports/channels/example
python3 -m tg_msg_manager.cli validate-dataset --path exports/channels/example --json
python3 -m tg_msg_manager.cli inspect-dataset --path exports/channels/example
python3 -m tg_msg_manager.cli inspect-dataset --path exports/channels/example --json
```

### C. README.md

Add compact reference only. Do not over-expand root README.

### D. CHANGELOG.md

Add new version entry:

```text
Stage 4A Dataset Validation / Inspection
```

Use project style.

---

## 6. STAGE REPORT

Create:

```text
docs/stages/reports/STAGE_4A_DATASET_VALIDATION_INSPECTION_REPORT.md
```

Required sections:

```text
# Stage 4A — Dataset Validation / Inspection Report

## 1. Summary
## 2. Commands added
## 3. Modules added
## 4. Validation coverage
## 5. Inspection coverage
## 6. Files changed
## 7. Tests
## 8. Verification results
## 9. Runtime behavior statement
## 10. Remaining limitations
## 11. Status
```

Runtime behavior statement must say:

```text
No Telegram fetching behavior changed.
No channel export behavior changed.
No dataset schema changed.
No state schema changed.
No SQLite schema changed.
No analytics/OCR/STT/media optimization added.
```

Verification section must list only commands actually run.

---

## 7. LIFECYCLE CLEANUP

After all Stage 4A blocks are complete:

- [ ] Move Stage 4A task files from:
  ```text
  docs/stages/active/
  ```
  to:
  ```text
  docs/stages/completed/
  ```

- [ ] Move general prompts to:
  ```text
  docs/archive/old_prompts/
  ```

- [ ] Update:
  ```text
  docs/stages/README.md
  ```

- [ ] Ensure:
  ```text
  docs/stages/active/
  ```
  contains only unfinished or next active work.

If Stage 4A is complete and no Stage 4B task exists yet:

```text
Current active stage files:
- None.
```

Do not create Stage 4B task files unless explicitly requested.

---

## 8. FINAL VERIFICATION

Run, at minimum:

```bash
pytest tests/test_dataset_validation_*.py
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
python3 -m tg_msg_manager.cli validate-dataset --help
python3 -m tg_msg_manager.cli inspect-dataset --help
```

If practical:

```bash
pytest tests/test_channel_export_*.py
make test
make verify
```

Do not claim commands passed unless actually run.

---

## 9. COMPLETION CRITERIA

Stage 4A is complete only if:

- [ ] `validate-dataset` works.
- [ ] `inspect-dataset` works.
- [ ] commands do not require Telegram client.
- [ ] validators are read-only.
- [ ] JSONL / manifest / state validation is covered.
- [ ] media validation is covered.
- [ ] discussion validation is covered.
- [ ] Markdown and JSON report renderers are covered.
- [ ] fixture contract tests exist.
- [ ] docs are updated.
- [ ] changelog is updated.
- [ ] stage report exists.
- [ ] stage lifecycle cleanup is done.
- [ ] no exporter behavior changed.
- [ ] no dataset/state/SQLite schema changed.
- [ ] no analytics/media processing added.
