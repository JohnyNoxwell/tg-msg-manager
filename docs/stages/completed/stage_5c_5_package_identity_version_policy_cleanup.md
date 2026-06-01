# STAGE 5C.5 — PACKAGE IDENTITY / VERSION POLICY CLEANUP

Status: completed
Stage: 5C.5
Type: packaging documentation / metadata cleanup
Depends on: Stage 5C.4 complete; current package metadata in `pyproject.toml`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Execute Stage 5C.5 only.

Goal:
Clarify package identity, public entrypoints, and version policy without renaming the package or changing runtime behavior.

Do not start Stage 5D.0.
Do not publish, tag, or release anything.
Use `AGENTS.md` compact output format.

## 1. PURPOSE

Resolve stale or ambiguous package identity surfaces, such as project name, module name, console script, README branding, and version source. Keep the cleanup factual and small.

## 2. FILES TO INSPECT

Required:
- `AGENTS.md`
- this stage file
- `pyproject.toml`
- `tg_msg_manager/__init__.py`
- `README.md`
- `COMMANDS.md`
- `docs/README.md`
- `docs/development/README.md`
- `docs/development/CLI_CONTRACT.md`
- `tests/cli/test_cli.py`

May change:
- `pyproject.toml`
- `README.md`
- `COMMANDS.md`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- `docs/development/README.md`
- `docs/README.md`
- `docs/stages/reports/STAGE_5C_5_PACKAGE_IDENTITY_VERSION_POLICY_CLEANUP_REPORT.md`
- `docs/stages/README.md`
- this stage file location during lifecycle cleanup

Do not read or change:
- runtime services/storage code;
- ignored local artifacts;
- archive files;
- completed stage files unrelated to this stage.

## 3. HARD PROHIBITIONS

- Do not rename `tg-msg-manager`, `tg_msg_manager`, or the `tg-msg-manager` console script.
- Do not add a runtime version API unless a concrete current import contract already requires it.
- Do not change command behavior, aliases, parser behavior, output formats, or packaging dependencies.
- Do not add build dependencies.
- Do not alter SQLite schema, dataset formats, state files, or export behavior.
- Do not add analytics, OSINT, profiling, OCR, STT, media recognition, or LLM behavior.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Audit identity surfaces.
   - Record current package name, module name, console script, version, description, README title, and docs references.
   - Do not edit yet.

2. Decide the version policy.
   - Prefer `pyproject.toml` as the single packaging version source unless current code proves otherwise.
   - If no runtime `__version__` exists, document that absence; do not create one by default.

3. Patch stale metadata/docs only.
   - If `pyproject.toml` description is stale, update only the description.
   - Create `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`.
   - Link it from development/docs indexes.
   - Keep README/COMMANDS edits minimal and factual.

4. Verify public entrypoints.
   - Run section 6 commands.
   - Confirm the console script mapping remains unchanged.

5. Report and cleanup.
   - Create the Russian report.
   - Perform lifecycle cleanup only after report exists.

## 5. REQUIRED DOCS

Required:
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- `docs/development/README.md`
- `docs/README.md`
- `docs/stages/reports/STAGE_5C_5_PACKAGE_IDENTITY_VERSION_POLICY_CLEANUP_REPORT.md`
- `docs/stages/README.md` during lifecycle cleanup

Conditional:
- `pyproject.toml` only if metadata description is stale.
- `README.md` / `COMMANDS.md` only if identity wording is stale.

## 6. TESTS / VERIFICATION

Run:
- `python3 -m tg_msg_manager.cli --help`
- `python3 -m compileall tg_msg_manager`
- `python3 -m pytest tests/cli/test_cli.py -q`
- `git diff --check`

Do not run packaging publish commands.

## 7. REPORT

Create `docs/stages/reports/STAGE_5C_5_PACKAGE_IDENTITY_VERSION_POLICY_CLEANUP_REPORT.md` in Russian.

Include:
- identity surfaces audited;
- metadata/docs changed;
- version policy chosen;
- checks run;
- confirmation that package/module/script names were preserved;
- confirmation that runtime behavior, CLI behavior, dataset formats, and SQLite schema were unchanged.

## 8. COMPLETION CRITERIA

- Identity and version policy doc exists and is indexed.
- No package/module/script rename occurs.
- Public CLI still imports and shows help.
- lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- No full diffs.
- No release notes unless explicitly requested.
- No markdown tables in the final response.
