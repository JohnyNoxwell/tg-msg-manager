# STAGE 5C.4 — PRIVACY & SENSITIVE ARTIFACTS GUIDE

Status: completed
Stage: 5C.4
Type: documentation
Depends on: current `.gitignore`, runtime artifact directories, and config docs

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Execute Stage 5C.4 only.

Goal:
Document which local files and directories can contain secrets or private Telegram data, and how contributors/agents must avoid exposing them.

Do not start Stage 5C.5 or later stages.
Do not inspect private artifact contents.
Use `AGENTS.md` compact output format.

## 1. PURPOSE

Add a current privacy and sensitive artifacts guide for a local Telegram export/data pipeline. The guide must be operational and factual, not a security product claim.

## 2. FILES TO INSPECT

Required:
- `AGENTS.md`
- this stage file
- `.gitignore`
- `config.example.json`
- `README.md`
- `COMMANDS.md`
- `docs/README.md`
- `docs/development/README.md`
- `tests/fixtures/stage5/README.md`

May inspect names only:
- `git status --ignored --short`

May change:
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `docs/development/README.md`
- `docs/README.md`
- `README.md`
- `docs/stages/reports/STAGE_5C_4_PRIVACY_SENSITIVE_ARTIFACTS_GUIDE_REPORT.md`
- `docs/stages/README.md`
- this stage file location during lifecycle cleanup

Do not read or change contents of:
- `config.json`
- `config.local.json`
- `.env`
- `*.session`
- `messages.db`
- `DB_EXPORTS/`
- `exports/`
- `PRIVAT_DIALOGS/`
- `PUBLIC_GROUPS/`
- local logs with private data

## 3. HARD PROHIBITIONS

- Do not print, copy, summarize, or inspect real private messages, config secrets, session data, or database contents.
- Do not delete or move local artifacts.
- Do not change `.gitignore` unless a concrete missing sensitive pattern is found.
- Do not change runtime code.
- Do not add encryption, redaction, upload, analytics, OSINT, profiling, OCR, STT, or LLM behavior.
- Do not change CLI behavior, dataset formats, or SQLite schema.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Inventory sensitive artifact names.
   - Use `.gitignore`, config docs, and `git status --ignored --short`.
   - Record paths by category only.
   - Do not open ignored artifact files.

2. Draft the guide.
   - Create `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`.
   - Cover credentials, Telethon sessions, SQLite DB, exports, logs, fixtures, reports, and screenshots.
   - Include agent rules for not reading ignored private artifacts unless explicitly scoped.

3. Link the guide.
   - Add a link in `docs/development/README.md`.
   - Add a link in `docs/README.md`.
   - Add a short root `README.md` link only if it fits existing docs navigation.

4. Verify.
   - Run section 6 checks.
   - Confirm no private file contents appear in diff.

5. Report and cleanup.
   - Create the Russian report.
   - Perform lifecycle cleanup only after report exists.

## 5. REQUIRED DOCS

Required:
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `docs/development/README.md`
- `docs/README.md`
- `docs/stages/reports/STAGE_5C_4_PRIVACY_SENSITIVE_ARTIFACTS_GUIDE_REPORT.md`
- `docs/stages/README.md` during lifecycle cleanup

Conditional:
- `README.md` only for a short navigation link.
- `.gitignore` only if a concrete sensitive pattern is missing.

## 6. TESTS / VERIFICATION

Run:
- `git status --ignored --short`
- `git diff --check`

No runtime tests are required for docs-only changes.

## 7. REPORT

Create `docs/stages/reports/STAGE_5C_4_PRIVACY_SENSITIVE_ARTIFACTS_GUIDE_REPORT.md` in Russian.

Include:
- files inspected;
- sensitive artifact categories documented;
- exact docs changed;
- checks run;
- confirmation that private artifact contents were not opened;
- confirmation that runtime, CLI, dataset formats, and SQLite schema were unchanged.

## 8. COMPLETION CRITERIA

- Guide exists and is linked from development/docs index.
- No secret or private artifact content is copied into docs.
- No runtime behavior changes are made.
- lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- No private filenames beyond category/path patterns unless already tracked public examples.
- No full diffs.
- No markdown tables in the final response.
