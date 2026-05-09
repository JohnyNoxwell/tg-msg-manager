# Stage Completion Auditor

## Purpose

Audit completed Codex work for a stage.

Use this skill after Codex claims a stage is complete. The goal is to determine whether the stage is actually complete according to the stage file and `AGENTS.md`.

This skill audits. It does not implement missing work unless explicitly requested.

## When To Use

Use after implementation, tests, report generation, or lifecycle cleanup.

Do not use before implementation. Use `stage-reviewer` instead.

## Inputs

Required:

```text
AGENTS.md
active stage file
stage report if it exists
changed files list or diff summary
Codex final response
```

Optional:

```text
changed file contents
test output
relevant docs changed
docs/stages/README.md
current docs/stages/active listing
current docs/stages/completed listing
```

Do not inspect unrelated source code or docs.

## Audit Checklist

### Scope Compliance

Check:

```text
changed files are within stage scope
optional files were changed only if justified
unrelated files were not changed
protected files, if touched, contain no new feature logic
```

### Behavior Preservation

Check that these are unchanged unless explicitly scoped:

```text
CLI command names
CLI flags
defaults
output filenames
output directory layout
SQLite schema
export behavior
sync behavior
delete behavior
retry behavior
scheduler behavior
state/incremental behavior
force/no-new-work behavior
data flow
```

### Architecture Compliance

Check:

```text
no raw SQL added to service layer
no business logic added to compatibility wrappers
no analytics/profiling/OSINT/LLM logic added to exporter
no broad refactor mixed into feature stage
protected files contain only orchestration or mechanical wiring
```

### Tests And Checks

Check:

```text
required commands were run or inability documented
test claims include exact commands
failures are recorded
skipped checks have exact reason
```

Do not accept “tests passed” without exact command evidence.

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
README/COMMANDS/CHANGELOG/docs were updated only when required
no docs churn
```

### Lifecycle

If stage is fully complete, check:

```text
completed stage files moved out of docs/stages/active/
completed stage files moved to docs/stages/completed/
general prompts moved to docs/archive/old_prompts/ when applicable
docs/stages/README.md updated if lifecycle changed
docs/stages/active/ contains only unfinished or next active work
```

## Output Format

Return only:

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

No implementation suggestions unless needed to fix a blocker.

Do not restate the stage.

Do not paste full diffs.

If incomplete, list only the minimum required fixes.

## Example

Input state:

```text
report exists
compile and pytest ran
stage task file still remains in docs/stages/active/
```

Output:

```text
VERDICT:
- incomplete

BLOCKERS:
- lifecycle cleanup missing: completed stage file still in docs/stages/active/

SCOPE:
- pass: changed files are within stage scope

CHECKS:
- pass: required checks were recorded

DOCS:
- pass: required report exists

LIFECYCLE:
- fail: active directory still contains completed stage task

PATCHES:
- move completed stage task to docs/stages/completed/ and update docs/stages/README.md
```
