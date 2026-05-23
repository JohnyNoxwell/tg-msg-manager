# STAGE 4C.0 — ARCHITECTURE STABILIZATION AUDIT BEFORE EXPANSION REPORT

## Статус

- Stage 4C.0 завершён как read-only architecture audit.
- Runtime code, tests, `AGENTS.md`, root user docs, architecture docs, development docs, CLI behavior, SQLite schema и dataset formats не менялись.
- Создан только factual stage report; lifecycle cleanup выполнен после отчёта.

## CLI decomposition status

- `tg_msg_manager/cli_commands.py` является compatibility aggregator: только re-export command handlers и `__all__`.
- `tg_msg_manager/cli/commands/` содержит focused handlers по подсистемам: export, channel export, dataset validation/inspection, DB export, maintenance, retry, report, setup/schedule.
- Compatibility imports используются и покрыты тестами: `tg_msg_manager/cli/__init__.py`, `tg_msg_manager/cli_menu.py`, `tests/cli/test_channel_export_cli.py`, `tests/services/dataset_validation/test_dataset_validation_contracts.py`.
- CLI handlers остаются thin: они собирают options/context, вызывают service layer и печатают high-level output. Raw SQL, Telegram traversal и dataset formatting logic в handlers не обнаружены.
- `README.md` и `COMMANDS.md` отражают текущий command surface, но `README.md` содержит устаревшие flat test path references для E2E теста.

## Channel export service/workflow status

- `tg_msg_manager/services/channel_export/service.py` остаётся orchestration facade: нормализует options, resolves source, выбирает run mode, собирает workflow context и делегирует full/incremental paths.
- Full, incremental и no-new-posts paths вынесены в `tg_msg_manager/services/channel_export/workflows/`.
- Discussion logic остаётся в `tg_msg_manager/services/channel_export/discussions/`.
- Media behavior остаётся в media-specific modules (`media_*`, `media_processor`, `media_policy`).
- Manifest/result/state handling делегированы focused modules; опасного дублирования в audited paths не найдено.
- Риск: `ChannelExportWorkflowContext` уже концентрирует много collaborators и helper methods. Это не блокер сейчас, но Stage 4C.1 should document its boundary as workflow wiring/helper context, not a place for new product logic.

## Tests layout status

- Tests grouped by subsystem directories: `tests/cli/`, `tests/core/`, `tests/e2e/`, `tests/infrastructure/`, `tests/services/`, `tests/architecture/`.
- Fixtures remain under `tests/fixtures/` and were reachable during collection/test run.
- `python3 -m unittest discover -s tests -q` passed: 453 tests.
- `python3 -m pytest --collect-only -q` passed: 493 tests collected.
- Risk: root pytest collection also sees existing `scratch/test_whitelist.py` because no pytest config narrows collection to `tests/`. CI does not use pytest directly.

## AGENTS.md rule status

- `AGENTS.md` already covers:
  - CLI thin boundary;
  - service orchestration-only boundary;
  - protected service facades;
  - compatibility wrappers;
  - storage SQL boundary;
  - channel export service boundary;
  - discussion/media module ownership;
  - skill selection;
  - stage lifecycle;
  - output discipline.
- AGENTS.md update not needed.

## Docs / CI / test command status

- `.github/workflows/ci.yml` runs `make verify`; the Makefile targets are valid.
- `Makefile` uses `python3 -m unittest discover -s tests -q`; this passed.
- `docs/development/CLI_CONTRACT.md` references dotted test module names under the grouped layout and is current enough for audited scope.
- `README.md` still references `tests/test_fixture_e2e.py` and `python3 -m unittest tests.test_fixture_e2e -q`; current path/module is `tests/e2e/test_fixture_e2e.py` / `tests.e2e.test_fixture_e2e`.
- Architecture docs contain stale flat test path references:
  - `docs/architecture/PRIVATE_ARCHIVE_ENTRYPOINT_AUDIT.md`
  - `docs/architecture/DB_EXPORT_ENTRYPOINT_AUDIT.md`
  - `docs/architecture/PRIVATE_ARCHIVE_IMPORT_RESOLUTION.md`
  - `docs/architecture/PROJECT_ARCHITECTURE_OVERVIEW.md`

## Risks found

- Stale documentation paths after test layout grouping can mislead future stage agents and reviewers.
- Root pytest collection includes `scratch/test_whitelist.py`; this is not a CI failure but should be treated as a collection hygiene risk if pytest becomes a primary verification command.
- `docs/stages/README.md` was stale before lifecycle cleanup: it said active stage files were `none` while active stage files existed.

## Stage 4C.1 decision

- Stage 4C.1 is needed.
- Reason: architecture docs need synchronization for test path references, and Stage 4C.1 is the scoped docs-sync stage after this audit.
- Exact minimal Stage 4C.1 patch set should:
  - update stale flat test path references in the named architecture docs;
  - update README E2E test path/command only if Stage 4C.1 chooses to include root user docs under its optional scope;
  - document or explicitly defer the root pytest `scratch/` collection hygiene risk;
  - avoid runtime code, tests, command surface, SQLite, dataset, and behavior changes.

## Expansion readiness decision

- Decision: `READY_AFTER_DOC_SYNC`.
- Blockers before Stage 4D: stale architecture/test-path documentation must be synchronized by Stage 4C.1.
- No targeted runtime refactor is required before dataset-contract work.

## Recommended next stage

- Run `docs/stages/active/stage_4c_1_architecture_rules_sync_after_audit.md`.
- Do not start Stage 4D until Stage 4C.1 completes or records that no doc sync remains.

## Checks

- `python3 -m pytest --collect-only -q`: passed, 493 tests collected.
- `python3 -m unittest discover -s tests -q`: passed, 453 tests.

## Self-check

- Stage scope preserved: yes.
- Forbidden runtime/test/AGENTS/user-doc/architecture-doc/development-doc changes avoided before lifecycle cleanup: yes.
- Required report exists: yes.
- Required checks were run: yes.
- Docs updated only for required lifecycle cleanup: yes.
- Lifecycle cleanup completed: yes.
- `stage-completion-auditor`: not run; no such skill/tool is available in this session.
- `architecture-guard`: not run; no such skill/tool is available in this session.
