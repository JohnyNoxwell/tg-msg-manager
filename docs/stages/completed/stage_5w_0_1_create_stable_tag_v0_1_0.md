# STAGE 5W.0.1 — CREATE STABLE TAG v0.1.0

Status: completed
Stage: 5W.0.1
Type: release operation
Depends on:
`docs/stages/reports/STAGE_5W_0_STABLE_TAG_V0_1_0_PLAN_REPORT.md` with
`PASSED` and final decision
`READY_FOR_STAGE_5W_0_1_CREATE_STABLE_TAG_V0_1_0`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply stage-reviewer, architecture-guard, and
stage-completion-auditor from `.skills/`; record their exact paths and
verdicts in the report. Before execution, write a plan of at most five
bullets. This stage may create and push only annotated tag `v0.1.0` on exact
commit `2f4ae2448d2e0b3217debd31f093127358215d7f`. Stop without destructive
actions on any failed prerequisite, existing stable tag, or push failure.

## 1. PURPOSE

Create and push stable annotated tag `v0.1.0` on the verified peeled target of
`v0.1.0-rc2`, then record verifiable local and remote tag evidence. Package
artifact verification is a separate next stage.

## 2. FILES TO INSPECT

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_5W_0_STABLE_TAG_V0_1_0_PLAN_REPORT.md`

Writable repository paths are limited to
`docs/stages/reports/STAGE_5W_0_1_CREATE_STABLE_TAG_V0_1_0_REPORT.md`,
`docs/stages/README.md` only for lifecycle state, lifecycle movement of this
stage file, and the authorized local/remote tag ref `v0.1.0`. Do not inspect
source, tests, unrelated existing reports, private artifacts, credentials,
Telegram sessions, exports, logs, media, screenshots, databases, `.pypirc`,
or shell history.

## 3. HARD PROHIBITIONS

- Do not edit production code, tests, `pyproject.toml`, package metadata,
  version, dependencies, workflows, CLI behavior, SQLite, dataset/export
  contracts, changelog, release notes, or unrelated docs.
- Do not build/install/test/publish/upload, dispatch workflows, create a
  GitHub Release, run Telegram/live commands, or start the next stage.
- Do not create/delete/overwrite/push any tag except new `v0.1.0`; never use
  force push or `git push --tags`; do not modify `v0.1.0-rc1` or
  `v0.1.0-rc2`.
- Do not read credentials, tokens, secrets, `.pypirc`, shell history, private
  artifacts, Telegram sessions, or real exports/logs/media/screenshots/DBs.
- Do not run rollback automatically. If local creation or remote push has
  occurred, preserve and report the exact resulting state.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify the prerequisite report, allowed worktree state, `git diff --check`,
   exact local/remote annotated RC2 object and peeled target, and local/remote
   absence of `v0.1.0`. Stop on any mismatch or unrelated change.
2. Create exactly:
   `git tag -a v0.1.0 2f4ae2448d2e0b3217debd31f093127358215d7f -m "tg-msg-manager v0.1.0"`.
3. Push exactly `git push origin v0.1.0`; do not force push. On failure,
   preserve the local tag and stop with its exact state recorded.
4. Verify local/remote stable tag objects and peeled targets match; verify
   stable and RC2 peeled targets match, while their annotated tag objects
   differ.
5. Write the Russian factual report, apply stage-completion-auditor, and
   complete lifecycle cleanup only on `PASSED`. Do not start the next stage.

## 5. REQUIRED DOCS

Create only
`docs/stages/reports/STAGE_5W_0_1_CREATE_STABLE_TAG_V0_1_0_REPORT.md`.
Update `docs/stages/README.md` only for lifecycle state. On `PASSED`, move this
task to
`docs/stages/completed/stage_5w_0_1_create_stable_tag_v0_1_0.md`; otherwise
leave it active. Do not change changelog or release notes.

## 6. TESTS / VERIFICATION

Run preflight before tag creation:

```bash
git status --short
git diff --check
git cat-file -t v0.1.0-rc2
git rev-parse v0.1.0-rc2
git rev-parse v0.1.0-rc2^{}
git ls-remote --tags origin refs/tags/v0.1.0-rc2 'refs/tags/v0.1.0-rc2^{}'
git show-ref --tags --verify --quiet refs/tags/v0.1.0; echo $?
git ls-remote --tags origin refs/tags/v0.1.0 'refs/tags/v0.1.0^{}'
```

Require RC2 type `tag`, object
`962f3e413cd87d443ab5775e59e9539e84dfe57f`, peeled target
`2f4ae2448d2e0b3217debd31f093127358215d7f`, matching remote object/peeled
target, local stable absence exit code `1`, and empty remote stable output.

After creation and push, run:

```bash
git cat-file -t v0.1.0
git rev-parse v0.1.0
git rev-parse v0.1.0^{}
git ls-remote --tags origin refs/tags/v0.1.0 'refs/tags/v0.1.0^{}'
git rev-parse v0.1.0-rc2
git rev-parse v0.1.0-rc2^{}
git status --short
git diff --check
```

Require stable type `tag`; matching local/remote stable tag object; stable
peeled target equal to the exact approved commit locally/remotely and equal
to RC2 peeled target; stable tag object different from RC2 tag object. Do not
claim a check passed unless it was run.

Rollback commands may be documented but never executed:

```bash
git tag -d v0.1.0
git push origin :refs/tags/v0.1.0
```

## 7. REPORT

Write a compact Russian report with: stage/status; prerequisite and preflight
evidence; RC2 local/remote object and peeled target; stable absence evidence;
exact create/push commands and results; new stable local/remote object and
peeled target; peeled-target equality and tag-object inequality checks;
commands run; forbidden actions explicitly skipped; confirmations that no
build/install/tests/publish/workflow dispatch/GitHub Release or
credential/secret/private-artifact access occurred; files changed; rollback
commands as documentation only; skill evidence; lifecycle notes; exact final
decision; and next recommended stage.

On success use final decision
`READY_FOR_STAGE_5W_0_2_STABLE_TAG_PACKAGE_ARTIFACT_VERIFICATION` and recommend
only `STAGE_5W_0_2_STABLE_TAG_PACKAGE_ARTIFACT_VERIFICATION`: build wheel and
sdist from exact `v0.1.0` source and verify package artifacts.

## 8. COMPLETION CRITERIA

Status is `PASSED` only when `v0.1.0` was absent locally/remotely before the
stage; the exact annotated tag was created and pushed; local/remote stable
objects match; local/remote stable peeled targets match the approved commit
and RC2 peeled target; stable and RC2 tag objects differ; no forbidden action
or out-of-scope change occurred; the report exists; stage-completion-auditor
passes; and lifecycle cleanup is completed according to `AGENTS.md`.

Use `BLOCKED` or `FAILED` and leave the task active if prerequisites fail,
`v0.1.0` already exists, unrelated worktree changes exist, `git diff --check`
fails, creation/push/verification fails, destructive action would be needed,
or credential/private-artifact access would be required. Never delete or
overwrite a local or remote tag automatically.

## 9. OUTPUT LIMITS

Follow `AGENTS.md`. Keep interim output to blockers or required questions.
Final response must use the required `AGENTS.md` structure and stay within its
character limit. Do not print full diffs, logs, credentials, secrets, private
artifact contents, or broad summaries.
