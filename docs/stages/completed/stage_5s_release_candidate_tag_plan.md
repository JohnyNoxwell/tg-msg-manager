# STAGE 5S — RELEASE CANDIDATE TAG PLAN

Status: active task
Stage: 5S
Type: report / plan
Depends on: Stage 5P `PASSED`; Stage 5Q without blockers; Stage 5R.0-5R.1 `PASSED`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply `.skills/stage-reviewer/SKILL.md`,
`.skills/architecture-guard/SKILL.md`, and
`.skills/stage-completion-auditor/SKILL.md` after report/cleanup.

This stage lists future commands only. Never create/delete/push a tag here.

## 1. PURPOSE

Prepare an evidence-backed, reversible plan for a future separate RC tag
execution stage. Do not assume `v0.1.0-rc1`; derive a candidate only after
inspecting package version and existing tags.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `pyproject.toml`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- Stage 5P, Stage 5Q checklist, and Stage 5R reports
- `docs/stages/README.md`

Writable paths:

- `docs/stages/reports/STAGE_5S_RELEASE_CANDIDATE_TAG_PLAN_REPORT.md`
- `docs/stages/README.md`
- lifecycle move of this stage file

## 3. HARD PROHIBITIONS

- Do not create/delete/push tags, commits, branches, releases, package artifacts,
  version changes, or publish/upload actions.
- Do not change production code, tests, docs, CLI behavior, SQLite schema,
  dataset/export contracts, package metadata, or dependencies.
- Do not read private artifacts, sessions, credentials, real exports/logs/media/
  screenshots/DB files, or inject real Telegram data.
- Do not add analytics, OSINT, profiling, identity/media analysis, GUI/SaaS,
  or LLM-dependent core behavior.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify every prerequisite report and stop on missing/failed evidence.
2. Inspect working-tree summary, recent commits, package version, and existing tags.
3. Propose one non-conflicting RC tag and list exact future inspect/create/push commands.
4. List local and remote tag rollback commands, with remote deletion requiring
   separate explicit approval.
5. Create the Russian plan report, then complete lifecycle cleanup.

## 5. REQUIRED DOCS

Report-only. State explicitly that publishing and tag execution require separate
stages. No rollback is performed here; rollback commands are plan text only.

## 6. TESTS / VERIFICATION

Run inspection commands only:

```bash
git status --short
git log --oneline -5
git tag --list
git diff --check
```

List but do not execute future commands equivalent to:

```bash
git tag -a <candidate> -m "tg-msg-manager <candidate>"
git push origin <candidate>
git tag -d <candidate>
git push origin :refs/tags/<candidate>
```

## 7. REPORT

Create `docs/stages/reports/STAGE_5S_RELEASE_CANDIDATE_TAG_PLAN_REPORT.md` in Russian.

Include: `PASSED`, `FAILED`, or `PARTIAL`; prerequisite evidence; package
version/existing-tag findings; proposed candidate and rationale; commands run
and results; failures; commands not run and why; future commands not executed;
rollback plan; files changed; no
tag/push/publish/version/behavior change; final recommendation; applied skill
paths; lifecycle notes.

## 8. COMPLETION CRITERIA

- Plan has explicit prerequisites, candidate, future commands, and rollback notes.
- No tag, push, publish, version bump, or package state change occurred.
- Required report exists and lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`. Do not paste git logs or claim a tag exists.
