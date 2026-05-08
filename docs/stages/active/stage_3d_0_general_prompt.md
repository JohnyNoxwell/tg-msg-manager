# GENERAL PROMPT — EXECUTE STAGE 3D.0 PROJECT GOVERNANCE / DOCS REORGANIZATION

Status: active
Stage: 3D.0
Scope: general execution prompt

```text
Read AGENTS.md first.

You are working on tg-msg-manager.

Your task is to execute Stage 3D.0 — Project Governance / Documentation Reorganization / Agent Rules Hardening.

This is a documentation/governance stage.
This is not a feature stage.
Do not change runtime behavior.
Do not implement new Telegram export features.
Do not change SQLite schema.
Do not change existing CLI behavior.
```

## 1. EXECUTE THESE FILES IN ORDER

Run the sub-stages strictly in this order:

```text
1. docs/stages/active/stage_3d_0_1_documentation_audit.md
2. docs/stages/active/stage_3d_0_2_target_structure_and_migration_plan.md
3. docs/stages/active/stage_3d_0_3_move_and_normalize_documentation.md
4. docs/stages/active/stage_3d_0_4_documentation_indexes_and_navigation.md
5. docs/stages/active/stage_3d_0_5_agents_md_rewrite.md
6. docs/stages/active/stage_3d_0_6_root_readme_commands_changelog_alignment.md
7. docs/stages/active/stage_3d_0_7_verification_and_governance_report.md
```

Do not skip stages.
Do not merge stages.
Do not rewrite AGENTS.md before docs structure and indexes are stable.
Do not move files before the audit and migration plan are complete.

## 2. GLOBAL RULES

Hard prohibitions:

```text
- no runtime feature changes
- no Telegram feature additions
- no Stage 3C follow-up features
- no Stage 3D product features
- no analytics
- no OSINT interpretation
- no sentiment analysis
- no bot detection
- no user profiling
- no narrative classification
- no OCR
- no speech-to-text
- no image/video/audio analysis
- no SQLite schema changes
- no migrations
- no DB persistence additions
- no GUI/dashboard/SaaS features
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

Protected files:

```text
tg_msg_manager/services/export/service.py
tg_msg_manager/services/db_export/service.py
tg_msg_manager/services/private_archive/service.py
tg_msg_manager/services/context/engine.py
tg_msg_manager/services/channel_export/service.py
```

Do not add feature logic to protected files.

## 2A. NON-NEGOTIABLE DOCUMENTATION POLICY

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

A stage is not complete until documentation and reports match the implemented behavior.

Do not leave code behavior ahead of documentation.

Do not claim completion if required documentation is stale, missing, or still describes old behavior.


## 3. STAGE OBJECTIVE

By the end of Stage 3D.0, the repository should have:

```text
- organized documentation tree
- separated active/completed/report/archive docs
- clear docs indexes
- rewritten AGENTS.md as repository-level agent contract
- README/COMMANDS/CHANGELOG aligned with new docs paths
- final governance report
```

Target documentation structure:

```text
docs/
  README.md

  architecture/
    README.md

  development/
    README.md

  stages/
    README.md
    active/
    completed/
    reports/

  roadmap/
    README.md

  archive/
    README.md
    legacy_notes/
    old_prompts/
    deprecated_stage_files/
```

Adapt only if the current repo structure justifies it.

## 4. EXECUTION PROTOCOL FOR EACH SUB-STAGE

For each sub-stage:

```text
1. Read the stage file completely.
2. Inspect the files it asks you to inspect.
3. Write a short plan before editing.
4. Execute only that stage scope.
5. Create the required report.
6. Run the required checks.
7. Stop and summarize the sub-stage result.
8. Move to the next sub-stage only if the current one is complete.
```

If blocked:

```text
- stop immediately
- report exact blocker
- do not continue to the next stage
- do not improvise outside scope
```

## 5. IMPORTANT ORDERING RULE

Correct ordering:

```text
1. audit current docs
2. design target docs structure
3. move/sort docs
4. create docs indexes
5. rewrite AGENTS.md
6. align root README/COMMANDS/CHANGELOG
7. verify and write final governance report
```

Do not rewrite AGENTS.md first.

Reason:

```text
AGENTS.md must point to stable docs paths.
```

## 6. AGENTS.md FINAL CONTRACT

When Stage 3D.0.5 is reached, AGENTS.md must become concise repository-level guidance.

It should include:

```text
- mandatory first step
- project identity
- architecture rules
- protected files
- documentation map
- relevant-doc selection policy
- stage workflow
- coding rules
- testing policy
- documentation policy
- documentation update triggers
- rule that docs are part of implementation
- rule that a stage is not complete while required docs are stale
- forbidden behavior
- stop-and-report conditions
```

It must not include:

```text
- full stage histories
- full reports
- huge roadmap dumps
- archived notes
- all documentation content
```

AGENTS.md should tell agents:

```text
Read AGENTS.md first.
Then read the active task file.
Then read only relevant referenced docs.
Do not read the whole docs tree by default.
Do not use archive as current guidance unless explicitly asked.
```

## 7. FINAL VERIFICATION

At the end of Stage 3D.0.7, run or report inability to run:

```bash
find docs -maxdepth 4 -type f | sort
python3 -m compileall tg_msg_manager
python3 -m tg_msg_manager.cli --help
python3 -m tg_msg_manager.cli export-channel --help
pytest tests/test_channel_export_*.py
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
```

If docs-only and some checks are unnecessary or unavailable, explain clearly. Do not claim unrun tests passed.

## 8. FINAL REPORT

Create:

```text
docs/stages/reports/STAGE_3D_0_PROJECT_GOVERNANCE_DOCS_REORGANIZATION_REPORT.md
```

It must state:

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

## 9. FINAL RESPONSE FORMAT

```text
## Summary
- Stage 3D.0 docs governance completed
- docs tree reorganized
- AGENTS.md rewritten
- root docs aligned

## Files changed
- path
- path

## Behavior preserved
- no runtime behavior changes
- no SQLite changes
- no legacy CLI changes
- no feature additions

## Verification
- command: result
- command: result

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
