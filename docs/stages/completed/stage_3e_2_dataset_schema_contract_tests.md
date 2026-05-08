# STAGE 3E.2 — DATASET SCHEMA CONTRACT TESTS

## 0. CODEX ENTRY PROMPT

```text
Read AGENTS.md first.

You are working on tg-msg-manager.

This task is part of the post-Stage-3C hardening sequence.

This is a stabilization/refactor/hardening phase, not a product expansion phase.

Follow this file exactly.
Do not skip required verification.
Do not start later stages unless explicitly instructed by the active task.
```

---

## 1. GLOBAL PURPOSE

The purpose of this hardening sequence is to make the post-Stage-3C foundation safer before adding new product features.

The priorities are:

```text
1. keep stage lifecycle clean
2. keep ChannelExportService thin
3. make dataset writes safer
4. lock dataset schemas with tests
5. harden state consistency
```

This sequence must reduce future scaling risk without changing public behavior unless the active stage explicitly allows it.

---

## 2. HARD PROHIBITIONS

Do not implement:

```text
- new Telegram export features
- new analytics
- OSINT interpretation
- sentiment analysis
- bot detection
- user profiling
- influence scoring
- narrative classification
- OCR
- speech-to-text
- image/video/audio analysis
- GUI/dashboard/SaaS features
- new database-backed channel export persistence
- SQLite schema changes
- migrations
- Stage 4 features
```

Do not change behavior of existing user-facing commands unless explicitly required by the current stage:

```text
export
db-export
export-pm
export-channel
retry
report
clean
delete
schedule
setup
```

Protected hot-path/service facade files:

```text
tg_msg_manager/services/export/service.py
tg_msg_manager/services/db_export/service.py
tg_msg_manager/services/private_archive/service.py
tg_msg_manager/services/context/engine.py
tg_msg_manager/services/channel_export/service.py
```

Rules for protected files:

```text
- Do not add new feature logic to protected files.
- Only orchestration, delegation, or mechanical wiring is allowed.
- If a protected file must change, explain why in the plan.
- Keep protected-file diffs minimal.
```

---

## 3. NON-NEGOTIABLE DOCUMENTATION POLICY

Documentation is part of the implementation.

For every change, check whether documentation must be updated.

Update documentation in the same change when modifying:

```text
- CLI commands or flags
- output files
- dataset schemas
- manifest formats
- state file formats
- media behavior
- discussion behavior
- incremental behavior
- force/no-new-work behavior
- architecture boundaries
- developer workflow
- testing commands
- stage status
- known limitations
```

A stage is not complete until documentation and reports match implemented behavior.

Do not leave code behavior ahead of documentation.

Do not claim completion if required documentation is stale, missing, or still describes old behavior.

---

## 4. REQUIRED PRE-TASK WORKFLOW

Before editing:

```text
1. Read AGENTS.md.
2. Read this active stage file completely.
3. Read only docs referenced by this stage.
4. Inspect relevant current code/docs.
5. Write a short plan.
6. Implement only this stage scope.
```

After editing:

```text
1. Run focused tests.
2. Run required verification commands.
3. Update docs if needed.
4. Create the required stage report.
5. Stop at the current stage boundary unless instructed otherwise.
```

---

## 5. PURPOSE OF THIS STAGE

Stage 3E.2 locks export-channel dataset schemas with explicit contract tests.

Goal:

```text
Prevent accidental changes to JSONL/manifest/state schemas as the project grows.
```

This is a test/documentation hardening stage.

---

## 6. SCOPE

Allowed:

```text
- add schema contract tests
- add representative fixtures/snapshots if appropriate
- document dataset schema contracts
- update docs that describe dataset fields
- add helper assertions for JSONL/state/manifest shape
```

Forbidden:

```text
- changing dataset schemas unless tests reveal docs mismatch and current behavior must be documented
- changing output filenames
- changing CLI behavior
- changing state behavior
- changing SQLite schema
- adding analytics
- broad refactor
```

If current implementation and docs disagree:

```text
- prefer documenting current behavior
- do not silently change behavior unless active task explicitly permits it
```

---

## 7. TARGET DATASET CONTRACTS

Lock schemas for:

```text
messages.jsonl
media_manifest.jsonl
discussion_comments.jsonl
discussion_threads.jsonl
manifest.json
channel_export_state.json
discussion_export_state.json
```

Also verify optional/conditional files:

```text
messages.txt
discussion_comments.txt
media/
```

TXT files do not need strict full snapshot testing unless current project already uses snapshots. Basic content smoke checks are enough.

---

## 8. TASKS

### A. Inspect current renderers and models

Inspect:

```text
tg_msg_manager/services/channel_export/models.py
tg_msg_manager/services/channel_export/jsonl_renderer.py
tg_msg_manager/services/channel_export/media_manifest_writer.py
tg_msg_manager/services/channel_export/manifest_writer.py
tg_msg_manager/services/channel_export/state_manager.py
tg_msg_manager/services/channel_export/discussions/models.py
tg_msg_manager/services/channel_export/discussions/jsonl_renderer.py
tg_msg_manager/services/channel_export/discussions/payload_writer.py
tg_msg_manager/services/channel_export/discussions/state_manager.py
```

Record actual fields.

### B. Create schema documentation

Create or update:

```text
docs/architecture/DATASET_FORMAT.md
```

Required sections:

```text
# Dataset Format

## 1. Overview
## 2. messages.jsonl
## 3. media_manifest.jsonl
## 4. discussion_comments.jsonl
## 5. discussion_threads.jsonl
## 6. manifest.json
## 7. channel_export_state.json
## 8. discussion_export_state.json
## 9. TXT projections
## 10. Compatibility rules
## 11. Schema change policy
```

Schema change policy must state:

```text
Any dataset schema change requires:
- explicit active stage scope
- tests
- docs update
- changelog/update note if public behavior changes
```

### C. Add schema assertion helpers

Create focused test helper if useful:

```text
tests/helpers/test_dataset_contracts.py
```

or existing test utilities path.

Possible helpers:

```text
assert_exact_keys(record, expected_keys)
assert_required_keys(record, required_keys)
assert_jsonl_records(path)
assert_iso_datetime_or_none(value)
assert_manifest_contract(manifest)
```

Do not over-engineer.

### D. Contract tests for messages.jsonl

Add tests verifying:

- [ ] required top-level keys
- [ ] stable key names
- [ ] message_id type
- [ ] channel_id type
- [ ] timestamp format
- [ ] text nullable behavior
- [ ] media field shape
- [ ] reactions/forwards/raw_payload shape if present
- [ ] no unexpected accidental key drift unless intentionally allowed

### E. Contract tests for media_manifest.jsonl

Verify statuses:

```text
metadata_only
downloaded
already_exists
skipped_by_size
skipped_by_type
failed
```

Tests:

- [ ] all statuses valid
- [ ] downloaded has path/sha256 where expected
- [ ] already_exists has path/sha256 where expected
- [ ] skipped_by_size has reason/size where expected
- [ ] skipped_by_type has reason/type where expected
- [ ] failed has error
- [ ] no final `pending` in committed manifest

### F. Contract tests for discussion_comments.jsonl

Verify fields:

- [ ] message_id
- [ ] discussion_chat_id
- [ ] channel_id
- [ ] channel_message_id
- [ ] discussion_root_message_id
- [ ] author_id
- [ ] author_name
- [ ] username
- [ ] timestamp
- [ ] text
- [ ] reply_to_id
- [ ] media
- [ ] reactions
- [ ] raw_payload

Verify:

- [ ] no full media download fields are required
- [ ] reply tree is not reconstructed
- [ ] `reply_to_id` is preserved

### G. Contract tests for discussion_threads.jsonl

Verify statuses:

```text
not_available
not_linked
no_comments
exported
partial
failed
```

Verify fields:

- [ ] channel_id
- [ ] channel_username
- [ ] channel_message_id
- [ ] discussion_chat_id
- [ ] discussion_root_message_id
- [ ] comments_count
- [ ] exported_comments_count
- [ ] status
- [ ] error

### H. Contract tests for manifest.json

Verify:

- [ ] channel fields
- [ ] message_count/media_count
- [ ] media summary
- [ ] discussion block
- [ ] included_files
- [ ] status
- [ ] max_media_size/media_types behavior
- [ ] `--discussion none` manifest shape
- [ ] `--discussion full` manifest shape

### I. Contract tests for state files

Verify `channel_export_state.json`:

- [ ] schema_version
- [ ] channel identity fields
- [ ] message/media counters
- [ ] last_exported_message_id
- [ ] run status
- [ ] updated_at/last_run_at fields if present

Verify `discussion_export_state.json`:

- [ ] schema_version
- [ ] channel_id
- [ ] discussion_chat_id
- [ ] thread_count_total
- [ ] comment_count_total
- [ ] failed_thread_count_total
- [ ] last_run_status
- [ ] updated_at

### J. Snapshot strategy

Use one of:

```text
- exact key-set tests
- lightweight inline expected dicts
- fixture snapshots
```

Avoid brittle tests for non-contract fields like ordering of unrelated docs.

Do not introduce heavy snapshot tooling unless already used.

### K. Docs and changelog

Update:

```text
docs/architecture/DATASET_FORMAT.md
docs/development/TESTING.md
README.md or COMMANDS.md only if current docs are stale
CHANGELOG.md if project convention requires
```

### L. Report

Create:

```text
docs/stages/reports/STAGE_3E_2_DATASET_SCHEMA_CONTRACT_TESTS_REPORT.md
```

Required sections:

```text
# Stage 3E.2 — Dataset Schema Contract Tests Report

## 1. Summary
## 2. Schemas covered
## 3. Tests added
## 4. Docs updated
## 5. Compatibility policy
## 6. Verification results
## 7. Runtime behavior statement
## 8. Remaining limitations
## 9. Status
```

Must state:

```text
No intended runtime behavior change.
No CLI behavior change.
No SQLite schema change.
No product feature added.
```

---

## 9. VERIFICATION

Run:

```bash
pytest tests/test_channel_export_*.py
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
```

If practical:

```bash
make test
make verify
```

---

## 10. COMPLETION CRITERIA

Complete only if:

- [ ] dataset schema docs exist/updated
- [ ] messages schema contract tested
- [ ] media manifest contract tested
- [ ] discussion comments contract tested
- [ ] discussion threads contract tested
- [ ] manifest contract tested
- [ ] state files contract tested
- [ ] tests pass or failures documented
- [ ] report created
- [ ] no behavior change unless explicitly documented
- [ ] no SQLite change

---

## 11. FINAL CLEANUP

After this stage is complete and report exists:

- [ ] Move this task file from `docs/stages/active/` to `docs/stages/completed/`.
- [ ] Update `docs/stages/README.md`.
- [ ] Ensure `docs/stages/active/` contains only unfinished or next active work.

---

## 12. FINAL RESPONSE FORMAT

```text
## Summary
- dataset schema contracts added
- docs updated

## Files changed
- path
- path

## Verification
- command: result

## Behavior
- runtime unchanged unless stated
- CLI unchanged
- SQLite unchanged

## Stage status
Stage 3E.2: complete / partial / blocked
```
