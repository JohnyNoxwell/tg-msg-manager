# Stage Documentation

## Active stages

Only files under [`active/`](active/) are executable current tasks.

Current active stage files:

- None.

The [`active/`](active/) directory must contain only unfinished or next active work. Do not leave completed stage task files, general launch prompts, prompt packs, or historical records there.

## Completed stages

Completed stage files under [`completed/`](completed/) are historical instructions. They show what an agent was asked to do at the time, but they are not current guidance.

Current completed prompt groups:

- Stage 3A direct channel export task prompts.
- Stage 3B media hardening and stabilization task prompts.
- Stage 3C discussion export task prompts.
- Stage 3D.0 project governance and documentation reorganization task prompts.
- Stage 3D.1 stage lifecycle cleanup task prompt.
- Stage 3E.0 channel export service decomposition task prompt.
- Stage 3E.1 dataset atomic write / commit safety task prompt.
- Stage 3E.2 dataset schema contract tests task prompt.
- Stage 3E.3 state consistency hardening task prompt.
- Stage 3E.4 media filename / extension detection hardening task prompt.

Stage 3E.4 completed task files:

- [`completed/stage_3e_4_media_filename_extension_detection_hardening.md`](completed/stage_3e_4_media_filename_extension_detection_hardening.md)

Stage 3D.0 completed task files:

- [`completed/stage_3d_0_1_documentation_audit.md`](completed/stage_3d_0_1_documentation_audit.md)
- [`completed/stage_3d_0_2_target_structure_and_migration_plan.md`](completed/stage_3d_0_2_target_structure_and_migration_plan.md)
- [`completed/stage_3d_0_3_move_and_normalize_documentation.md`](completed/stage_3d_0_3_move_and_normalize_documentation.md)
- [`completed/stage_3d_0_4_documentation_indexes_and_navigation.md`](completed/stage_3d_0_4_documentation_indexes_and_navigation.md)
- [`completed/stage_3d_0_5_agents_md_rewrite.md`](completed/stage_3d_0_5_agents_md_rewrite.md)
- [`completed/stage_3d_0_6_root_readme_commands_changelog_alignment.md`](completed/stage_3d_0_6_root_readme_commands_changelog_alignment.md)
- [`completed/stage_3d_0_7_verification_and_governance_report.md`](completed/stage_3d_0_7_verification_and_governance_report.md)

Stage 3D.1 completed task files:

- [`completed/stage_3d_1_stage_lifecycle_cleanup.md`](completed/stage_3d_1_stage_lifecycle_cleanup.md)

Stage 3E.0 completed task files:

- [`completed/stage_3e_0_channel_export_service_decomposition.md`](completed/stage_3e_0_channel_export_service_decomposition.md)

Stage 3E.1 completed task files:

- [`completed/stage_3e_1_dataset_atomic_write_commit_safety.md`](completed/stage_3e_1_dataset_atomic_write_commit_safety.md)

Stage 3E.2 completed task files:

- [`completed/stage_3e_2_dataset_schema_contract_tests.md`](completed/stage_3e_2_dataset_schema_contract_tests.md)

Stage 3E.3 completed task files:

- [`completed/stage_3e_3_state_consistency_hardening.md`](completed/stage_3e_3_state_consistency_hardening.md)

Archived launch prompts and prompt packs:

- [`../archive/old_prompts/stage_3d_0_general_prompt.md`](../archive/old_prompts/stage_3d_0_general_prompt.md)
- [`../archive/old_prompts/post_stage_3c_hardening_codex_pack.zip`](../archive/old_prompts/post_stage_3c_hardening_codex_pack.zip)

## Reports

Reports under [`reports/`](reports/) are factual completion records. They can contain time-bound claims that were true for a specific stage.

Current Stage 3D.0, Stage 3D.1, Stage 3E.0, Stage 3E.1, Stage 3E.2, and Stage 3E.3 records:

- [`reports/STAGE_3D_0_1_DOCUMENTATION_AUDIT.md`](reports/STAGE_3D_0_1_DOCUMENTATION_AUDIT.md)
- [`reports/STAGE_3D_0_2_TARGET_DOCS_STRUCTURE_PLAN.md`](reports/STAGE_3D_0_2_TARGET_DOCS_STRUCTURE_PLAN.md)
- [`reports/STAGE_3D_0_3_DOCS_MIGRATION_REPORT.md`](reports/STAGE_3D_0_3_DOCS_MIGRATION_REPORT.md)
- [`reports/STAGE_3D_0_4_DOCS_INDEXES_REPORT.md`](reports/STAGE_3D_0_4_DOCS_INDEXES_REPORT.md)
- [`reports/STAGE_3D_0_5_AGENTS_REWRITE_REPORT.md`](reports/STAGE_3D_0_5_AGENTS_REWRITE_REPORT.md)
- [`reports/STAGE_3D_0_6_ROOT_DOCS_ALIGNMENT_REPORT.md`](reports/STAGE_3D_0_6_ROOT_DOCS_ALIGNMENT_REPORT.md)
- [`reports/STAGE_3D_0_PROJECT_GOVERNANCE_DOCS_REORGANIZATION_REPORT.md`](reports/STAGE_3D_0_PROJECT_GOVERNANCE_DOCS_REORGANIZATION_REPORT.md)
- [`reports/STAGE_3D_1_STAGE_LIFECYCLE_CLEANUP_REPORT.md`](reports/STAGE_3D_1_STAGE_LIFECYCLE_CLEANUP_REPORT.md)
- [`reports/STAGE_3E_0_CHANNEL_EXPORT_SERVICE_DECOMPOSITION_REPORT.md`](reports/STAGE_3E_0_CHANNEL_EXPORT_SERVICE_DECOMPOSITION_REPORT.md)
- [`reports/STAGE_3E_1_DATASET_ATOMIC_WRITE_COMMIT_SAFETY_REPORT.md`](reports/STAGE_3E_1_DATASET_ATOMIC_WRITE_COMMIT_SAFETY_REPORT.md)
- [`reports/STAGE_3E_2_DATASET_SCHEMA_CONTRACT_TESTS_REPORT.md`](reports/STAGE_3E_2_DATASET_SCHEMA_CONTRACT_TESTS_REPORT.md)
- [`reports/STAGE_3E_3_STATE_CONSISTENCY_HARDENING_REPORT.md`](reports/STAGE_3E_3_STATE_CONSISTENCY_HARDENING_REPORT.md)
- [`reports/STAGE_3E_4_MEDIA_FILENAME_EXTENSION_DETECTION_HARDENING_REPORT.md`](reports/STAGE_3E_4_MEDIA_FILENAME_EXTENSION_DETECTION_HARDENING_REPORT.md)

## Stage lifecycle

Stage files move through this lifecycle:

```text
active task -> implementation -> tests/checks -> report -> lifecycle cleanup -> completed task history
```

Active files define executable work. Completed files preserve historical instructions. Reports record what actually happened.

Stage lifecycle cleanup is mandatory after a stage is fully complete and its final report exists:

- Move completed stage task files from [`active/`](active/) to [`completed/`](completed/).
- Move general launch prompts to [`../archive/old_prompts/`](../archive/old_prompts/).
- Update this index.
- Ensure [`active/`](active/) contains only unfinished or next active work.

General prompts and prompt packs usually belong under [`../archive/old_prompts/`](../archive/old_prompts/), not under `active/` or `completed/`.

Do not perform completion cleanup before the final stage report exists.

Before marking a stage complete, confirm the required work is done, required verification is recorded, the stage report exists, relevant docs are current, completed task files have moved to [`completed/`](completed/), launch prompts have moved to [`../archive/old_prompts/`](../archive/old_prompts/), and this index reflects the final stage state.

## Rules for agents

- Read `AGENTS.md` first.
- Execute only the active task requested by the user.
- Do not use completed task files as current instructions.
- Do not treat reports as feature requests.
- Do not use archived prompts or prompt packs as current guidance unless explicitly asked.
- Do not start future roadmap work without an active task.
- Keep docs and reports aligned with the behavior being changed.
