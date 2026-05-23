---
name: stage-completion-auditor
description: Audit completed Codex work for a tg-msg-manager stage after implementation, checks, report, or lifecycle cleanup and before accepting the stage as complete. Use when Codex claims a stage is complete and the result must be checked against AGENTS.md, the active stage file, stage report, changed files, test/check output, docs rules, and lifecycle state.
---

# Stage Completion Auditor

## Purpose

Audit completed Codex work for a stage.

Determine whether the stage is complete according to the stage file and `AGENTS.md`.

Do not implement missing work unless explicitly requested.

## When To Use

Use:

```text
after Codex claims a stage is complete
after implementation/checks/report/lifecycle cleanup
before accepting a stage as complete
```

Do not use:

```text
before implementation
for architecture-only review before code changes
```

If `.skills/stage-reviewer` exists, use `stage-reviewer` for pre-implementation review.

## Inputs

Request these inputs when available:

```text
AGENTS.md
active stage file
stage report
Codex final response
changed files list
test/check output
relevant docs changed
lifecycle file locations
```

Do not require full diffs unless necessary.

## Audit Checklist

### Scope Compliance

Check:

```text
changed files are within stage scope
optional files were changed only if justified
unrelated files were not changed
protected files were not changed beyond allowed mechanical wiring
```

### Behavior Preservation

Check that these remain unchanged unless explicitly scoped:

```text
CLI command names
CLI flags
defaults
output filenames
output directory layout
SQLite schema
dataset formats
export behavior
sync behavior
delete behavior
retry behavior
scheduler behavior
media behavior
discussion behavior
validation/inspection behavior
state/incremental/force/no-new-work behavior
```

### Architecture Compliance

Check:

```text
no raw SQL in service layer
no business logic in compatibility wrappers
no analytics/profiling/OSINT/LLM logic in exporter core
no broad refactor mixed into feature stage
protected files contain only orchestration or mechanical wiring
```

### Tests And Checks

Check:

```text
required commands were run or inability documented
exact commands are recorded
failures are recorded
skipped checks have exact reason
do not accept "tests passed" without command evidence
```

### Docs And Report

Check:

```text
required report exists
report records exact files changed
report records exact checks run
report records what changed
report records what remained unchanged
report records what was not run and why
report records completion status
docs were updated only if required
no docs churn
```

### Lifecycle

Check:

```text
completed stage files moved out of docs/stages/active/
completed stage files moved to docs/stages/completed/
launch prompts archived when project rules require it
docs/stages/README.md updated if lifecycle changed
active directory contains only unfinished or next active work
```

## Output Format

Return exactly:

```text
VERDICT:
- complete/incomplete

BLOCKERS:
- <blocker or none>

SCOPE:
- pass/fail: <short reason>

CHECKS:
- pass/fail: <short reason>

DOCS:
- pass/fail: <short reason>

LIFECYCLE:
- pass/fail: <short reason>

PATCHES:
- <specific next correction or none>
```

## Rules

No long prose.

No full diffs.

Do not restate the whole stage.

Do not implement fixes unless explicitly requested.

If incomplete, list only minimum required fixes.

If complete, keep notes short.

If evidence is insufficient, mark incomplete and name the missing evidence.

## Example

Input state:

```text
report exists
tests ran
stage file still remains in docs/stages/active/
```

Output:

```text
VERDICT:
- incomplete

BLOCKERS:
- lifecycle cleanup missing

SCOPE:
- pass: changed files are within stage scope

CHECKS:
- pass: exact test commands are recorded

DOCS:
- pass: required report exists

LIFECYCLE:
- fail: completed stage file remains in docs/stages/active/

PATCHES:
- move completed stage file to docs/stages/completed/
```
