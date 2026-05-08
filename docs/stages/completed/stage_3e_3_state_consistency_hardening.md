# STAGE 3E.3 — STATE CONSISTENCY HARDENING

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

Stage 3E.3 hardens state consistency after dataset write safety and schema contracts.

Goal:

```text
Make channel_export_state.json and discussion_export_state.json consistency rules explicit, tested, and resistant to partial failure paths.
```

This is reliability hardening.

---

## 6. SCOPE

Allowed:

```text
- clarify state lifecycle
- add state consistency validators/helpers
- add tests for state invariants
- add tests for failure paths
- document state consistency guarantees
- improve state manager guardrails without changing schema if possible
```

Forbidden:

```text
- SQLite schema changes
- state schema changes unless explicitly justified and documented
- CLI behavior changes
- dataset schema changes
- new export features
- analytics
- broad unrelated refactor
```

If a state schema change seems required, stop and report. Do not proceed without explicit approval.

---

## 7. STATE CONSISTENCY PRINCIPLES

Required principles:

```text
1. State is a committed checkpoint, not a write-ahead log.
2. State must only describe dataset contents that were successfully written and committed.
3. Manifest must correspond to the same committed run as state.
4. Discussion state must not advance if channel manifest/state commit failed.
5. No-new-posts run must not mutate discussion state.
6. Force run may rebuild state for the current forced dataset.
7. Incremental run may advance state only for newly committed posts.
8. Failed per-thread discussion records may be written as dataset facts, but state must reflect committed files only.
```

---

## 8. TASKS

### A. Inspect current state managers

Inspect:

```text
tg_msg_manager/services/channel_export/state_manager.py
tg_msg_manager/services/channel_export/discussions/state_manager.py
tg_msg_manager/services/channel_export/service.py
tg_msg_manager/services/channel_export/models.py
tg_msg_manager/services/channel_export/discussions/models.py
```

Record:

- [ ] state fields
- [ ] save order
- [ ] load behavior
- [ ] channel identity validation
- [ ] discussion state merge behavior
- [ ] no-new-posts behavior
- [ ] force behavior
- [ ] manifest failure behavior

### B. Create/update state architecture doc

Create or update:

```text
docs/architecture/STATE_AND_INCREMENTAL_MODEL.md
```

Required sections:

```text
# State and Incremental Model

## 1. Purpose
## 2. Channel state
## 3. Discussion state
## 4. Full/force run
## 5. Incremental run
## 6. No-new-posts run
## 7. Manifest/state ordering
## 8. Failure behavior
## 9. Consistency invariants
## 10. Non-goals
```

Must state:

```text
State files are not analytics.
State files are not source-of-truth message databases.
State files are export checkpoint metadata.
```

### C. Define invariants

Add tests or helper functions for invariants:

Channel state:

- [ ] channel_id matches resolved channel
- [ ] last_exported_message_id is not lower than previous after successful incremental run
- [ ] message_count_total does not decrease in incremental mode
- [ ] media counters do not become negative
- [ ] last_run_status reflects committed run
- [ ] state path is saved only after manifest success

Discussion state:

- [ ] channel_id matches channel state channel_id
- [ ] discussion_chat_id matches resolved discussion source when available
- [ ] thread_count_total does not decrease in incremental append mode
- [ ] comment_count_total does not decrease in incremental append mode
- [ ] failed_thread_count_total is non-negative
- [ ] no-new-posts does not mutate discussion state
- [ ] discussion state is not saved if channel manifest/state commit fails

### D. Add state consistency helpers

If useful, create:

```text
tg_msg_manager/services/channel_export/state_consistency.py
```

Possible functions:

```text
validate_channel_state_for_incremental(previous_state, new_state)
validate_discussion_state_for_incremental(previous_state, new_state)
validate_discussion_state_matches_channel(channel_state, discussion_state)
```

Rules:

- [ ] no filesystem writes
- [ ] no Telegram calls
- [ ] no CLI imports
- [ ] no schema changes
- [ ] used by tests or service only where valuable

If helpers are not necessary, implement tests directly and explain in report.

### E. Harden state managers

Only if needed:

- [ ] add validation for negative counters
- [ ] add channel identity validation where missing
- [ ] avoid silently accepting incompatible discussion state
- [ ] preserve backward compatibility with current state schema
- [ ] tests for invalid state

Do not make old valid states unreadable unless explicitly justified.

### F. Failure-path tests

Add/update tests for:

- [ ] payload write failure does not save channel state
- [ ] manifest write failure does not save channel state
- [ ] discussion payload failure does not save discussion state
- [ ] channel manifest failure does not save discussion state
- [ ] no-new-posts does not resolve/fetch/mutate discussion state
- [ ] incremental success advances both states consistently
- [ ] force success rebuilds state consistently
- [ ] invalid channel state for wrong channel is rejected
- [ ] invalid discussion state mismatch is rejected or safely ignored, according to chosen contract

### G. Docs

Update:

```text
docs/architecture/STATE_AND_INCREMENTAL_MODEL.md
docs/architecture/DATASET_WRITE_SAFETY.md
README.md or COMMANDS.md if known limitations changed
```

If Stage 3E.1 already improved atomic write behavior, reflect that here.

### H. Report

Create:

```text
docs/stages/reports/STAGE_3E_3_STATE_CONSISTENCY_HARDENING_REPORT.md
```

Required sections:

```text
# Stage 3E.3 — State Consistency Hardening Report

## 1. Summary
## 2. State invariants
## 3. Channel state behavior
## 4. Discussion state behavior
## 5. Failure-path coverage
## 6. Docs updated
## 7. Verification results
## 8. Runtime behavior statement
## 9. Remaining limitations
## 10. Status
```

Must state:

```text
No CLI behavior changed.
No dataset schema changed unless explicitly stated.
No state schema changed unless explicitly stated.
No SQLite schema changed.
No product feature was added.
```

---

## 9. VERIFICATION

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

## 10. COMPLETION CRITERIA

Complete only if:

- [ ] state model doc updated
- [ ] state invariants defined
- [ ] state consistency tested
- [ ] failure paths tested
- [ ] no-new-posts state behavior tested
- [ ] force/incremental state behavior tested
- [ ] report created
- [ ] no SQLite change
- [ ] no product feature added
- [ ] behavior changes, if any, documented

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
- state consistency hardened
- invariants tested

## Files changed
- path
- path

## Verification
- command: result

## Behavior
- CLI unchanged
- dataset schema unchanged unless stated
- state schema unchanged unless stated
- SQLite unchanged

## Stage status
Stage 3E.3: complete / partial / blocked
```
