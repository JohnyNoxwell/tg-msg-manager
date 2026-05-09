# AGENTS.md

## 1. Operating mode

Before editing code or docs:

1. Read this file.
2. Identify the active task/stage file.
3. Read only docs referenced by that task.
4. Inspect only files you may change.
5. Write a compact plan: max 5 bullets.
6. Implement only requested scope.

Do not read the whole docs tree by default.
Do not treat archive files as current instructions unless explicitly asked.
Do not restate the task back to the user.

## 2. Output discipline

Minimize token usage.

Reports, including stage reports and other factual completion records, must be written in Russian unless the user explicitly requests another language.

Final response must use exactly this structure:

```text
DONE:
- <one-line result>

CHANGED:
- <path>

CHECKS:
- <command>: <passed|failed|not run: reason>

PRESERVED:
- behavior: <yes|no|n/a>
- CLI: <yes|no|n/a>
- SQLite: <yes|no|n/a>
- scope: <yes|no|n/a>

NOTES:
- <blocker/caveat or none>

STAGE:
- <complete|incomplete: reason|n/a>
```

Limits:

- Final response: max 1200 characters unless explicitly requested otherwise.
- Interim response: max 600 characters.
- Plan: max 5 bullets.
- No markdown tables unless requested.
- No full diffs unless requested.
- No large code blocks copied from files.
- No generic summaries, essays, speculation, apologies, motivational text, or future recommendations unless required.
- No repeated task context.

Allowed interim output only if blocked or a required question exists:

```text
BLOCKED:
- <exact blocker>
```

```text
QUESTION:
- <one minimal question required to continue>
```

If asked for a commit message, output only:

```text
<type>: <short imperative summary>
```

If asked for PR text, use only:

```text
## Summary
- ...

## Checks
- ...
```

Maximum 5 bullets total.

## 3. Project boundary

`tg-msg-manager` is a local Telegram export/data pipeline and CLI project.

It is not a SaaS monitoring platform, analytics engine, OSINT interpretation engine, profiling system, or GUI dashboard.

Dataset export comes first. Interpretation, analytics, profiling, classification, and LLM reports stay outside the exporter unless a future active stage explicitly scopes them.

Preferred boundary:

```text
export -> validate/inspect -> post-processing -> optional LLM report
```

## 4. Architecture rules

- CLI is thin: parse args, validate basic input, call services, render high-level results.
- Services orchestrate only; no raw SQL or large feature algorithms.
- Feature logic lives in focused modules with one responsibility.
- Do not bloat service facades.
- Preserve public CLI behavior unless the active stage explicitly allows changes.
- SQLite schema changes are forbidden unless explicitly scoped.
- Dataset format changes require regression tests and docs.
- Preserve state, incremental, force, and no-new-work behavior unless explicitly changed.
- Any behavior change requires tests and docs.

Channel export:

- Channel export logic: `tg_msg_manager/services/channel_export/`.
- Media logic: media-specific channel export modules.
- Discussion logic: `tg_msg_manager/services/channel_export/discussions/`.
- `ChannelExportService` remains orchestration-only.

Current architecture guidance: `docs/architecture/README.md`.

## 5. Protected files

Do not add feature logic to protected service facades:

```text
tg_msg_manager/services/export/service.py
tg_msg_manager/services/db_export/service.py
tg_msg_manager/services/private_archive/service.py
tg_msg_manager/services/context/engine.py
tg_msg_manager/services/channel_export/service.py
```

Only orchestration or mechanical wiring is allowed. If a protected file must change, state why in the plan and keep the change minimal.

Compatibility wrappers and aggregators are also protected:

```text
tg_msg_manager/services/exporter.py
tg_msg_manager/services/context_engine.py
tg_msg_manager/services/db_exporter.py
tg_msg_manager/services/private_archive.py
tg_msg_manager/core/models/service_payloads.py
tg_msg_manager/infrastructure/storage/interface.py
```

Storage SQL belongs under `tg_msg_manager/infrastructure/storage/`.
Core/domain must not import infrastructure.
Infrastructure must not import services.
CLI must not be imported by service/core/infrastructure modules.

## 6. Docs policy

Documentation map:

- `docs/README.md` - documentation index and selection policy.
- `docs/architecture/` - current architecture rules and snapshots.
- `docs/development/` - CLI contracts, testing, PR checklist, workflow.
- `docs/stages/active/` - executable current stage tasks.
- `docs/stages/completed/` - historical task files.
- `docs/stages/reports/` - factual reports and baselines.
- `docs/roadmap/` - roadmap/backlog only, not implementation permission.
- `docs/archive/` - old prompts/deprecated notes, not current guidance.

Root docs: `README.md`, `COMMANDS.md`, `CHANGELOG.md`.

For any task, read only:

1. `AGENTS.md`.
2. Active stage/task file.
3. Docs referenced by that stage.
4. Development/testing docs relevant to changed files.
5. Recent reports only if required by the task.

Do not read by default: all completed stages, all reports, archive files, unrelated roadmap files.

Update docs in the same change when modifying CLI flags, output files, schemas, manifests, state files, media/discussion behavior, incremental/force/no-new-work behavior, architecture boundaries, developer workflow, testing commands, stage status, or known limitations.

Do not leave code behavior ahead of docs.
Do not duplicate large docs content inside `AGENTS.md`; link to docs instead.

## Skill Selection

Use the narrowest matching skill:

- `stage-reviewer` before implementing a stage file.
- `stage-completion-auditor` after claimed stage completion.
- `architecture-guard` for CLI, services, storage, protected files, or architecture-boundary changes.
- `discussion-export-diagnoser` for channel discussion export failures/artifacts.
- `bugfix-stage-writer` when creating a bugfix stage from an observed defect.

If the user names a skill, use it.
Do not use multiple skills unless clearly required.

## 7. Stage workflow

Every stage should:

1. define scope/prohibitions;
2. inspect current code/docs;
3. implement atomic tasks;
4. add/update tests when behavior changes;
5. update docs when behavior/docs change;
6. run verification;
7. create a factual report;
8. perform cleanup only after the final report exists.

Lifecycle:

```text
active task -> implementation -> tests/checks -> report -> cleanup -> completed history
```

Only `docs/stages/active/` contains executable current tasks.
Completed stage files are historical instructions.
Reports are factual records, not instructions.
Archived files are not current instructions.

After final report exists and stage is complete:

- move completed task files to `docs/stages/completed/`;
- move launch prompts to `docs/archive/old_prompts/` unless task says otherwise;
- update `docs/stages/README.md`;
- leave only unfinished/next active work in `docs/stages/active/`.

Do not mark complete unless implementation/docs are done, required checks are run or documented, report exists, relevant docs are updated, and cleanup is done.

## 8. Coding rules

- Preserve behavior first.
- Make small, isolated changes.
- Follow existing project style.
- Prefer typed, explicit, domain-specific models.
- Use focused modules instead of broad utilities.
- No raw SQL in service layer.
- No business logic in compatibility wrappers.
- Do not mix refactor, feature work, formatting churn, and behavior changes unless explicitly scoped.
- Do not change command names, args, defaults, formats, filenames, output layout, retry behavior, report format, or DB schema unless explicitly scoped.

## 9. Testing

Run focused tests first. Then broader verification if behavior changed.

Do not claim tests passed unless actually run. If unable, state why.

Common commands:

```bash
pytest tests/test_channel_export_*.py
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
make test
make verify
```

Docs-only changes do not require every code test unless the task requires final verification.

## 10. Forbidden unless explicitly scoped

- analytics;
- OSINT interpretation;
- sentiment analysis;
- bot detection;
- user profiling;
- narrative classification;
- OCR;
- speech-to-text;
- image/video/audio analysis;
- SQLite schema changes/migrations;
- DB persistence for channel posts or discussion comments;
- GUI/dashboard/SaaS features;
- hidden product features;
- broad refactors in feature stages;
- changes to legacy command behavior.

## 11. Stop and report

Stop if:

- active task conflicts with `AGENTS.md`;
- required docs are missing;
- requested change requires forbidden SQLite changes;
- protected-file changes would exceed orchestration/wiring;
- tests reveal unrelated baseline failures;
- next stage would start without request;
- required docs are stale and cannot be corrected within scope;
- preserving behavior conflicts with requested implementation.

Use compact blocker format:

```text
BLOCKED:
- <exact blocker>

CHANGED:
- <path or none>

CHECKS:
- <command>: <result>

NEXT:
- <single concrete next action>
```

Do not continue to the next stage.
