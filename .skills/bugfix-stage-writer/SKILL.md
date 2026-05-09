# Bugfix Stage Writer

## Purpose

Generate narrow Codex stage files for bug fixes.

Use this skill when a defect has an observed symptom, runtime error, failing test, bad artifact, or incorrect behavior.

Bugfix stages must focus on reproduction, diagnosis, minimal patching, regression coverage, and non-regression checks.

## When To Use

Use for:

```text
runtime exceptions
failed exports
wrong output format
compatibility bugs
broken CLI path
incorrect state/incremental behavior
test regressions
```

Do not use for feature work. Use the general stage writer or feature-stage mode instead.

## Inputs

Useful inputs:

```text
bug symptom
observed output
error traceback
affected command
affected artifact
expected behavior
actual behavior
suspected files
related stage/context
```

If key data is missing, generate a diagnostic-first bugfix stage that inspects the failing path before editing.

## Generated Stage Structure

Generate this structure:

```text
# STAGE <ID> — <BUGFIX TITLE>

Status: active task
Stage: <ID>
Type: bugfix
Depends on: <exact files/artifacts/current failing path>

---

## 0. CODEX ENTRY CONTRACT
## 1. SYMPTOM
## 2. REPRODUCTION / OBSERVED OUTPUT
## 3. LIKELY CAUSE
## 4. FILES TO INSPECT
## 5. HARD PROHIBITIONS
## 6. MINIMAL PATCH TASKS
## 7. REGRESSION TESTS
## 8. NON-REGRESSION CHECKS
## 9. REQUIRED DOCS
## 10. REPORT
## 11. COMPLETION CRITERIA
## 12. OUTPUT LIMITS
```

## Section Rules

### CODEX ENTRY CONTRACT

Use:

```text
Read AGENTS.md first.

Execute Stage <ID> — <TITLE>.

Goal:
Fix the observed bug with the smallest safe patch.

Do not start later stages.
Do not add new features.
Do not change public CLI behavior, output formats, SQLite schema, or data flow except as required to fix this bug.

Use AGENTS.md compact output format.
```

### SYMPTOM

Include:

```text
what failed
where it failed
visible error/output
affected mode/path
```

Keep it factual.

### REPRODUCTION / OBSERVED OUTPUT

Include exact command/output if available.

If no reproduction command is available, say:

```text
No direct reproduction command provided. Confirm failing path from artifacts/output before editing.
```

### LIKELY CAUSE

State as hypothesis, not fact, unless proven.

Use:

```text
Likely cause:
- ...
```

### FILES TO INSPECT

Use exact files where possible.

Pattern:

```text
Required:
- path/to/failing_module.py
- path/to/test_file.py if known

Optional only if needed:
- path/to/caller.py

May read:
- AGENTS.md
- this stage file
- tests for affected path

Do not read or change:
- unrelated source modules
- unrelated docs
- docs/archive
- completed stages
- existing docs/stages/reports files unrelated to this stage
```

### HARD PROHIBITIONS

Always include:

```text
Do not add features.
Do not perform broad refactors.
Do not change command names, CLI flags, defaults, output files, output directory layout, SQLite schema, or data flow unless required by the bug fix.
Do not add analytics, OSINT logic, profiling, fingerprinting, OCR, STT, media recognition, or LLM-dependent behavior.
Do not add new runtime dependencies.
Do not modify protected files except for mechanical wiring required by the fix.
```

### MINIMAL PATCH TASKS

Use this pattern:

```text
1. Confirm the failing path.
   - inspect <file/function>
   - compare with observed symptom
   - do not edit yet

2. Patch the narrow cause.
   - change <specific function/module>
   - keep public behavior unchanged except the bug fix

3. Add regression coverage.
   - add or update focused test
   - assert previous failure case

4. Run focused verification.
   - compile
   - lint
   - focused pytest
```

### REGRESSION TESTS

Require at least one regression test when practical.

If a regression test cannot be added, require exact explanation.

### NON-REGRESSION CHECKS

Include checks for behavior that must not change.

Examples:

```text
CLI flags/defaults unchanged
JSONL schema unchanged
TXT profile behavior unchanged
state/incremental behavior unchanged
```

Adapt to the bug.

### REQUIRED DOCS

Use:

```text
Do not update docs unless the bug fix changes documented behavior, known limitations, or user-facing examples.

Required:
- docs/stages/reports/<REPORT_NAME>.md

Conditional:
- CHANGELOG.md only if project convention records this bug fix
- README.md/COMMANDS.md only if documented examples become inaccurate
```

### REPORT

Require:

```text
docs/stages/reports/<REPORT_NAME>.md
```

Report must record:

```text
exact files changed
exact checks run
bug fixed
behavior unchanged
what was not run and why
completion status
```

### COMPLETION CRITERIA

Use:

```text
This stage is complete when:

- bug is fixed with minimal scoped change;
- regression coverage exists or inability is documented;
- prohibited behavior remains unchanged;
- docs were updated only if required, or no docs update was needed;
- tests/checks are recorded;
- report exists;
- lifecycle cleanup is completed according to AGENTS.md.
```

### OUTPUT LIMITS

End with:

```text
Use AGENTS.md compact final response format.

Final response must contain only:

DONE:
- ...

CHANGED:
- ...

CHECKS:
- ...

NOTES:
- ...

STAGE:
- complete/incomplete: <reason if incomplete>

Do not paste full diffs.
Do not explain the task back to the user.
Do not include broad summaries.
Do not include future recommendations unless required by a real blocker.
```

## Rules

Bugfix stages must not authorize:

```text
feature expansion
broad refactor
formatting churn
schema changes unless explicitly required
public CLI changes unless explicitly required
new dependencies
future-stage work
```

Prefer exact paths and exact symptoms.

Do not over-explain.

## Example Skeleton

```text
# STAGE 4A.X — FIX PYTHON 3.9 UNION TYPE COMPATIBILITY

Status: active task
Stage: 4A.X
Type: bugfix
Depends on: affected modules using PEP 604 runtime unions

## 1. SYMPTOM

Python 3.9 raises:
TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'

## 3. LIKELY CAUSE

PEP 604 union annotations are evaluated at runtime on Python 3.9.

## 6. MINIMAL PATCH TASKS

1. Confirm offending annotations.
   - search affected files for `| None`
   - do not edit yet

2. Replace runtime-incompatible annotations.
   - use Optional[...] or Union[...]
   - preserve behavior

3. Add/import typing helpers as needed.
```
