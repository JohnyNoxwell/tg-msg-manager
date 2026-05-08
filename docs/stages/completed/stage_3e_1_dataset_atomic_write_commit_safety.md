# STAGE 3E.1 — DATASET ATOMIC WRITE / COMMIT SAFETY

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

Stage 3E.1 hardens dataset writing so export-channel is safer against partial writes.

Goal:

```text
Introduce an explicit dataset write/commit model that reduces risk of corrupted or partially advanced datasets when failures occur.
```

This stage is reliability hardening.

It must preserve public behavior and dataset schemas.

---

## 6. SCOPE

Allowed:

```text
- introduce temporary write sessions for channel dataset files
- introduce commit/rollback semantics for payload writers where safe
- ensure state is saved only after payload + manifest commit succeeds
- ensure manifest/state ordering is explicit and tested
- improve failure cleanup of temporary files
- add tests for writer failure and manifest failure
- document atomicity guarantees and limitations
```

Forbidden:

```text
- changing output filenames
- changing JSONL schemas
- changing TXT content format unless unavoidable and documented
- changing manifest schema
- changing state schema
- changing CLI flags/defaults
- adding SQLite persistence
- adding full transactional database layer
- adding analytics
- broad refactor unrelated to dataset writes
```

---

## 7. CURRENT RISK

Current known limitation:

```text
append-only incremental dataset can leave already appended payload files if a run fails mid-write
```

This stage should improve that where feasible.

Do not overclaim full ACID guarantees if filesystem behavior cannot guarantee it.

---

## 8. TARGET WRITE MODEL

Preferred conceptual model:

```text
prepare
write temp payloads
write temp manifests/state candidates
commit payloads
commit manifest
commit state last
cleanup temp files
```

For overwrite/full runs:

```text
write to temp files -> atomic replace final files
```

For append/incremental runs:

Preferred safe model:

```text
copy existing final file to temp
append new records to temp
atomic replace final file
```

Alternative if copying large files is not acceptable:

```text
document limitation and add stronger state safety only
```

But if using alternative, explain in report.

State rule:

```text
Never advance channel_export_state.json or discussion_export_state.json unless all required dataset payload and manifest writes have succeeded.
```

---

## 9. TASKS

### A. Inspect current writers

Inspect:

```text
tg_msg_manager/services/channel_export/payload_writer.py
tg_msg_manager/services/channel_export/media_manifest_writer.py
tg_msg_manager/services/channel_export/manifest_writer.py
tg_msg_manager/services/channel_export/state_manager.py
tg_msg_manager/services/channel_export/discussions/payload_writer.py
tg_msg_manager/services/channel_export/discussions/state_manager.py
tg_msg_manager/services/channel_export/service.py
```

Identify:

- [ ] where files are opened
- [ ] append vs overwrite behavior
- [ ] when stats are finalized
- [ ] when manifest is written
- [ ] when state is saved
- [ ] what happens on exceptions
- [ ] whether temp files already exist

### B. Define atomicity contract

Create/update architecture doc:

```text
docs/architecture/DATASET_WRITE_SAFETY.md
```

If file exists, update it.

Required sections:

```text
# Dataset Write Safety

## 1. Purpose
## 2. Write phases
## 3. Full/force run behavior
## 4. Incremental append behavior
## 5. Manifest/state ordering
## 6. Discussion dataset behavior
## 7. Guarantees
## 8. Non-guarantees
## 9. Failure behavior
```

Must be honest about limitations.

### C. Introduce temp file utilities

Create focused module if absent:

```text
tg_msg_manager/services/channel_export/atomic_writer.py
```

Possible contents:

```text
AtomicTextFile
AtomicJsonFile
atomic_replace
temp_path_for
cleanup_temp
```

Rules:

- [ ] keep it generic but not overbuilt
- [ ] no Telegram logic
- [ ] no state-specific logic
- [ ] no JSON schema knowledge
- [ ] use pathlib
- [ ] ensure temp files are in same directory as final file where possible
- [ ] use atomic replace/rename where supported by Python stdlib

### D. Harden full/overwrite payload writes

For overwrite mode:

- [ ] write `messages.jsonl` to temp then replace
- [ ] write `messages.txt` to temp then replace
- [ ] write `media_manifest.jsonl` to temp then replace if included
- [ ] write discussion files to temp then replace
- [ ] ensure temp files are cleaned on failure
- [ ] ensure final files are not replaced if temp write fails

### E. Harden incremental/append payload writes

For append mode, choose and implement one strategy:

Preferred:

- [ ] copy existing final file to temp
- [ ] append new records to temp
- [ ] replace final file only after session finishes
- [ ] if failure occurs, final file remains unchanged

If not implementing copy-append-replace:

- [ ] document why
- [ ] add tests for state-not-advanced on failure
- [ ] keep known limitation in docs

Do not silently keep old limitation without documenting it.

### F. Harden manifest write

- [ ] write manifest to temp JSON file
- [ ] replace final manifest only after JSON serialization succeeds
- [ ] if manifest write fails, state must not advance
- [ ] test manifest failure state safety

### G. Harden state save ordering

- [ ] channel state saved after payload and manifest commit
- [ ] discussion state saved after payload and manifest commit
- [ ] no state advance on payload failure
- [ ] no state advance on manifest failure
- [ ] ensure discussion state and channel state do not diverge after failed manifest write

### H. Failure cleanup

- [ ] temp files cleaned after success
- [ ] temp files cleaned or left with predictable suffix after failure
- [ ] document cleanup behavior
- [ ] tests should not leave temp files unless intentionally asserted

### I. Tests

Add/update tests for:

- [ ] full overwrite writes through temp and commits final files
- [ ] full overwrite failure does not replace existing final files
- [ ] incremental append success preserves existing rows and adds new rows
- [ ] incremental append failure does not partially append if implemented
- [ ] manifest failure prevents state save
- [ ] discussion payload failure prevents discussion state save
- [ ] channel payload failure prevents channel state save
- [ ] temp cleanup on success
- [ ] temp cleanup/failure behavior
- [ ] no schema changes to written JSONL fields

Do not weaken existing tests.

### J. Docs

Update:

```text
README.md
COMMANDS.md
docs/architecture/DATASET_WRITE_SAFETY.md
docs/architecture/STATE_AND_INCREMENTAL_MODEL.md
docs/stages/reports/
```

Only if relevant files exist. Use actual repo structure.

Known limitations must be updated if improved.

If append rollback remains partial, document it honestly.

### K. Report

Create:

```text
docs/stages/reports/STAGE_3E_1_DATASET_ATOMIC_WRITE_COMMIT_SAFETY_REPORT.md
```

Required sections:

```text
# Stage 3E.1 — Dataset Atomic Write / Commit Safety Report

## 1. Summary
## 2. Atomic write model
## 3. Files/modules changed
## 4. Full/force write behavior
## 5. Incremental append behavior
## 6. Manifest/state ordering
## 7. Discussion dataset behavior
## 8. Failure behavior
## 9. Guarantees
## 10. Remaining limitations
## 11. Tests
## 12. Verification results
## 13. Status
```

Must state:

```text
No CLI behavior changed.
No dataset schema changed.
No state schema changed.
No SQLite schema changed.
No product feature was added.
```

---

## 10. VERIFICATION

Run:

```bash
pytest tests/test_channel_export_*.py
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
python3 -m tg_msg_manager.cli export-channel --help
```

If practical:

```bash
make test
make verify
```

---

## 11. COMPLETION CRITERIA

Complete only if:

- [ ] write safety contract documented
- [ ] overwrite writes use temp/commit or equivalent safety
- [ ] incremental append safety improved or limitation clearly documented
- [ ] manifest write safety improved
- [ ] state save ordering tested
- [ ] discussion state ordering tested
- [ ] tests added/updated
- [ ] report created
- [ ] no CLI behavior changed
- [ ] no schema changed
- [ ] no SQLite changed

---

## 12. FINAL CLEANUP

After this stage is complete and report exists:

- [ ] Move this task file from `docs/stages/active/` to `docs/stages/completed/`.
- [ ] Update `docs/stages/README.md`.
- [ ] Ensure `docs/stages/active/` contains only unfinished or next active work.

---

## 13. FINAL RESPONSE FORMAT

```text
## Summary
- dataset write safety hardened
- state save ordering preserved/strengthened

## Files changed
- path
- path

## Verification
- command: result

## Guarantees
- item
- item

## Remaining limitations
- item
- item

## Behavior
- CLI unchanged
- dataset schema unchanged
- state schema unchanged
- SQLite unchanged

## Stage status
Stage 3E.1: complete / partial / blocked
```
