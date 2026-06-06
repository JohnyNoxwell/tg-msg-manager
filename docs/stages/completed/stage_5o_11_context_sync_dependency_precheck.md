# STAGE 5O.11 — Context Sync Dependency Precheck

Status: complete
Stage: 5O.11
Type: implementation
Depends on: completed Stage 5O.0 report and current context/sync behavior

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` and this file before editing.
- Do not start unless `docs/stages/reports/STAGE_5O_0_REFACTORING_GUARDRAILS_REPORT.md` exists or the user explicitly overrides the dependency.
- Use `stage-reviewer` before implementation; if unavailable, read `.skills/stage-reviewer/SKILL.md` manually and state that in the report.
- Use `architecture-guard` because this stage touches service contracts; if unavailable, read `.skills/architecture-guard/SKILL.md` manually and state that in the report.
- Write a compact plan with no more than 5 bullets before edits.

## 1. PURPOSE

Add focused characterization tests around context/deep-mode and sync range scanning before replacing private-method and duck-typed dependencies.

## 2. FILES TO INSPECT

- `tg_msg_manager/services/context/engine.py`
- `tg_msg_manager/services/context/rounds.py`
- `tg_msg_manager/services/context/resolvers.py`
- `tg_msg_manager/services/context/fetchers.py`
- `tg_msg_manager/services/sync/range_scanner.py`
- `tg_msg_manager/services/sync/tracked_runner.py`
- context/sync tests under `tests/services/`

May change:

- focused tests under `tests/services/context/` or `tests/services/sync/`
- existing context/sync tests only for organization needed by this stage
- `docs/stages/reports/STAGE_5O_11_CONTEXT_SYNC_DEPENDENCY_PRECHECK_REPORT.md`
- lifecycle updates required by `AGENTS.md`

## 3. HARD PROHIBITIONS

- Do not change production code in this stage unless a test helper needs mechanical import cleanup.
- Do not change deep-mode heuristics, message ordering, range-scan behavior, fallback behavior, or storage behavior.
- Do not run live Telegram integrations.
- Do not read private artifacts, sessions, exports, logs, media, or local databases.
- Do not read existing `docs/stages/reports/` files unrelated to this stage.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Add focused tests for `CandidatePoolResolver` or the smallest current resolver unit that exposes candidate selection behavior.
2. Add focused tests for `SyncRangeScanner` buffer/range behavior using synthetic clients/storage.
3. Add tests that document current fallback behavior when optional storage methods are absent.
4. Keep tests deterministic and free of network or real Telegram credentials.
5. Document any behavior that remains covered only by existing omnibus tests.

## 5. REQUIRED DOCS

- No user docs required.
- Create the required report in Russian.

## 6. TESTS / VERIFICATION

Run:

- `pytest tests/services -k context`
- `pytest tests/services -k sync`
- `pytest tests/services/test_services.py`
- `python3 -m compileall tg_msg_manager`
- `ruff check tests/services`

## 7. REPORT

Create `docs/stages/reports/STAGE_5O_11_CONTEXT_SYNC_DEPENDENCY_PRECHECK_REPORT.md` in Russian with:

- behaviors characterized;
- remaining coverage gaps;
- commands run and results;
- confirmation that production behavior was unchanged.

## 8. COMPLETION CRITERIA

- Context/sync high-risk behavior has focused tests or documented blockers.
- Production behavior is unchanged.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Keep final response under 1200 characters unless the user asks otherwise.
