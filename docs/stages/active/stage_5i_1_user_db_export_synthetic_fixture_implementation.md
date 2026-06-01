# STAGE 5I.1 — User/DB Export Synthetic Fixture Implementation

Status: active task
Stage: 5I.1
Type: implementation
Depends on: docs/stages/reports/STAGE_5H_2_USER_DB_EXPORT_SYNTHETIC_FIXTURES_PLAN_REPORT.md and docs/development/NON_CHANNEL_SYNTHETIC_FIXTURES_PLAN.md

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Then read `.skills/stage-reviewer/SKILL.md`, `.skills/architecture-guard/SKILL.md`, `.skills/stage-completion-auditor/SKILL.md`, and this stage file. Use `stage-reviewer` before implementation, `architecture-guard` before reporting, and `stage-completion-auditor` before claiming completion.

Do not execute 5I.2 or 5I.3.

## 1. PURPOSE

Create the first privacy-safe synthetic fixture set for user/group `export` and `db-export`. The stage adds checked-in synthetic fixture data and expected outputs only where current repository structure supports them.

This stage must not change runtime behavior, tests, CLI behavior, schemas, or final contract docs.

## 2. FILES TO INSPECT

Required docs:

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/reports/STAGE_5H_1_NON_CHANNEL_EXPORT_CONTRACT_DESIGN_PRECHECK_REPORT.md`
- `docs/stages/reports/STAGE_5H_2_USER_DB_EXPORT_SYNTHETIC_FIXTURES_PLAN_REPORT.md`
- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_DESIGN.md`
- `docs/development/NON_CHANNEL_SYNTHETIC_FIXTURES_PLAN.md`
- `docs/architecture/TXT_RENDERING.md`
- `docs/architecture/DATASET_FORMAT.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `README.md`
- `COMMANDS.md`
- `docs/stages/README.md`

Inspect only as needed to choose fixture paths and output names:

- `tg_msg_manager/cli_parser.py`
- `tg_msg_manager/services/export/`
- `tg_msg_manager/services/db_export/`
- `tg_msg_manager/services/rendering/`
- `tg_msg_manager/services/context/`
- `tg_msg_manager/infrastructure/storage/`
- `tests/`
- `tests/fixtures/`
- `tests/cli/`
- `tests/services/db_export/`
- `tests/services/rendering/`

Allowed to create or edit:

- `tests/fixtures/non_channel_export/**`
- `tests/fixtures/db_export/**`
- `docs/examples/non_channel_export/**`
- `docs/examples/db_export/**`
- `docs/stages/reports/STAGE_5I_1_USER_DB_EXPORT_SYNTHETIC_FIXTURE_IMPLEMENTATION_REPORT.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_5i_1_user_db_export_synthetic_fixture_implementation.md`

Optional link-only updates if required:

- `docs/development/NON_CHANNEL_SYNTHETIC_FIXTURES_PLAN.md`
- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_DESIGN.md`

## 3. HARD PROHIBITIONS

- Do not change runtime code, test code, CLI behavior, output formats, TXT rendering, JSONL schema, SQLite schema, storage behavior, services, or protected files.
- Do not create final contract docs.
- Do not include `export-pm`, private archive outputs, private archive fixtures, real Telegram data, real IDs, real usernames, real chat names, real message text, screenshots, sessions, DB files, logs, credentials, media files, or private artifacts.
- Do not add binary media.
- Do not use realistic private conversations or sensitive-looking content.
- Do not add runtime dependencies.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Inspect current fixture/example layout and choose the minimal safe fixture locations.
2. Create synthetic fixture README files that state all data is artificial and `export-pm` is out of scope.
3. Create a small synthetic corpus for user/group `export` and `db-export` using obvious synthetic IDs, usernames, chat titles, timestamps, message text, and relative paths.
4. Add expected outputs for compact JSONL, TXT `context-readable`, and TXT `legacy` only if they can be represented without runtime changes.
5. Include reply-present, reply-missing, before/target/after context, two synthetic chats, and media metadata-only cases where safe.
6. Add `.export_state` and `.writer_state` expected files only if current output shape is clear; otherwise defer them in the report.
7. Update only optional docs listed above if fixture locations need links.

## 5. REQUIRED DOCS

Create the stage report. Update `docs/stages/README.md` during lifecycle cleanup. Update optional docs only for short links to fixture locations; do not duplicate fixture content.

## 6. TESTS / VERIFICATION

Run:

```bash
git diff --check
```

Run any existing fixture/static checks if found during inspection. If none exist, record that contract tests are deferred to 5I.2.

Manual verification required:

- All fixture data is obviously synthetic.
- No real-looking IDs, usernames, chat names, message text, paths, media, DB files, logs, screenshots, or sessions were added.
- No runtime, CLI, SQLite, TXT, JSONL, or output behavior changed.

## 7. REPORT

Create `docs/stages/reports/STAGE_5I_1_USER_DB_EXPORT_SYNTHETIC_FIXTURE_IMPLEMENTATION_REPORT.md` in Russian. Include status/outcome token, files inspected, fixture files created, cases covered, cases deferred, privacy verification, docs links changed or not changed, checks run, no runtime/CLI/SQLite/output behavior changes, `export-pm` out-of-scope confirmation, and lifecycle notes.

Allowed outcome tokens:

- `SYNTHETIC_FIXTURES_IMPLEMENTED_MINIMAL_SET`
- `SYNTHETIC_FIXTURES_IMPLEMENTED_WITH_DOC_LINKS`
- `SYNTHETIC_FIXTURES_PARTIALLY_IMPLEMENTED_DEFERRED_COMPLEX_CASES`
- `BLOCKED_FIXTURE_SCOPE_UNCLEAR`

## 8. COMPLETION CRITERIA

- Synthetic fixture files are created under approved paths or the stage blocks with exact reason.
- Fixture README files document privacy boundaries.
- Required report exists.
- Required checks and manual verification are recorded.
- No runtime/test-code/CLI/SQLite/output behavior changed.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`, be in Russian, avoid full diffs, and mention only changed files, checks, preservation, notes, and stage status.
