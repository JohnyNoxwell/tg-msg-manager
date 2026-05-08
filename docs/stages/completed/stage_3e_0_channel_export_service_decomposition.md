# STAGE 3E.0 — CHANNEL EXPORT SERVICE DECOMPOSITION

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

Stage 3E.0 reduces future scaling risk by decomposing `ChannelExportService` without changing behavior.

Primary goal:

```text
Make ChannelExportService thinner while preserving public CLI behavior, dataset outputs, state behavior, manifest behavior, media behavior, and discussion behavior.
```

This is a refactor-only stage.

---

## 6. SCOPE

Allowed:

```text
- extract orchestration helpers from ChannelExportService into focused modules
- move result-building logic to a result builder
- move included-files construction to a focused builder
- move manifest construction coordination to a manifest coordinator/builder wrapper
- move no-new-posts handling to a focused handler if useful
- move run mode branching helpers if useful
- add tests preserving current behavior
- update architecture docs
- create Stage 3E.0 report
```

Forbidden:

```text
- new export-channel flags
- changed command defaults
- changed output filenames
- changed dataset schemas
- changed state schemas
- changed manifest fields
- changed media behavior
- changed discussion behavior
- changed incremental/force/no-new-posts behavior
- SQLite schema changes
- DB persistence changes
- broad project-wide refactor
```

---

## 7. CURRENT RISK

`ChannelExportService` currently owns too many orchestration details:

```text
- option normalization
- full run orchestration
- incremental run orchestration
- no-new-posts path
- media preparation delegation
- discussion export delegation
- manifest building
- state saving order
- result building
- included files calculation
```

It should remain the public service facade, but should delegate more internal construction and coordination.

---

## 8. TARGET DESIGN

Preferred new focused modules under:

```text
tg_msg_manager/services/channel_export/
```

Suggested modules:

```text
result_builder.py
included_files_builder.py
manifest_coordinator.py
no_new_posts_handler.py
run_context.py
```

Only create modules that are actually useful. Do not over-engineer.

Expected responsibilities:

### `included_files_builder.py`

```text
Build tuple/list of dataset files included in manifest/result context.
Know about include_jsonl/include_txt/media_mode/discussion result.
No filesystem writes.
No service calls.
```

### `result_builder.py`

```text
Build ChannelExportResult from channel, plan, options, run_mode, state, stats, discussion_result.
No side effects except optionally preparing event payload data if existing design requires it.
No filesystem writes.
```

### `manifest_coordinator.py`

```text
Build manifest dictionary by wrapping existing build_manifest and discussion manifest logic.
No filesystem writes unless explicitly named writer is already responsible.
Prefer pure build function/coordinator.
```

### `no_new_posts_handler.py`

```text
Handle incremental no-new-posts branch if extraction reduces service complexity.
Must preserve:
- no discussion resolver
- no discussion fetch
- no discussion state mutation
- manifest behavior
- event emission
- result shape
```

### `run_context.py`

Optional.

```text
Small dataclass for entity/channel_identity/plan/state/run_mode if it simplifies signatures.
Do not introduce framework complexity.
```

---

## 9. TASKS

### A. Baseline inspection

- [ ] Read `AGENTS.md`.
- [ ] Read channel export architecture docs.
- [ ] Inspect `tg_msg_manager/services/channel_export/service.py`.
- [ ] Inspect existing channel export modules.
- [ ] Inspect Stage 3C report.
- [ ] Inspect channel export tests.
- [ ] Identify behavior that must not change.

### B. Baseline tests

Before refactor, run focused tests if possible:

```bash
pytest tests/test_channel_export_*.py
```

If not possible, document why.

### C. Extract included files builder

- [ ] Create `tg_msg_manager/services/channel_export/included_files_builder.py`.
- [ ] Move `_included_files` logic out of `ChannelExportService`.
- [ ] Preserve exact output ordering.
- [ ] Preserve media inclusion behavior.
- [ ] Preserve discussion file inclusion behavior.
- [ ] Add focused tests for:
  - [ ] metadata mode
  - [ ] full media mode
  - [ ] include_jsonl false
  - [ ] include_txt false
  - [ ] discussion_result none
  - [ ] discussion_result with comments/threads/state paths

### D. Extract result builder

- [ ] Create `tg_msg_manager/services/channel_export/result_builder.py`.
- [ ] Move `_build_result` construction logic out of `ChannelExportService`.
- [ ] Preserve all `ChannelExportResult` fields.
- [ ] Decide whether event emission remains in service or is a separate explicit call.
- [ ] Prefer keeping event emission in service or a small coordinator, not hidden inside pure builder.
- [ ] Add tests comparing result fields with previous expected values.

### E. Extract manifest coordinator

- [ ] Create `tg_msg_manager/services/channel_export/manifest_coordinator.py`.
- [ ] Move `_build_manifest` logic out of `ChannelExportService`.
- [ ] Preserve all manifest fields.
- [ ] Preserve discussion manifest block.
- [ ] Preserve media summary fields.
- [ ] Add tests for:
  - [ ] no discussion
  - [ ] discussion full result
  - [ ] media metadata
  - [ ] media full with size/type options

### F. Evaluate no-new-posts extraction

Only extract if it reduces complexity cleanly.

If extracting:

- [ ] Create `no_new_posts_handler.py`.
- [ ] Preserve no-new-posts behavior exactly.
- [ ] Ensure discussion resolver is not called.
- [ ] Ensure discussion state is not mutated.
- [ ] Ensure manifest writing behavior is preserved.
- [ ] Ensure event emission is preserved.
- [ ] Add or update tests.

If not extracting:

- [ ] Document why in Stage 3E.0 report.

### G. Keep ChannelExportService as facade

After extraction, `ChannelExportService` should mostly:

```text
- normalize options
- resolve source
- build plan
- load/determine state/run mode
- call full/incremental runner methods
- delegate media/discussion/result/manifest helpers
- emit high-level events
```

Do not make it a god object again.

### H. Preserve tests

Update existing tests only for import/path changes.

Do not weaken tests.

Do not delete coverage.

Add tests where extracted builders are introduced.

### I. Docs

Update relevant docs if architecture changed:

```text
docs/architecture/CHANNEL_EXPORT_ARCHITECTURE.md
docs/architecture/ARCHITECTURE.md
docs/development/AGENT_WORKFLOW.md
docs/stages/reports/
```

If files have different names, use actual repo docs.

Docs must state:

```text
ChannelExportService is orchestration-only.
Result/manifest/included-files construction is delegated to focused modules.
No behavior change intended.
```

### J. Report

Create:

```text
docs/stages/reports/STAGE_3E_0_CHANNEL_EXPORT_SERVICE_DECOMPOSITION_REPORT.md
```

Required sections:

```text
# Stage 3E.0 — Channel Export Service Decomposition Report

## 1. Summary
## 2. Refactor scope
## 3. Modules added
## 4. ChannelExportService responsibilities after refactor
## 5. Behavior preserved
## 6. Tests added/updated
## 7. Verification results
## 8. Runtime behavior statement
## 9. Remaining risks
## 10. Status
```

Must state:

```text
No public CLI behavior changed.
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

Do not claim unrun commands passed.

---

## 11. COMPLETION CRITERIA

Complete only if:

- [ ] ChannelExportService is thinner.
- [ ] New helper modules are focused.
- [ ] Behavior is preserved.
- [ ] Tests pass or failures are documented.
- [ ] Docs updated if architecture docs exist.
- [ ] Stage report created.
- [ ] No CLI behavior changed.
- [ ] No dataset schema changed.
- [ ] No state schema changed.
- [ ] No SQLite schema changed.
- [ ] No feature added.

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
- ChannelExportService decomposition completed
- behavior preserved

## Files changed
- path
- path

## Verification
- command: result

## Behavior
- CLI unchanged
- dataset schema unchanged
- state schema unchanged
- SQLite unchanged

## Stage status
Stage 3E.0: complete / partial / blocked
```
