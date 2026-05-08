# Stage Documentation

## Active stages

Only files under [`active/`](active/) are executable current tasks.

Current active Stage 3D.0 files:

- [`active/stage_3d_0_general_prompt.md`](active/stage_3d_0_general_prompt.md)
- [`active/stage_3d_0_1_documentation_audit.md`](active/stage_3d_0_1_documentation_audit.md)
- [`active/stage_3d_0_2_target_structure_and_migration_plan.md`](active/stage_3d_0_2_target_structure_and_migration_plan.md)
- [`active/stage_3d_0_3_move_and_normalize_documentation.md`](active/stage_3d_0_3_move_and_normalize_documentation.md)
- [`active/stage_3d_0_4_documentation_indexes_and_navigation.md`](active/stage_3d_0_4_documentation_indexes_and_navigation.md)
- [`active/stage_3d_0_5_agents_md_rewrite.md`](active/stage_3d_0_5_agents_md_rewrite.md)
- [`active/stage_3d_0_6_root_readme_commands_changelog_alignment.md`](active/stage_3d_0_6_root_readme_commands_changelog_alignment.md)
- [`active/stage_3d_0_7_verification_and_governance_report.md`](active/stage_3d_0_7_verification_and_governance_report.md)

## Completed stages

Completed stage files under [`completed/`](completed/) are historical instructions. They show what an agent was asked to do at the time, but they are not current guidance.

Current completed prompt groups:

- Stage 3A direct channel export task prompts.
- Stage 3B media hardening and stabilization task prompts.
- Stage 3C discussion export task prompts.

## Reports

Reports under [`reports/`](reports/) are factual completion records. They can contain time-bound claims that were true for a specific stage.

Current Stage 3D.0 records:

- [`reports/STAGE_3D_0_1_DOCUMENTATION_AUDIT.md`](reports/STAGE_3D_0_1_DOCUMENTATION_AUDIT.md)
- [`reports/STAGE_3D_0_2_TARGET_DOCS_STRUCTURE_PLAN.md`](reports/STAGE_3D_0_2_TARGET_DOCS_STRUCTURE_PLAN.md)
- [`reports/STAGE_3D_0_3_DOCS_MIGRATION_REPORT.md`](reports/STAGE_3D_0_3_DOCS_MIGRATION_REPORT.md)

## Stage lifecycle

Stage files move through this lifecycle:

```text
active -> completed -> report
```

Active files define executable work. Completed files preserve historical instructions. Reports record what actually happened.

## Rules for agents

- Read `AGENTS.md` first.
- Execute only the active task requested by the user.
- Do not use completed task files as current instructions.
- Do not treat reports as feature requests.
- Do not start future roadmap work without an active task.
- Keep docs and reports aligned with the behavior being changed.
