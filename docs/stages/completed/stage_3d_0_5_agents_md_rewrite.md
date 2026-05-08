# STAGE 3D.0.5 — AGENTS.md REWRITE

Status: completed
Stage: 3D.0
Scope: repository agent contract rewrite task

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

Rewrite `AGENTS.md` as the central repository-level instruction contract for coding agents.

This must happen after docs structure and indexes are stable.

`AGENTS.md` should not contain all documentation. It should contain:

```text
- mandatory rules
- protected boundaries
- documentation map
- workflow
- relevant-doc selection policy
```

Target size:

```text
150-300 lines if possible.
```

Do not create a huge file that consumes excessive agent context.

---

## 7. INPUT

Read:

```text
docs/README.md
docs/architecture/README.md
docs/development/README.md
docs/stages/README.md
docs/roadmap/README.md
docs/archive/README.md
docs/stages/reports/STAGE_3D_0_2_TARGET_DOCS_STRUCTURE_PLAN.md
docs/stages/reports/STAGE_3D_0_4_DOCS_INDEXES_REPORT.md
```

If docs indexes are missing, stop and report that Stage 3D.0.4 must be completed first.

---

## 8. AGENTS.md REQUIRED STRUCTURE

Rewrite/create `AGENTS.md` with sections:

```text
# AGENTS.md

## 1. Mandatory first step
## 2. Project identity
## 3. Non-negotiable architecture rules
## 4. Protected files and boundaries
## 5. Documentation map
## 6. Relevant-doc selection policy
## 7. Stage workflow
## 8. Coding rules
## 9. Testing policy
## 10. Documentation policy
## 11. Forbidden behavior
## 12. Stop-and-report conditions
## 13. Final response expectations
```

---

## 9. MANDATORY FIRST STEP

Include near top:

```text
Before editing code or documentation:
1. Read this AGENTS.md.
2. Identify the active task/stage file.
3. Read only the documentation referenced by that task.
4. Inspect files you plan to change.
5. Write a short plan.
6. Implement only the requested scope.
```

Add:

```text
Do not read the whole docs tree by default.
Do not use archive files as current instructions unless explicitly asked.
```

---

## 10. PROJECT IDENTITY

State:

```text
tg-msg-manager is a local Telegram export/data pipeline project.

It is not:
- a SaaS monitoring platform
- an analytics engine
- an OSINT interpretation engine
- a GUI dashboard
```

State direction:

```text
Dataset export first.
Interpretation/analytics are out of the exporter pipeline unless explicitly introduced by a future stage.
```

---

## 11. NON-NEGOTIABLE ARCHITECTURE RULES

Include:

```text
- CLI is thin.
- Services are orchestration-only.
- Feature logic must live in focused modules.
- Do not bloat service facades.
- Existing public CLI behavior must remain stable unless the active stage explicitly allows changes.
- SQLite schema changes are forbidden unless the active stage explicitly allows them.
- Dataset format changes require tests and docs.
- State/incremental behavior must be preserved.
- Any behavior change requires tests.
```

Channel export-specific:

```text
- Channel export logic lives under tg_msg_manager/services/channel_export/.
- Media download logic lives under channel_export media-specific modules.
- Discussion export logic lives under tg_msg_manager/services/channel_export/discussions/.
- ChannelExportService remains orchestration-only.
```

---

## 12. PROTECTED FILES

Include protected list:

```text
tg_msg_manager/services/export/service.py
tg_msg_manager/services/db_export/service.py
tg_msg_manager/services/private_archive/service.py
tg_msg_manager/services/context/engine.py
tg_msg_manager/services/channel_export/service.py
```

Rules:

```text
Do not add new feature logic to protected files.
Only orchestration or mechanical wiring is allowed where appropriate.
If a protected file must change, explain why in the plan and keep the change minimal.
```

---

## 13. DOCUMENTATION MAP

Reference current docs:

```text
docs/README.md
docs/architecture/
docs/development/
docs/stages/active/
docs/stages/completed/
docs/stages/reports/
docs/roadmap/
docs/archive/
```

Explain what each is for.

---

## 14. RELEVANT-DOC SELECTION POLICY

Include:

```text
For any task, read:
1. AGENTS.md
2. the active stage/task file
3. architecture docs referenced by that stage
4. development/testing docs relevant to changed files
5. recent stage reports only if the task depends on prior stage behavior

Do not read:
- all completed stage files by default
- all reports by default
- archive by default
```

---

## 15. STAGE WORKFLOW

Include:

```text
Every stage should:
1. define scope
2. define prohibitions
3. inspect current code/docs
4. implement atomic tasks
5. add/update tests
6. update docs if behavior changes
7. run verification
8. create a factual report
```

Lifecycle:

```text
active task -> implementation -> tests -> report -> move task to completed
```

---

## 16. TESTING POLICY

Include:

```text
Run focused tests first.
Then run broader verification if behavior changed.
Do not claim tests passed unless actually run.
If unable to run tests, state why.
```

Common commands:

```bash
pytest tests/test_channel_export_*.py
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
make test
make verify
```

Do not require every command for docs-only changes unless repo policy demands it.

---

## 17. DOCUMENTATION POLICY

Include this as a non-negotiable rule in `AGENTS.md`:

```text
Documentation is part of the implementation.

For every change, check whether documentation must be updated.

Update documentation in the same change when modifying:
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

A stage is not complete until documentation and reports match the implemented behavior.

Do not leave code behavior ahead of documentation.

Do not claim completion if required documentation is stale, missing, or still describes old behavior.
```

Also include:

```text
- Stage reports are factual records, not instructions.
- Completed stage files are historical.
- Active stage files are executable instructions.
- Archive is not current guidance.
- Do not duplicate large content inside AGENTS.md.
- Do not copy all documentation into AGENTS.md.
- AGENTS.md should point to the relevant docs instead of embedding them.
```

Required documentation targets may include:

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

---

## 18. FORBIDDEN BEHAVIOR

Include:

```text
- no analytics unless explicitly scoped
- no profiling
- no narrative classification
- no OCR/STT/media analysis
- no SQLite changes unless explicitly scoped
- no hidden feature additions
- no broad refactors in feature stages
- no changing legacy command behavior without explicit scope
```

---

## 19. STOP-AND-REPORT CONDITIONS

Include:

```text
Stop and report if:
- active task conflicts with AGENTS.md
- required docs are missing
- a requested change requires SQLite schema changes but stage forbids it
- implementation would require changing protected files beyond orchestration
- tests reveal unrelated baseline failures
- you are about to start a later stage
```

---

## 20. REPORT

Create:

```text
docs/stages/reports/STAGE_3D_0_5_AGENTS_REWRITE_REPORT.md
```

Required sections:

```text
# Stage 3D.0.5 — AGENTS.md Rewrite Report

## 1. Summary
## 2. AGENTS.md structure
## 3. Rules added
## 4. Documentation map added
## 5. Context-size policy
## 6. Protected boundaries
## 7. Remaining alignment work
```

---

## 21. VERIFICATION

Run:

```bash
grep -n "Read this AGENTS.md" AGENTS.md || true
grep -n "Do not read the whole docs tree" AGENTS.md || true
grep -n "docs/stages/active" AGENTS.md || true
grep -n "Protected" AGENTS.md || true
```

Optionally:

```bash
python3 -m compileall tg_msg_manager
```

only if code files were touched.

---

## 22. COMPLETION CRITERIA

Complete only if:

- [ ] AGENTS.md exists.
- [ ] AGENTS.md is concise.
- [ ] AGENTS.md has mandatory first-step workflow.
- [ ] AGENTS.md has protected file rules.
- [ ] AGENTS.md has docs map.
- [ ] AGENTS.md says not to read whole docs tree by default.
- [ ] AGENTS.md says archive is not current guidance.
- [ ] AGENTS.md defines stop-and-report conditions.
- [ ] AGENTS.md states documentation is part of implementation.
- [ ] AGENTS.md states stages are not complete while required docs are stale or missing.
- [ ] AGENTS.md lists documentation update triggers.
- [ ] Report created.
- [ ] Runtime code unchanged.

---

## 23. FINAL RESPONSE FORMAT

```text
## Summary
- AGENTS.md rewritten
- docs map added
- context policy added

## Files changed
- AGENTS.md
- docs/stages/reports/STAGE_3D_0_5_AGENTS_REWRITE_REPORT.md

## Checks
- command/result

## Stage status
Stage 3D.0.5: complete / partial / blocked
```
