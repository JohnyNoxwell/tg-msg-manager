# Stage 3D.0.2 - Target Docs Structure Plan

## 1. Summary

This plan uses `docs/stages/reports/STAGE_3D_0_1_DOCUMENTATION_AUDIT.md` as input.

Stage 3D.0.2 is plan-only:

- no files were moved;
- no directories were created;
- `AGENTS.md` was not rewritten;
- no runtime code was changed.

The target tree separates current guidance from historical records:

- current architecture guidance goes under `docs/architecture/`;
- development, testing, CLI, PR, and agent workflow guidance goes under `docs/development/`;
- executable stage tasks go under `docs/stages/active/`;
- completed task prompts go under `docs/stages/completed/`;
- factual completion records go under `docs/stages/reports/`;
- roadmap/backlog docs go under `docs/roadmap/`;
- old prompts, deprecated plans, and superseded notes go under `docs/archive/`.

## 2. Target directory structure

Create this structure in Stage 3D.0.3:

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

Do not create deeper nested folders in Stage 3D.0 unless a moved file would otherwise lose important status context.

## 3. Directory responsibility rules

`docs/architecture/`

- Current architecture rules, boundaries, storage/model decisions, split maps, and architecture snapshots.
- May contain historical architecture audits only when they are still useful current references and are clearly labeled.
- Must not contain active task prompts.

`docs/development/`

- Developer workflow, CLI contracts, testing guidance, PR checklist, facade baselines, and documentation rules.
- May link to historical reports when needed.
- Must not contain product roadmap authorization.

`docs/stages/active/`

- Only currently executable stage task files.
- Agents may execute files here when explicitly requested or when they are the active task.
- Active files should use current paths after Stage 3D.0.3.

`docs/stages/completed/`

- Completed task instruction files.
- Historical prompt content can be stale and must not be treated as current behavior unless current docs say so.

`docs/stages/reports/`

- Factual reports, baselines, audits, and completion records.
- Reports can contain time-bound or stage-bound claims. Indexes must label them as records, not current instructions.

`docs/roadmap/`

- Current roadmap, backlog, deferred work, and future-direction notes.
- Roadmap entries are not authorization to implement a feature.

`docs/archive/`

- Superseded notes, deprecated plans, old prompts, brainstorms, and legacy backlog archives.
- Archive content is not current guidance unless an active task explicitly says to use it.

## 4. File migration map

| Current path | Target path | Action | Reason |
| --- | --- | --- | --- |
| `AGENTS.md` | `AGENTS.md` | keep, rewrite later | Root agent contract must stay discoverable; rewrite only after docs paths and indexes are stable. |
| `README.md` | `README.md` | keep, update references later | Main user-facing entrypoint. |
| `COMMANDS.md` | `COMMANDS.md` | keep, update references later | Root command reference remains convenient. |
| `CHANGELOG.md` | `CHANGELOG.md` | keep, add Stage 3D.0 entry later | Root changelog remains current history. |
| `PROJECT_ARCHITECTURE_OVERVIEW.md` | `docs/architecture/PROJECT_ARCHITECTURE_OVERVIEW.md` | move | Current architecture snapshot belongs with architecture docs. |
| `ROADMAP.md` | `docs/roadmap/ROADMAP.md` | move | Current roadmap belongs under roadmap tree. |
| `LOCAL_BACKLOG.md` | `docs/archive/legacy_notes/LOCAL_BACKLOG.md` | move | Closed local note, not active roadmap. |
| `BRAINSTORM.md` | `docs/archive/old_prompts/BRAINSTORM.md` | move | Brainstorm includes prohibited OSINT/profiling ideas and must be non-current guidance. |
| `docs/ARCHITECTURE_RULES.md` | `docs/architecture/ARCHITECTURE_RULES.md` | move, update links | Current architecture rules. |
| `docs/PR_CHECKLIST.md` | `docs/development/PR_CHECKLIST.md` | move | Development checklist. |
| `docs/sqlite_message_id_audit.md` | `docs/architecture/SQLITE_MESSAGE_ID_AUDIT.md` | move, normalize filename | Current storage identity audit. |
| `docs/db_baseline_report.md` | `docs/archive/legacy_notes/DB_BASELINE_REPORT.md` | move, normalize filename | Historical baseline. |
| `docs/export_smoke_scenarios.md` | `docs/archive/legacy_notes/EXPORT_SMOKE_SCENARIOS.md` | move, normalize filename | Historical smoke notes superseded by live checklist. |
| `docs/testing/LIVE_SMOKE_CHECKLIST.md` | `docs/development/LIVE_SMOKE_CHECKLIST.md` | move | Testing guidance belongs under development. |
| `docs/refactor/README.md` | `docs/archive/legacy_notes/REFACTOR_DOCS_INDEX.md` | move, supersede | Old index is incomplete after Stage 3C and will be replaced by `docs/stages/README.md`. |
| `docs/refactor/CLI_CONTRACT.md` | `docs/development/CLI_CONTRACT.md` | move | Current CLI contract. |
| `docs/refactor/CONTEXT_ENGINE_SPLIT_MAP.md` | `docs/architecture/CONTEXT_ENGINE_SPLIT_MAP.md` | move | Current context architecture map. |
| `docs/architecture/CONTEXT_RELATION_TABLES_DECISION.md` | `docs/architecture/CONTEXT_RELATION_TABLES_DECISION.md` | move, update links | Current table-status decision. |
| `docs/refactor/DB_EXPORT_ENTRYPOINT_AUDIT.md` | `docs/architecture/DB_EXPORT_ENTRYPOINT_AUDIT.md` | move | Current entrypoint compatibility note. |
| `docs/refactor/DB_EXPORT_SERVICE_SPLIT_MAP.md` | `docs/architecture/DB_EXPORT_SERVICE_SPLIT_MAP.md` | move | Current DB export split map. |
| `docs/refactor/EXPORT_SERVICE_SPLIT_MAP.md` | `docs/architecture/EXPORT_SERVICE_SPLIT_MAP.md` | move | Current export split map. |
| `docs/refactor/FACADE_SIZE_BASELINE.md` | `docs/development/FACADE_SIZE_BASELINE.md` | move | Development guardrail baseline. |
| `docs/refactor/LEGACY_INVENTORY.md` | `docs/archive/legacy_notes/LEGACY_INVENTORY.md` | move | Historical legacy inventory. |
| `docs/refactor/PAYLOADS_SPLIT_MAP.md` | `docs/architecture/PAYLOADS_SPLIT_MAP.md` | move | Current payload architecture map. |
| `docs/refactor/PRIVATE_ARCHIVE_ENTRYPOINT_AUDIT.md` | `docs/architecture/PRIVATE_ARCHIVE_ENTRYPOINT_AUDIT.md` | move | Current private archive entrypoint note. |
| `docs/refactor/PRIVATE_ARCHIVE_IMPORT_RESOLUTION.md` | `docs/architecture/PRIVATE_ARCHIVE_IMPORT_RESOLUTION.md` | move | Current compatibility/import note. |
| `docs/refactor/PRIVATE_ARCHIVE_SPLIT_MAP.md` | `docs/architecture/PRIVATE_ARCHIVE_SPLIT_MAP.md` | move | Current private archive split map. |
| `docs/refactor/SQLITE_WRITE_PATH_SPLIT_MAP.md` | `docs/architecture/SQLITE_WRITE_PATH_SPLIT_MAP.md` | move | Current storage write split map. |
| `docs/refactor/STORAGE_CONTRACT_SPLIT_MAP.md` | `docs/architecture/STORAGE_CONTRACT_SPLIT_MAP.md` | move | Current storage contract architecture map. |
| `docs/refactor/STAGE_0_BASELINE.md` | `docs/stages/reports/STAGE_0_BASELINE.md` | move | Stage record. |
| `docs/refactor/STAGE_0_CLI_SURFACE.md` | `docs/stages/reports/STAGE_0_CLI_SURFACE.md` | move | Stage record. |
| `docs/refactor/STAGE_0_FINAL_REPORT.md` | `docs/stages/reports/STAGE_0_FINAL_REPORT.md` | move | Stage report. |
| `docs/refactor/STAGE_0_REFACTOR_REPORT.md` | `docs/stages/reports/STAGE_0_REFACTOR_REPORT.md` | move | Stage report. |
| `docs/refactor/STAGE_0_SCRIPT_AUDIT.md` | `docs/stages/reports/STAGE_0_SCRIPT_AUDIT.md` | move | Stage audit. |
| `docs/refactor/STAGE_0_SMOKE_SCENARIOS.md` | `docs/stages/reports/STAGE_0_SMOKE_SCENARIOS.md` | move | Stage record. |
| `docs/refactor/STAGE_0_SQLITE_READ_INVENTORY.md` | `docs/stages/reports/STAGE_0_SQLITE_READ_INVENTORY.md` | move | Stage inventory. |
| `docs/refactor/STAGE_0_STORAGE_DECISIONS.md` | `docs/stages/reports/STAGE_0_STORAGE_DECISIONS.md` | move | Stage decision record. |
| `docs/refactor/STAGE_1_BASELINE.md` | `docs/stages/reports/STAGE_1_BASELINE.md` | move | Stage record. |
| `docs/refactor/STAGE_1_CONSISTENCY_BASELINE.md` | `docs/stages/reports/STAGE_1_CONSISTENCY_BASELINE.md` | move | Stage record. |
| `docs/refactor/STAGE_1_CONSISTENCY_REPORT.md` | `docs/stages/reports/STAGE_1_CONSISTENCY_REPORT.md` | move | Stage report. |
| `docs/refactor/STAGE_1_REFACTOR_REPORT.md` | `docs/stages/reports/STAGE_1_REFACTOR_REPORT.md` | move | Stage report. |
| `docs/refactor/STAGE_2_READINESS_BASELINE.md` | `docs/stages/reports/STAGE_2_READINESS_BASELINE.md` | move | Stage record. |
| `docs/refactor/STAGE_2_READINESS_REPORT.md` | `docs/stages/reports/STAGE_2_READINESS_REPORT.md` | move | Stage report. |
| `docs/refactor/STAGE_3A_BASELINE.md` | `docs/stages/reports/STAGE_3A_BASELINE.md` | move | Stage record. |
| `docs/refactor/STAGE_3A_DIRECT_CHANNEL_EXPORT_REPORT.md` | `docs/stages/reports/STAGE_3A_DIRECT_CHANNEL_EXPORT_REPORT.md` | move | Historical report; index must note stale media-full statements are historical. |
| `docs/refactor/STAGE_3A_1_BASELINE.md` | `docs/stages/reports/STAGE_3A_1_BASELINE.md` | move | Stage record. |
| `docs/refactor/STAGE_3A_1_CHANNEL_EXPORT_OPERATIONAL_HARDENING_REPORT.md` | `docs/stages/reports/STAGE_3A_1_CHANNEL_EXPORT_OPERATIONAL_HARDENING_REPORT.md` | move | Stage report. |
| `docs/refactor/STAGE_3B_MEDIA_DOWNLOAD_HARDENING_REPORT.md` | `docs/stages/reports/STAGE_3B_MEDIA_DOWNLOAD_HARDENING_REPORT.md` | move | Stage report. |
| `docs/refactor/STAGE_3B_1_CHANNEL_EXPORT_STABILIZATION_REPORT.md` | `docs/stages/reports/STAGE_3B_1_CHANNEL_EXPORT_STABILIZATION_REPORT.md` | move | Stage report. |
| `docs/refactor/STAGE_3C_CHANNEL_DISCUSSION_CONTEXT_EXPORT_DESIGN.md` | `docs/architecture/STAGE_3C_CHANNEL_DISCUSSION_CONTEXT_EXPORT_DESIGN.md` | move | Current discussion export architecture design. |
| `docs/refactor/STAGE_3C_CHANNEL_DISCUSSION_CONTEXT_EXPORT_REPORT.md` | `docs/stages/reports/STAGE_3C_CHANNEL_DISCUSSION_CONTEXT_EXPORT_REPORT.md` | move | Final Stage 3C report. |
| `docs/refactor/STAGE_3C_2_DISCUSSION_RESOLVER_AND_MODELS_REPORT.md` | `docs/stages/reports/STAGE_3C_2_DISCUSSION_RESOLVER_AND_MODELS_REPORT.md` | move | Stage report. |
| `docs/refactor/STAGE_3C_3_DISCUSSION_FETCH_AND_WRITERS_REPORT.md` | `docs/stages/reports/STAGE_3C_3_DISCUSSION_FETCH_AND_WRITERS_REPORT.md` | move | Historical sub-stage report; index must note integration was later completed. |
| `docs/stages/reports/STAGE_3D_0_1_DOCUMENTATION_AUDIT.md` | `docs/stages/reports/STAGE_3D_0_1_DOCUMENTATION_AUDIT.md` | move during Stage 3D.0.3 | Current Stage 3D.0 record. |
| `docs/stages/reports/STAGE_3D_0_2_TARGET_DOCS_STRUCTURE_PLAN.md` | `docs/stages/reports/STAGE_3D_0_2_TARGET_DOCS_STRUCTURE_PLAN.md` | move during Stage 3D.0.3 after creation | Current Stage 3D.0 record. |
| `docs/stages/stage_3d_0_1_documentation_audit.md` | `docs/stages/active/stage_3d_0_1_documentation_audit.md` | move | Active Stage 3D.0 task file. |
| `docs/stages/stage_3d_0_2_target_structure_and_migration_plan.md` | `docs/stages/active/stage_3d_0_2_target_structure_and_migration_plan.md` | move | Active Stage 3D.0 task file. |
| `docs/stages/stage_3d_0_3_move_and_normalize_documentation.md` | `docs/stages/active/stage_3d_0_3_move_and_normalize_documentation.md` | move | Active Stage 3D.0 task file. |
| `docs/stages/stage_3d_0_4_documentation_indexes_and_navigation.md` | `docs/stages/active/stage_3d_0_4_documentation_indexes_and_navigation.md` | move | Active Stage 3D.0 task file. |
| `docs/stages/stage_3d_0_5_agents_md_rewrite.md` | `docs/stages/active/stage_3d_0_5_agents_md_rewrite.md` | move | Active Stage 3D.0 task file. |
| `docs/stages/stage_3d_0_6_root_readme_commands_changelog_alignment.md` | `docs/stages/active/stage_3d_0_6_root_readme_commands_changelog_alignment.md` | move | Active Stage 3D.0 task file. |
| `docs/stages/stage_3d_0_7_verification_and_governance_report.md` | `docs/stages/active/stage_3d_0_7_verification_and_governance_report.md` | move | Active Stage 3D.0 task file. |
| `docs/stages/stage_3d_0_general_prompt.md` | `docs/stages/active/stage_3d_0_general_prompt.md` | move | General active Stage 3D.0 prompt. |
| `docs/stages/stage_3c_1_discussion_architecture_contract.md` | `docs/stages/completed/stage_3c_1_discussion_architecture_contract.md` | move | Completed task prompt. |
| `docs/stages/stage_3c_2_discussion_resolver_and_models.md` | `docs/stages/completed/stage_3c_2_discussion_resolver_and_models.md` | move | Completed task prompt. |
| `docs/stages/stage_3c_3_discussion_fetch_and_writers.md` | `docs/stages/completed/stage_3c_3_discussion_fetch_and_writers.md` | move | Completed task prompt. |
| `docs/stages/stage_3c_4_discussion_integration_tests_docs.md` | `docs/stages/completed/stage_3c_4_discussion_integration_tests_docs.md` | move | Completed task prompt. |
| `docs/stages/stage_3b_1_channel_export_stabilization_pass_codex_tasks.md` | `docs/stages/completed/stage_3b_1_channel_export_stabilization_pass_codex_tasks.md` | move | Completed task prompt. |
| `docs/stages/stage_3b_media_download_hardening_codex_tasks.md` | `docs/stages/completed/stage_3b_media_download_hardening_codex_tasks.md` | move | Completed task prompt. |
| `docs/stages/stage_3a_1_channel_export_operational_hardening_codex_tasks.md` | `docs/stages/completed/stage_3a_1_channel_export_operational_hardening_codex_tasks.md` | move | Completed task prompt. |
| `docs/stages/stage_3a_direct_channel_export_agent_tasks.md` | `docs/stages/completed/stage_3a_direct_channel_export_agent_tasks.md` | move | Completed task prompt. |
| `docs/stages/stage_3a_direct_channel_export_backlog.md` | `docs/archive/deprecated_stage_files/stage_3a_direct_channel_export_backlog.md` | move | Superseded Stage 3A backlog, covered by reports. |
| `backlog/stage_1_consistency_pass.md` | `docs/archive/deprecated_stage_files/stage_1_consistency_pass.md` | move | Deprecated stage prompt outside docs tree. |
| `backlog/stage_1_db_export_archive_storage_refactor.md` | `docs/archive/deprecated_stage_files/stage_1_db_export_archive_storage_refactor.md` | move | Deprecated stage prompt outside docs tree. |
| `backlog/stage_2_readiness_hardening.md` | `docs/archive/deprecated_stage_files/stage_2_readiness_hardening.md` | move | Deprecated stage prompt outside docs tree. |
| `backlog/archive/README.md` | `docs/archive/deprecated_stage_files/backlog_archive_README.md` | move, rename to avoid collision | Existing archive index. |
| `backlog/archive/TODO.md` | `docs/archive/deprecated_stage_files/TODO.md` | move | Deprecated backlog note. |
| `backlog/archive/refactor.md` | `docs/archive/deprecated_stage_files/refactor.md` | move | Deprecated backlog note. |
| `backlog/archive/sqlite_architecture_hardening_todo.md` | `docs/archive/deprecated_stage_files/sqlite_architecture_hardening_todo.md` | move | Deprecated backlog note. |
| `backlog/archive/stage_0_refactor_baseline.md` | `docs/archive/deprecated_stage_files/stage_0_refactor_baseline.md` | move | Deprecated backlog note. |
| `backlog/archive/stagt_0.md` | `docs/archive/deprecated_stage_files/stagt_0.md` | move | Deprecated backlog note. |
| `backlog/archive/stagt_1.md` | `docs/archive/deprecated_stage_files/stagt_1.md` | move | Deprecated backlog note. |
| `backlog/archive/stagt_2.md` | `docs/archive/deprecated_stage_files/stagt_2.md` | move | Deprecated backlog note. |
| `backlog/archive/stagt_3.md` | `docs/archive/deprecated_stage_files/stagt_3.md` | move | Deprecated backlog note. |
| `backlog/archive/stagt_4.md` | `docs/archive/deprecated_stage_files/stagt_4.md` | move | Deprecated backlog note. |
| `backlog/archive/stagt_5.md` | `docs/archive/deprecated_stage_files/stagt_5.md` | move | Deprecated backlog note. |
| `backlog/archive/stagt_6_legacy.md` | `docs/archive/deprecated_stage_files/stagt_6_legacy.md` | move | Deprecated backlog note. |
| `backlog/archive/stagt_7_legacy.md` | `docs/archive/deprecated_stage_files/stagt_7_legacy.md` | move | Deprecated backlog note. |
| `backlog/archive/stagt_8_legacy.md` | `docs/archive/deprecated_stage_files/stagt_8_legacy.md` | move | Deprecated backlog note. |

## 5. Index files to create

Create these index files in Stage 3D.0.4 after moves:

| Path | Purpose |
| --- | --- |
| `docs/README.md` | Top-level docs map and relevant-doc selection policy. |
| `docs/architecture/README.md` | Current architecture docs index and warning that reports are historical. |
| `docs/development/README.md` | Development workflow, testing, CLI contracts, PR checklist, docs policy. |
| `docs/stages/README.md` | Stage workflow, active/completed/report separation, current active list. |
| `docs/roadmap/README.md` | Roadmap/backlog index and warning that roadmap is not implementation approval. |
| `docs/archive/README.md` | Archive scope and non-current guidance warning. |

## 6. AGENTS.md rewrite plan

Do not rewrite `AGENTS.md` until Stage 3D.0.5.

Final `AGENTS.md` should be concise and point to stable docs paths. It should include:

- mandatory first step: read `AGENTS.md`, then the active task file, then only relevant referenced docs;
- project identity: local Telegram history data pipeline and CLI, not a general scripting collection;
- architecture rules summary with links to `docs/architecture/`;
- protected files and hot-path facade list;
- documentation map;
- relevant-doc selection policy;
- stage workflow and active/completed/report/archive distinctions;
- coding rules preserving CLI/export/storage behavior;
- testing policy and final verification expectations;
- documentation policy and update triggers;
- explicit rule that docs are part of implementation;
- explicit rule that a stage is incomplete while required docs are stale;
- forbidden behavior list for analytics, OSINT/profiling, OCR/speech/media analysis, schema changes, GUI/SaaS, and feature work outside scope;
- stop-and-report conditions for missing prerequisite docs, contradictory instructions, required behavior change, schema change pressure, or stale docs that cannot be reconciled.

It should not include:

- full stage histories;
- full reports;
- roadmap dumps;
- archived notes;
- the entire old long-form architecture rulebook.

## 7. Link/reference update plan

Update current docs and active Stage 3D.0 files after moves:

- `README.md`: add docs navigation links; update any old `docs/refactor/` or `docs/testing/` references if present.
- `COMMANDS.md`: add docs navigation links if appropriate; keep command behavior text unchanged.
- `CHANGELOG.md`: add Stage 3D.0 docs/governance entry only; do not claim feature changes.
- `AGENTS.md`: update all docs paths during Stage 3D.0.5.
- `docs/architecture/ARCHITECTURE_RULES.md`: update `docs/architecture/CONTEXT_RELATION_TABLES_DECISION.md` reference to `docs/architecture/CONTEXT_RELATION_TABLES_DECISION.md`.
- `docs/stages/active/stage_3d_0_*.md`: normalize references from `docs/refactor/STAGE_3D_0_*` to `docs/stages/reports/STAGE_3D_0_*`.
- `docs/stages/README.md`: list active task files and report files.
- Historical files in `docs/stages/completed/`, `docs/stages/reports/`, and `docs/archive/` may keep old paths if changing them would rewrite historical context. Indexes must warn that historical references can be stale.

Search commands for Stage 3D.0.3/3D.0.4:

```bash
grep -R "docs/refactor" -n README.md COMMANDS.md CHANGELOG.md AGENTS.md docs || true
grep -R "docs/testing" -n README.md COMMANDS.md CHANGELOG.md AGENTS.md docs || true
grep -R "PROJECT_ARCHITECTURE_OVERVIEW.md" -n README.md COMMANDS.md CHANGELOG.md AGENTS.md docs || true
```

## 8. Risks

- Old stage reports intentionally contain stale claims. Reports must be indexed as historical records to avoid turning stale claims into current instructions.
- Moving `docs/stages/reports/STAGE_3D_0_2_TARGET_DOCS_STRUCTURE_PLAN.md` during Stage 3D.0.3 changes the location of the plan while Stage 3D.0 is still running. Active stage files must be updated to point at `docs/stages/reports/`.
- The user prompt references `docs/stages/active/...`, but the current task files are still flat under `docs/stages/`. Stage 3D.0.3 should resolve this mismatch.
- `BRAINSTORM.md` contains prohibited ideas. Archive indexes and `AGENTS.md` must say archive content is not current guidance.
- Renaming lowercase root docs such as `docs/sqlite_message_id_audit.md` should be limited to documentation paths and reflected in indexes.

## 9. Do-not-move list

Do not move in Stage 3D.0:

- `AGENTS.md`
- `README.md`
- `COMMANDS.md`
- `CHANGELOG.md`
- runtime/export directories such as `DB_EXPORTS/`, `exports/`, `LOGS/`
- runtime state files such as `messages.db`, `config.json`, `*.session`
- source code under `tg_msg_manager/`
- tests under `tests/`
- generated caches such as `.pytest_cache/`, `.ruff_cache/`, `__pycache__/`

Do not delete `.DS_Store` files as part of this stage unless a maintainer explicitly asks for cleanup. They are ignored by the docs indexes.

## 10. Next sub-stage checklist

Stage 3D.0.3 should:

- create target directories;
- move files according to this plan;
- preserve all historical content by moving rather than deleting;
- add clear archive/current status notes only where needed;
- update active Stage 3D.0 file references to current report paths;
- create `docs/stages/reports/STAGE_3D_0_3_DOCS_MIGRATION_REPORT.md`;
- run filesystem inventory checks;
- leave `AGENTS.md` rewrite for Stage 3D.0.5.
