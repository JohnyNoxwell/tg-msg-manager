# STAGE 5Z.1 — FIRST-RUN CONFIG BOOTSTRAP AND PATCH RELEASE v0.1.2

Status: active task
Stage: 5Z.1
Type: bugfix and release operation
Depends on: observed first-run behavior where `~/TG_MSG_MANAGER` is created without `config.json`, and explicit user authorization to commit and publish.

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md`. Fix the observed bug with the smallest safe patch, then
commit, tag, and publish `0.1.2`. Do not start later stages or add features.

## 1. SYMPTOM

After a PyPI-installed CLI first run, the working directory exists but the
base `config.json` file is absent.

## 2. REPRODUCTION / OBSERVED OUTPUT

Run `tg-msg-manager` with a clean `HOME`; inspect `~/TG_MSG_MANAGER`.

## 3. LIKELY CAUSE

`build_app_runtime` creates runtime directories before loading settings but
does not create a missing configuration file.

## 4. FILES TO INSPECT

Required: `tg_msg_manager/core/config.py`, `tg_msg_manager/core/runtime.py`,
`tg_msg_manager/cli/__init__.py`, focused tests, `README.md`,
`docs/user/QUICKSTART.md`, `CHANGELOG.md`, `pyproject.toml`, release workflow,
this stage lifecycle path, its report, and `docs/stages/README.md`.

Do not change unrelated modules, docs, workflows, dependencies, or schemas.

## 5. HARD PROHIBITIONS

Do not overwrite an existing config. Do not include real credentials. Do not
change command names, flags, SQLite schema, dataset formats, or export logic.
Do not dispatch PyPI publication more than once.

## 6. MINIMAL PATCH TASKS

1. Create a safe default `config.json` atomically when missing.
2. Stop credential-requiring commands with a clear setup message until
   placeholders are replaced.
3. Add focused regression coverage and update bilingual first-run docs.
4. Set version `0.1.2`, commit, push, tag, publish once, and verify public
   version visibility.

## 7. REGRESSION TESTS

Run only focused config/CLI tests required for the first-run path.

## 8. NON-REGRESSION CHECKS

Existing config content, local commands without credentials, CLI names,
SQLite schema, datasets, and exports remain unchanged.

## 9. REQUIRED DOCS

Update user-facing first-run docs and changelog. Create
`docs/stages/reports/STAGE_5Z_1_FIRST_RUN_CONFIG_BOOTSTRAP_AND_PATCH_RELEASE_V0_1_2_REPORT.md`.

## 10. REPORT

Record changed files, focused checks, commit, tag, publish run, public PyPI
evidence, preserved behavior, and lifecycle actions in Russian.

## 11. COMPLETION CRITERIA

Complete when first run creates a safe config without overwriting existing
content and `0.1.2` is committed, tagged, published once, publicly visible,
reported, and moved to completed stages.

## 12. OUTPUT LIMITS

Follow `AGENTS.md`; no full diffs, credentials, private artifacts, or broad
summaries.
