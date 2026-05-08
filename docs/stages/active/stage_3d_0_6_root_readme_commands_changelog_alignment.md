# STAGE 3D.0.6 — ROOT README / COMMANDS / CHANGELOG ALIGNMENT

Status: active
Stage: 3D.0
Scope: root documentation alignment task

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

Align root documentation with the reorganized docs structure and rewritten `AGENTS.md`.

Update:

```text
README.md
COMMANDS.md
CHANGELOG.md
```

Only where needed.

Do not rewrite the entire project docs.

Do not change runtime behavior.

---

## 7. INPUT

Read:

```text
AGENTS.md
docs/README.md
docs/stages/reports/STAGE_3D_0_3_DOCS_MIGRATION_REPORT.md
docs/stages/reports/STAGE_3D_0_4_DOCS_INDEXES_REPORT.md
docs/stages/reports/STAGE_3D_0_5_AGENTS_REWRITE_REPORT.md
```

If AGENTS.md rewrite report is missing, stop and report that Stage 3D.0.5 must be completed first.

---

## 8. README.md TASKS

Root `README.md` should remain user-facing.

Do not turn it into a full developer manual.

Update README to include:

- [ ] short project identity
- [ ] where documentation lives
- [ ] link to `docs/README.md`
- [ ] link to `COMMANDS.md`
- [ ] link to `AGENTS.md` for coding agents
- [ ] current major capabilities
- [ ] current known limitations if already documented
- [ ] no stale claims about Stage 3B/3C being not implemented if they are implemented
- [ ] no links to old moved paths

Do not duplicate:

```text
full architecture docs
full stage history
full agent rules
```

---

## 9. COMMANDS.md TASKS

Update command documentation only if paths or behavior descriptions are stale.

Check:

- [ ] `export`
- [ ] `db-export`
- [ ] `export-pm`
- [ ] `export-channel`
- [ ] `retry`
- [ ] `report`
- [ ] `clean`
- [ ] `delete`
- [ ] `schedule`
- [ ] `setup`

For `export-channel`, ensure it reflects current implemented behavior:

- [ ] `--media none|metadata|full`
- [ ] default media mode
- [ ] `--max-media-size`
- [ ] `--media-types`
- [ ] if Stage 3C is complete, `--discussion none|full`
- [ ] if Stage 3C is complete, `--max-comments-per-post`
- [ ] current known limitations
- [ ] no stale "not implemented yet" claims

Do not invent behavior not implemented.

---

## 10. CHANGELOG.md TASKS

Update CHANGELOG with Stage 3D.0 docs/governance entry.

Entry should say:

```text
- documentation tree reorganized
- stage docs separated into active/completed/reports/archive
- AGENTS.md rewritten as repository agent contract
- root docs aligned
```

Do not claim runtime features were added.

Do not exaggerate.

---

## 11. PATH REFERENCE CLEANUP

Search and fix current docs references.

Search:

```bash
grep -R "docs/refactor" -n README.md COMMANDS.md CHANGELOG.md docs || true
grep -R "docs/stages/" -n README.md COMMANDS.md CHANGELOG.md docs || true
grep -R "not implemented yet" -n README.md COMMANDS.md CHANGELOG.md docs || true
```

Tasks:

- [ ] Update references from old locations to new locations.
- [ ] Avoid updating archived docs unless necessary.
- [ ] Ensure root docs do not link to moved old paths.
- [ ] Ensure README points to docs index.
- [ ] Ensure command docs match current CLI.

---

## 12. REPORT

Create:

```text
docs/stages/reports/STAGE_3D_0_6_ROOT_DOCS_ALIGNMENT_REPORT.md
```

Required sections:

```text
# Stage 3D.0.6 — Root Docs Alignment Report

## 1. Summary
## 2. README changes
## 3. COMMANDS changes
## 4. CHANGELOG changes
## 5. Path references updated
## 6. Stale claims removed
## 7. Runtime behavior statement
## 8. Remaining documentation risks
```

---

## 13. VERIFICATION

Run:

```bash
grep -R "not implemented yet" -n README.md COMMANDS.md docs || true
grep -R "docs/refactor" -n README.md COMMANDS.md docs || true
python3 -m tg_msg_manager.cli export-channel --help
```

If code untouched, tests optional.

If any code touched:

```bash
python3 -m compileall tg_msg_manager
pytest tests/test_channel_export_*.py
```

---

## 14. COMPLETION CRITERIA

Complete only if:

- [ ] README points to new docs structure.
- [ ] README is not bloated.
- [ ] COMMANDS reflects current CLI.
- [ ] CHANGELOG has Stage 3D.0 docs/governance entry.
- [ ] stale "not implemented yet" claims removed where false.
- [ ] old moved paths fixed where relevant.
- [ ] report created.
- [ ] runtime code unchanged.
- [ ] existing CLI behavior unchanged.

---

## 15. FINAL RESPONSE FORMAT

```text
## Summary
- root docs aligned
- stale references fixed
- no runtime changes

## Files changed
- README.md
- COMMANDS.md
- CHANGELOG.md
- report path

## Checks
- command/result

## Stage status
Stage 3D.0.6: complete / partial / blocked
```
