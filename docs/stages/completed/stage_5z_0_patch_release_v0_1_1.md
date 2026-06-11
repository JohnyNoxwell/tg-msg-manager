# STAGE 5Z.0 — PATCH RELEASE v0.1.1

Status: completed
Stage: 5Z.0
Type: release operation
Depends on: clean synchronized `main`, successful CI for commit `2b9182f`, existing PyPI Trusted Publishing workflow, existing GitHub Release `v0.1.0`, and explicit user authorization to release.

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md`. Apply `.skills/stage-reviewer/SKILL.md`,
`.skills/architecture-guard/SKILL.md`, and
`.skills/stage-completion-auditor/SKILL.md`. Execute irreversible actions only
after preceding checks pass. Never retry a package publication dispatch.

## 1. PURPOSE

Prepare, verify, tag, publish, and publicly verify patch release `0.1.1`
containing the stable visible runtime directory and bilingual installation
documentation.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `pyproject.toml`
- `CHANGELOG.md`
- `.github/workflows/ci.yml`
- `.github/workflows/pypi-publish.yml`
- `docs/stages/README.md`

Writable repository paths are limited to `pyproject.toml`, `CHANGELOG.md`, this
stage lifecycle path, its report, and `docs/stages/README.md`.

## 3. HARD PROHIBITIONS

- Do not change runtime behavior, CLI, dependencies, workflows, tests, SQLite,
  datasets, exports, services, scheduler, aliases, or unrelated docs.
- Do not force push, overwrite/delete tags, use `git push --tags`, publish to
  TestPyPI, or dispatch PyPI publication more than once.
- Do not publish before local verification and exact remote tag verification.
- Do not access private Telegram artifacts, credentials, secrets, or `.pypirc`.
- Do not retry publication automatically after a failed dispatch.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Set `pyproject.toml` version to `0.1.1` and create concise bilingual
   `0.1.1` changelog notes.
2. Run full verification, build wheel/sdist, run `twine check`, and verify
   artifact metadata plus isolated installed CLI help.
3. Commit release preparation, push `main`, and require successful CI.
4. Verify local/remote absence of `v0.1.1`, create and push exactly one
   annotated tag `v0.1.1`, then verify matching peeled targets.
5. Dispatch `pypi-publish.yml` exactly once for `v0.1.1`, wait for success,
   and publicly verify PyPI `0.1.1` files.
6. Create and verify one non-draft, non-prerelease GitHub Release for existing
   tag `v0.1.1`.
7. Create the Russian factual report and complete lifecycle cleanup.

## 5. REQUIRED DOCS

Create:

```text
docs/stages/reports/STAGE_5Z_0_PATCH_RELEASE_V0_1_1_REPORT.md
```

Update `docs/stages/README.md` only during lifecycle cleanup. Move this stage
to `docs/stages/completed/` only after all release checks pass.

## 6. TESTS / VERIFICATION

Required:

```bash
git diff --check
make verify
python -m build
python -m twine check dist/*
```

Also verify exact artifact version/metadata, isolated wheel install and
`tg-msg-manager --help`, successful CI, annotated local/remote tag equality,
exactly one successful PyPI workflow dispatch, public PyPI wheel/sdist, and
structured GitHub Release fields. Do not claim unrun checks passed.

## 7. REPORT

Write a compact Russian report with exact commits, tag objects/targets,
commands and checks, artifact filenames/SHA-256, CI and publish run IDs,
public PyPI evidence, GitHub Release URL, skills applied, preserved boundaries,
files changed, and lifecycle actions.

## 8. COMPLETION CRITERIA

Complete only if `0.1.1` is verified locally, tagged and pushed exactly once,
published through one successful Trusted Publishing run, publicly visible on
PyPI with wheel and sdist, represented by a verified GitHub Release, reported,
and lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Follow `AGENTS.md`. Do not print credentials, full logs, full API bodies, full
diffs, private artifacts, or broad summaries.
