# STAGE 5W.1 — PYPI TRUSTED PUBLISHING SETUP

Status: completed
Stage: 5W.1
Type: release workflow implementation
Depends on:
`docs/stages/reports/STAGE_5W_0_3_STABLE_TAG_ISOLATED_INSTALL_SMOKE_REPORT.md`
with `PASSED` and final decision
`READY_FOR_STAGE_5W_1_PYPI_TRUSTED_PUBLISHING_SETUP`; exact annotated tag
`v0.1.0`; GitHub repository `JohnyNoxwell/tg-msg-manager`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply stage-reviewer before implementation,
architecture-guard during workflow review, and stage-completion-auditor before
claiming completion; read matching `.skills/*/SKILL.md` files when tools are
unavailable and record evidence in the report. Write a plan of at most five
bullets. This is setup-only: do not dispatch the workflow, publish, register
the PyPI publisher, or start Stage 5W.2.

## 1. PURPOSE

Create and verify a manual-only, exact-tag, OIDC-only main PyPI workflow;
create or verify GitHub Environment `pypi`; and record the exact PyPI Trusted
Publisher tuple for a separate manual registration stage.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `.github/workflows/testpypi-publish.yml`, if present, as read-only reference
- `.github/workflows/pypi-publish.yml`, if present
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_5W_0_3_STABLE_TAG_ISOLATED_INSTALL_SMOKE_REPORT.md`

Writable repository paths are limited to
`.github/workflows/pypi-publish.yml`,
`docs/stages/reports/STAGE_5W_1_PYPI_TRUSTED_PUBLISHING_SETUP_REPORT.md`,
`docs/stages/README.md`, and lifecycle movement of this stage file. Do not
inspect existing reports unrelated to this stage, credentials, tokens,
secrets, `.pypirc`, shell history, private artifacts, Telegram sessions,
exports, logs, screenshots, media, or local databases.

## 3. HARD PROHIBITIONS

- Do not dispatch any workflow; do not publish/upload to PyPI or TestPyPI;
  do not register a PyPI publisher or create a PyPI project/token.
- Do not create a GitHub Release; create/delete/modify/push tags; run
  `git push`; or use `gh workflow run`/`workflow_dispatch`.
- Do not use or read secrets, tokens, credentials, username/password,
  `.pypirc`, shell history, or private/runtime artifacts. Do not create
  environment secrets.
- Do not edit production code, tests, package metadata/version/dependencies,
  existing TestPyPI workflow, changelog/release notes, CLI/runtime behavior,
  SQLite/schema/migrations, or dataset/export contracts.
- Do not run builds, installs, full tests, Telegram/live/runtime commands, or
  automatic workflow triggers.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Run worktree and exact local/remote `v0.1.0` preflight. Stop before editing
   on unrelated changes, `git diff --check` failure, or tag mismatch.
2. Inspect the TestPyPI workflow only as a structural reference. Create or
   verify `.github/workflows/pypi-publish.yml` with only `workflow_dispatch`
   and required string input `tag`.
3. Require `v*`; checkout `refs/tags/${{ inputs.tag }}`; verify `HEAD` equals
   the peeled tag target; build once; run `python -m twine check dist/*`; and
   pass `dist/*` from a build job to a separate publish job through artifacts.
4. Configure the publish job with `needs: build`, `environment: pypi`,
   `permissions: { id-token: write }`, and
   `pypa/gh-action-pypi-publish@release/v1`, with no TestPyPI endpoint or
   stored credentials.
5. Verify GitHub Environment `pypi` through `gh api`; create it only if absent
   and authorized. Record the exact publisher tuple, verify structure/final
   scope, write the report, audit completion, and perform lifecycle cleanup
   only on `PASSED`.

## 5. REQUIRED DOCS

Create only
`docs/stages/reports/STAGE_5W_1_PYPI_TRUSTED_PUBLISHING_SETUP_REPORT.md`.
Update `docs/stages/README.md` only for lifecycle state. On `PASSED`, move this
task to
`docs/stages/completed/stage_5w_1_pypi_trusted_publishing_setup.md`. If
environment creation/verification is unavailable, leave the task active and
record `PARTIAL` plus the exact manual step. Do not change changelog or release
notes.

## 6. TESTS / VERIFICATION

Run before editing:

```bash
git status --short
git diff --check
git cat-file -t v0.1.0
git rev-parse v0.1.0
git rev-parse v0.1.0^{}
git ls-remote --tags origin refs/tags/v0.1.0 'refs/tags/v0.1.0^{}'
```

Require type `tag`, object
`0a1474402f6a95c96ed84f6ed627c4a62eb7e13c`, peeled target
`2f4ae2448d2e0b3217debd31f093127358215d7f`, and matching remote evidence.
Only expected stage/lifecycle/report/workflow changes may exist.

Create or verify the environment, without secrets:

```bash
gh auth status
gh api -H "Accept: application/vnd.github+json" "/repos/JohnyNoxwell/tg-msg-manager/environments/pypi"
gh api --method PUT -H "Accept: application/vnd.github+json" "/repos/JohnyNoxwell/tg-msg-manager/environments/pypi"
gh api -H "Accept: application/vnd.github+json" "/repos/JohnyNoxwell/tg-msg-manager/environments/pypi"
```

Run the `PUT` only when the first environment `GET` reports that `pypi` is
absent; otherwise record existing-environment evidence without recreating it.
If `gh` is unavailable, unauthorized, or lacks permission, do not fail workflow
setup. Record `PARTIAL`, decision
`READY_FOR_MANUAL_GITHUB_ENVIRONMENT_PYPI_CREATION_BEFORE_STAGE_5W_2`, and:
`Create GitHub Environment named pypi in JohnyNoxwell/tg-msg-manager, then
rerun/complete verification.`

Run local structural checks:

```bash
test -f .github/workflows/pypi-publish.yml
ruby -e "require 'yaml'; YAML.load_file('.github/workflows/pypi-publish.yml')"
rg -n "workflow_dispatch|inputs:|tag:|refs/tags/|python -m build|python -m twine check dist/\\*|actions/upload-artifact|actions/download-artifact|needs: build|environment: pypi|id-token: write|pypa/gh-action-pypi-publish@release/v1" .github/workflows/pypi-publish.yml
rg -n "test\\.pypi\\.org|repository-url|username:|password:|api-token:|secrets\\.|TWINE_USERNAME|TWINE_PASSWORD|PYPI_API_TOKEN|push:|pull_request:|release:|schedule:|workflow_run:" .github/workflows/pypi-publish.yml
git status --short
git diff --check
```

The positive `rg` must find every required control. The prohibited-pattern
`rg` must return no matches. If Ruby YAML parsing is unavailable, use an
already-installed YAML parser or documented text structural verification; do
not install dependencies. Do not run tests, builds, installs, workflow
dispatch, publish/upload, release, tag, push, or live/runtime commands.

## 7. REPORT

Write a compact Russian report containing: stage/status; prerequisite and
working-tree evidence; local/remote stable-tag evidence; workflow path,
only-trigger/input/exact-checkout/peeled-target/build/twine/artifact-handoff/
publish-job controls; prohibited-pattern results; environment creation or
verification evidence and exact manual step if needed; exact tuple:

```text
PyPI project: tg-msg-manager
owner: JohnyNoxwell
repository: tg-msg-manager
workflow filename: pypi-publish.yml
environment name: pypi
```

Also record commands run and explicitly skipped; unchanged boundaries; no
dispatch/publish/upload/release/tag/push/build/install/test/live command or
credential/private-artifact access; files changed; skill evidence; lifecycle
state; final decision; and next stage. On full success use
`READY_FOR_STAGE_5W_2_PYPI_TRUSTED_PUBLISHER_REGISTRATION` and recommend only
`STAGE_5W_2_PYPI_TRUSTED_PUBLISHER_REGISTRATION`: manual registration of the
exact PyPI Trusted Publisher/Pending Publisher tuple without publishing.

## 8. COMPLETION CRITERIA

`PASSED` requires exact local/remote stable-tag evidence; syntax-valid
manual-only workflow with required tag input, exact tag checkout and peeled
target verification; separate build/publish jobs; build once and `twine check`
before artifact upload; publish job with `needs: build`, environment `pypi`,
OIDC permission, and required publish action; no TestPyPI endpoint or stored
credentials; verified GitHub Environment `pypi`; recorded tuple; no forbidden
action/access/change; report; passing completion audit; and lifecycle cleanup
completed according to `AGENTS.md`.

Use `PARTIAL` and leave active only when workflow setup passes but environment
creation/verification requires the documented manual step. Use `BLOCKED` and
leave active when preflight/tag/worktree evidence fails or forbidden access is
required. Use `FAILED` and leave active when workflow structural verification
fails or the report cannot be created. Do not start Stage 5W.2.

## 9. OUTPUT LIMITS

Follow `AGENTS.md`. Keep interim output to blockers or required questions.
Final response must use the required `AGENTS.md` structure and stay within its
character limit. Do not print the full workflow, broad diffs, credentials,
secrets, private artifacts, or verbose command output.
