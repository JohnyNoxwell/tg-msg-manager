# STAGE 3D.0.1 — DOCUMENTATION AUDIT

Status: active
Stage: 3D.0
Scope: documentation audit task

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

Perform a documentation audit only.

Do not move files yet.

Do not rewrite `AGENTS.md` yet.

Do not reorganize the docs tree yet.

Expected output:

```text
docs/stages/reports/STAGE_3D_0_1_DOCUMENTATION_AUDIT.md
```

This audit becomes the input for the next sub-stage.

---

## 7. AUDIT SCOPE

Inspect:

```text
AGENTS.md
README.md
COMMANDS.md
CHANGELOG.md
docs/
tests/
```

Find and classify:

```text
- architecture docs
- development rules
- CLI docs
- testing docs
- roadmap docs
- stage task files
- stage reports
- old prompts
- deprecated plans
- duplicated docs
- broken or stale references
- files that should remain in place
- files that should move
- files that should be archived
```

---

## 8. CLASSIFICATION CATEGORIES

For each relevant doc, classify as one of:

```text
current_architecture
current_development_rule
current_cli_doc
current_testing_doc
active_stage_task
completed_stage_task
stage_report
roadmap
backlog
archive_candidate
deprecated
duplicate
unknown
```

Also record recommended target location:

```text
keep
move_to_docs_architecture
move_to_docs_development
move_to_docs_stages_active
move_to_docs_stages_completed
move_to_docs_stages_reports
move_to_docs_roadmap
move_to_docs_archive
needs_manual_review
```

---

## 9. TASKS

### A. Inventory

- [ ] List root documentation files.
- [ ] List all files under `docs/`.
- [ ] List stage task files.
- [ ] List stage report files.
- [ ] List roadmap/backlog-like files.
- [ ] List testing/smoke checklist files.
- [ ] List old prompt/deprecated files.
- [ ] List architecture-like files.
- [ ] List development-rule-like files.

### B. Identify current active docs

- [ ] Identify the current active stage docs, if any.
- [ ] Identify the latest completed stage reports.
- [ ] Identify current architecture docs.
- [ ] Identify current testing docs.
- [ ] Identify current CLI docs.
- [ ] Identify current roadmap docs.

### C. Detect duplicates and stale docs

Search for duplicated or stale concepts:

- [ ] Stage 0
- [ ] Stage 3A
- [ ] Stage 3A.1
- [ ] Stage 3B
- [ ] Stage 3B.1
- [ ] Stage 3C
- [ ] AGENTS
- [ ] architecture rules
- [ ] CLI behavior
- [ ] SQLite schema
- [ ] media full not implemented
- [ ] discussion export
- [ ] old not-implemented claims

For each suspect stale item:

- [ ] record file path
- [ ] record stale claim
- [ ] record whether to update, move, or archive later

### D. Detect broken references

- [ ] Search docs for links to files that no longer exist.
- [ ] Search README/COMMANDS/CHANGELOG for outdated paths.
- [ ] Record broken paths.
- [ ] Do not fix them yet unless trivial and isolated.

### E. Write audit file

Create:

```text
docs/stages/reports/STAGE_3D_0_1_DOCUMENTATION_AUDIT.md
```

Required sections:

```text
# Stage 3D.0.1 — Documentation Audit

## 1. Summary
## 2. Current root docs
## 3. Current docs tree
## 4. Stage task files
## 5. Stage reports
## 6. Architecture docs
## 7. Development/testing docs
## 8. Roadmap/backlog docs
## 9. Archive/deprecated candidates
## 10. Duplicate/stale content
## 11. Broken or suspicious references
## 12. Recommended migration map
## 13. Risks
## 14. Next sub-stage recommendation
```

The recommended migration map should be a table:

```text
| Current path | Classification | Recommended target | Action |
```

---

## 10. VERIFICATION

Run no code tests unless code was changed.

Recommended checks:

```bash
find docs -type f | sort
find . -maxdepth 2 -type f | sort
```

If available, use grep/search to verify inventory.

---

## 11. COMPLETION CRITERIA

Complete only if:

- [ ] Audit file exists.
- [ ] It lists current docs.
- [ ] It classifies stage files.
- [ ] It identifies reports.
- [ ] It identifies stale/duplicate docs.
- [ ] It proposes target locations.
- [ ] No docs were moved.
- [ ] AGENTS.md was not rewritten.
- [ ] Runtime code was not changed.

---

## 12. FINAL RESPONSE FORMAT

```text
## Summary
- audit completed
- no docs moved
- no runtime changes

## Files changed
- docs/stages/reports/STAGE_3D_0_1_DOCUMENTATION_AUDIT.md

## Findings
- current docs count
- archive candidates count
- stale references count

## Tests
- not run; docs-audit only

## Stage status
Stage 3D.0.1: complete / partial / blocked
```
