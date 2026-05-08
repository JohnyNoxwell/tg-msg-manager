# STAGE 3D.0.4 — DOCUMENTATION INDEXES AND NAVIGATION

Status: active
Stage: 3D.0
Scope: documentation index task

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

Create documentation index files and navigation after the docs tree has been reorganized.

Do not rewrite `AGENTS.md` yet.

Expected result:

```text
docs/README.md
docs/architecture/README.md
docs/development/README.md
docs/stages/README.md
docs/roadmap/README.md
docs/archive/README.md
```

---

## 7. INPUT

Read:

```text
docs/stages/reports/STAGE_3D_0_1_DOCUMENTATION_AUDIT.md
docs/stages/reports/STAGE_3D_0_2_TARGET_DOCS_STRUCTURE_PLAN.md
docs/stages/reports/STAGE_3D_0_3_DOCS_MIGRATION_REPORT.md
```

If migration report is missing, stop and report that Stage 3D.0.3 must be completed first.

---

## 8. INDEX DESIGN PRINCIPLES

Index files must be:

```text
- short
- navigational
- explicit about what is current
- explicit about what is archived
- useful for agents
- not a duplicate of all content
```

Do not copy full docs into index files.

Each index should answer:

```text
- what is in this folder
- what to read first
- what not to read by default
- which files are current
- which files are historical
```

---

## 9. CREATE DOCS ROOT INDEX

Create/update:

```text
docs/README.md
```

Required sections:

```text
# Documentation Index

## 1. How to use this documentation
## 2. For coding agents
## 3. Architecture docs
## 4. Development docs
## 5. Stages
## 6. Roadmap
## 7. Archive
## 8. Rule: do not read everything by default
```

Must include:

```text
Read AGENTS.md first.
Then read the active stage file.
Then read only referenced architecture/development docs.
Do not read archive unless explicitly asked.
```

---

## 10. CREATE ARCHITECTURE INDEX

Create/update:

```text
docs/architecture/README.md
```

Required sections:

```text
# Architecture Documentation

## Purpose
## Current architecture docs
## Channel export docs
## Dataset/state docs
## Media/discussion docs
## Rules for adding architecture docs
```

Must state:

```text
Architecture docs are stable references.
Stage task files should not replace architecture docs.
```

---

## 11. CREATE DEVELOPMENT INDEX

Create/update:

```text
docs/development/README.md
```

Required sections:

```text
# Development Documentation

## Purpose
## Development rules
## Testing
## CLI contracts
## Agent workflow
## Documentation rules
```

Must state:

```text
Development docs define how changes are made.
They do not define product roadmap by themselves.
```

---

## 12. CREATE STAGES INDEX

Create/update:

```text
docs/stages/README.md
```

Required sections:

```text
# Stage Documentation

## Active stages
## Completed stages
## Reports
## Stage lifecycle
## Rules for agents
```

Must define lifecycle:

```text
active -> completed -> report
```

Must state:

```text
Only files under docs/stages/active/ are executable current tasks.
Completed stage files are historical instructions.
Reports are factual completion records.
```

---

## 13. CREATE ROADMAP INDEX

Create/update:

```text
docs/roadmap/README.md
```

Required sections:

```text
# Roadmap Documentation

## Current roadmap
## Next steps
## Backlog
## Deferred
## Rules
```

Must state:

```text
Roadmap items are not implementation permission.
Implementation requires an active stage task.
```

---

## 14. CREATE ARCHIVE INDEX

Create/update:

```text
docs/archive/README.md
```

Required sections:

```text
# Archive

## Purpose
## What is archived here
## How agents should treat archived files
## Legacy notes
## Old prompts
## Deprecated stage files
```

Must state:

```text
Do not use archived files as current instructions unless the user explicitly asks.
```

---

## 15. LINK CHECK TASKS

- [ ] Ensure each index links to existing files only.
- [ ] Avoid links to files that do not exist.
- [ ] Avoid raw old paths from before migration.
- [ ] Do not over-link archived docs.
- [ ] Prefer relative links.

---

## 16. REPORT

Create:

```text
docs/stages/reports/STAGE_3D_0_4_DOCS_INDEXES_REPORT.md
```

Required sections:

```text
# Stage 3D.0.4 — Docs Indexes Report

## 1. Summary
## 2. Index files created
## 3. Navigation rules
## 4. Agent usage rules
## 5. Link checks
## 6. Remaining docs alignment work
```

---

## 17. VERIFICATION

Run:

```bash
find docs -name README.md -type f | sort
grep -R "docs/refactor" -n README.md COMMANDS.md docs || true
grep -R "not implemented yet" -n README.md COMMANDS.md docs || true
```

Do not mass-fix all results in this stage unless they are index-related. Record remaining issues for 3D.0.6.

---

## 18. COMPLETION CRITERIA

Complete only if:

- [ ] docs root index exists.
- [ ] architecture index exists.
- [ ] development index exists.
- [ ] stages index exists.
- [ ] roadmap index exists.
- [ ] archive index exists.
- [ ] indexes are navigational, not bloated.
- [ ] archive is clearly marked non-current.
- [ ] active stage rule is clear.
- [ ] report created.
- [ ] AGENTS.md not rewritten yet.
- [ ] runtime code unchanged.

---

## 19. FINAL RESPONSE FORMAT

```text
## Summary
- docs indexes created
- navigation rules added
- no runtime changes

## Files changed
- path
- path

## Tests/checks
- command/result

## Stage status
Stage 3D.0.4: complete / partial / blocked
```
