# STAGE 5H.3 — Private Archive Contract Deferred Decision

Status: active task
Stage: 5H.3
Type: docs decision
Depends on: `docs/stages/reports/STAGE_5G_2_NON_CHANNEL_DATASET_CONTRACT_PRECHECK_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.
Use `.skills/stage-reviewer/SKILL.md` before executing this stage.
Use `.skills/architecture-guard/SKILL.md` because this stage touches private archive, storage, CLI, media, and contract boundaries.
Use `.skills/stage-completion-auditor/SKILL.md` before claiming completion.
Do not execute any later stage.

## 1. PURPOSE

Record whether and how private archive contract work should remain deferred.
Keep `export-pm` outside user/group plus DB export contract work.
Produce a report-only or docs-only deferred decision.
Do not create a private archive contract.

## 2. FILES TO INSPECT

Required docs:

```text
AGENTS.md
.skills/stage-reviewer/SKILL.md
.skills/architecture-guard/SKILL.md
.skills/stage-completion-auditor/SKILL.md
docs/stages/reports/STAGE_5G_2_NON_CHANNEL_DATASET_CONTRACT_PRECHECK_REPORT.md
docs/architecture/CURRENT_PROJECT_CONTEXT.md
docs/architecture/README.md
docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md
README.md
COMMANDS.md
docs/stages/README.md
```

Inspect code/tests only as needed:

```text
tg_msg_manager/cli_parser.py
tg_msg_manager/cli/commands/
tg_msg_manager/services/private_archive/
tg_msg_manager/services/rendering/
tg_msg_manager/infrastructure/storage/
tests/services/private_archive/
```

Allowed to change:

```text
docs/stages/reports/STAGE_5H_3_PRIVATE_ARCHIVE_CONTRACT_DEFERRED_DECISION_REPORT.md
docs/stages/README.md
docs/stages/completed/stage_5h_3_private_archive_contract_deferred_decision.md
docs/architecture/PRIVATE_ARCHIVE_CONTRACT_DEFERRED_DECISION.md
```

Do not inspect real private dialogs, Telegram exports, sessions, credentials, logs, screenshots, local DB files, media, or ignored private content.

## 3. HARD PROHIBITIONS

Do not create a private archive contract.
Do not change runtime behavior, CLI behavior, folder naming, log rendering, media handling, SQLite behavior, sync state behavior, tests, command names, flags, defaults, filenames, or output layouts.
Do not create private archive fixtures.
Do not include `export-pm` in user/group plus DB export contract work.
Do not use real or realistic private conversation content, names, IDs, paths, logs, screenshots, sessions, DB files, or media.
Protected private archive service facades may be inspected only; do not edit them.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Inspect required docs and minimum code/tests needed; do not edit yet.
2. Decide whether `export-pm` is a dataset contract candidate, an archive contract candidate, or neither.
3. Identify possible future contract surfaces and implementation details.
4. Assess readiness of tests, docs, synthetic fixtures, media policy, and sequencing after user+DB export contracts.
5. Define privacy constraints for any future private archive examples.
6. Recommend one future path from the allowed outcome tokens.
7. Optionally create `docs/architecture/PRIVATE_ARCHIVE_CONTRACT_DEFERRED_DECISION.md` as deferred decision only.
8. Write the required report in Russian.
9. Complete lifecycle cleanup according to `AGENTS.md`.

## 5. REQUIRED DOCS

Always create:

```text
docs/stages/reports/STAGE_5H_3_PRIVATE_ARCHIVE_CONTRACT_DEFERRED_DECISION_REPORT.md
```

Optional if useful:

```text
docs/architecture/PRIVATE_ARCHIVE_CONTRACT_DEFERRED_DECISION.md
```

Update `docs/stages/README.md` during lifecycle cleanup.
No final contract docs, fixture files, test files, or user-facing docs are allowed in this stage.

## 6. TESTS / VERIFICATION

Run:

```bash
git diff --check
```

If a decision doc is created, verify:

```text
it is marked deferred decision, not final contract
it does not create runtime guarantees
it uses no private or realistic example data
it keeps export-pm outside user/group plus DB export contract work
```

Runtime tests are not required for report-only or decision-only work.
Do not claim checks passed unless they were run.

## 7. REPORT

Report must be factual and written in Russian.
Include:

```text
status and outcome token
files inspected
current understanding of export-pm output family
whether it remains deferred
why it must stay separate from user/group plus DB export contracts
future prerequisites
privacy constraints
whether an optional decision doc was created
no runtime/CLI/SQLite behavior changes confirmation
private artifact boundary confirmation
checks run
lifecycle notes
architecture-guard: applied from .skills/architecture-guard/SKILL.md
stage-reviewer: applied from .skills/stage-reviewer/SKILL.md
stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md
```

Outcome token must be one of:

```text
PRIVATE_ARCHIVE_CONTRACT_DEFERRED_DECISION_RECORDED
PRIVATE_ARCHIVE_CONTRACT_PRECHECK_RECOMMENDED_LATER
PRIVATE_ARCHIVE_FIXTURES_FIRST_RECOMMENDED
PRIVATE_ARCHIVE_CONTRACT_NOT_RECOMMENDED
BLOCKED_INSUFFICIENT_CONTEXT
```

## 8. COMPLETION CRITERIA

Required report exists.
Optional decision doc, if created, is deferred-decision only.
`export-pm` remains outside user/group plus DB export contracts.
No runtime, CLI, SQLite, media, sync state, service, fixture, test, or behavior changed.
Required check is run or failure is recorded.
Lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`.
No full diffs.
No broad summaries.
No private archive contract text.
No future-stage implementation.
End with `OUTPUT LIMITS`.
