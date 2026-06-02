# STAGE 5M.5 — Deferred Contract Coverage Prioritization

Status: active task
Stage: 5M.5
Type: docs plan / prioritization
Depends on: docs/stages/reports/STAGE_5M_0_EXTERNAL_RISK_AUDIT_VERIFICATION_REPORT.md

---

## 0. CODEX ENTRY CONTRACT

1. Read `AGENTS.md` first.
2. Apply `.skills/stage-reviewer/SKILL.md` before implementation.
3. Apply `.skills/architecture-guard/SKILL.md` because this stage covers dataset contract, storage, service, fixture, and private archive boundaries.
4. Apply `.skills/stage-completion-auditor/SKILL.md` before claiming completion.
5. Do not implement tests or change runtime behavior in this stage.

## 1. PURPOSE

Turn deferred contract coverage gaps into a prioritized roadmap.

## 2. FILES TO INSPECT

Read:

```text
AGENTS.md
.skills/stage-reviewer/SKILL.md
.skills/architecture-guard/SKILL.md
.skills/stage-completion-auditor/SKILL.md
docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md
docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md
docs/development/NON_CHANNEL_SYNTHETIC_FIXTURES_PLAN.md
docs/architecture/PRIVATE_ARCHIVE_CONTRACT_DEFERRED_DECISION.md
docs/stages/reports/STAGE_5J_2_FIXTURE_TO_CONTRACT_VERIFICATION_REPORT.md
docs/stages/reports/STAGE_5L_1_RELEASE_CANDIDATE_DECISION_RECHECK_REPORT.md
tests/fixtures/non_channel_export/
tests/fixtures/db_export/
tests/services/rendering/
tests/services/db_export/
tests/cli/
tg_msg_manager/services/db_export/
tg_msg_manager/services/export/
tg_msg_manager/services/file_writer.py
tg_msg_manager/infrastructure/storage/
docs/stages/README.md
```

May change only:

```text
docs/development/DEFERRED_CONTRACT_COVERAGE_PRIORITIZATION.md
docs/development/README.md
docs/stages/reports/STAGE_5M_5_DEFERRED_CONTRACT_COVERAGE_PRIORITIZATION_REPORT.md
docs/stages/README.md
docs/stages/completed/stage_5m_5_deferred_contract_coverage_prioritization.md
```

Optional minimal cross-link only if needed:

```text
docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md
docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md
```

## 3. HARD PROHIBITIONS

- Do not implement tests, modify fixtures, change runtime/CLI/output/SQLite behavior, or alter storage/service logic.
- Do not include `export-pm` in the non-channel contract.
- Do not read private artifacts or require real Telegram data.
- Do not add analytics, OSINT interpretation, profiling, media analysis, OCR, STT, or LLM-dependent core behavior.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Inspect current contract docs, fixture coverage, tests, and relevant code boundaries without editing.
2. Rank generated-output filenames, `_partN` paths, rotation thresholds, DB-backed no-new-work / skip behavior, `.export_state`, full raw JSON profile, SQLite schema as public contract, real Telegram smoke checks, and private archive / `export-pm` contract.
3. For each item, record risk level, user-facing impact, regression likelihood, test feasibility, fixture needs, runtime-change needs, private-data needs, stage size, and recommended order.
4. Create or update the prioritization doc and minimal cross-links only if needed.
5. Write the report.

## 5. REQUIRED DOCS

Create `docs/stages/reports/STAGE_5M_5_DEFERRED_CONTRACT_COVERAGE_PRIORITIZATION_REPORT.md` in Russian.

Create or update `docs/development/DEFERRED_CONTRACT_COVERAGE_PRIORITIZATION.md`.

## 6. TESTS / VERIFICATION

Run:

```bash
git diff --check
```

Do not claim checks passed unless actually run.

## 7. REPORT

Report must include:

- outcome token;
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`;
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`;
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`;
- files inspected;
- prioritized coverage matrix;
- recommended stage order and stage sizes;
- explicit no-runtime/no-test/no-fixture-change confirmation.

Outcome token must be one of:

```text
DEFERRED_CONTRACT_COVERAGE_PRIORITIZED
DEFERRED_CONTRACT_COVERAGE_PRIORITIZED_WITH_DOC_CREATED
DEFERRED_CONTRACT_COVERAGE_BLOCKED_NEEDS_SOURCE_REVIEW
```

## 8. COMPLETION CRITERIA

- Every deferred coverage item is ranked with concrete reasoning.
- Prioritization doc and report exist.
- No tests, fixtures, runtime, CLI, output, or SQLite behavior changed.
- Lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- No full diffs, broad summaries, or implementation-stage content beyond prioritized planning.
