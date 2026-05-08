# Stage 3D.0.3 - Docs Migration Report

## 1. Summary

Stage 3D.0.3 executed the Stage 3D.0.2 migration plan.

Completed:

- target docs directories created;
- active Stage 3D.0 task files moved to `docs/stages/active/`;
- completed task prompts moved to `docs/stages/completed/`;
- stage reports and baselines moved to `docs/stages/reports/`;
- current architecture docs moved to `docs/architecture/`;
- development and testing docs moved to `docs/development/`;
- roadmap moved to `docs/roadmap/`;
- deprecated backlog, old prompts, and superseded notes moved to `docs/archive/`;
- compact status headers added to active and completed task files;
- compact archive notices added to the main archived prompt/note files;
- active Stage 3D.0 path references normalized from `docs/refactor/` to `docs/stages/reports/`.

Not done in this sub-stage:

- `AGENTS.md` was not rewritten;
- full index files were not created;
- root `README.md`, `COMMANDS.md`, and `CHANGELOG.md` were not aligned yet;
- runtime code was not changed.

## 2. Directories created

- `docs/architecture/`
- `docs/development/`
- `docs/stages/active/`
- `docs/stages/completed/`
- `docs/stages/reports/`
- `docs/roadmap/`
- `docs/archive/`
- `docs/archive/legacy_notes/`
- `docs/archive/old_prompts/`
- `docs/archive/deprecated_stage_files/`

The old empty `docs/refactor/`, `docs/testing/`, and `backlog/` directories were removed after their files were moved.

## 3. Files moved

| Old path | New path | Reason |
| --- | --- | --- |
| `PROJECT_ARCHITECTURE_OVERVIEW.md` | `docs/architecture/PROJECT_ARCHITECTURE_OVERVIEW.md` | Current architecture snapshot. |
| `ROADMAP.md` | `docs/roadmap/ROADMAP.md` | Current roadmap. |
| `LOCAL_BACKLOG.md` | `docs/archive/legacy_notes/LOCAL_BACKLOG.md` | Closed local note. |
| `BRAINSTORM.md` | `docs/archive/old_prompts/BRAINSTORM.md` | Old prompt/brainstorm, not current guidance. |
| `docs/ARCHITECTURE_RULES.md` | `docs/architecture/ARCHITECTURE_RULES.md` | Current architecture rules. |
| `docs/PR_CHECKLIST.md` | `docs/development/PR_CHECKLIST.md` | Development checklist. |
| `docs/sqlite_message_id_audit.md` | `docs/architecture/SQLITE_MESSAGE_ID_AUDIT.md` | Current storage identity audit. |
| `docs/db_baseline_report.md` | `docs/archive/legacy_notes/DB_BASELINE_REPORT.md` | Historical database baseline. |
| `docs/export_smoke_scenarios.md` | `docs/archive/legacy_notes/EXPORT_SMOKE_SCENARIOS.md` | Historical smoke notes. |
| `docs/testing/LIVE_SMOKE_CHECKLIST.md` | `docs/development/LIVE_SMOKE_CHECKLIST.md` | Current testing guidance. |
| `docs/refactor/README.md` | `docs/archive/legacy_notes/REFACTOR_DOCS_INDEX.md` | Superseded refactor index. |
| `docs/refactor/CLI_CONTRACT.md` | `docs/development/CLI_CONTRACT.md` | Current CLI contract. |
| `docs/refactor/FACADE_SIZE_BASELINE.md` | `docs/development/FACADE_SIZE_BASELINE.md` | Development guardrail baseline. |
| `docs/refactor/LEGACY_INVENTORY.md` | `docs/archive/legacy_notes/LEGACY_INVENTORY.md` | Historical legacy inventory. |
| `docs/refactor/CONTEXT_ENGINE_SPLIT_MAP.md` | `docs/architecture/CONTEXT_ENGINE_SPLIT_MAP.md` | Current architecture map. |
| `docs/refactor/CONTEXT_RELATION_TABLES_DECISION.md` | `docs/architecture/CONTEXT_RELATION_TABLES_DECISION.md` | Current relation-table decision. |
| `docs/refactor/DB_EXPORT_ENTRYPOINT_AUDIT.md` | `docs/architecture/DB_EXPORT_ENTRYPOINT_AUDIT.md` | Current architecture note. |
| `docs/refactor/DB_EXPORT_SERVICE_SPLIT_MAP.md` | `docs/architecture/DB_EXPORT_SERVICE_SPLIT_MAP.md` | Current architecture map. |
| `docs/refactor/EXPORT_SERVICE_SPLIT_MAP.md` | `docs/architecture/EXPORT_SERVICE_SPLIT_MAP.md` | Current architecture map. |
| `docs/refactor/PAYLOADS_SPLIT_MAP.md` | `docs/architecture/PAYLOADS_SPLIT_MAP.md` | Current architecture map. |
| `docs/refactor/PRIVATE_ARCHIVE_ENTRYPOINT_AUDIT.md` | `docs/architecture/PRIVATE_ARCHIVE_ENTRYPOINT_AUDIT.md` | Current architecture note. |
| `docs/refactor/PRIVATE_ARCHIVE_IMPORT_RESOLUTION.md` | `docs/architecture/PRIVATE_ARCHIVE_IMPORT_RESOLUTION.md` | Current compatibility note. |
| `docs/refactor/PRIVATE_ARCHIVE_SPLIT_MAP.md` | `docs/architecture/PRIVATE_ARCHIVE_SPLIT_MAP.md` | Current architecture map. |
| `docs/refactor/SQLITE_WRITE_PATH_SPLIT_MAP.md` | `docs/architecture/SQLITE_WRITE_PATH_SPLIT_MAP.md` | Current architecture map. |
| `docs/refactor/STORAGE_CONTRACT_SPLIT_MAP.md` | `docs/architecture/STORAGE_CONTRACT_SPLIT_MAP.md` | Current architecture map. |
| `docs/refactor/STAGE_3C_CHANNEL_DISCUSSION_CONTEXT_EXPORT_DESIGN.md` | `docs/architecture/STAGE_3C_CHANNEL_DISCUSSION_CONTEXT_EXPORT_DESIGN.md` | Current discussion export architecture design. |
| `docs/refactor/STAGE_0_*.md` | `docs/stages/reports/STAGE_0_*.md` | Stage 0 records and reports. |
| `docs/refactor/STAGE_1_*.md` | `docs/stages/reports/STAGE_1_*.md` | Stage 1 records and reports. |
| `docs/refactor/STAGE_2_*.md` | `docs/stages/reports/STAGE_2_*.md` | Stage 2 records and reports. |
| `docs/refactor/STAGE_3A*.md` | `docs/stages/reports/STAGE_3A*.md` | Stage 3A records and reports. |
| `docs/refactor/STAGE_3B*.md` | `docs/stages/reports/STAGE_3B*.md` | Stage 3B records and reports. |
| `docs/refactor/STAGE_3C_*_REPORT.md` | `docs/stages/reports/STAGE_3C_*_REPORT.md` | Stage 3C reports. |
| `docs/refactor/STAGE_3D_0_1_DOCUMENTATION_AUDIT.md` | `docs/stages/reports/STAGE_3D_0_1_DOCUMENTATION_AUDIT.md` | Stage 3D.0 report. |
| `docs/refactor/STAGE_3D_0_2_TARGET_DOCS_STRUCTURE_PLAN.md` | `docs/stages/reports/STAGE_3D_0_2_TARGET_DOCS_STRUCTURE_PLAN.md` | Stage 3D.0 report. |
| `docs/stages/stage_3d_0_*.md` | `docs/stages/active/stage_3d_0_*.md` | Active Stage 3D.0 tasks. |
| `docs/stages/stage_3c_*.md` | `docs/stages/completed/stage_3c_*.md` | Completed Stage 3C tasks. |
| `docs/stages/stage_3b*.md` | `docs/stages/completed/stage_3b*.md` | Completed Stage 3B tasks. |
| `docs/stages/stage_3a_*codex_tasks.md` | `docs/stages/completed/stage_3a_*codex_tasks.md` | Completed Stage 3A tasks. |
| `docs/stages/stage_3a_direct_channel_export_agent_tasks.md` | `docs/stages/completed/stage_3a_direct_channel_export_agent_tasks.md` | Completed Stage 3A task. |
| `docs/stages/stage_3a_direct_channel_export_backlog.md` | `docs/archive/deprecated_stage_files/stage_3a_direct_channel_export_backlog.md` | Superseded Stage 3A backlog. |
| `backlog/stage_1_consistency_pass.md` | `docs/archive/deprecated_stage_files/stage_1_consistency_pass.md` | Deprecated stage prompt. |
| `backlog/stage_1_db_export_archive_storage_refactor.md` | `docs/archive/deprecated_stage_files/stage_1_db_export_archive_storage_refactor.md` | Deprecated stage prompt. |
| `backlog/stage_2_readiness_hardening.md` | `docs/archive/deprecated_stage_files/stage_2_readiness_hardening.md` | Deprecated stage prompt. |
| `backlog/archive/*.md` | `docs/archive/deprecated_stage_files/` | Existing backlog archive moved into docs archive. |

## 4. Files archived

Archived as legacy notes:

- `docs/archive/legacy_notes/DB_BASELINE_REPORT.md`
- `docs/archive/legacy_notes/EXPORT_SMOKE_SCENARIOS.md`
- `docs/archive/legacy_notes/LEGACY_INVENTORY.md`
- `docs/archive/legacy_notes/LOCAL_BACKLOG.md`
- `docs/archive/legacy_notes/REFACTOR_DOCS_INDEX.md`

Archived as old prompts:

- `docs/archive/old_prompts/BRAINSTORM.md`

Archived as deprecated stage files:

- `docs/archive/deprecated_stage_files/TODO.md`
- `docs/archive/deprecated_stage_files/backlog_archive_README.md`
- `docs/archive/deprecated_stage_files/refactor.md`
- `docs/archive/deprecated_stage_files/sqlite_architecture_hardening_todo.md`
- `docs/archive/deprecated_stage_files/stage_0_refactor_baseline.md`
- `docs/archive/deprecated_stage_files/stage_1_consistency_pass.md`
- `docs/archive/deprecated_stage_files/stage_1_db_export_archive_storage_refactor.md`
- `docs/archive/deprecated_stage_files/stage_2_readiness_hardening.md`
- `docs/archive/deprecated_stage_files/stage_3a_direct_channel_export_backlog.md`
- `docs/archive/deprecated_stage_files/stagt_0.md`
- `docs/archive/deprecated_stage_files/stagt_1.md`
- `docs/archive/deprecated_stage_files/stagt_2.md`
- `docs/archive/deprecated_stage_files/stagt_3.md`
- `docs/archive/deprecated_stage_files/stagt_4.md`
- `docs/archive/deprecated_stage_files/stagt_5.md`
- `docs/archive/deprecated_stage_files/stagt_6_legacy.md`
- `docs/archive/deprecated_stage_files/stagt_7_legacy.md`
- `docs/archive/deprecated_stage_files/stagt_8_legacy.md`

## 5. Files left in place

- `AGENTS.md`
- `README.md`
- `COMMANDS.md`
- `CHANGELOG.md`
- runtime/export/state files and directories
- source files under `tg_msg_manager/`
- tests under `tests/`
- generated local cache files
- `.DS_Store` files under `docs/`

## 6. Status headers added

Active status headers were added to:

- `docs/stages/active/stage_3d_0_1_documentation_audit.md`
- `docs/stages/active/stage_3d_0_2_target_structure_and_migration_plan.md`
- `docs/stages/active/stage_3d_0_3_move_and_normalize_documentation.md`
- `docs/stages/active/stage_3d_0_4_documentation_indexes_and_navigation.md`
- `docs/stages/active/stage_3d_0_5_agents_md_rewrite.md`
- `docs/stages/active/stage_3d_0_6_root_readme_commands_changelog_alignment.md`
- `docs/stages/active/stage_3d_0_7_verification_and_governance_report.md`
- `docs/stages/active/stage_3d_0_general_prompt.md`

Completed status headers were added to completed Stage 3A, Stage 3B, and Stage 3C task prompts under `docs/stages/completed/`.

Archive notices were added to:

- `docs/archive/deprecated_stage_files/stage_3a_direct_channel_export_backlog.md`
- `docs/archive/old_prompts/BRAINSTORM.md`
- `docs/archive/legacy_notes/LOCAL_BACKLOG.md`

## 7. Known path references still needing update

To handle in Stage 3D.0.4 through Stage 3D.0.6:

- `AGENTS.md` still references old docs paths and must wait for Stage 3D.0.5.
- `README.md`, `COMMANDS.md`, and `CHANGELOG.md` still need navigation alignment in Stage 3D.0.6.
- Historical reports can still mention old paths such as `docs/refactor/`; indexes must label reports as historical.
- `docs/architecture/PROJECT_ARCHITECTURE_OVERVIEW.md` is still a 2026-05-05 snapshot and should be treated as a snapshot until a separate architecture refresh updates it.
- Active Stage 3D.0 files still include grep checks for `docs/refactor` strings; those checks are intentional stale-reference detection commands.

## 8. Runtime behavior statement

No runtime behavior changed.

This stage did not change:

- CLI command names or flags;
- export behavior;
- `db-export` behavior;
- `export-pm` behavior;
- `export-channel` behavior;
- retry/report/clean/delete/schedule/setup behavior;
- SQLite schema;
- migrations;
- source code under `tg_msg_manager/`;
- tests under `tests/`.

## 9. Next sub-stage recommendation

Proceed to Stage 3D.0.4.

Next stage should create the docs index files and make navigation explicit:

- `docs/README.md`
- `docs/architecture/README.md`
- `docs/development/README.md`
- `docs/stages/README.md`
- `docs/roadmap/README.md`
- `docs/archive/README.md`
