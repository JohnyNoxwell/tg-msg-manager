# STAGE 4A.2 — MEDIA / DISCUSSION VALIDATORS

Status: active task  
Stage: 4A.2  
Type: dataset relationship validation  
Depends on: Stage 4A.1

---

## 0. CODEX ENTRY CONTRACT

```text
Read AGENTS.md first.

Execute Stage 4A.2 — Media / Discussion Validators.

Implement read-only validation for media_manifest.jsonl and optional discussion dataset files.
Do not download media.
Do not analyze media.
Do not optimize media.
Do not call Telegram.
Do not infer meaning from posts or comments.
```

---

## 1. PURPOSE

Validate cross-file relationships that are not covered by basic JSON/manifest/state checks.

Target files:

```text
media_manifest.jsonl
media/
discussion_comments.jsonl
discussion_comments.txt
discussion_threads.jsonl
discussion_export_state.json
```

---

## 2. MEDIA VALIDATOR TASKS

Implement in:

```text
tg_msg_manager/services/dataset_validation/media_validator.py
```

### A. Load media manifest

- [ ] Check `media_manifest.jsonl` exists.
- [ ] Parse via shared JSONL validator.
- [ ] Invalid line is error.
- [ ] Non-object row is error.
- [ ] Empty media manifest is valid if dataset has no media.

### B. Validate media statuses

Use current known statuses:

```text
metadata_only
downloaded
already_exists
skipped_by_size
skipped_by_type
failed
```

Tasks:

- [ ] Accept known statuses.
- [ ] Warn on unknown status.
- [ ] Count statuses.
- [ ] Include status counts in summary.
- [ ] Do not treat `failed` as structural error; report warning.
- [ ] Do not treat skipped statuses as error.

### C. Validate media paths

Fields may include current schema names such as:

```text
final_path
path
relative_path
```

Tasks:

- [ ] Inspect actual schema tests/docs before choosing fields.
- [ ] If status is `downloaded` or `already_exists`, require a usable final path if current schema provides one.
- [ ] Resolve path relative to dataset root unless stored absolute path is intentionally supported.
- [ ] Report error if path escapes dataset root via `..`.
- [ ] Report error if status is `downloaded` or `already_exists` but file is missing.
- [ ] Warn if metadata-only/skipped/failed rows have no file path.
- [ ] Do not hash files unless already cheap and clearly supported by existing manifest fields.

### D. Optional sha256 check

Only implement if trivial and current schema consistently includes `sha256`.

- [ ] If `sha256` exists and file exists, optionally verify hash under `--strict`.
- [ ] Do not make sha256 verification default if it can be expensive.
- [ ] If not implemented, document as remaining limitation.

Default recommendation:

```text
Do not verify sha256 in Stage 4A unless already cheap and clearly scoped.
```

---

## 3. DISCUSSION VALIDATOR TASKS

Implement in:

```text
tg_msg_manager/services/dataset_validation/discussion_validator.py
```

### A. Detect discussion presence

Discussion is considered present if any of these exists:

```text
discussion_comments.jsonl
discussion_comments.txt
discussion_threads.jsonl
discussion_export_state.json
```

Tasks:

- [ ] If none exists, discussion summary should say absent.
- [ ] If some but not all expected discussion files exist, report warning or error depending on missing file.
- [ ] If `discussion_comments.jsonl` exists and is invalid, report error.
- [ ] If `discussion_threads.jsonl` exists and is invalid, report error.

### B. Validate comments

- [ ] Parse `discussion_comments.jsonl`.
- [ ] Validate every row is object.
- [ ] Count comments.
- [ ] Detect duplicate discussion comment ids if field exists.
- [ ] Validate non-negative ids/counters if present.
- [ ] Validate `channel_post_id` / equivalent field links to known message ids if current schema provides it.
- [ ] If link field is missing for all rows, warn rather than invent schema.
- [ ] Do not analyze comment text.

### C. Validate threads

- [ ] Parse `discussion_threads.jsonl`.
- [ ] Validate every row is object.
- [ ] Count threads.
- [ ] Validate thread references to channel post ids if field exists.
- [ ] Compare thread comment counts to observed comments if fields allow it.
- [ ] Use warning for count mismatch unless clearly corrupt.
- [ ] Do not reconstruct reply trees.

### D. Discussion TXT

- [ ] If discussion comments JSONL exists, expect `discussion_comments.txt`.
- [ ] Missing TXT may be warning or error; prefer warning if JSONL is authoritative.
- [ ] Do not parse TXT semantics.

---

## 4. CROSS-FILE VALIDATION

Use outputs from Stage 4A.1:

```text
message_id set
manifest object
state object
media records
discussion records
```

Tasks:

- [ ] Compare media record count to manifest media count where field exists.
- [ ] Compare discussion comment/thread counts to manifest discussion summary where fields exist.
- [ ] Compare discussion state counters to observed counts where fields exist.
- [ ] Validate discussion records reference known channel posts where feasible.
- [ ] Validate file paths listed in manifest included files exist where feasible.

Do not require perfect strictness for old datasets unless the field is clearly part of current contract.

---

## 5. ISSUE CODES

Recommended issue codes:

```text
unknown_media_status
missing_media_manifest
invalid_media_path
media_path_escape
media_file_missing
failed_media_records_present
invalid_discussion_comments_jsonl
invalid_discussion_threads_jsonl
missing_discussion_file
duplicate_discussion_comment_id
discussion_comment_unlinked
discussion_thread_unlinked
discussion_count_mismatch
manifest_included_file_missing
```

---

## 6. TESTS

Create / update:

```text
tests/test_dataset_validation_media.py
tests/test_dataset_validation_discussions.py
```

Required media tests:

- [ ] empty valid media manifest.
- [ ] downloaded media with existing file is ok.
- [ ] downloaded media with missing file is error.
- [ ] already_exists media with missing file is error.
- [ ] failed media produces warning, not error.
- [ ] skipped_by_size does not require file.
- [ ] skipped_by_type does not require file.
- [ ] unknown media status produces warning.
- [ ] path traversal via `../` is error.

Required discussion tests:

- [ ] no discussion files is valid absent discussion.
- [ ] valid discussion files produce counts.
- [ ] invalid discussion_comments.jsonl is error.
- [ ] invalid discussion_threads.jsonl is error.
- [ ] discussion comment linked to missing channel post produces warning/error according to policy.
- [ ] discussion files present but discussion_state missing produces warning.
- [ ] duplicate discussion comment id produces warning/error according to policy.

Use small temp fixtures.

---

## 7. VERIFICATION

Run:

```bash
pytest tests/test_dataset_validation_media.py tests/test_dataset_validation_discussions.py
pytest tests/test_dataset_validation_*.py
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
```

Do not claim commands passed unless actually run.

---

## 8. COMPLETION CRITERIA

Complete only if:

- [ ] media manifest validates statuses and paths.
- [ ] missing downloaded media files are detected.
- [ ] failed media is warning, not fatal dataset corruption.
- [ ] discussion files are optional but validated when present.
- [ ] discussion linkage checks use actual known schema fields.
- [ ] tests cover valid and broken media/discussion datasets.
- [ ] no media download or analysis logic added.
