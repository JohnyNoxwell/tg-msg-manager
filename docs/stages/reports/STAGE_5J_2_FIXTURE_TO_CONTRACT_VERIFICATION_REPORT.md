# Отчет Stage 5J.2 - Fixture-To-Contract Verification

## Статус

Stage 5J.2 завершен.

## Итоговый вывод

FIXTURE_TO_CONTRACT_VERIFICATION_COMPLETE_AFTER_DOC_FIXES

## Проверенные файлы

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/reports/STAGE_5J_1_NON_CHANNEL_CONTRACT_TESTS_IMPLEMENTATION_REPORT.md`
- Stage 5I.1/5I.2/5I.3 reports
- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md`
- `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md`
- `docs/development/NON_CHANNEL_SYNTHETIC_FIXTURES_PLAN.md`
- `docs/architecture/TXT_RENDERING.md`
- `docs/architecture/PRIVATE_ARCHIVE_CONTRACT_DEFERRED_DECISION.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `docs/stages/README.md`
- `tests/fixtures/non_channel_export/`
- `tests/fixtures/db_export/`
- `tests/services/rendering/`
- `tests/services/db_export/`
- `tests/cli/`

## Claim-to-fixture/test mapping

- Scope: user/group `export` and `db-export` under `DB_EXPORTS/`.
  Fixture support: both fixture directories exist.
  Test support: rendering, JSONL, writer-state, CLI scope tests.
  Deferred: private archive / `export-pm`.
- TXT `context-readable` markers.
  Fixture support: `expected_export_context_readable.txt` and `expected_db_context_readable.txt`.
  Test support: renderer golden match plus marker assertions.
  Deferred: broad cosmetic line immutability.
- TXT `legacy` markers.
  Fixture support: `expected_export_legacy.txt` and `expected_db_legacy.txt`.
  Test support: renderer golden match plus date/reply/missing-reply assertions.
  Deferred: broad cosmetic line immutability.
- Compact `ai` JSONL key set.
  Fixture support: `expected_export_ai.jsonl` and `expected_db_ai.jsonl`.
  Test support: allowed-key set, empty-value omission, reply/topic/media/forward/edit/reaction assertions, serializer golden match.
  Deferred: full raw JSON profile.
- `.writer_state`.
  Fixture support: `expected_writer_state.json`.
  Test support: path, `current_part`, and `current_count` shape.
  Deferred: DB-backed no-new-work/skip behavior.
- `.export_state`.
  Fixture support: no current fixture by design.
  Test support: absence assertion.
  Deferred: legacy fallback only if future scope explicitly covers it.
- Filenames and part files.
  Fixture support: writer-state path only.
  Test support: partial path assertion.
  Deferred: generated output filenames, `_partN` paths, and exact rotation thresholds.
- Privacy and sensitive artifacts.
  Fixture support: fixture README files and synthetic payloads.
  Test support: README boundary assertions and payload marker scan.
  Deferred: real Telegram smoke data.
- `export-pm` exclusion.
  Fixture support: fixture README out-of-scope wording.
  Test support: README assertions and CLI contract scope assertion.
  Deferred: private archive contract tests.

## Docs fixes

- `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md`: status and execution wording updated from future-only plan to plan plus focused implemented tests.
- `docs/development/NON_CHANNEL_SYNTHETIC_FIXTURES_PLAN.md`: status, fixture locations, tests, and deferred items updated to reflect 5I.1 fixtures and 5J.1 tests.
- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md`: known limitations updated to state focused tests exist and broader generated-output coverage remains planned.

## Missing coverage

- Generated output filenames and `_partN` paths.
- Exact rotation thresholds.
- DB-backed no-new-work/skip behavior.
- Full raw JSON profile.
- SQLite schema as a public contract.
- Real Telegram smoke data.
- Private archive / `export-pm` contract.

## Проверки

- `python3 -m unittest discover tests -p '*non_channel*contract*.py'`: passed, 14 tests.
- `git diff --check`: passed.

## Навыки

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`

## Подтверждения

- Runtime code, tests, fixtures, expected outputs, CLI behavior, SQLite schema, storage behavior, TXT rendering, JSONL schema, and output behavior were not changed.
- Private artifacts, real exports, sessions, credentials, ignored DB files, logs, screenshots, media and real Telegram data were not read.
- `export-pm` remains excluded from the non-channel user/group + `db-export` contract.

## Lifecycle

- Финальный отчет создан.
- Stage-файл перенесен из `docs/stages/active/` в `docs/stages/completed/`.
- `docs/stages/README.md` обновлен.
