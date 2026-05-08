# STAGE 3D.0.2 — TARGET STRUCTURE AND MIGRATION PLAN

Status: completed
Stage: 3D.0
Scope: documentation structure planning task

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

Use the Stage 3D.0.1 audit to create a concrete target documentation structure and migration plan.

Do not move files yet.

Do not rewrite `AGENTS.md` yet.

Expected output:

```text
docs/stages/reports/STAGE_3D_0_2_TARGET_DOCS_STRUCTURE_PLAN.md
```

---

## 7. INPUT

Read:

```text
docs/stages/reports/STAGE_3D_0_1_DOCUMENTATION_AUDIT.md
```

If missing, stop and report that Stage 3D.0.1 must be completed first.

---

## 8. TARGET STRUCTURE REQUIREMENTS

Design a final docs structure that supports:

```text
- agent onboarding
- architecture rules
- development rules
- active stage execution
- completed stage history
- stage reports
- roadmap/backlog
- archived/deprecated notes
```

Recommended structure:

```text
docs/
  README.md
  architecture/
  development/
  stages/
    active/
    completed/
    reports/
  roadmap/
  archive/
```

Do not create excessive nested folders unless audit proves they are necessary.

---

## 9. MIGRATION PLAN TASKS

### A. Confirm target directories

Define target directories:

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

### B. Map each existing doc

For every doc from the audit:

- [ ] choose final location
- [ ] choose action:
  - [ ] keep
  - [ ] move
  - [ ] copy then archive
  - [ ] merge later
  - [ ] update reference only
  - [ ] manual review
- [ ] explain why

### C. Define active/completed/report rules

Write rules:

```text
docs/stages/active/
  only currently executable stage task files

docs/stages/completed/
  completed task instruction files

docs/stages/reports/
  factual completion reports

docs/archive/
  old prompts, deprecated plans, superseded notes
```

### D. Define README/index files to create

Plan index files:

- [ ] `docs/README.md`
- [ ] `docs/architecture/README.md`
- [ ] `docs/development/README.md`
- [ ] `docs/stages/README.md`
- [ ] `docs/roadmap/README.md`
- [ ] `docs/archive/README.md`

### E. Define AGENTS.md rewrite target

Plan final `AGENTS.md` content, but do not rewrite it yet.

It should include:

- [ ] mandatory pre-task workflow
- [ ] protected files
- [ ] architecture rules
- [ ] docs map
- [ ] relevant-doc selection rule
- [ ] stage workflow
- [ ] testing policy
- [ ] documentation policy
- [ ] stop-and-report conflict rule

### F. Define path update strategy

Plan which files need path updates:

- [ ] root README
- [ ] COMMANDS.md
- [ ] CHANGELOG.md
- [ ] docs index files
- [ ] stage reports
- [ ] active stage files

Do not mass-edit old archived docs unless necessary.

---

## 10. WRITE PLAN FILE

Create:

```text
docs/stages/reports/STAGE_3D_0_2_TARGET_DOCS_STRUCTURE_PLAN.md
```

Required sections:

```text
# Stage 3D.0.2 — Target Docs Structure Plan

## 1. Summary
## 2. Target directory structure
## 3. Directory responsibility rules
## 4. File migration map
## 5. Index files to create
## 6. AGENTS.md rewrite plan
## 7. Link/reference update plan
## 8. Risks
## 9. Do-not-move list
## 10. Next sub-stage checklist
```

File migration map table:

```text
| Current path | Target path | Action | Reason |
```

---

## 11. VERIFICATION

No tests required unless code changed.

Run simple filesystem checks if useful.

---

## 12. COMPLETION CRITERIA

Complete only if:

- [ ] Plan file exists.
- [ ] It uses the audit as input.
- [ ] It defines final docs directories.
- [ ] It maps existing docs to targets.
- [ ] It defines index files.
- [ ] It defines AGENTS.md rewrite plan.
- [ ] It defines path update strategy.
- [ ] No files were moved yet.
- [ ] AGENTS.md was not rewritten.
- [ ] Runtime code was not changed.

---

## 13. FINAL RESPONSE FORMAT

```text
## Summary
- target docs structure planned
- migration map prepared
- no files moved

## Files changed
- docs/stages/reports/STAGE_3D_0_2_TARGET_DOCS_STRUCTURE_PLAN.md

## Tests
- not run; docs-plan only

## Stage status
Stage 3D.0.2: complete / partial / blocked
```
