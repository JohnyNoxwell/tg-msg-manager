# STAGE 4A.1 — JSONL / MANIFEST / STATE VALIDATORS

Status: active task  
Stage: 4A.1  
Type: deterministic dataset structure validation  
Depends on: Stage 4A.0

---

## 0. CODEX ENTRY CONTRACT

```text
Read AGENTS.md first.

Execute Stage 4A.1 — JSONL / Manifest / State Validators.

Implement read-only structural validators for exported channel datasets.
Do not implement analytics.
Do not inspect message meaning.
Do not call Telegram.
Do not repair datasets.
```

---

## 1. PURPOSE

Implement core validators for:

```text
manifest.json
messages.jsonl
channel_export_state.json
optional discussion_export_state.json
```

Also create reusable JSONL parsing functions for later media/discussion validators.

---

## 2. REQUIRED INPUTS

Dataset path:

```text
exports/channels/<dataset>/
```

Expected required files for base channel dataset:

```text
manifest.json
messages.jsonl
messages.txt
media_manifest.jsonl
channel_export_state.json
```

Optional discussion files:

```text
discussion_comments.jsonl
discussion_comments.txt
discussion_threads.jsonl
discussion_export_state.json
```

Presence of optional discussion files depends on `discussion_mode` / manifest contents / actual files.

---

## 3. VALIDATION PRINCIPLES

Read-only:

```text
Open files, parse files, collect issues.
Never write, rewrite, normalize, repair, migrate, or delete dataset files.
```

Deterministic:

```text
Same dataset -> same report.
Stable issue ordering.
Stable JSON output.
```

Lenient where older datasets may exist:

```text
If exact current schema is not fully known, report warnings for optional drift instead of crashing.
```

Strict for corruption:

```text
Invalid JSON, invalid JSONL, missing required files, duplicate message_id are errors.
```

---

## 4. JSONL VALIDATOR TASKS

Implement in:

```text
tg_msg_manager/services/dataset_validation/jsonl_validator.py
```

### A. Core function

- [ ] Add function to read JSONL file line by line.
- [ ] Return parsed list or iterable of dictionaries.
- [ ] Track line numbers.
- [ ] Ignore final empty trailing line.
- [ ] Treat non-empty invalid JSON line as error.
- [ ] Treat valid JSON value that is not object/dict as error.
- [ ] Do not silently skip malformed lines.
- [ ] Do not load huge files in a way that blocks future streaming extension if easy.

Suggested API:

```python
def load_jsonl_records(path: Path) -> tuple[list[dict], list[ValidationIssue]]:
    ...
```

or streaming equivalent.

### B. Messages validation

- [ ] Validate `messages.jsonl` exists.
- [ ] Validate every row is JSON object.
- [ ] Validate every row has a usable `message_id` or current schema equivalent.
- [ ] Detect duplicate `message_id`.
- [ ] Count records.
- [ ] Collect `message_id` set for discussion linkage checks.
- [ ] Do not validate text semantics.

### C. TXT presence

- [ ] Check `messages.txt` exists.
- [ ] If missing, report error.
- [ ] Do not parse message text semantics.

---

## 5. MANIFEST VALIDATOR TASKS

Implement in:

```text
tg_msg_manager/services/dataset_validation/manifest_validator.py
```

### A. Load manifest

- [ ] Check `manifest.json` exists.
- [ ] Parse JSON.
- [ ] Invalid JSON is error.
- [ ] Non-object root is error.

### B. Shape checks

Check expected fields based on actual current dataset contract.

At minimum:

- [ ] dataset/channel identity fields exist if current schema defines them.
- [ ] message/media count fields are non-negative integers if present.
- [ ] discussion summary fields are non-negative if present.
- [ ] included files list is sane if present.
- [ ] referenced files in manifest exist where feasible.
- [ ] unknown optional fields do not fail validation.

### C. Count comparison

- [ ] Compare manifest message count to observed `messages.jsonl` count if field exists.
- [ ] Compare manifest media count to observed `media_manifest.jsonl` count if field exists.
- [ ] Compare discussion counts if fields exist.
- [ ] Use warnings for count drift unless it clearly proves corruption.
- [ ] Use errors for impossible negative counts.

---

## 6. STATE VALIDATOR TASKS

Implement in:

```text
tg_msg_manager/services/dataset_validation/state_validator.py
```

### A. Channel state

- [ ] Check `channel_export_state.json` exists.
- [ ] Parse JSON.
- [ ] Invalid JSON is error.
- [ ] Non-object root is error.
- [ ] Validate counters are non-negative if present.
- [ ] Validate `last_exported_message_id` is non-negative if present.
- [ ] Validate `last_run_status` if present.
- [ ] Warn if state and manifest channel identity conflict.
- [ ] Warn/error if state counts are impossible relative to actual files.

### B. Discussion state

- [ ] If `discussion_export_state.json` exists, parse it.
- [ ] Invalid JSON is error.
- [ ] Non-object root is error.
- [ ] Validate counters are non-negative if present.
- [ ] Warn if discussion state exists but no discussion payload files exist.
- [ ] Warn if discussion files exist but discussion state is missing.
- [ ] Do not require discussion state when discussion mode is none.

---

## 7. MODELS / ISSUE SHAPE

Use existing `models.py` from Stage 4A.0.

Every issue should include:

```text
severity: error/warning
code: stable machine-readable code
message: human-readable message
path: optional file path
line: optional JSONL line number
```

Recommended codes:

```text
missing_required_file
invalid_json
invalid_jsonl
invalid_jsonl_object
duplicate_message_id
missing_message_id
negative_count
manifest_count_mismatch
state_count_mismatch
state_identity_mismatch
discussion_state_without_payload
discussion_payload_without_state
```

---

## 8. TESTS

Create / update:

```text
tests/test_dataset_validation_jsonl.py
tests/test_dataset_validation_manifest_state.py
```

Required tests:

- [ ] valid minimal dataset returns no errors.
- [ ] missing `manifest.json` returns error.
- [ ] invalid `manifest.json` returns error.
- [ ] invalid `messages.jsonl` line returns error with line number.
- [ ] duplicate `message_id` returns error.
- [ ] missing `channel_export_state.json` returns error.
- [ ] invalid `channel_export_state.json` returns error.
- [ ] negative counters return error.
- [ ] count mismatch returns warning or error according to chosen policy.
- [ ] discussion state missing while discussion files exist returns warning.
- [ ] discussion state present while discussion files absent returns warning.

Use temporary directories and small fixture files. Do not require Telegram.

---

## 9. VERIFICATION

Run:

```bash
pytest tests/test_dataset_validation_jsonl.py tests/test_dataset_validation_manifest_state.py
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
```

If names differ, run the equivalent dataset validation test files.

---

## 10. COMPLETION CRITERIA

Complete only if:

- [ ] JSONL parser is deterministic and reports line-level errors.
- [ ] required base files are checked.
- [ ] manifest loads and validates shape.
- [ ] channel state loads and validates shape.
- [ ] discussion state handling is optional and sane.
- [ ] duplicate message ids are detected.
- [ ] tests cover valid and broken datasets.
- [ ] no runtime export code changed.
