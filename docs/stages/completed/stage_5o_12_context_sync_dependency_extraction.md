# STAGE 5O.12 — Context Sync Dependency Extraction

Status: active task
Stage: 5O.12
Type: implementation
Depends on: completed Stage 5O.11 report and current context/sync implementation

---

## 0. CODEX ENTRY CONTRACT

- Read `AGENTS.md` and this file before editing.
- Do not start unless `docs/stages/reports/STAGE_5O_11_CONTEXT_SYNC_DEPENDENCY_PRECHECK_REPORT.md` exists or the user explicitly overrides the dependency.
- Use `stage-reviewer` before implementation; if unavailable, read `.skills/stage-reviewer/SKILL.md` manually and state that in the report.
- Use `architecture-guard` because this stage touches service boundaries and protected context facade wiring; if unavailable, read `.skills/architecture-guard/SKILL.md` manually and state that in the report.
- Write a compact plan with no more than 5 bullets before edits.

## 1. PURPOSE

Replace the highest-risk private-method or duck-typed dependency in context/sync with an explicit internal dependency object or protocol while preserving deep-mode and sync behavior.

## 2. FILES TO INSPECT

- `tg_msg_manager/services/context/engine.py`
- `tg_msg_manager/services/context/rounds.py`
- `tg_msg_manager/services/context/resolvers.py`
- `tg_msg_manager/services/context/fetchers.py`
- `tg_msg_manager/services/sync/range_scanner.py`
- `tg_msg_manager/services/sync/tracked_runner.py`
- focused tests created by Stage 5O.11
- `docs/architecture/CONTEXT_ENGINE_SPLIT_MAP.md`

May change:

- context/sync modules listed above
- new internal protocols/dependency modules under `tg_msg_manager/services/context/` or `tg_msg_manager/services/sync/`
- focused context/sync tests
- `docs/stages/reports/STAGE_5O_12_CONTEXT_SYNC_DEPENDENCY_EXTRACTION_REPORT.md`
- lifecycle updates required by `AGENTS.md`

## 3. HARD PROHIBITIONS

- Do not change public `DeepModeEngine` behavior, sync message ordering, scan range behavior, fallback behavior, checkpoint behavior, or storage contracts.
- Do not add raw SQL to services.
- Do not change protected `tg_msg_manager/services/context/engine.py` beyond mechanical wiring.
- Do not run live Telegram integrations.
- Do not read existing `docs/stages/reports/` files unrelated to this stage, except the Stage 5O.11 dependency report.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Choose exactly one dependency seam from the Stage 5O.11 report: either context round runner private engine calls or one sync duck-typed storage capability path.
2. Introduce an explicit internal protocol/dependency object for that one seam.
3. Update the caller and callee to use the explicit dependency without changing algorithms.
4. Keep compatibility fallback behavior where it exists today.
5. Stop after one seam is extracted; leave remaining seams for future stages.

## 5. REQUIRED DOCS

- Update `docs/architecture/CONTEXT_ENGINE_SPLIT_MAP.md` only if ownership boundaries changed.
- Create the required report in Russian.

## 6. TESTS / VERIFICATION

Run:

- `pytest tests/services -k context`
- `pytest tests/services -k sync`
- `pytest tests/services/test_services.py`
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager/services/context tg_msg_manager/services/sync tests/services`

## 7. REPORT

Create `docs/stages/reports/STAGE_5O_12_CONTEXT_SYNC_DEPENDENCY_EXTRACTION_REPORT.md` in Russian with:

- seam extracted;
- behavior preserved;
- tests run and results;
- remaining seams explicitly deferred.

## 8. COMPLETION CRITERIA

- One high-risk context/sync dependency is explicit and tested.
- Protected facade changes are mechanical only.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- Do not include full diffs.
- Keep final response under 1200 characters unless the user asks otherwise.
