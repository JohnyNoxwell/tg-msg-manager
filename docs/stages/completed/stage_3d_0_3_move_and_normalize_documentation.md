# STAGE 3D.0.3 — MOVE AND NORMALIZE DOCUMENTATION

Status: completed
Stage: 3D.0
Scope: documentation migration task

## 0. CODEX ENTRY PROMPT

```text
Read AGENTS.md first.

You are working on tg-msg-manager.

This task is part of Stage 3D.0 — Project Governance / Documentation Reorganization / Agent Rules Hardening.

Follow this file exactly.

This is a documentation/governance stage, not a feature stage.
Do not change runtime behavior.
Do not implement new product functionality.
Do not start the next functional roadmap stage.
```

---

## 1. GLOBAL PURPOSE

Stage 3D.0 exists to make the repository self-governing for future agent work.

Goal:

```text
The repository should clearly tell a coding agent:
- what the project is
- where documentation lives
- which docs are current
- which docs are archived
- what rules are mandatory
- what files are protected
- how to pick relevant docs without loading the whole docs tree
- how to execute stages safely
```

This stage must make future prompts shorter and safer.

---

## 2. HARD PROHIBITIONS

Do not implement:

```text
- new Telegram features
- Stage 3C follow-up features
- Stage 3D product features
- analytics
- OSINT interpretation
- sentiment analysis
- bot detection
- user profiling
- narrative classification
- OCR
- speech-to-text
- image/video/audio analysis
- SQLite schema changes
- migrations
- DB persistence for channel posts or discussions
- GUI/dashboard/SaaS features
```

Do not change behavior of:

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

Do not add feature logic to protected files:

```text
tg_msg_manager/services/export/service.py
tg_msg_manager/services/db_export/service.py
tg_msg_manager/services/private_archive/service.py
tg_msg_manager/services/context/engine.py
tg_msg_manager/services/channel_export/service.py
```

This stage is docs/governance only unless a tiny mechanical import/path fix is required by a documentation move. If any code change seems necessary, document why before editing.

---

## 3. REQUIRED EXECUTION RULES

Before editing:

```text
1. Read AGENTS.md.
2. Inspect current docs layout.
3. Inspect README.md, COMMANDS.md, CHANGELOG.md.
4. Inspect docs/architecture/, docs/development/, docs/stages/, and docs/archive/ if present.
5. Write a short plan before editing.
```

During editing:

```text
- preserve information
- do not delete historical docs unless explicitly superseded and safely archived
- prefer moving docs over rewriting them
- add clear status headers to stage/task docs where useful
- do not create broken links
- do not update AGENTS.md until target docs paths are stable
```

After editing:

```text
- verify no runtime behavior changed
- verify docs navigation works
- create/update the stage report requested by the task
```

---

---

## 3A. NON-NEGOTIABLE DOCUMENTATION POLICY

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

Relevant documentation may include:

```text
README.md
COMMANDS.md
CHANGELOG.md
docs/README.md
docs/architecture/
docs/development/
docs/stages/active/
docs/stages/completed/
docs/stages/reports/
docs/development/LIVE_SMOKE_CHECKLIST.md or docs/development/TESTING.md
```

A stage is not complete until documentation and reports match the implemented behavior.

Do not leave code behavior ahead of documentation.

Do not claim completion if required documentation is stale, missing, or still describes old behavior.

For docs-only governance stages, update navigation and reports in the same change.

---

## 4. TARGET HIGH-LEVEL STRUCTURE

The final target structure should be close to:

```text
docs/
  README.md

  architecture/
    README.md
    ARCHITECTURE.md
    CHANNEL_EXPORT_ARCHITECTURE.md
    DATASET_FORMAT.md
    STATE_AND_INCREMENTAL_MODEL.md
    MEDIA_HANDLING.md
    DISCUSSION_EXPORT.md

  development/
    README.md
    DEVELOPMENT_RULES.md
    TESTING.md
    CLI_CONTRACTS.md
    AGENT_WORKFLOW.md
    DOCUMENTATION_RULES.md

  stages/
    README.md
    active/
    completed/
    reports/

  roadmap/
    README.md
    ROADMAP.md
    NEXT_STEPS.md
    BACKLOG.md
    DEFERRED.md

  archive/
    README.md
    legacy_notes/
    old_prompts/
    deprecated_stage_files/
```

Do not force this exact structure if the current repo already has a compatible structure. Preserve useful existing conventions where reasonable.

---

## 5. STAGE 3D.0 SPLIT

Stage 3D.0 is split into these sub-stages:

```text
3D.0.1 — Documentation Audit
3D.0.2 — Target Structure and Migration Plan
3D.0.3 — Move and Normalize Documentation
3D.0.4 — Documentation Indexes and Navigation
3D.0.5 — AGENTS.md Rewrite
3D.0.6 — Root README / COMMANDS / CHANGELOG Alignment
3D.0.7 — Verification and Governance Report
```

Execute only the current file scope.

---


## 6. PURPOSE OF THIS SUB-STAGE

Execute the migration plan from Stage 3D.0.2.

This stage moves and normalizes documentation files.

Do not rewrite `AGENTS.md` yet.

Do not create full index/navigation docs yet beyond minimal placeholders if required.

---

## 7. INPUT

Read:

```text
docs/stages/reports/STAGE_3D_0_1_DOCUMENTATION_AUDIT.md
docs/stages/reports/STAGE_3D_0_2_TARGET_DOCS_STRUCTURE_PLAN.md
```

If either is missing, stop and report.

---

## 8. ALLOWED ACTIONS

Allowed:

```text
- create target docs directories
- move stage task files
- move stage reports
- move roadmap/backlog docs
- move architecture docs
- move development/testing docs
- move deprecated docs into archive
- add status headers to moved stage files
- add short archive notices where useful
- preserve file contents
```

Forbidden:

```text
- deleting historical docs without archiving
- rewriting AGENTS.md
- changing runtime code
- changing CLI behavior
- changing tests except docs path expectations if they exist
- editing documentation content beyond status/path normalization
```

---

## 9. DIRECTORY CREATION TASKS

Create if missing:

- [ ] `docs/architecture/`
- [ ] `docs/development/`
- [ ] `docs/stages/`
- [ ] `docs/stages/active/`
- [ ] `docs/stages/completed/`
- [ ] `docs/stages/reports/`
- [ ] `docs/roadmap/`
- [ ] `docs/archive/`
- [ ] `docs/archive/legacy_notes/`
- [ ] `docs/archive/old_prompts/`
- [ ] `docs/archive/deprecated_stage_files/`

Do not create unused directories if the plan explicitly says not to.

---

## 10. FILE MOVEMENT TASKS

Follow the migration map exactly.

### A. Stage task files

- [ ] Move completed stage task files to `docs/stages/completed/`.
- [ ] Move active task files to `docs/stages/active/`.
- [ ] Move deprecated stage task files to `docs/archive/deprecated_stage_files/`.
- [ ] Preserve filenames unless the migration plan explicitly renames them.
- [ ] Add a short status header if missing:
  ```text
  Status: completed
  Stage: <stage>
  Scope: <scope>
  ```

### B. Stage reports

- [ ] Move stage completion reports to `docs/stages/reports/`.
- [ ] Preserve report contents.
- [ ] Preserve chronological meaning.
- [ ] Do not merge reports in this stage.

### C. Architecture docs

- [ ] Move stable architecture docs to `docs/architecture/`.
- [ ] Preserve content.
- [ ] Do not combine architecture docs yet unless plan requires it.

### D. Development docs

- [ ] Move testing docs to `docs/development/` unless they are smoke-specific under existing accepted location.
- [ ] Move agent workflow/development rules to `docs/development/`.
- [ ] Move CLI contract docs to `docs/development/` or preserve root `COMMANDS.md` as planned.

### E. Roadmap/backlog docs

- [ ] Move roadmap docs to `docs/roadmap/`.
- [ ] Move backlog/deferred docs to `docs/roadmap/`.
- [ ] Keep active stage tasks out of roadmap.

### F. Archive

- [ ] Move old prompts to `docs/archive/old_prompts/`.
- [ ] Move superseded notes to `docs/archive/legacy_notes/`.
- [ ] Move deprecated stage docs to `docs/archive/deprecated_stage_files/`.
- [ ] Add archive README later in Stage 3D.0.4, not necessarily now.

---

## 11. NORMALIZATION TASKS

For moved stage files:

- [ ] Add status header if missing.
- [ ] Ensure first lines make status clear:
  - [ ] active
  - [ ] completed
  - [ ] archived
- [ ] Do not rewrite the whole file.
- [ ] Do not change instructions in completed files except to mark them completed.
- [ ] Do not alter factual reports.

For archived files:

- [ ] Add short notice if useful:
  ```text
  Archived: this file is preserved for history and should not be used as current instructions unless explicitly referenced.
  ```

---

## 12. PATH REFERENCE HANDLING

During moves:

- [ ] Record old path -> new path.
- [ ] Do not update all links yet unless trivial.
- [ ] Create a path-change list for Stage 3D.0.4 and 3D.0.6.
- [ ] Avoid broken internal references where easy.
- [ ] Do not mass-edit archived files.

---

## 13. REPORT

Create:

```text
docs/stages/reports/STAGE_3D_0_3_DOCS_MIGRATION_REPORT.md
```

Required sections:

```text
# Stage 3D.0.3 — Docs Migration Report

## 1. Summary
## 2. Directories created
## 3. Files moved
## 4. Files archived
## 5. Files left in place
## 6. Status headers added
## 7. Known path references still needing update
## 8. Runtime behavior statement
## 9. Next sub-stage recommendation
```

Files moved table:

```text
| Old path | New path | Reason |
```

---

## 14. VERIFICATION

Run:

```bash
find docs -type f | sort
git status --short
```

If no code changed, tests are optional.

If any code changed accidentally, stop and revert or explain.

Recommended:

```bash
python3 -m compileall tg_msg_manager
```

only if code files were touched.

---

## 15. COMPLETION CRITERIA

Complete only if:

- [ ] Target directories exist.
- [ ] Planned files moved.
- [ ] Stage task files sorted.
- [ ] Reports sorted.
- [ ] Archive candidates archived.
- [ ] Status headers added where useful.
- [ ] Migration report created.
- [ ] AGENTS.md not rewritten.
- [ ] Runtime code not changed.
- [ ] Existing project behavior unchanged.

---

## 16. FINAL RESPONSE FORMAT

```text
## Summary
- docs moved and normalized
- archive created
- no runtime changes

## Files changed
- path
- path

## Moved
- old -> new

## Tests
- command/result or not run; docs-only

## Stage status
Stage 3D.0.3: complete / partial / blocked
```
