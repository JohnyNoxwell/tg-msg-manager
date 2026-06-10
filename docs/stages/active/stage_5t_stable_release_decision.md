# STAGE 5T — STABLE RELEASE DECISION

Status: active task
Stage: 5T
Type: decision report
Depends on: Stage 5P/5Q/5R reports and Stage 5S tag plan; separate RC tag execution evidence if it exists

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Apply `.skills/stage-reviewer/SKILL.md`,
`.skills/architecture-guard/SKILL.md`, and
`.skills/stage-completion-auditor/SKILL.md` after report/cleanup.

Do not create a stable tag, publish, or create the next stage. Without separate
RC tag execution evidence, the maximum recommendation is `KEEP_AS_RELEASE_CANDIDATE`.

## 1. PURPOSE

Make an evidence-backed decision between stable-release-stage readiness,
blocking fixes, or remaining at release-candidate status.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `pyproject.toml`
- `README.md`
- `COMMANDS.md`
- `docs/development/CLI_CONTRACT.md`
- `docs/development/RELEASE_CANDIDATE_DECISION.md`
- Stage 5P, Stage 5Q checklist, Stage 5R, and Stage 5S reports
- `docs/stages/README.md`

Read only if present:

- a separately authorized RC tag execution report
- a separately authorized post-RC smoke report

Writable paths:

- `docs/stages/reports/STAGE_5T_STABLE_RELEASE_DECISION_REPORT.md`
- `docs/stages/README.md`
- lifecycle move of this stage file

## 3. HARD PROHIBITIONS

- Do not create/delete/push tags, publish/upload packages, bump versions, build
  artifacts, or claim stable release occurred.
- Do not change production code, tests, docs, CLI behavior/contracts, SQLite
  schema, dataset/export contracts, package metadata, or dependencies.
- Do not read private artifacts, sessions, credentials, real exports/logs/media/
  screenshots/DB files, or inject real Telegram data.
- Do not add analytics, OSINT, profiling, identity/media analysis, GUI/SaaS,
  or LLM-dependent core behavior.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify prerequisite reports and classify missing/failed evidence.
2. Determine whether a separately authorized RC tag and post-wheel smoke evidence exist.
3. Evaluate docs/CLI alignment, known limitations/deferred areas, unresolved
   blockers, and version/tag/package coherence.
4. Produce exactly one allowed recommendation and name the next required stage
   only when stable readiness is approved.
5. Create the Russian decision report, then complete lifecycle cleanup.

## 5. REQUIRED DOCS

Report-only. Do not refine release notes or known-limitations docs here; stale
docs require a separate fix stage.

No rollback applies because this stage must not mutate release state.

## 6. TESTS / VERIFICATION

Required inspection only:

```bash
git status --short
git tag --list
git diff --check
```

Do not rerun release/build/publish actions.

## 7. REPORT

Create `docs/stages/reports/STAGE_5T_STABLE_RELEASE_DECISION_REPORT.md` in Russian.

Include: `PASSED`, `FAILED`, or `PARTIAL`; evidence links; commands/results;
failures; commands not run and why; unresolved blockers; docs/deferred/version/tag/package
coherence; files changed; no behavior/CLI/SQLite/dataset/tag/publish/version
change; final recommendation; applied skill paths; lifecycle notes; exactly one recommendation:

- `READY_FOR_STABLE_RELEASE_STAGE`
- `NOT_READY_FIX_BLOCKERS_FIRST`
- `KEEP_AS_RELEASE_CANDIDATE`

## 8. COMPLETION CRITERIA

- Decision is explicit and evidence-backed.
- `READY_FOR_STABLE_RELEASE_STAGE` requires separate RC tag execution evidence
  and successful installed-wheel smoke evidence.
- No stable tag/publish/version/package state change occurred.
- Required report exists and lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`. Do not claim release completion.
