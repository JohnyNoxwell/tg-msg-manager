# STAGE 5Q.1 — PACKAGING METADATA / DEPENDENCY READINESS

Status: completed
Stage: 5Q.1
Type: packaging audit
Depends on: Stage 5P and Stage 5Q.0 reports with `PASSED`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply `.skills/stage-reviewer/SKILL.md`,
`.skills/architecture-guard/SKILL.md`, and
`.skills/stage-completion-auditor/SKILL.md` after report/cleanup.

Stop if prerequisites are not `PASSED`. Do not build packages or start 5Q.2.

## 1. PURPOSE

Audit packaging metadata, package identity, dependencies, build backend, and
entrypoint declarations without changing package state.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `pyproject.toml`
- `README.md`
- `Makefile`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- `docs/development/RELEASE_CHECKLIST_SCOPE.md`
- `docs/stages/reports/STAGE_5K_1_PACKAGING_METADATA_READINESS_AUDIT_REPORT.md`
- Stage 5P and Stage 5Q.0 reports
- `docs/stages/README.md`

Writable paths:

- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md` only for factual correction
- `docs/stages/reports/STAGE_5Q_1_PACKAGING_METADATA_DEPENDENCY_READINESS_REPORT.md`
- `docs/stages/README.md`
- lifecycle move of this stage file

## 3. HARD PROHIBITIONS

- Do not change `pyproject.toml`, version, dependencies, build backend,
  console script, package contents, production code, tests, CLI behavior,
  SQLite schema, dataset/export contracts, tags, artifacts, or publish state.
- Do not invent missing license/author/readme metadata; report it.
- Do not read private artifacts, sessions, credentials, real exports/logs/media/
  screenshots/DB files, or inject real Telegram data.
- Do not add analytics, OSINT, profiling, identity/media analysis, GUI/SaaS,
  or LLM-dependent core behavior.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify prerequisite reports and inspect metadata before editing.
2. Audit name, version source, console script, Python requirement, build backend,
   dependencies/dev extras, README metadata, and optional license/author fields.
3. Compare findings with the package identity/version policy; correct that doc
   only when it is factually stale.
4. Classify blockers and non-blocking gaps without building/installing.
5. Create the Russian report, then complete lifecycle cleanup.

## 5. REQUIRED DOCS

Default is report-only. Missing metadata is a finding, not permission to add it.
Rollback: revert only an inaccurate policy-doc correction.

## 6. TESTS / VERIFICATION

Required:

```bash
python3 -c 'import pathlib, tomllib; data=tomllib.loads(pathlib.Path("pyproject.toml").read_text()); print(data["project"]["name"]); print(data["project"]["version"]); print(data["project"].get("scripts", {}))'
git diff --check
```

If `tomllib` is unavailable on Python 3.9/3.10, record that exact reason and
inspect `pyproject.toml` directly; this alone is not a packaging blocker. Do not
run build/install/upload commands.

## 7. REPORT

Create `docs/stages/reports/STAGE_5Q_1_PACKAGING_METADATA_DEPENDENCY_READINESS_REPORT.md`
in Russian.

Include: `PASSED`, `FAILED`, or `PARTIAL`; commands/results; failures; metadata
summary; commands not run and why; blockers/non-blocking gaps; files changed; version and
`pyproject.toml` unchanged confirmation; no behavior/CLI/SQLite/dataset change;
final recommendation; applied skill paths; lifecycle notes.

## 8. COMPLETION CRITERIA

- Packaging readiness is evidence-backed without changing package state.
- Stage 5Q.2 is allowed only for `PASSED`, or `PARTIAL` with no blocking issue.
- Required report exists and lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`. Do not paste metadata dumps or broad summaries.
