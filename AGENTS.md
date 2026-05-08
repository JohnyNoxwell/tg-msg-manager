# AGENTS.md

## 1. Mandatory first step

Before editing code or documentation:

1. Read this AGENTS.md.
2. Identify the active task or stage file.
3. Read only the documentation referenced by that task.
4. Inspect files you plan to change.
5. Write a short plan before editing.
6. Implement only the requested scope.

Do not read the whole docs tree by default.
Do not use archive files as current instructions unless explicitly asked.

## 2. Project identity

`tg-msg-manager` is a local Telegram export/data pipeline and CLI project.

It is not:

- a SaaS monitoring platform;
- an analytics engine;
- an OSINT interpretation engine;
- a profiling system;
- a GUI dashboard.

Dataset export comes first. Interpretation, analytics, profiling, and classification are out of the exporter pipeline unless a future active stage explicitly scopes them.

## 3. Non-negotiable architecture rules

- CLI is thin: parse args, validate basic input, call services, and render high-level results.
- Services are orchestration-only and must not contain raw SQL or large feature algorithms.
- Feature logic must live in focused modules with one responsibility.
- Do not bloat service facades.
- Existing public CLI behavior must remain stable unless the active stage explicitly allows changes.
- SQLite schema changes are forbidden unless the active stage explicitly allows them.
- Dataset format changes require regression tests and documentation updates.
- State, incremental, force, and no-new-work behavior must be preserved unless explicitly changed.
- Any behavior change requires tests and docs.

Channel export rules:

- Channel export logic lives under `tg_msg_manager/services/channel_export/`.
- Media download logic lives in media-specific channel export modules.
- Discussion export logic lives under `tg_msg_manager/services/channel_export/discussions/`.
- `ChannelExportService` remains orchestration-only.

Current architecture guidance lives in `docs/architecture/README.md`.

## 4. Protected files and boundaries

Do not add new feature logic to these protected service facades:

```text
tg_msg_manager/services/export/service.py
tg_msg_manager/services/db_export/service.py
tg_msg_manager/services/private_archive/service.py
tg_msg_manager/services/context/engine.py
tg_msg_manager/services/channel_export/service.py
```

Only orchestration or mechanical wiring is allowed where appropriate. If a protected file must change, explain why in the plan and keep the change minimal.

Compatibility wrappers and aggregators are also protected from new business logic:

```text
tg_msg_manager/services/exporter.py
tg_msg_manager/services/context_engine.py
tg_msg_manager/services/db_exporter.py
tg_msg_manager/services/private_archive.py
tg_msg_manager/core/models/service_payloads.py
tg_msg_manager/infrastructure/storage/interface.py
```

Storage SQL belongs under `tg_msg_manager/infrastructure/storage/`. Core/domain code must not import infrastructure. Infrastructure must not import services. CLI must not be imported by service/core/infrastructure modules.

## 5. Documentation map

- `docs/README.md` - top-level documentation index and doc selection policy.
- `docs/architecture/` - current architecture rules, split maps, storage/model decisions, and architecture snapshots.
- `docs/development/` - CLI contracts, testing guidance, PR checklist, and development workflow.
- `docs/stages/active/` - executable current stage task files.
- `docs/stages/completed/` - historical task instruction files.
- `docs/stages/reports/` - factual completion reports and baselines.
- `docs/roadmap/` - roadmap/backlog navigation; not implementation permission.
- `docs/archive/` - old prompts, deprecated plans, and superseded notes; not current guidance.

Root user-facing docs:

- `README.md`
- `COMMANDS.md`
- `CHANGELOG.md`

## 6. Relevant-doc selection policy

For any task, read:

1. `AGENTS.md`.
2. The active stage or task file.
3. Architecture docs referenced by that stage.
4. Development/testing docs relevant to changed files.
5. Recent stage reports only if the task depends on prior stage behavior.

Do not read by default:

- all completed stage files;
- all reports;
- archive files;
- roadmap files unrelated to the request.

If the active task references archive material, read only the named archived file.

## 7. Stage workflow

Every stage should:

1. define scope;
2. define prohibitions;
3. inspect current code/docs;
4. implement atomic tasks;
5. add or update tests when behavior changes;
6. update docs if behavior, workflow, architecture, formats, or known limitations change;
7. run verification;
8. create a factual report.

Lifecycle:

```text
active task -> implementation -> tests/checks -> report -> lifecycle cleanup -> completed task history
```

Only files under `docs/stages/active/` are executable current tasks. Completed stage files are historical instructions. Stage reports are factual records, not instructions.

Stage lifecycle cleanup is mandatory. When a stage is fully complete and its final report exists, the agent must:

- move completed stage task files from `docs/stages/active/` to `docs/stages/completed/`;
- move general launch prompts to `docs/archive/old_prompts/`;
- update `docs/stages/README.md`;
- ensure `docs/stages/active/` contains only unfinished or next active work.

Do not perform completion cleanup before the final stage report exists.

## 8. Coding rules

- Preserve behavior first.
- Make small, isolated changes.
- Follow existing project style and local patterns.
- Prefer typed, explicit, domain-specific models.
- Use focused modules instead of broad utility modules.
- Do not add raw SQL to service layer.
- Do not add business logic to compatibility wrappers.
- Do not mix refactor, feature work, formatting churn, and behavioral changes unless the active task explicitly scopes it.
- Do not change command names, arguments, defaults, export formats, output filenames, output directory layout, retry behavior, report format, or database schema without explicit task scope.

## 9. Testing policy

Run focused tests first. Then run broader verification if behavior changed.

Do not claim tests passed unless actually run. If unable to run tests, state why.

Common commands:

```bash
pytest tests/test_channel_export_*.py
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
make test
make verify
```

Docs-only changes do not require every code test unless the active task requires final verification.

## 10. Documentation policy

Documentation is part of the implementation.

For every change, check whether documentation must be updated.

Update documentation in the same change when modifying:

- CLI commands or flags;
- output files;
- dataset schemas;
- manifest formats;
- state file formats;
- media behavior;
- discussion behavior;
- incremental behavior;
- force/no-new-work behavior;
- architecture boundaries;
- developer workflow;
- testing commands;
- stage status;
- known limitations.

A stage is not complete until documentation and reports match the implemented behavior.

Do not leave code behavior ahead of documentation.
Do not claim completion if required documentation is stale, missing, or still describes old behavior.
Do not duplicate large docs content inside `AGENTS.md`; link to the relevant docs instead.

Required documentation targets may include:

```text
README.md
COMMANDS.md
CHANGELOG.md
docs/README.md
docs/architecture/
docs/development/
docs/stages/active/
docs/stages/completed/
docs/stages/reports/
docs/development/LIVE_SMOKE_CHECKLIST.md
```

## 11. Forbidden behavior

Do not add unless explicitly scoped by the active task:

- analytics;
- OSINT interpretation;
- sentiment analysis;
- bot detection;
- user profiling;
- narrative classification;
- OCR;
- speech-to-text;
- image/video/audio analysis;
- SQLite schema changes or migrations;
- DB persistence for channel posts or discussion comments;
- GUI/dashboard/SaaS features;
- hidden product features;
- broad refactors in feature stages;
- changes to legacy command behavior.

## 12. Stop-and-report conditions

Stop and report if:

- the active task conflicts with `AGENTS.md`;
- required docs are missing;
- a requested change requires SQLite schema changes but the stage forbids it;
- implementation would require protected-file changes beyond orchestration or mechanical wiring;
- tests reveal unrelated baseline failures;
- you are about to start a later stage not requested by the active task;
- required docs are stale and cannot be corrected within scope;
- preserving behavior conflicts with the requested implementation.

Report the exact blocker and do not continue to the next stage.

## 13. Final response expectations

Final responses should state:

- what changed;
- which files changed;
- what checks ran and their results;
- what was not run and why;
- whether behavior, SQLite schema, CLI contracts, and feature scope were preserved;
- remaining limitations or follow-up work when relevant.

For stage work, include per-stage status when the task requests it.
