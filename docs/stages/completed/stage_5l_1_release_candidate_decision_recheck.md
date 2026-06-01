# STAGE 5L.1 — RELEASE CANDIDATE DECISION RECHECK

Status: active task
Stage: 5L.1
Type: decision recheck
Depends on: Stage 5K.3/5K.4 reports and Stage 5L.0 focused Ruff formatting fix evidence if present

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Apply these skills before implementation:

- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md` after checks/report/cleanup

Do not perform an actual release.
Do not start any later stage.

If `docs/stages/reports/STAGE_5L_0_FOCUSED_RUFF_FORMATTING_FIX_REPORT.md` is absent, locate the actual 5L.0 report from `docs/stages/README.md` or `docs/stages/reports/`. If no 5L.0 report exists, do not guess; block or continue only as a verification run with an explicit missing-evidence note.

## 1. PURPOSE

Recheck the Stage 5K.4 release-candidate decision after the focused Ruff formatting fix that was expected to remove the 5K.3/5K.4 formatting blocker.

Produce a factual Russian report with the updated decision.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/stages/reports/STAGE_5K_3_LOCAL_VERIFICATION_MATRIX_REPORT.md`
- `docs/stages/reports/STAGE_5K_4_RELEASE_CANDIDATE_DECISION_REPORT.md`
- `docs/stages/reports/STAGE_5L_0_FOCUSED_RUFF_FORMATTING_FIX_REPORT.md` if present
- `docs/development/RELEASE_CHECKLIST_SCOPE.md`
- `docs/development/LOCAL_VERIFICATION_MATRIX.md`
- `docs/development/RELEASE_CANDIDATE_DECISION.md`
- `README.md`
- `COMMANDS.md`
- `CHANGELOG.md`
- `pyproject.toml`
- `Makefile`
- `docs/development/PACKAGE_IDENTITY_AND_VERSION_POLICY.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md`
- `docs/stages/README.md`

Read only if needed to resolve 5L.0 evidence:

- `docs/stages/reports/`

Writable paths:

- `docs/stages/reports/STAGE_5L_1_RELEASE_CANDIDATE_DECISION_RECHECK_REPORT.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_5l_1_release_candidate_decision_recheck.md`
- `docs/development/RELEASE_CANDIDATE_DECISION.md` optional

Do not edit README, COMMANDS, CHANGELOG, pyproject, Makefile, runtime code, tests, fixtures, or architecture docs by default.

## 3. HARD PROHIBITIONS

- Do not publish a release, create tags, bump version, change `pyproject.toml`, add runtime `__version__`, build/upload package artifacts, or claim a release occurred.
- Do not change runtime behavior, CLI behavior, output formats, TXT rendering, JSONL schema, SQLite schema/storage behavior, services, tests, fixtures, Makefile, or package behavior.
- Do not reformat code again unless this stage is explicitly re-scoped.
- Do not read private artifacts, sessions, credentials, real exports, logs, screenshots, SQLite DB contents, media, or ignored private files.
- Do not include `export-pm` / private archive in the user/group + `db-export` contract scope.
- Do not add analytics, OSINT, profiling, OCR/STT, media recognition, GUI/SaaS, or LLM-dependent behavior.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify required 5K reports exist and resolve 5L.0 evidence path if present.
2. Inspect 5K.4 blocker and 5L.0 scope; confirm whether 5L.0 was formatting-only.
3. Run required recheck commands and record exact results.
4. Classify updated release-candidate posture using the decision logic below.
5. Update `docs/development/RELEASE_CANDIDATE_DECISION.md` only if useful to supersede the 5K.4 blocked decision.
6. Create the Stage 5L.1 report in Russian.
7. Complete lifecycle cleanup according to `AGENTS.md`.

## 5. REQUIRED DOCS

Default writable docs are report plus stage index.

If `docs/development/RELEASE_CANDIDATE_DECISION.md` is updated, keep it factual and state that no release, tag, version bump, package build/upload, or publish occurred.

## 6. TESTS / VERIFICATION

Required:

```bash
git diff --check
make format-check
make verify
python3 -m unittest discover tests -p '*non_channel*contract*.py'
```

Recommended if environment permits:

```bash
make test
python3 -m unittest tests.e2e.test_fixture_e2e -q
```

Do not fix failures in this stage. Record exact failures or skip reasons.

## 7. REPORT

Create `docs/stages/reports/STAGE_5L_1_RELEASE_CANDIDATE_DECISION_RECHECK_REPORT.md` in Russian.

Include status/outcome token, files inspected, resolved 5L.0 report path or missing-evidence note, 5K.4 blocker summary, whether 5L.0 removed the blocker, commands run and exact results, updated readiness classification, blockers, non-blocking gaps, durable decision doc update status, release boundary confirmation, version unchanged confirmation, no release/tag/package-publish confirmation, no runtime/CLI/SQLite/output behavior changes confirmation, private artifact boundary confirmation, `architecture-guard: applied from .skills/architecture-guard/SKILL.md`, and lifecycle notes.

Decision logic:

- `READY_FOR_RELEASE_CANDIDATE_CHECKLIST`: all required recheck commands pass and release boundary is intact.
- `READY_FOR_LIMITED_EXTERNAL_USE_WITH_GREEN_LOCAL_CHECKS`: formatting is fixed and local checks pass, with live Telegram smoke checks still manual/session-dependent.
- `BLOCKED_BY_FORMATTING_FAILURES`: formatting still fails.
- `BLOCKED_BY_TEST_FAILURES`: tests fail.
- `BLOCKED_BY_MISSING_5L0_EVIDENCE`: 5L.0 evidence is missing and commands cannot be rerun.
- `BLOCKED_BY_RELEASE_BOUNDARY_VIOLATION`: release boundary was violated.

## 8. COMPLETION CRITERIA

- Required files were inspected or missing files were recorded.
- Required commands were run or exact skip reasons were recorded.
- Updated decision is explicit.
- Required report exists.
- Lifecycle cleanup is completed according to `AGENTS.md`.
- No release action occurred.
- Version remained unchanged.
- Runtime/CLI/SQLite/output behavior remained unchanged.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md` final format.

Do not paste full diffs, large file excerpts, broad summaries, or release claims.
