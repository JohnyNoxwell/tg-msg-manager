# STAGE 5H.1 — Non-Channel Export Contract Design Precheck

Status: active task
Stage: 5H.1
Type: docs design precheck
Depends on: `docs/stages/reports/STAGE_5G_2_NON_CHANNEL_DATASET_CONTRACT_PRECHECK_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.
Use `.skills/stage-reviewer/SKILL.md` before executing this stage.
Use `.skills/architecture-guard/SKILL.md` because this stage touches export, DB export, dataset contract, CLI, service, and storage boundaries.
Use `.skills/stage-completion-auditor/SKILL.md` before claiming completion.
Do not execute any later stage.

## 1. PURPOSE

Design the next safe non-channel export contract work without changing runtime behavior or output formats.
Decide whether the next formal stage should create shared TXT rules, limited JSONL expectations, separate docs, fixtures-first work, or no contract yet.
Do not create a final contract by default.

## 2. FILES TO INSPECT

Required docs:

```text
AGENTS.md
.skills/stage-reviewer/SKILL.md
.skills/architecture-guard/SKILL.md
.skills/stage-completion-auditor/SKILL.md
docs/stages/reports/STAGE_5G_2_NON_CHANNEL_DATASET_CONTRACT_PRECHECK_REPORT.md
docs/architecture/CURRENT_PROJECT_CONTEXT.md
docs/architecture/DATASET_CONTRACT_V1.md
docs/architecture/DATASET_FORMAT.md
docs/architecture/TXT_RENDERING.md
docs/architecture/README.md
README.md
COMMANDS.md
docs/user/QUICKSTART.md
docs/development/README.md
docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md
docs/stages/README.md
```

Inspect code/tests only as needed to answer design questions:

```text
tg_msg_manager/cli_parser.py
tg_msg_manager/cli/commands/export.py
tg_msg_manager/cli/commands/db_export.py
tg_msg_manager/cli/__init__.py
tg_msg_manager/services/export/
tg_msg_manager/services/db_export/
tg_msg_manager/services/rendering/
tg_msg_manager/services/context/
tg_msg_manager/infrastructure/storage/read/
tg_msg_manager/infrastructure/storage/write/
tests/cli/
tests/services/db_export/
tests/services/rendering/
```

Allowed to change:

```text
docs/stages/reports/STAGE_5H_1_NON_CHANNEL_EXPORT_CONTRACT_DESIGN_PRECHECK_REPORT.md
docs/stages/README.md
docs/stages/completed/stage_5h_1_non_channel_export_contract_design_precheck.md
docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_DESIGN.md
```

Do not inspect private artifacts, real exports, sessions, credentials, logs, screenshots, local DB files, or ignored private content.

## 3. HARD PROHIBITIONS

Do not change runtime behavior, CLI behavior, output formats, TXT rendering, JSONL schema, SQLite, storage behavior, exporter services, DB export services, private archive services, command names, flags, defaults, filenames, or output layouts.
Do not add or change tests.
Do not create fixtures.
Do not create a final `*_CONTRACT_V1.md` unless every prerequisite is proven and the report explains why this is still precheck-safe.
Do not include `export-pm` in the user/group plus DB export contract.
Do not use real Telegram IDs, usernames, message text, logs, DB files, or sessions.
Protected service facades may be inspected only; do not edit them.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Inspect required docs and the minimum code/tests needed; do not edit yet.
2. Define the recommended contract boundary for user/group `export` and `db-export`.
3. Decide whether `.export_state/`, `.writer_state/`, and part rotation should be contract surfaces or deferred.
4. Compare shared and differing TXT projection rules for `context-readable` and `legacy`.
5. Decide whether JSONL expectations are shared enough to document and which keys are stable.
6. Decide whether fixtures must precede final contract work, including whether 5H.2 should run first.
7. Optionally create `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_DESIGN.md` as design/precheck only.
8. Write the required report in Russian.
9. Complete lifecycle cleanup according to `AGENTS.md`.

## 5. REQUIRED DOCS

Always create:

```text
docs/stages/reports/STAGE_5H_1_NON_CHANNEL_EXPORT_CONTRACT_DESIGN_PRECHECK_REPORT.md
```

Optional if justified:

```text
docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_DESIGN.md
```

Update `docs/stages/README.md` during lifecycle cleanup.
No user-facing docs updates are allowed unless the optional design doc changes architecture navigation and the report justifies the link.

## 6. TESTS / VERIFICATION

Run:

```bash
git diff --check
```

If a design doc is created, verify:

```text
it is marked design/precheck, not final contract
it does not imply runtime guarantees beyond current evidence
it contains no private or real example data
it preserves Dataset Contract V1 boundaries
```

Runtime tests are not required for report-only or design-only work.
Do not claim checks passed unless they were run.

## 7. REPORT

Report must be factual and written in Russian.
Include:

```text
status and outcome token
files inspected
contract boundary recommendation
TXT projection recommendation
JSONL expectation recommendation
fixtures/tests prerequisites
whether a design doc was created
recommended next stage
explicit export-pm deferral confirmation
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
NON_CHANNEL_CONTRACT_DESIGN_PRECHECK_COMPLETE_FIXTURES_FIRST
NON_CHANNEL_CONTRACT_DESIGN_PRECHECK_COMPLETE_DESIGN_DOC_CREATED
NON_CHANNEL_CONTRACT_DESIGN_PRECHECK_COMPLETE_READY_FOR_CONTRACT_STAGE
NON_CHANNEL_CONTRACT_DESIGN_PRECHECK_COMPLETE_NOT_READY
BLOCKED_INSUFFICIENT_EVIDENCE
```

## 8. COMPLETION CRITERIA

Required report exists.
Optional design doc, if created, is clearly precheck/design only.
`export-pm` remains deferred and outside the user/group plus DB export contract.
No runtime, CLI, SQLite, dataset, storage, service, fixture, or test behavior changed.
Required check is run or failure is recorded.
Lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`.
No full diffs.
No broad summaries.
No final contract text unless explicitly scoped by this stage and justified.
No future-stage implementation.
End with `OUTPUT LIMITS`.
