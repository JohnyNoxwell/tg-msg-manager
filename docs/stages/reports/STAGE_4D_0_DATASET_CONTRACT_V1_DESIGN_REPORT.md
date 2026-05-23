# STAGE 4D.0 — DATASET CONTRACT V1 DESIGN REPORT

## Статус

- Stage 4D.0 завершён.
- Создан formal v1 filesystem dataset contract для текущих direct channel export datasets.
- Runtime code, tests, CLI behavior, output layout, manifest/state formats, JSONL schemas, TXT profiles, media/discussion behavior и SQLite schema не менялись.

## Созданный contract doc

- `docs/architecture/DATASET_CONTRACT_V1.md`
- Документ описывает существующее поведение `export-channel` и не вводит новые runtime requirements.
- `docs/architecture/README.md` обновлён индексной ссылкой на новый contract doc.

## Inspect sources

- `AGENTS.md`
- `docs/stages/active/stage_4d_0_dataset_contract_v1_design.md`
- `COMMANDS.md`
- `README.md`
- `docs/architecture/DATASET_FORMAT.md`
- `docs/architecture/DATASET_VALIDATION.md`
- `docs/architecture/DATASET_WRITE_SAFETY.md`
- `docs/architecture/STATE_AND_INCREMENTAL_MODEL.md`
- `docs/architecture/README.md`
- `tg_msg_manager/services/channel_export/`
- `tg_msg_manager/services/channel_export/discussions/`
- `tg_msg_manager/services/dataset_validation/`
- `tests/services/channel_export/`
- `tests/services/dataset_validation/`

## Covered artifacts

- `manifest.json`
- `messages.jsonl`
- `messages.txt`
- `media_manifest.jsonl`
- `media/`
- `channel_export_state.json`
- `run_changelog.jsonl`
- `discussion_metadata.jsonl`
- `discussion_comments.jsonl`
- `discussion_comments.txt`
- `discussion_threads.jsonl`
- `discussion_export_state.json`

## Covered behavior

- media modes: `none`, `metadata`, `full`;
- discussion modes: `none`, `metadata`, `full`;
- full, force, incremental, and no-new-posts runs;
- `include_jsonl` / `include_txt` service options;
- partial failure boundaries for payload, manifest, state, media, and discussion writes;
- validation and inspection boundaries;
- future pipeline boundary: `export -> validate/inspect -> dataset doctor -> post-processing -> optional LLM report`.

## Known gaps

- Dataset Contract V1 is anchored on direct channel export only.
- Group/user `export`, `db-export`, and `export-pm` are marked `UNKNOWN_NEEDS_CHECK` for this contract because this stage did not inspect or formalize those output families.
- The contract does not add a validator, doctor, post-processing layer, or new schema version.

## Checks

- `python3 -m compileall tg_msg_manager`: passed.
- `ruff check tg_msg_manager tests`: passed.
- `git diff --check`: passed.

## Не выполнялось

- `make test`: not run; docs-only stage required compileall/ruff.
- `stage-completion-auditor`: not run; no such skill/tool is available in this session.
- `architecture-guard`: not run; no such skill/tool is available in this session.

## Completion status

- `DATASET_CONTRACT_V1.md` exists: yes.
- Contract documents existing behavior only: yes.
- No runtime code changed: yes.
- No tests changed: yes.
- Required checks run: yes.
- Required report exists: yes.
- Lifecycle cleanup completed: yes.
