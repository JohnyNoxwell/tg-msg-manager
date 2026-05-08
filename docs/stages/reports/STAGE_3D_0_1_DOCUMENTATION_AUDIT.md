# Stage 3D.0.1 - Documentation Audit

## 1. Summary

Stage 3D.0.1 audited the repository documentation layout before any file moves.

No runtime code was changed. No docs were moved. `AGENTS.md` was not rewritten.

Inventory results:

- Root documentation files: 8 relevant Markdown files plus `COMMANDS.md` and `CHANGELOG.md`.
- `docs/` Markdown files: 62.
- Stage task files currently under `docs/stages/`: 17.
- Refactor/report/support files currently under `docs/refactor/`: 39 before this audit, 40 after this audit.
- Testing docs: `docs/testing/LIVE_SMOKE_CHECKLIST.md` plus legacy `docs/export_smoke_scenarios.md`.

The current tree mixes active task prompts, completed task prompts, reports, architecture notes, testing docs, roadmap/backlog notes, and historical baselines. Stage 3D.0 should reorganize them into stable current docs, stage records, reports, roadmap, and archive sections.

## 2. Current root docs

| Current path | Classification | Notes |
| --- | --- | --- |
| `AGENTS.md` | current_development_rule | Current large agent rulebook. Should become concise repository-level contract in Stage 3D.0.5. |
| `README.md` | current_cli_doc | Main bilingual user-facing command and behavior document. Needs links to new docs tree after migration. |
| `COMMANDS.md` | current_cli_doc | Focused command reference, currently mostly `export-channel` and interactive menu. |
| `CHANGELOG.md` | current_development_rule | Current historical change record. Should add Stage 3D.0 docs/governance entry only after migration. |
| `PROJECT_ARCHITECTURE_OVERVIEW.md` | current_architecture | Large architecture snapshot. Current enough to preserve, but should move under `docs/architecture/`. |
| `ROADMAP.md` | roadmap | Current roadmap with completed foundation status and future directions. Should move under `docs/roadmap/`. |
| `LOCAL_BACKLOG.md` | archive_candidate | Local closed note about a specific verification item. Should archive. |
| `BRAINSTORM.md` | archive_candidate | Contains OSINT/profiling/product brainstorming that is not current governance. Should archive and mark non-guidance. |

Other root files found by `find . -maxdepth 2 -type f` include runtime/export artifacts such as `DB_TARGETS.txt` and files under `DB_EXPORTS/`. They are not documentation governance inputs.

## 3. Current docs tree

Current `docs/` top-level:

- `docs/ARCHITECTURE_RULES.md`
- `docs/PR_CHECKLIST.md`
- `docs/db_baseline_report.md`
- `docs/export_smoke_scenarios.md`
- `docs/sqlite_message_id_audit.md`
- `docs/refactor/`
- `docs/stages/`
- `docs/testing/`

Non-document files:

- `docs/.DS_Store`
- `docs/stages/.DS_Store`

These `.DS_Store` files should not be indexed as documentation and can be ignored or removed outside the stage if cleanup is explicitly requested.

## 4. Stage task files

Current active-or-recent task prompt files live flat under `docs/stages/`. This is ambiguous because active, completed, and prompt files are not separated.

| Current path | Classification | Recommended target | Action |
| --- | --- | --- | --- |
| `docs/stages/stage_3d_0_1_documentation_audit.md` | active_stage_task | `docs/stages/active/stage_3d_0_1_documentation_audit.md` | Move during Stage 3D.0.3 after migration plan. |
| `docs/stages/stage_3d_0_2_target_structure_and_migration_plan.md` | active_stage_task | `docs/stages/active/stage_3d_0_2_target_structure_and_migration_plan.md` | Move during Stage 3D.0.3. |
| `docs/stages/stage_3d_0_3_move_and_normalize_documentation.md` | active_stage_task | `docs/stages/active/stage_3d_0_3_move_and_normalize_documentation.md` | Move during Stage 3D.0.3. |
| `docs/stages/stage_3d_0_4_documentation_indexes_and_navigation.md` | active_stage_task | `docs/stages/active/stage_3d_0_4_documentation_indexes_and_navigation.md` | Move during Stage 3D.0.3. |
| `docs/stages/stage_3d_0_5_agents_md_rewrite.md` | active_stage_task | `docs/stages/active/stage_3d_0_5_agents_md_rewrite.md` | Move during Stage 3D.0.3. |
| `docs/stages/stage_3d_0_6_root_readme_commands_changelog_alignment.md` | active_stage_task | `docs/stages/active/stage_3d_0_6_root_readme_commands_changelog_alignment.md` | Move during Stage 3D.0.3. |
| `docs/stages/stage_3d_0_7_verification_and_governance_report.md` | active_stage_task | `docs/stages/active/stage_3d_0_7_verification_and_governance_report.md` | Move during Stage 3D.0.3. |
| `docs/stages/stage_3d_0_general_prompt.md` | active_stage_task | `docs/stages/active/stage_3d_0_general_prompt.md` | Move with active Stage 3D.0 prompts. |
| `docs/stages/stage_3c_1_discussion_architecture_contract.md` | completed_stage_task | `docs/stages/completed/stage_3c_1_discussion_architecture_contract.md` | Move to completed history. |
| `docs/stages/stage_3c_2_discussion_resolver_and_models.md` | completed_stage_task | `docs/stages/completed/stage_3c_2_discussion_resolver_and_models.md` | Move to completed history. |
| `docs/stages/stage_3c_3_discussion_fetch_and_writers.md` | completed_stage_task | `docs/stages/completed/stage_3c_3_discussion_fetch_and_writers.md` | Move to completed history. |
| `docs/stages/stage_3c_4_discussion_integration_tests_docs.md` | completed_stage_task | `docs/stages/completed/stage_3c_4_discussion_integration_tests_docs.md` | Move to completed history. |
| `docs/stages/stage_3b_1_channel_export_stabilization_pass_codex_tasks.md` | completed_stage_task | `docs/stages/completed/stage_3b_1_channel_export_stabilization_pass_codex_tasks.md` | Move to completed history. |
| `docs/stages/stage_3b_media_download_hardening_codex_tasks.md` | completed_stage_task | `docs/stages/completed/stage_3b_media_download_hardening_codex_tasks.md` | Move to completed history. |
| `docs/stages/stage_3a_1_channel_export_operational_hardening_codex_tasks.md` | completed_stage_task | `docs/stages/completed/stage_3a_1_channel_export_operational_hardening_codex_tasks.md` | Move to completed history. |
| `docs/stages/stage_3a_direct_channel_export_agent_tasks.md` | completed_stage_task | `docs/stages/completed/stage_3a_direct_channel_export_agent_tasks.md` | Move to completed history. |
| `docs/stages/stage_3a_direct_channel_export_backlog.md` | backlog | `docs/roadmap/stage_3a_direct_channel_export_backlog.md` or `docs/archive/deprecated_stage_files/` | Prefer archive if superseded by Stage 3A reports. |

## 5. Stage reports

Current stage reports and baselines live under `docs/refactor/`:

- Stage 0: `STAGE_0_BASELINE.md`, `STAGE_0_CLI_SURFACE.md`, `STAGE_0_SCRIPT_AUDIT.md`, `STAGE_0_SMOKE_SCENARIOS.md`, `STAGE_0_SQLITE_READ_INVENTORY.md`, `STAGE_0_STORAGE_DECISIONS.md`, `STAGE_0_REFACTOR_REPORT.md`, `STAGE_0_FINAL_REPORT.md`
- Stage 1: `STAGE_1_BASELINE.md`, `STAGE_1_REFACTOR_REPORT.md`, `STAGE_1_CONSISTENCY_BASELINE.md`, `STAGE_1_CONSISTENCY_REPORT.md`
- Stage 2: `STAGE_2_READINESS_BASELINE.md`, `STAGE_2_READINESS_REPORT.md`
- Stage 3A: `STAGE_3A_BASELINE.md`, `STAGE_3A_DIRECT_CHANNEL_EXPORT_REPORT.md`
- Stage 3A.1: `STAGE_3A_1_BASELINE.md`, `STAGE_3A_1_CHANNEL_EXPORT_OPERATIONAL_HARDENING_REPORT.md`
- Stage 3B: `STAGE_3B_MEDIA_DOWNLOAD_HARDENING_REPORT.md`
- Stage 3B.1: `STAGE_3B_1_CHANNEL_EXPORT_STABILIZATION_REPORT.md`
- Stage 3C: `STAGE_3C_CHANNEL_DISCUSSION_CONTEXT_EXPORT_DESIGN.md`, `STAGE_3C_CHANNEL_DISCUSSION_CONTEXT_EXPORT_REPORT.md`, `STAGE_3C_2_DISCUSSION_RESOLVER_AND_MODELS_REPORT.md`, `STAGE_3C_3_DISCUSSION_FETCH_AND_WRITERS_REPORT.md`
- Stage 3D.0: this audit report

Recommended target for factual stage reports: `docs/stages/reports/`.

Baselines and split maps can either move to `docs/stages/reports/` as historical records or to `docs/architecture/` when they are still current architecture references. The migration plan should separate current rules from historical baselines.

## 6. Architecture docs

Current architecture-like docs:

- `PROJECT_ARCHITECTURE_OVERVIEW.md`
- `docs/ARCHITECTURE_RULES.md`
- `docs/sqlite_message_id_audit.md`
- `docs/refactor/CLI_CONTRACT.md`
- `docs/refactor/CONTEXT_ENGINE_SPLIT_MAP.md`
- `docs/architecture/CONTEXT_RELATION_TABLES_DECISION.md`
- `docs/refactor/DB_EXPORT_ENTRYPOINT_AUDIT.md`
- `docs/refactor/DB_EXPORT_SERVICE_SPLIT_MAP.md`
- `docs/refactor/EXPORT_SERVICE_SPLIT_MAP.md`
- `docs/refactor/FACADE_SIZE_BASELINE.md`
- `docs/refactor/PAYLOADS_SPLIT_MAP.md`
- `docs/refactor/PRIVATE_ARCHIVE_ENTRYPOINT_AUDIT.md`
- `docs/refactor/PRIVATE_ARCHIVE_IMPORT_RESOLUTION.md`
- `docs/refactor/PRIVATE_ARCHIVE_SPLIT_MAP.md`
- `docs/refactor/SQLITE_WRITE_PATH_SPLIT_MAP.md`
- `docs/refactor/STORAGE_CONTRACT_SPLIT_MAP.md`
- `docs/refactor/STAGE_3C_CHANNEL_DISCUSSION_CONTEXT_EXPORT_DESIGN.md`

Recommended target:

- Current architecture and rules: `docs/architecture/`.
- Developer workflow and checks: `docs/development/`.
- Historical split maps and baselines: `docs/stages/reports/` or `docs/archive/legacy_notes/` depending on currency.

## 7. Development/testing docs

Current development/testing docs:

- `docs/PR_CHECKLIST.md`
- `docs/testing/LIVE_SMOKE_CHECKLIST.md`
- `docs/export_smoke_scenarios.md`
- `docs/refactor/README.md`
- `docs/refactor/LEGACY_INVENTORY.md`
- Stage-specific verification notes embedded in `docs/refactor/STAGE_*` reports.

Recommended target:

- `docs/development/PR_CHECKLIST.md`
- `docs/development/TESTING.md` or `docs/development/LIVE_SMOKE_CHECKLIST.md`
- `docs/development/AGENT_WORKFLOW.md`
- Historical smoke scenarios can move to `docs/archive/legacy_notes/` if superseded by live smoke docs.

## 8. Roadmap/backlog docs

Current roadmap/backlog-like docs:

- `ROADMAP.md`
- `LOCAL_BACKLOG.md`
- `BRAINSTORM.md`
- `backlog/stage_1_consistency_pass.md`
- `backlog/stage_1_db_export_archive_storage_refactor.md`
- `backlog/stage_2_readiness_hardening.md`
- `backlog/archive/*.md`
- `docs/stages/stage_3a_direct_channel_export_backlog.md`

Recommended target:

- Current product roadmap: `docs/roadmap/ROADMAP.md`.
- Safe backlog with current governance: `docs/roadmap/BACKLOG.md` or `docs/roadmap/DEFERRED.md`.
- OSINT/profiling brainstorm and old backlog archive: `docs/archive/old_prompts/` or `docs/archive/legacy_notes/`, clearly marked as non-current guidance.

## 9. Archive/deprecated candidates

Archive candidates:

- `BRAINSTORM.md`: contains OSINT/profiling, sentiment, bot/user profiling, dossier concepts that are explicitly forbidden for Stage 3D.0 and should not guide current work.
- `LOCAL_BACKLOG.md`: closed local note.
- `backlog/archive/*.md`: already archived, but outside the target docs tree.
- `docs/db_baseline_report.md`: historical pre-hardening DB baseline.
- `docs/export_smoke_scenarios.md`: historical smoke scenarios likely superseded by `docs/testing/LIVE_SMOKE_CHECKLIST.md`.
- `docs/refactor/STAGE_3A_DIRECT_CHANNEL_EXPORT_REPORT.md`: has stale statements that `--media full` is not implemented. Keep as historical report, but do not treat as current behavior.
- Stage task prompt files for completed Stage 3A/3B/3C work: keep as history under `docs/stages/completed/`.

## 10. Duplicate/stale content

Detected stale or duplicate claims to handle in later stages:

| Path | Stale or duplicate claim | Later action |
| --- | --- | --- |
| `docs/refactor/STAGE_3A_DIRECT_CHANNEL_EXPORT_REPORT.md` | Says `--media full` is exposed but blocked/not implemented. Current README/COMMANDS/CHANGELOG say Stage 3B implemented controlled full media. | Keep as historical report under `docs/stages/reports/`; index as historical, not current behavior. |
| `docs/refactor/STAGE_3C_3_DISCUSSION_FETCH_AND_WRITERS_REPORT.md` | Says full integration into `export-channel` remains Stage 3C.4 work. Current README/COMMANDS/CHANGELOG indicate Stage 3C integration exists. | Keep as Stage 3C.3 historical report; current docs should point to final Stage 3C report. |
| `PROJECT_ARCHITECTURE_OVERVIEW.md` | Header says snapshot from 2026-05-05 and post-Stage-2 status even though Stage 3C is now documented in README/CHANGELOG. | Move to architecture and mark as architecture snapshot or refresh in a later architecture-specific task. |
| `ROADMAP.md` | Includes future analytics/dashboard/search directions that are not active Stage 3D.0 work. | Move to roadmap and ensure AGENTS says roadmap is not automatic authorization. |
| `BRAINSTORM.md` | Contains OSINT/profiling/sentiment/dossier ideas forbidden by Stage 3D.0. | Archive and mark not current guidance. |
| `docs/refactor/README.md` | Index stops at Stage 3B.1 and omits Stage 3C reports. | Supersede with `docs/stages/README.md` and reports index. |
| `AGENTS.md` | Large full rule dump and old path references to `docs/refactor/*.md`. | Rewrite after docs paths are stable in Stage 3D.0.5. |
| `docs/ARCHITECTURE_RULES.md` | Duplicates much of `AGENTS.md`; references `docs/architecture/CONTEXT_RELATION_TABLES_DECISION.md`. | Move under `docs/architecture/` and update references after migration. |

No current root README/COMMANDS claims were found saying `--media full` is not implemented for channel posts. Both correctly state that discussion comment full media remains unimplemented.

## 11. Broken or suspicious references

Suspicious or soon-to-be-stale references:

- `docs/stages/stage_3d_0_general_prompt.md` references `docs/stages/active/...` paths that do not exist yet. This is target-state guidance, not current-state breakage.
- `AGENTS.md` references `docs/refactor/*.md` and `docs/testing/LIVE_SMOKE_CHECKLIST.md`; these paths should be updated after migration.
- `docs/ARCHITECTURE_RULES.md` references `docs/architecture/CONTEXT_RELATION_TABLES_DECISION.md`; update when moved.
- `PROJECT_ARCHITECTURE_OVERVIEW.md` references `backlog/archive/TODO.md`; this file exists but is outside the target docs tree.
- Stage prompt files contain many references to old locations such as `docs/refactor/STAGE_*`. Historical task files can keep old references if indexed as historical, but active Stage 3D.0 files should be path-normalized after moves.

No fixes were applied in this audit stage.

## 12. Recommended migration map

| Current path | Classification | Recommended target | Action |
| --- | --- | --- | --- |
| `AGENTS.md` | current_development_rule | keep root | Rewrite only in Stage 3D.0.5 after docs indexes exist. |
| `README.md` | current_cli_doc | keep root | Align links in Stage 3D.0.6. |
| `COMMANDS.md` | current_cli_doc | keep root | Align docs references in Stage 3D.0.6. |
| `CHANGELOG.md` | current_development_rule | keep root | Add Stage 3D.0 docs/governance entry in Stage 3D.0.6. |
| `PROJECT_ARCHITECTURE_OVERVIEW.md` | current_architecture | `docs/architecture/PROJECT_ARCHITECTURE_OVERVIEW.md` | Move. |
| `docs/ARCHITECTURE_RULES.md` | current_architecture | `docs/architecture/ARCHITECTURE_RULES.md` | Move and update references. |
| `docs/sqlite_message_id_audit.md` | current_architecture | `docs/architecture/SQLITE_MESSAGE_ID_AUDIT.md` | Move. |
| `docs/PR_CHECKLIST.md` | current_development_rule | `docs/development/PR_CHECKLIST.md` | Move. |
| `docs/testing/LIVE_SMOKE_CHECKLIST.md` | current_testing_doc | `docs/development/LIVE_SMOKE_CHECKLIST.md` | Move or index from development. |
| `docs/export_smoke_scenarios.md` | current_testing_doc | `docs/archive/legacy_notes/export_smoke_scenarios.md` | Archive as historical smoke notes unless still needed. |
| `docs/db_baseline_report.md` | archive_candidate | `docs/archive/legacy_notes/db_baseline_report.md` | Archive as historical baseline. |
| `docs/refactor/CLI_CONTRACT.md` | current_cli_doc | `docs/development/CLI_CONTRACT.md` | Move. |
| `docs/architecture/CONTEXT_RELATION_TABLES_DECISION.md` | current_architecture | `docs/architecture/CONTEXT_RELATION_TABLES_DECISION.md` | Move and update references. |
| `docs/refactor/*_SPLIT_MAP.md` | current_architecture | `docs/architecture/` or `docs/archive/legacy_notes/` | Keep current maps in architecture if still useful; archive stale maps. |
| `docs/refactor/*ENTRYPOINT_AUDIT.md` | current_architecture | `docs/architecture/` or `docs/archive/legacy_notes/` | Preserve; classify currency in migration plan. |
| `docs/refactor/FACADE_SIZE_BASELINE.md` | current_development_rule | `docs/development/FACADE_SIZE_BASELINE.md` | Move. |
| `docs/refactor/LEGACY_INVENTORY.md` | archive_candidate | `docs/archive/legacy_notes/LEGACY_INVENTORY.md` | Archive. |
| `docs/refactor/STAGE_*.md` | stage_report | `docs/stages/reports/` | Move factual reports/baselines to reports. |
| `docs/refactor/STAGE_3C_CHANNEL_DISCUSSION_CONTEXT_EXPORT_DESIGN.md` | current_architecture | `docs/architecture/DISCUSSION_EXPORT.md` or `docs/stages/reports/` | Preserve current architecture content; plan exact target next. |
| `docs/refactor/README.md` | duplicate | `docs/archive/legacy_notes/refactor_README.md` | Supersede with `docs/stages/README.md`. |
| `docs/stages/stage_3d_0_*.md` | active_stage_task | `docs/stages/active/` | Move in Stage 3D.0.3. |
| `docs/stages/stage_3c_*.md` | completed_stage_task | `docs/stages/completed/` | Move in Stage 3D.0.3. |
| `docs/stages/stage_3b*.md` | completed_stage_task | `docs/stages/completed/` | Move in Stage 3D.0.3. |
| `docs/stages/stage_3a*.md` | completed_stage_task | `docs/stages/completed/` | Move in Stage 3D.0.3, except backlog may archive. |
| `ROADMAP.md` | roadmap | `docs/roadmap/ROADMAP.md` | Move. |
| `LOCAL_BACKLOG.md` | archive_candidate | `docs/archive/legacy_notes/LOCAL_BACKLOG.md` | Archive. |
| `BRAINSTORM.md` | archive_candidate | `docs/archive/old_prompts/BRAINSTORM.md` | Archive and mark non-current guidance. |
| `backlog/*.md` | backlog | `docs/archive/deprecated_stage_files/` | Archive unless a maintainer reactivates them. |
| `backlog/archive/*.md` | archive_candidate | `docs/archive/deprecated_stage_files/` | Move archive into target docs archive. |

## 13. Risks

- Historical stage reports contain intentionally stale statements. Indexes must label them as historical records so agents do not treat them as current behavior.
- Moving documents will break old inline references unless Stage 3D.0.3 and Stage 3D.0.4 update navigation and path references carefully.
- `AGENTS.md` currently duplicates detailed architecture rules. Rewriting it too early would create unstable references; keep the ordered stage plan.
- Roadmap and brainstorm content includes analytics/OSINT/profiling ideas. It must not be interpreted as active permission for Stage 3D.0 or future agent work.
- `PROJECT_ARCHITECTURE_OVERVIEW.md` is a useful snapshot but may not fully reflect Stage 3C. It should not be the only current architecture source until refreshed or clearly labeled.

## 14. Next sub-stage recommendation

Proceed to Stage 3D.0.2.

The migration plan should:

1. Create the target structure under `docs/`.
2. Keep active Stage 3D.0 task files separate from completed historical task prompts.
3. Move factual reports into `docs/stages/reports/`.
4. Move current architecture/development docs out of `docs/refactor/`.
5. Archive brainstorm/old prompt/deprecated backlog files as non-current guidance.
6. Define which path references must be updated in Stage 3D.0.3 and Stage 3D.0.4.
