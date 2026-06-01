# STAGE 5H.2 — User + DB Export Synthetic Fixtures Plan

Status: active task
Stage: 5H.2
Type: docs planning
Depends on: `docs/stages/reports/STAGE_5G_2_NON_CHANNEL_DATASET_CONTRACT_PRECHECK_REPORT.md`; preferably `docs/stages/reports/STAGE_5H_1_NON_CHANNEL_EXPORT_CONTRACT_DESIGN_PRECHECK_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.
Use `.skills/stage-reviewer/SKILL.md` before executing this stage.
Use `.skills/architecture-guard/SKILL.md` because this stage plans tests/fixtures for export, DB export, storage, and dataset contract boundaries.
Use `.skills/stage-completion-auditor/SKILL.md` before claiming completion.
Do not execute any later stage.

## 1. PURPOSE

Plan privacy-safe synthetic fixtures for user/group `export` and `db-export`.
Decide fixture families, locations, expected outputs, generated versus checked-in artifacts, future tests, and out-of-scope areas.
Default to plan/report only.

## 2. FILES TO INSPECT

Required docs:

```text
AGENTS.md
.skills/stage-reviewer/SKILL.md
.skills/architecture-guard/SKILL.md
.skills/stage-completion-auditor/SKILL.md
docs/stages/reports/STAGE_5G_2_NON_CHANNEL_DATASET_CONTRACT_PRECHECK_REPORT.md
docs/stages/reports/STAGE_5H_1_NON_CHANNEL_EXPORT_CONTRACT_DESIGN_PRECHECK_REPORT.md
docs/architecture/CURRENT_PROJECT_CONTEXT.md
docs/architecture/TXT_RENDERING.md
docs/architecture/DATASET_FORMAT.md
docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md
README.md
COMMANDS.md
docs/stages/README.md
```

If the 5H.1 report is absent, either block with `SYNTHETIC_FIXTURES_PLAN_COMPLETE_WAIT_FOR_5H1` or proceed as an independent plan with an explicit report note.

Inspect current tests/fixtures only as needed:

```text
tests/
tests/fixtures/
tests/cli/
tests/services/db_export/
tests/services/rendering/
tg_msg_manager/services/export/
tg_msg_manager/services/db_export/
tg_msg_manager/services/rendering/
tg_msg_manager/infrastructure/storage/
```

Allowed to change:

```text
docs/stages/reports/STAGE_5H_2_USER_DB_EXPORT_SYNTHETIC_FIXTURES_PLAN_REPORT.md
docs/stages/README.md
docs/stages/completed/stage_5h_2_user_db_export_synthetic_fixtures_plan.md
docs/development/NON_CHANNEL_SYNTHETIC_FIXTURES_PLAN.md
```

Do not inspect private artifacts, real exports, sessions, credentials, screenshots, logs, local DB files, media, or ignored private content.

## 3. HARD PROHIBITIONS

Do not create fixtures from Telegram exports.
Do not create final golden fixtures unless a later implementation stage explicitly scopes it.
Do not change runtime behavior, CLI behavior, output formats, TXT rendering, JSONL schema, SQLite, storage behavior, tests, command names, flags, defaults, filenames, or output layouts.
Do not add dependencies.
Do not include private archive or `export-pm` fixtures except to mark them out of scope or deferred.
Do not use real IDs, usernames, chat titles, message text, paths, logs, DB files, screenshots, sessions, or media.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Inspect required docs and minimum existing tests/fixtures needed; do not edit yet.
2. Decide whether to wait for 5H.1 or continue as an independent planning stage.
3. Recommend fixture families for user/group `export` and `db-export`, including shared versus separate corpus choices.
4. Recommend expected TXT, JSONL, state, part-rotation, and `DB_EXPORTS` layout coverage.
5. Define privacy safeguards for synthetic IDs, usernames, chat titles, text, timestamps, and paths.
6. Recommend exact future fixture/doc paths without creating runtime fixtures by default.
7. Recommend future test strategy and which checks remain deferred.
8. Optionally create `docs/development/NON_CHANNEL_SYNTHETIC_FIXTURES_PLAN.md` as plan-only.
9. Write the required report in Russian.
10. Complete lifecycle cleanup according to `AGENTS.md`.

## 5. REQUIRED DOCS

Always create:

```text
docs/stages/reports/STAGE_5H_2_USER_DB_EXPORT_SYNTHETIC_FIXTURES_PLAN_REPORT.md
```

Optional if useful:

```text
docs/development/NON_CHANNEL_SYNTHETIC_FIXTURES_PLAN.md
```

Update `docs/stages/README.md` during lifecycle cleanup.
No runtime fixture files, test files, or user-facing docs are allowed in this stage.

## 6. TESTS / VERIFICATION

Run:

```bash
git diff --check
```

If a planning doc is created, verify:

```text
it is marked plan, not implementation
it contains only synthetic placeholder examples, if any
it contains no real IDs, usernames, message text, paths, or private data
it does not claim tests or fixtures already exist unless they do
```

Runtime tests are not required for plan-only work.
Do not claim checks passed unless they were run.

## 7. REPORT

Report must be factual and written in Russian.
Include:

```text
status and outcome token
files inspected
recommended fixture families
recommended fixture locations
recommended expected outputs
privacy safeguards
recommended future tests
what is explicitly deferred
whether a planning doc was created
no runtime/CLI/SQLite/dataset behavior changes confirmation
private artifact boundary confirmation
checks run
lifecycle notes
architecture-guard: applied from .skills/architecture-guard/SKILL.md
stage-reviewer: applied from .skills/stage-reviewer/SKILL.md
stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md
```

Outcome token must be one of:

```text
SYNTHETIC_FIXTURES_PLAN_COMPLETE_DOC_CREATED
SYNTHETIC_FIXTURES_PLAN_COMPLETE_REPORT_ONLY
SYNTHETIC_FIXTURES_PLAN_COMPLETE_WAIT_FOR_5H1
BLOCKED_INSUFFICIENT_CONTEXT
```

## 8. COMPLETION CRITERIA

Required report exists.
Optional planning doc, if created, is plan-only and synthetic-only.
No runtime fixtures, tests, CLI, SQLite, dataset, storage, service, or behavior changed.
Private archive and `export-pm` remain out of scope.
Required check is run or failure is recorded.
Lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`.
No full diffs.
No broad summaries.
No fixture implementation.
No future-stage implementation.
End with `OUTPUT LIMITS`.
