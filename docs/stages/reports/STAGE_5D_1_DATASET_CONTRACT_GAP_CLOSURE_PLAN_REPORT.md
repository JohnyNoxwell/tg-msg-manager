# Отчет Stage 5D.1 - Dataset Contract Gap Closure Plan

## Статус

Stage 5D.1 завершен.

## Проверенные файлы

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/architecture/DATASET_CONTRACT_COVERAGE_MATRIX.md`
- `docs/architecture/DATASET_CONTRACT_V1.md`
- `docs/architecture/DATASET_FORMAT.md`
- `docs/stages/active/stage_5d_1_dataset_contract_gap_closure_plan.md`
- `docs/stages/README.md`
- `tests/services/channel_export/test_channel_export_dataset_contracts.py`
- `tests/services/channel_export/test_channel_export_service.py`
- `tests/services/channel_export/test_channel_export_included_files_builder.py`
- `tests/services/dataset_validation/test_dataset_validation_contracts.py`
- `tg_msg_manager/services/channel_export/run_changelog.py`
- `tg_msg_manager/services/channel_export/included_files_builder.py`
- `tg_msg_manager/services/channel_export/payload_writer.py`
- `tg_msg_manager/services/channel_export/media_policy.py`
- `tg_msg_manager/services/channel_export/post_mapper.py`

## Классификация gaps

- `run_changelog.jsonl` exact key set: `test-only`; закрывается Stage 5D.2.
- TXT projections: `docs-only`; Stage 5D.3 должен закрепить, что контракт ограничен stable smoke assertions, без full golden snapshot.
- `--media none`: `test-only`; закрывается Stage 5D.4.
- Full, force, incremental, no-new-posts: `test-only` для компактной contract-level матрицы; service tests уже покрывают основные runtime-факты.
- `include_jsonl=False` / `include_txt=False`: `behavior-mismatch`; manifest omission покрыт, но file absence не доказан, а `payload_writer` открывает оба payload файла.
- Non-channel dataset families: `out-of-scope` для Dataset Contract V1.

## Порядок 5D

1. Stage 5D.2 - run changelog key set tests.
2. Stage 5D.3 - TXT projection contract clarification.
3. Stage 5D.4 - channel export mode matrix tests.
4. Stage 5D.5 - safe first export guide.

## Изменения

- Измененные файлы: `docs/architecture/DATASET_CONTRACT_COVERAGE_MATRIX.md`, `docs/stages/reports/STAGE_5D_1_DATASET_CONTRACT_GAP_CLOSURE_PLAN_REPORT.md`, `docs/stages/completed/stage_5d_1_dataset_contract_gap_closure_plan.md`, `docs/stages/README.md`.
- `docs/architecture/DATASET_CONTRACT_COVERAGE_MATRIX.md` уточняет stale строки по discussion no-new-posts, run modes и include options.
- Runtime behavior не менялся.
- CLI не менялся.
- Dataset format не менялся.
- SQLite behavior и schema не менялись.

## Проверки

- `git diff --check`: passed.
- Code tests не запускались: stage docs/planning, Python runtime и tests не менялись.

## Skills

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`

## Completion

- Gap closure plan recorded.
- Matrix updated where the factual inventory was stale.
- Lifecycle cleanup completed: active task file moved to `docs/stages/completed/`, `docs/stages/README.md` updated.
