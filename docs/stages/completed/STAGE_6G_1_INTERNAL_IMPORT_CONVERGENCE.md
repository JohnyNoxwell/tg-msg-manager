# STAGE 6G.1 — Internal Import Convergence

Status: active task
Stage: 6G.1
Type: implementation
Depends on: `docs/stages/reports/STAGE_6G_0_COMPATIBILITY_SURFACE_BASELINE_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` first.
- Read the Stage 6G.0 report before editing.
- Apply `stage-reviewer` before executing this stage.
- Apply `architecture-guard` because this stage changes compatibility-wrapper usage.
- Preserve public compatibility imports.
- Do not start Stage 6G.2.

## 1. PURPOSE

Move internal production imports away from deprecated compatibility wrappers so those wrappers remain external/backward-compatible surfaces only.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `docs/stages/reports/STAGE_6G_0_COMPATIBILITY_SURFACE_BASELINE_REPORT.md`
- `docs/architecture/ARCHITECTURE_RULES.md`
- `tg_msg_manager/application/services.py`
- `tg_msg_manager/testing/runtime.py`
- `tg_msg_manager/cli/__init__.py`
- `tg_msg_manager/cli_menu.py`
- `tg_msg_manager/services/exporter.py`
- `tg_msg_manager/services/context_engine.py`
- `tg_msg_manager/services/db_exporter.py`
- `tg_msg_manager/services/private_archive.py`
- `tg_msg_manager/core/models/service_payloads.py`
- `tg_msg_manager/cli_commands.py`
- `tests/architecture/test_architecture_wrappers.py`
- `tests/architecture/test_static_boundaries.py`
- Directly affected focused tests identified by import changes.
- `docs/stages/reports/STAGE_6G_1_INTERNAL_IMPORT_CONVERGENCE_REPORT.md` may be created.

## 3. HARD PROHIBITIONS

- Do not remove compatibility wrapper files.
- Do not change public import behavior of wrappers.
- Do not change CLI command names, flags, defaults, output files, output formats, or command dispatch behavior.
- Do not change SQLite schema, dataset formats, manifests, state, incremental, force, or no-new-work behavior.
- Do not add business logic to compatibility wrappers, service facades, CLI aggregators, or storage interface aggregators.
- Do not migrate test imports that explicitly assert backward compatibility unless replacing them with clearer compatibility tests.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Replace internal production imports from service wrappers with canonical package or service-module imports.
2. Replace internal production imports from `tg_msg_manager/cli_commands.py` with `tg_msg_manager/cli/commands` imports where safe.
3. Keep compatibility tests that prove old imports still resolve to canonical implementations.
4. Add or tighten static architecture tests so new production code cannot import deprecated compatibility surfaces except explicitly allowlisted wrappers/tests.
5. Update architecture docs only if the canonical import guidance changes.

## 5. REQUIRED DOCS

- Create `docs/stages/reports/STAGE_6G_1_INTERNAL_IMPORT_CONVERGENCE_REPORT.md`.
- Update `docs/architecture/ARCHITECTURE_RULES.md` only if new guardrails are added or existing guidance is stale.

## 6. TESTS / VERIFICATION

Run focused checks first:

```bash
python3 -m pytest tests/architecture/test_architecture_wrappers.py tests/architecture/test_static_boundaries.py -q
python3 -m pytest tests/services/test_services.py tests/services/sync/test_sync_system.py tests/cli/test_channel_export_cli.py tests/services/dataset_validation/test_dataset_validation_contracts.py -q
python3 -m compileall tg_msg_manager
```

Then run completion gates:

```bash
make verify
make pre-commit
```

Do not claim completion if `make verify` cannot run.

## 7. REPORT

The report must be in Russian and include:

- changed imports;
- retained compatibility imports/tests;
- static guardrail changes;
- docs changed or reason none were needed;
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`;
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`;
- commands run and results.

## 8. COMPLETION CRITERIA

- Internal production imports no longer depend on deprecated compatibility wrappers identified for migration in Stage 6G.0.
- Public compatibility imports still pass tests.
- Required tests and gates pass.
- Required report exists.
- Lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must use the `AGENTS.md` final format.
- Maximum 1200 characters.
- No full diffs.
- No broad summaries.
