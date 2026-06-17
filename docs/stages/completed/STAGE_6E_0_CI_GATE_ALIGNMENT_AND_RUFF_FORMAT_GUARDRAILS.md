# STAGE 6E.0 - CI GATE ALIGNMENT AND RUFF FORMAT GUARDRAILS

Status: active task
Stage: 6E.0
Type: bugfix
Depends on: GitHub Actions CI run 27715824577 failure in `test (3.11)` / `Run quality gates`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Execute Stage 6E.0 - CI gate alignment and Ruff format guardrails.

Goal:
Fix the process-level root cause where Codex can mark a stage complete without running the same full gate that GitHub Actions runs.

Do not start later stages.
Do not implement unrelated fixes.
Do not change project code except formatting drift required by `ruff format`.
Do not change public CLI behavior, output formats, SQLite schema, Telegram export logic, or data flow.

Use AGENTS.md compact output format.

## 1. SYMPTOM

GitHub Actions run `27715824577` failed in CI.

Failed job:
- `test (3.11)`

Failed step:
- `Run quality gates`

Command:

```bash
make verify
```

Failure:

```text
ruff format --check tg_msg_manager tests
Would reformat:
- tests/architecture/test_application_runtime_contract.py
- tests/architecture/test_static_boundaries.py
- tests/cli/test_cli.py
- tests/infrastructure/storage/test_storage_sqlite.py
- tg_msg_manager/application/resources.py
- tg_msg_manager/infrastructure/storage/_sqlite_write_path.py

6 files would be reformatted, 350 files already formatted
make[1]: *** [Makefile:14: format-check] Error 1
make: *** [Makefile:21: verify] Error 2
```

## 2. REPRODUCTION / OBSERVED OUTPUT

CI installs development dependencies and runs full repository verification:

```bash
python -m pip install -e .[dev]
make verify
```

`make verify` runs:

```bash
make lint
make format-check
make test
```

`format-check` checks the full repository scope:

```bash
ruff format --check tg_msg_manager tests
```

Observed bad completion pattern from previous stage reports:

```text
make verify: not run
```

## 3. LIKELY CAUSE

Likely cause:
- stage completion policy allows code/test stages to complete without `make verify`;
- focused checks can miss repo-wide formatter drift;
- `ruff>=0.15.0,<0.16` can resolve to different patch versions locally and in CI;
- CI run `27715824577` installed `ruff-0.15.17`.

## 4. FILES TO INSPECT

Required:
- `AGENTS.md`
- `Makefile`
- `pyproject.toml`
- `.github/workflows/ci.yml`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_6D_1_THROTTLER_RATE_RECOVERY_REPORT.md`

Optional only if present and needed:
- `.pre-commit-config.yaml`
- `docs/development/`
- `docs/stages/active/`

May create:
- `docs/stages/reports/STAGE_6E_0_CI_GATE_ALIGNMENT_AND_RUFF_FORMAT_GUARDRAILS_REPORT.md`

Do not read or change:
- unrelated source modules beyond formatting drift found by `ruff format`;
- unrelated docs;
- `docs/archive`;
- completed stage files except the required report listed above;
- existing `docs/stages/reports` files unrelated to this stage.

## 5. HARD PROHIBITIONS

Do not change CLI behavior.
Do not change SQLite schema.
Do not change export formats.
Do not change Telegram logic.
Do not change tests semantically unless required only for formatting.
Do not broaden architecture rules unrelated to CI/stage completion.
Do not add heavy dependency management tools unless explicitly justified in the report.
Do not add analytics, OSINT logic, profiling, fingerprinting, OCR, STT, media recognition, or LLM-dependent behavior.
Do not add new runtime dependencies.
Do not modify protected files except for mechanical documentation/policy alignment if explicitly required.
Do not mark this stage complete if `make verify` was not run after code/test/tooling changes.

## 6. MINIMAL PATCH TASKS

1. Confirm CI/local gate mismatch.
   - inspect `Makefile` and `.github/workflows/ci.yml`;
   - confirm the CI gate is `make verify`;
   - compare with the bad `make verify: not run` report pattern.

2. Align completion policy with CI.
   - update `AGENTS.md` so any stage touching code or tests cannot be marked `complete` unless full repo verification passed:

```bash
make verify
```

   - keep focused checks allowed but not a replacement for `make verify`;
   - allow exceptions only for docs-only stages with no code/test changes, or environment/tooling failure that makes `make verify` impossible;
   - require stages with impossible `make verify` to be marked incomplete or blocked, not complete.

3. Add explicit CI parity rule.
   - document that local/stage completion gate must match `.github/workflows/ci.yml`;
   - if CI runs `make verify`, local completion must run `make verify`.

4. Fix Ruff formatter drift.
   - prefer pinning Ruff exactly in `pyproject.toml`:

```toml
ruff==0.15.17
```

   - use an alternative lock file or dedicated constraints file only if better justified;
   - explain the chosen approach in the report.

5. Add a local pre-push/pre-commit guardrail.
   - minimally document that developers/Codex must run:

```bash
make pre-commit
```

   - add `.pre-commit-config.yaml` only if consistent with the project and not unnecessarily complex;
   - if `.pre-commit-config.yaml` is added, it must run equivalent checks or clearly document that `make verify` remains authoritative.

6. Format existing repository drift.
   - run:

```bash
ruff format tg_msg_manager tests
make verify
```

   - keep only resulting formatting and policy/tooling changes.

7. Update stage/report discipline.
   - update relevant docs/template language so future reports cannot claim completion with `make verify: not run` after code/test changes.

## 7. REGRESSION TESTS

No behavior regression test is required for policy/tooling-only changes.

If a test file is changed by this stage, the change must be formatting-only unless a separate required check proves a semantic test update is necessary.

## 8. NON-REGRESSION CHECKS

Required:

```bash
ruff format tg_msg_manager tests
make verify
git diff --check
```

If Ruff is pinned or dependency metadata changes, also run:

```bash
python -m pip install -e .[dev]
ruff --version
```

Non-regression expectations:
- CLI flags/defaults unchanged;
- SQLite schema unchanged;
- export formats unchanged;
- Telegram logic unchanged;
- tests changed only by formatting unless explicitly justified.

## 9. REQUIRED DOCS

Required:
- `AGENTS.md`
- `docs/stages/README.md` if active/completed stage index or discipline language changes;
- relevant `docs/development/` docs only if they already define verification, pre-commit, or contributor workflow rules;
- `docs/stages/reports/STAGE_6E_0_CI_GATE_ALIGNMENT_AND_RUFF_FORMAT_GUARDRAILS_REPORT.md`

Do not update unrelated docs.

## 10. REPORT

Create:

```text
docs/stages/reports/STAGE_6E_0_CI_GATE_ALIGNMENT_AND_RUFF_FORMAT_GUARDRAILS_REPORT.md
```

The report must be factual and written in Russian.

Record:
- exact Ruff version used;
- exact files changed;
- exact checks run;
- whether `make verify` passed;
- whether the CI parity rule was added;
- whether a pre-push/pre-commit guardrail was added;
- whether any exceptions remain;
- what was deliberately not changed;
- chosen Ruff drift approach and why;
- completion status.

## 11. COMPLETION CRITERIA

This stage is complete when:

- CI/local completion policy requires `make verify` for code/test changes;
- CI parity rule is documented;
- Ruff formatter drift is addressed with a justified narrow approach;
- local pre-push/pre-commit guardrail is added or documented;
- existing Ruff formatting drift is formatted;
- relevant docs/template language prevents `make verify: not run` completion after code/test changes;
- required checks are run and recorded;
- prohibited behavior remains unchanged;
- report exists;
- lifecycle cleanup is completed according to AGENTS.md.

If `make verify` cannot run after code/test/tooling changes, mark the stage incomplete or blocked and record the exact reason.

## 12. OUTPUT LIMITS

Use AGENTS.md compact final response format.

Final response must contain only:

```text
DONE:
- ...

CHANGED:
- ...

CHECKS:
- ...

PRESERVED:
- behavior: ...
- CLI: ...
- SQLite: ...
- scope: ...

NOTES:
- ...

STAGE:
- complete/incomplete: <reason if incomplete>
```

Do not paste full diffs.
Do not explain the task back to the user.
Do not include broad summaries.
Do not include future recommendations unless required by a real blocker.
