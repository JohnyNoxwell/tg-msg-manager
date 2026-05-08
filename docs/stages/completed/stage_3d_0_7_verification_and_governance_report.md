# STAGE 3D.0.7 — VERIFICATION AND GOVERNANCE REPORT

Status: completed
Stage: 3D.0
Scope: final verification and governance report task

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

Finalize Stage 3D.0 by verifying the documentation governance system and producing a final report.

This stage should not introduce new structure unless verification reveals a small docs issue.

---

## 7. INPUT

Read all Stage 3D.0 reports:

```text
docs/stages/reports/STAGE_3D_0_1_DOCUMENTATION_AUDIT.md
docs/stages/reports/STAGE_3D_0_2_TARGET_DOCS_STRUCTURE_PLAN.md
docs/stages/reports/STAGE_3D_0_3_DOCS_MIGRATION_REPORT.md
docs/stages/reports/STAGE_3D_0_4_DOCS_INDEXES_REPORT.md
docs/stages/reports/STAGE_3D_0_5_AGENTS_REWRITE_REPORT.md
docs/stages/reports/STAGE_3D_0_6_ROOT_DOCS_ALIGNMENT_REPORT.md
```

If any report is missing, stop and report which sub-stage is incomplete.

---

## 8. VERIFICATION GOALS

Confirm:

```text
- docs tree is organized
- active/completed/reports/archive are separated
- AGENTS.md is concise and usable
- root README points to docs
- COMMANDS reflects current CLI
- CHANGELOG records docs governance stage
- archive is clearly non-current
- agent workflow is explicit
- no runtime code behavior changed
```

---

## 9. FILE STRUCTURE CHECKS

Run or inspect equivalent:

```bash
find docs -maxdepth 3 -type d | sort
find docs -maxdepth 4 -type f | sort
```

Check:

- [ ] `docs/README.md` exists.
- [ ] `docs/architecture/README.md` exists.
- [ ] `docs/development/README.md` exists.
- [ ] `docs/stages/README.md` exists.
- [ ] `docs/roadmap/README.md` exists.
- [ ] `docs/archive/README.md` exists.
- [ ] `docs/stages/active/` exists.
- [ ] `docs/stages/completed/` exists.
- [ ] `docs/stages/reports/` exists.
- [ ] archive directories exist if planned.

---

## 10. AGENTS.md CHECKS

Verify `AGENTS.md` contains:

- [ ] mandatory first-step workflow
- [ ] project identity
- [ ] protected file list
- [ ] docs map
- [ ] relevant-doc selection policy
- [ ] do-not-read-whole-docs-tree rule
- [ ] archive-not-current rule
- [ ] testing policy
- [ ] stop-and-report conditions

Search:

```bash
grep -n "docs/stages/active" AGENTS.md
grep -n "Do not read" AGENTS.md
grep -n "archive" AGENTS.md
grep -n "SQLite" AGENTS.md
grep -n "Protected" AGENTS.md
```

---

## 11. STALE REFERENCE CHECKS

Search:

```bash
grep -R "not implemented yet" -n README.md COMMANDS.md docs || true
grep -R "docs/refactor" -n README.md COMMANDS.md docs || true
grep -R "old_prompts" -n README.md COMMANDS.md docs || true
```

Interpretation:

- [ ] false stale claims should be fixed.
- [ ] legitimate historical references inside archive may remain.
- [ ] report any remaining questionable references.

---

## 12. RUNTIME SAFETY CHECKS

Confirm no runtime behavior changes were made intentionally.

Run:

```bash
python3 -m compileall tg_msg_manager
python3 -m tg_msg_manager.cli --help
python3 -m tg_msg_manager.cli export-channel --help
```

If practical:

```bash
pytest tests/test_channel_export_*.py
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
```

If docs-only changes and full tests are expensive, at minimum run compile/help checks. Do not claim unrun tests passed.

---

## 13. FINAL GOVERNANCE REPORT

Create:

```text
docs/stages/reports/STAGE_3D_0_PROJECT_GOVERNANCE_DOCS_REORGANIZATION_REPORT.md
```

Required sections:

```text
# Stage 3D.0 — Project Governance / Documentation Reorganization Report

## 1. Summary
## 2. Final documentation structure
## 3. AGENTS.md contract
## 4. Stage documentation lifecycle
## 5. Architecture/development docs separation
## 6. Archive policy
## 7. Root docs alignment
## 8. Verification results
## 9. Runtime behavior statement
## 10. Remaining documentation limitations
## 11. Rules for future stages
## 12. Status
```

Must explicitly state:

```text
- no product feature was added
- no SQLite schema change was made
- no legacy CLI behavior was changed
- AGENTS.md is the repository-level agent contract
- active stage files live under docs/stages/active/
- completed task files are historical
- reports are factual records
- archive is not current guidance
```

---

## 14. OPTIONAL FINAL CLEANUP

Only if safe:

- [ ] Move Stage 3D.0 active task files to completed after all sub-stages are complete.
- [ ] Ensure final report is under `docs/stages/reports/`.
- [ ] Update docs/stages/README.md if active/completed lists changed.

Do not overdo cleanup.

---

## 15. COMPLETION CRITERIA

Complete only if:

- [ ] All prior Stage 3D.0 reports exist.
- [ ] Final governance report exists.
- [ ] Docs indexes exist.
- [ ] AGENTS.md is updated.
- [ ] Root README/COMMANDS/CHANGELOG aligned.
- [ ] Verification commands run and results recorded.
- [ ] Runtime code behavior unchanged.
- [ ] No new feature added.
- [ ] No SQLite schema changed.
- [ ] Stage 3D.0 marked complete.

---

## 16. FINAL RESPONSE FORMAT

```text
## Summary
- Stage 3D.0 docs governance complete
- AGENTS.md contract ready
- docs structure organized

## Files changed
- path
- path

## Verification
- command: result
- command: result

## Runtime behavior
- unchanged

## Remaining limitations
- item
- item

## Stage status
Stage 3D.0.1: complete / partial / blocked
Stage 3D.0.2: complete / partial / blocked
Stage 3D.0.3: complete / partial / blocked
Stage 3D.0.4: complete / partial / blocked
Stage 3D.0.5: complete / partial / blocked
Stage 3D.0.6: complete / partial / blocked
Stage 3D.0.7: complete / partial / blocked
Stage 3D.0: complete / partial / blocked
```
