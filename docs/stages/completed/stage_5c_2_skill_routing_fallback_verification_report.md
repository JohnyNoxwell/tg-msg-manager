# STAGE 5C.2 — SKILL ROUTING FALLBACK VERIFICATION REPORT

Status: completed
Stage: 5C.2
Type: governance audit
Depends on: current `AGENTS.md` skill fallback rules and `.skills/`

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first.

Execute Stage 5C.2 only.

Goal:
Verify that required project-local skill fallback files exist and that current instructions route agents to them before reporting missing skills.

Do not start Stage 5C.3 or later stages.
Do not implement skills or rewrite historical reports.
Use `AGENTS.md` compact output format.

## 1. PURPOSE

Produce a factual verification report for skill routing and fallback behavior. This stage exists because older reports may contain stale `no such skill/tool` claims even though local fallback files now exist.

## 2. FILES TO INSPECT

Required:
- `AGENTS.md`
- this stage file
- `.skills/stage-reviewer/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/discussion-export-diagnoser/SKILL.md`
- `.skills/bugfix-stage-writer/SKILL.md`
- `docs/stages/README.md`

May inspect with `rg` only:
- `docs/stages/reports/` for existing stale skill-routing report text

May change:
- `docs/stages/reports/STAGE_5C_2_SKILL_ROUTING_FALLBACK_VERIFICATION_REPORT.md`
- `docs/stages/README.md`
- this stage file location during lifecycle cleanup

Do not change:
- `.skills/` files
- `AGENTS.md` unless a concrete contradiction is found and the correction is strictly scoped
- historical reports
- runtime source code

## 3. HARD PROHIBITIONS

- Do not edit completed reports to rewrite history.
- Do not add, remove, or rename skills.
- Do not change stage workflow rules except for a concrete contradiction in `AGENTS.md`.
- Do not inspect archive files.
- Do not change CLI, services, storage, dataset behavior, or SQLite schema.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Verify local fallback files.
   - Confirm each required `.skills/<name>/SKILL.md` exists.
   - Read only the required file headings and purpose enough to verify identity.
   - Do not edit yet.

2. Verify `AGENTS.md` routing.
   - Confirm required skill names match local fallback paths.
   - Confirm the instruction says to check local files before reporting missing tools.

3. Check stale-report pattern.
   - Use `rg` to count current report occurrences of `no such skill/tool`.
   - Record them as historical evidence only.
   - Do not edit those reports.

4. Write the report.
   - Create the Russian verification report.
   - Include a pass/fail line for each required skill fallback file.
   - Include whether `AGENTS.md` needs a follow-up stage.

5. Verify and lifecycle cleanup.
   - Run section 6 checks.
   - Move the completed stage file only after the report exists.

## 5. REQUIRED DOCS

Required:
- `docs/stages/reports/STAGE_5C_2_SKILL_ROUTING_FALLBACK_VERIFICATION_REPORT.md`
- `docs/stages/README.md` during lifecycle cleanup

Conditional:
- `AGENTS.md` only if current fallback routing is internally contradictory.

## 6. TESTS / VERIFICATION

Run:
- `test -f .skills/stage-reviewer/SKILL.md`
- `test -f .skills/stage-completion-auditor/SKILL.md`
- `test -f .skills/architecture-guard/SKILL.md`
- `test -f .skills/discussion-export-diagnoser/SKILL.md`
- `test -f .skills/bugfix-stage-writer/SKILL.md`
- `git diff --check`

No runtime tests are required for report-only changes.

## 7. REPORT

Create `docs/stages/reports/STAGE_5C_2_SKILL_ROUTING_FALLBACK_VERIFICATION_REPORT.md` in Russian.

Include:
- exact files checked;
- fallback file existence results;
- `AGENTS.md` routing result;
- historical stale-report count, if any;
- checks run;
- confirmation that no runtime behavior changed.

## 8. COMPLETION CRITERIA

- Report exists and records each required fallback skill.
- Historical reports are left unchanged.
- Any `AGENTS.md` change is justified by a concrete contradiction.
- lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

- Final response must follow `AGENTS.md`.
- No full diffs.
- No long excerpts from skill files.
- No markdown tables in the final response.
