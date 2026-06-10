# STAGE 5U.2 — LICENSE METADATA DECISION

Status: active task
Stage: 5U.2
Type: packaging decision
Depends on: `docs/stages/reports/STAGE_5U_1_POST_RC_TAG_SMOKE_FROM_TAG_REPORT.md`
with `PASSED`; license gap in
`docs/stages/reports/STAGE_5Q_1_PACKAGING_METADATA_DEPENDENCY_READINESS_REPORT.md`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply `.skills/stage-reviewer/SKILL.md` before
implementation, `.skills/architecture-guard/SKILL.md` for scope confirmation,
and `.skills/stage-completion-auditor/SKILL.md` after report/cleanup.

Stop with `FAILED` if a required file is missing, prerequisite evidence is
ambiguous, or Stage 5U.1 is not `PASSED`. Do not start Stage 5U.3.

## 1. PURPOSE

Confirm prerequisite evidence and record the exact MIT package-metadata form
that Stage 5U.3 may apply. This stage makes no package or public-doc changes.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `LICENSE`
- `pyproject.toml`
- `README.md`
- `docs/stages/README.md`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- `docs/development/RELEASE_CANDIDATE_DECISION.md`
- `docs/stages/reports/STAGE_5U_CREATE_RELEASE_CANDIDATE_TAG_REPORT.md`
- `docs/stages/reports/STAGE_5U_1_POST_RC_TAG_SMOKE_FROM_TAG_REPORT.md`
- `docs/stages/reports/STAGE_5Q_1_PACKAGING_METADATA_DEPENDENCY_READINESS_REPORT.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`

Writable paths:

- `docs/stages/reports/STAGE_5U_2_LICENSE_METADATA_DECISION_REPORT.md`
- `docs/stages/README.md`
- lifecycle move of this stage file

## 3. HARD PROHIBITIONS

- Do not edit `LICENSE`, `pyproject.toml`, `README.md`, package policy,
  production code, tests, dependencies, build-system requirements, or version.
- Do not build/install/publish packages, create/delete/push tags, create a
  GitHub Release or stable tag, or start Stage 5U.3.
- Do not initialize Telegram, run live commands, or read private artifacts,
  sessions, credentials, real exports/logs/media/screenshots/DB files.
- Do not change CLI/runtime behavior, SQLite, dataset/export contracts, or add
  analytics, OSINT, profiling, identity/media analysis, GUI/SaaS, or
  LLM-dependent core behavior.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify Stage 5U.1 is `PASSED` and confirms exact-tag build/install/safe smoke,
   no TestPyPI/PyPI/GitHub Release, and no stable tag.
2. Verify Stage 5Q.1 records missing `pyproject.toml` license metadata as a
   non-blocking gap.
3. Inspect current license-related metadata with the required `tomllib` command;
   record name, version, license, license-files, classifiers, dependencies, and
   build-system requirement without editing.
4. Verify `LICENSE` is standard MIT text and record the existing holder mismatch
   `RP` versus required `R.P.`.
5. Decide the exact Stage 5U.3 metadata form. Because `setuptools>=61.0` must
   remain unchanged, use the compatible PEP 621 form
   `license = { file = "LICENSE" }` and add only the MIT classifier; do not add
   `license-files` or change the build-system floor.
6. Create the Russian report, run final checks, then complete lifecycle cleanup.

## 5. REQUIRED DOCS

Create only
`docs/stages/reports/STAGE_5U_2_LICENSE_METADATA_DECISION_REPORT.md`.
Do not update package/public docs in this decision stage.

## 6. TESTS / VERIFICATION

Required:

```bash
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
print(data["build-system"])
PY
git diff --check
git status --short
```

Do not claim checks passed unless run.

## 7. REPORT

Create the required report in Russian. Include: `PASSED` or `FAILED`;
prerequisite evidence; current LICENSE/header and metadata; exact metadata
decision and compatibility reason; unchanged name/version/dependencies/
build-system confirmation; commands/results; commands not run and why;
forbidden-action confirmation; final recommendation; applied skill paths; and
lifecycle notes.

For `PASSED`, final recommendation:
`Proceed to STAGE_5U_3_LICENSE_METADATA_APPLICATION`.

## 8. COMPLETION CRITERIA

- Prerequisite evidence is valid and the exact metadata form is decided.
- No package metadata, public docs, code, tests, behavior, dependency, version,
  tag, release, or publish state changed.
- Required report exists and lifecycle cleanup is completed according to
  `AGENTS.md`.

## 9. OUTPUT LIMITS

Follow `AGENTS.md`. Do not paste full reports, diffs, or license text.
