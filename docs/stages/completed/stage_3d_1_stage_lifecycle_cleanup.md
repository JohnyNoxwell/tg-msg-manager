# STAGE 3D.1 — STAGE LIFECYCLE CLEANUP

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

Stage 3D.1 fixes the stage documentation lifecycle after Stage 3D.0.

This is docs/governance cleanup only.

Goal:

```text
docs/stages/active/ contains only unfinished or next active work.
completed task files live under docs/stages/completed/.
stage reports live under docs/stages/reports/.
general launch prompts live under docs/archive/old_prompts/.
AGENTS.md requires this cleanup for future stages.
```

---

## 6. SCOPE

Allowed:

```text
- verify Stage 3D.0 final report exists
- verify Stage 3D.0 sub-stage reports exist
- move completed Stage 3D.0 task files out of docs/stages/active/
- move Stage 3D.0 general launch prompt to archive/old_prompts/
- update docs/stages/README.md
- update AGENTS.md stage lifecycle policy
- update docs/development/AGENT_WORKFLOW.md if present
- create Stage 3D.1 report
```

Forbidden:

```text
- runtime code changes
- CLI behavior changes
- test behavior changes
- channel export refactor
- dataset write changes
- schema changes
- starting Stage 3E.0
```

---

## 7. REQUIRED INPUTS

Inspect:

```text
AGENTS.md
docs/README.md
docs/stages/README.md
docs/stages/active/
docs/stages/completed/
docs/stages/reports/
docs/archive/
docs/development/AGENT_WORKFLOW.md
```

If `docs/development/AGENT_WORKFLOW.md` does not exist, do not create a large new file unless docs structure expects it. Prefer updating `AGENTS.md` and `docs/stages/README.md`.

---

## 8. TASKS

### A. Verify Stage 3D.0 completion

- [ ] Check whether final report exists:
  ```text
  docs/stages/reports/STAGE_3D_0_PROJECT_GOVERNANCE_DOCS_REORGANIZATION_REPORT.md
  ```
- [ ] Check whether Stage 3D.0 sub-stage reports exist.
- [ ] Confirm Stage 3D.0 task files are complete.
- [ ] If final report is missing, stop and report blocker.
- [ ] If sub-stage reports are missing but final report confirms completion, record this in Stage 3D.1 report.

### B. Inventory active stage files

List files under:

```text
docs/stages/active/
```

Classify each:

- [ ] Stage 3D.0 completed task
- [ ] Stage 3D.0 general prompt
- [ ] current active work
- [ ] unknown
- [ ] should remain active

Do not move unknown files without a reason.

### C. Move completed Stage 3D.0 task files

Move these if present:

```text
stage_3d_0_1_documentation_audit.md
stage_3d_0_2_target_structure_and_migration_plan.md
stage_3d_0_3_move_and_normalize_documentation.md
stage_3d_0_4_documentation_indexes_and_navigation.md
stage_3d_0_5_agents_md_rewrite.md
stage_3d_0_6_root_readme_commands_changelog_alignment.md
stage_3d_0_7_verification_and_governance_report.md
```

Target:

```text
docs/stages/completed/
```

Rules:

- [ ] Preserve filenames.
- [ ] Preserve content.
- [ ] Add or preserve status header if present.
- [ ] Do not move incomplete or unrelated task files.

### D. Move general prompt

Move if present:

```text
stage_3d_0_general_prompt.md
```

Preferred target:

```text
docs/archive/old_prompts/
```

Reason:

```text
This is a launch prompt, not an executable completed stage task.
```

If repository policy says general prompts belong elsewhere, follow repo policy and document why.

### E. Update AGENTS.md lifecycle policy

Add or strengthen:

```text
## Stage lifecycle policy

Stage task files have a lifecycle:

1. active — executable task files currently being worked on
2. completed — finished task files preserved for history
3. reports — factual completion reports
4. archive — deprecated, superseded, or old prompt files

Rules:

- Only currently executable task files may live in docs/stages/active/.
- When a stage is fully completed and its final report exists, move its task files from docs/stages/active/ to docs/stages/completed/.
- Do not leave completed stage files in docs/stages/active/.
- Do not move unfinished or partially completed stage files to completed/.
- Move general launch prompts to docs/archive/old_prompts/ unless the active task says otherwise.
- Stage reports must live in docs/stages/reports/.
- Archived files must not be treated as current instructions.
```

Add completion checklist:

```text
Before marking a stage complete:

- [ ] Required implementation/docs work is done.
- [ ] Required tests/checks were run or inability was documented.
- [ ] Required stage report exists under docs/stages/reports/.
- [ ] Relevant README/COMMANDS/CHANGELOG/docs were updated if behavior changed.
- [ ] Completed task files were moved from docs/stages/active/ to docs/stages/completed/.
- [ ] Launch/general prompts were moved to docs/archive/old_prompts/.
- [ ] docs/stages/README.md was updated.
- [ ] docs/stages/active/ contains only unfinished or next active work.
```

### F. Update docs/stages/README.md

Ensure it says:

- [ ] `active/` contains only executable current stage tasks.
- [ ] `completed/` contains finished historical task files.
- [ ] `reports/` contains factual completion reports.
- [ ] general prompts should usually go to `docs/archive/old_prompts/`.
- [ ] Stage cleanup is mandatory before marking a stage complete.

Add Stage 3D.0 to completed list if such list exists.

### G. Update docs/development/AGENT_WORKFLOW.md if present

If present, add the same lifecycle cleanup rule in shorter form.

Do not duplicate excessive content.

### H. Create Stage 3D.1 report

Create:

```text
docs/stages/reports/STAGE_3D_1_STAGE_LIFECYCLE_CLEANUP_REPORT.md
```

Required sections:

```text
# Stage 3D.1 — Stage Lifecycle Cleanup Report

## 1. Summary
## 2. Stage 3D.0 completion verification
## 3. Files moved to completed
## 4. Files moved to archive
## 5. AGENTS.md lifecycle policy update
## 6. docs/stages/README.md update
## 7. Active directory status
## 8. Runtime behavior statement
## 9. Verification results
## 10. Remaining limitations
## 11. Status
```

Must state:

```text
No runtime code was changed.
No CLI behavior was changed.
No SQLite schema was changed.
No product feature was added.
```

---

## 9. VERIFICATION

Run:

```bash
find docs/stages/active -maxdepth 1 -type f | sort
find docs/stages/completed -maxdepth 1 -type f | sort
find docs/stages/reports -maxdepth 1 -type f | sort
find docs/archive/old_prompts -maxdepth 1 -type f | sort
git status --short
```

If no runtime code changed, do not run full test suite unless repo policy requires it.

Optional:

```bash
python3 -m compileall tg_msg_manager
```

only if code was touched accidentally or by necessity.

---

## 10. COMPLETION CRITERIA

Complete only if:

- [ ] Stage 3D.0 final report exists.
- [ ] Completed Stage 3D.0 task files moved to `docs/stages/completed/`.
- [ ] Stage 3D.0 general prompt moved to `docs/archive/old_prompts/` or justified elsewhere.
- [ ] AGENTS.md lifecycle policy updated.
- [ ] docs/stages/README.md updated.
- [ ] Stage 3D.1 report created.
- [ ] `docs/stages/active/` contains only unfinished or next active work.
- [ ] Runtime code unchanged.
- [ ] CLI behavior unchanged.
- [ ] SQLite schema unchanged.

---

## 11. FINAL RESPONSE FORMAT

```text
## Summary
- Stage lifecycle cleanup completed
- completed task files moved
- lifecycle policy made mandatory

## Files changed
- path
- path

## Verification
- command: result

## Behavior
- runtime unchanged
- CLI unchanged
- SQLite unchanged

## Stage status
Stage 3D.1: complete / partial / blocked
```
