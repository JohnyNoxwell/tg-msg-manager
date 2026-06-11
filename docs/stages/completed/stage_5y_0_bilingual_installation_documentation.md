# STAGE 5Y.0 — BILINGUAL INSTALLATION DOCUMENTATION

Status: completed
Stage: 5Y.0
Type: docs
Depends on: `README.md`, `docs/user/QUICKSTART.md`, `pyproject.toml`, `config.example.json`, and the current stable PyPI package identity `tg-msg-manager`.

---

## 0. CODEX ENTRY CONTRACT

Before editing:

1. Read `AGENTS.md`.
2. Read and apply `.skills/stage-reviewer/SKILL.md`.
3. Inspect only files listed in this stage.
4. Write a compact plan with no more than 5 bullets.

During execution:

- Implement only this stage.
- Do not start future stages.
- Create the factual report before lifecycle cleanup.
- After the report exists, read and apply `.skills/stage-completion-auditor/SKILL.md`.
- Complete lifecycle cleanup according to `AGENTS.md`.

## 1. PURPOSE

Make installation and first-run documentation clear and visually scannable in
both Russian and English.

Document PyPI installation as the recommended user path, repository
installation as the latest-source path, editable installation as
developer-only, package upgrade commands, supported entrypoints, manual
`config.json` setup, and the visible cross-platform working directory.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `README.md`
- `docs/user/QUICKSTART.md`
- `pyproject.toml`
- `config.example.json`
- `docs/stages/README.md`

Do not inspect archive files, private artifacts, runtime source, unrelated
documentation, or existing `docs/stages/reports/` files unrelated to this
stage.

## 3. HARD PROHIBITIONS

Do not change:

- runtime code, package metadata, dependencies, or package version;
- CLI commands, flags, defaults, output, entrypoint mapping, or behavior;
- `config.example.json`;
- tests, SQLite schema, storage, datasets, services, exporters, scheduler, or
  aliases;
- existing reports unrelated to this stage.

Do not claim that `config.json` is created automatically.
Do not publish, tag, release, commit, or push.
Do not add runtime dependencies.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Replace the current repository-only quick-start installation blocks in both
   README languages with mirrored, scannable sections for PyPI, repository,
   developer editable install, upgrade, first launch, and working directory.
2. Make PyPI installation the recommended user path and include distinct
   macOS/Linux and Windows commands where command syntax differs.
3. Rewrite `docs/user/QUICKSTART.md` as a concise bilingual first-run guide
   covering install choice, manual `config.json` creation, first launch,
   working directory layout, exports, update, and links to canonical command
   and privacy docs.
4. Keep `COMMANDS.md` as the command reference; do not duplicate its command
   catalogue.

## 5. REQUIRED DOCS

Allowed documentation changes:

- `README.md`
- `docs/user/QUICKSTART.md`
- `docs/stages/reports/STAGE_5Y_0_BILINGUAL_INSTALLATION_DOCUMENTATION_REPORT.md`
- `docs/stages/README.md` and this stage file only during lifecycle cleanup
  after the report exists.

Do not update unrelated docs.

## 6. TESTS / VERIFICATION

Run:

```bash
rg -n "pip install tg-msg-manager|pip install --upgrade tg-msg-manager|pip install \\.|pip install -e|TG_MSG_MANAGER|config\\.json" README.md docs/user/QUICKSTART.md
git diff --check
```

Verify package name and console script against `pyproject.toml`.
Verify configuration fields against `config.example.json`.
Do not claim unrun checks passed.

## 7. REPORT

Create:

```text
docs/stages/reports/STAGE_5Y_0_BILINGUAL_INSTALLATION_DOCUMENTATION_REPORT.md
```

The report must be written in Russian and include:

- status;
- installation paths documented;
- bilingual parity confirmation;
- exact files changed;
- exact checks run;
- skills applied;
- confirmation that package identity, entrypoint, and config claims were
  verified;
- behavior, CLI, SQLite, dataset, storage, export, and private-artifact
  preservation confirmations;
- lifecycle actions.

## 8. COMPLETION CRITERIA

This stage is complete only if:

- README clearly distinguishes PyPI, repository, developer, and upgrade paths
  in Russian and English;
- quickstart gives a bilingual first-run path without duplicating
  `COMMANDS.md`;
- documentation does not claim automatic `config.json` creation;
- package and entrypoint claims match `pyproject.toml`;
- the factual report exists;
- `stage-completion-auditor` has been applied;
- lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`, stay under 1200 characters, and include
only meaningful sections.

Do not include full diffs, large copied file content, markdown tables, generic
summaries, speculation, or future recommendations.
