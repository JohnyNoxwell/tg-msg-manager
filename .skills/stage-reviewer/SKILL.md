# Stage Reviewer

## Purpose

Review a generated stage file before Codex implementation.

Use this skill to detect ambiguity, missing guardrails, scope creep, weak verification, docs churn risk, and conflicts with `AGENTS.md`.

This skill is for pre-flight review only. It does not implement the stage.

## When To Use

Use when the user provides or asks to validate a stage file.

Use before giving a stage file to Codex for implementation.

Do not use for auditing completed work. Use `stage-completion-auditor` instead.

## Inputs

Required:

```text
AGENTS.md
candidate stage file
```

Optional:

```text
stage-file-writer skill output
related examples/fixtures
```

Do not inspect runtime source code unless the stage file cannot be evaluated without path realism.

## Review Checklist

### Required Sections

The stage file should contain:

```text
CODEX ENTRY CONTRACT
PURPOSE
FILES TO INSPECT
HARD PROHIBITIONS
ATOMIC IMPLEMENTATION TASKS
REQUIRED DOCS
TESTS / VERIFICATION
REPORT
COMPLETION CRITERIA
OUTPUT LIMITS
```

Flag missing or weak sections.

### Structure

Check:

```text
stage title exists
stage ID exists
status exists
type exists
Depends on is concrete
required sections are present
section order is sane
```

### Scope

Check:

```text
FILES TO INSPECT uses exact paths or narrow directories
reading scope is limited
optional files are clearly marked
protected files are marked as mechanical wiring only if listed
unrelated docs/source/archive/completed stages are not authorized
```

### Prohibitions

Check:

```text
behavioral changes are prohibited unless explicitly scoped
CLI names, flags, defaults, output files, schema, and data flow are protected
analytics/OSINT/profiling/LLM-dependent logic is prohibited where relevant
new runtime dependencies are prohibited unless explicitly required
```

### Tasks

Check:

```text
tasks are atomic
inspection task says do not edit yet when useful
no broad refactor permission
no unrelated cleanup
no formatting churn unless scoped
no future-stage work
```

### Docs

Check:

```text
required report path exists
user-facing docs are conditional unless behavior/docs examples change
docs churn is not encouraged
```

### Verification

Check:

```text
compile/check/test commands exist
commands are focused
brittle globs have fallback wording
stage says not to claim tests passed unless actually run
```

### Completion

Check:

```text
report required
lifecycle cleanup required according to AGENTS.md
completion criteria are checkable
no vague criteria like UX feels better
```

### Output Limits

Check:

```text
compact final format exists
full diffs are prohibited by default
broad summaries are prohibited
```

## Output Format

Return only:

```text
VERDICT:
- pass/fail

BLOCKERS:
- <issue or none>

PATCHES:
- <specific correction or none>

RISK:
- low/medium/high

NOTES:
- <real caveat or none>
```

## Rules

Do not rewrite the whole stage unless explicitly requested.

Do not duplicate the full input.

Do not paste full diffs.

Keep patch suggestions concrete.

If the stage is safe, return `pass` and keep notes short.

## Example

Input weakness:

```text
No FILES TO INSPECT.
Task says: Refactor CLI and services.
No OUTPUT LIMITS.
```

Output:

```text
VERDICT:
- fail

BLOCKERS:
- missing FILES TO INSPECT
- broad implementation task authorizes unsafe refactor
- missing OUTPUT LIMITS

PATCHES:
- add FILES TO INSPECT with exact files/directories
- split refactor task into atomic inspection/wiring/test steps
- add compact final response format

RISK:
- high

NOTES:
- stage is not safe for Codex implementation yet
```
