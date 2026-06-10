# STAGE 5U.3 — LICENSE METADATA APPLICATION

Status: active task
Stage: 5U.3
Type: packaging metadata implementation
Depends on: `docs/stages/reports/STAGE_5U_2_LICENSE_METADATA_DECISION_REPORT.md`
with `PASSED`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply `.skills/stage-reviewer/SKILL.md` before
implementation, `.skills/architecture-guard/SKILL.md` for scope confirmation,
and `.skills/stage-completion-auditor/SKILL.md` after report/cleanup.

Stop with `FAILED` if Stage 5U.2 is absent/not `PASSED` or its metadata decision
differs from this task. Do not start Stage 5U.4.

## 1. PURPOSE

Apply the approved MIT license text/header and package/public documentation
metadata without building or publishing packages.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `LICENSE`
- `pyproject.toml`
- `README.md`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- `docs/stages/reports/STAGE_5U_2_LICENSE_METADATA_DECISION_REPORT.md`
- `docs/stages/README.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`

Writable paths:

- `LICENSE`
- `pyproject.toml`
- `README.md`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- `docs/stages/reports/STAGE_5U_3_LICENSE_METADATA_APPLICATION_REPORT.md`
- `docs/stages/README.md`
- lifecycle move of this stage file

## 3. HARD PROHIBITIONS

- Do not change production code, tests, CLI/runtime behavior, SQLite,
  dataset/export contracts, dependencies, optional dependencies, build system,
  Python requirement, scripts, package discovery, package name, or version.
- Do not build/install/publish packages, create/delete/push tags, create a
  GitHub Release or stable tag, or start Stage 5U.4.
- Do not initialize Telegram, run live commands, or read private artifacts,
  sessions, credentials, real exports/logs/media/screenshots/DB files.
- Do not rewrite unrelated README/policy sections or add custom legal clauses.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify the Stage 5U.2 decision and capture before-state metadata,
   dependencies, build-system, scripts, Python requirement, and package discovery.
2. Change only the existing MIT header holder from `RP` to `R.P.`; verify the
   remaining LICENSE text is the standard MIT text with no extra restrictions.
3. Add `license = { file = "LICENSE" }` and a minimal classifiers list containing
   only `License :: OSI Approved :: MIT License` under `[project]`.
4. Add a short README license section linking to `LICENSE`; do not claim
   TestPyPI/PyPI publication, stable release, or GitHub Release.
5. Add one factual package-policy note recording MIT licensing and the LICENSE
   metadata source.
6. Verify exact allowed-file scope and unchanged protected metadata.
7. Create the Russian report, run final checks, then complete lifecycle cleanup.

## 5. REQUIRED DOCS

- README license note: `MIT License. See [LICENSE](LICENSE).`
- Package policy: short factual MIT/license-source note only.
- Russian report:
  `docs/stages/reports/STAGE_5U_3_LICENSE_METADATA_APPLICATION_REPORT.md`.

## 6. TESTS / VERIFICATION

Required:

```bash
git diff --check
python3 - <<'PY'
import pathlib
import tomllib

data = tomllib.loads(pathlib.Path("pyproject.toml").read_text())
print(data["project"]["name"])
print(data["project"]["version"])
print(data["project"].get("license"))
print(data["project"].get("license-files"))
print(data["project"].get("classifiers", []))
print(data["project"].get("dependencies", []))
print(data["project"].get("optional-dependencies", {}))
print(data["project"].get("scripts", {}))
print(data["project"]["requires-python"])
print(data["build-system"])
print(data["tool"]["setuptools"]["packages"]["find"])
PY
git status --short
```

Do not run build, install, upload, Telegram, or runtime test commands.

## 7. REPORT

Create the required report in Russian. Include: `PASSED` or `FAILED`; Stage 5U.2
evidence; license decision; files changed; pyproject metadata before/after;
README/policy notes; exact commands/results; commands not run and why;
unchanged name/version/dependencies/build-system/scripts/Python/package
discovery confirmation; preserved behavior/CLI/SQLite/dataset/export contracts;
forbidden-action confirmation; final recommendation; applied skill paths; and
lifecycle notes.

For `PASSED`, final recommendation:
`Proceed to STAGE_5U_4_LICENSE_METADATA_PACKAGE_VERIFICATION`.

## 8. COMPLETION CRITERIA

- LICENSE has standard MIT text and `Copyright (c) 2026 R.P.`.
- Approved pyproject metadata, README note, and policy note are present.
- Protected package metadata and repository behavior remain unchanged.
- Required report exists and lifecycle cleanup is completed according to
  `AGENTS.md`.

## 9. OUTPUT LIMITS

Follow `AGENTS.md`. Do not paste full diffs, reports, or license text.
