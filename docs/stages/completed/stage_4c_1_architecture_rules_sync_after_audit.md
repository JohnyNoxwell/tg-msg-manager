# STAGE 4C.1 — ARCHITECTURE RULES SYNC AFTER AUDIT

Status: active task
Stage: 4C.1
Type: docs / architecture governance
Depends on: Stage 4C.0 audit report

---

## 0. CODEX ENTRY CONTRACT

```text
Read AGENTS.md first.

Execute Stage 4C.1 — Architecture Rules Sync After Audit.

Goal:
Apply only the minimal architecture rule/documentation updates required by Stage 4C.0.

Do not modify runtime code.
Do not modify tests.
Do not invent new architecture rules.
Do not start later stages.

Use AGENTS.md compact output format.
```

---

## 1. PURPOSE

This stage is conditional.

Run it only if Stage 4C.0 explicitly says that `AGENTS.md` or architecture/development docs need synchronization.

This stage must align project rules with the current decomposed structure without adding unnecessary text or duplicating large documentation.

---

## 2. FILES TO INSPECT

Required:

```text
AGENTS.md
docs/stages/reports/STAGE_4C_0_ARCHITECTURE_STABILIZATION_AUDIT_BEFORE_EXPANSION_REPORT.md
docs/architecture/
docs/development/
docs/stages/README.md
```

Optional only if Stage 4C.0 names them:

```text
README.md
COMMANDS.md
Makefile
.github/workflows/
```

Do not inspect:

```text
runtime source code
tests
docs/archive
unrelated reports
unrelated roadmap files
```

---

## 3. HARD PROHIBITIONS

Do not change:

```text
runtime code
tests
CLI behavior
channel export behavior
dataset behavior
SQLite schema
output formats
stage files unrelated to this sync
```

Do not add:

```text
new implementation instructions not supported by Stage 4C.0
broad architecture essays
duplicated AGENTS.md content in docs
new features
new dependencies
```

---

## 4. ATOMIC TASKS

### 4.1 Confirm Stage 4C.0 findings

- Read the Stage 4C.0 report.
- Extract only exact rule/doc sync needs.
- If the report says no sync is needed, stop and mark this stage complete with no changes except report.

### 4.2 Patch AGENTS.md only if required

Allowed examples:

```text
clarify tg_msg_manager/cli/commands ownership
clarify ChannelExportWorkflowContext boundary
clarify workflow modules ownership
clarify tests subsystem layout
clarify compatibility aggregator rule for cli_commands.py
```

Rules:

```text
keep patches short
do not duplicate docs/architecture content
do not weaken existing prohibitions
do not add broad future roadmap text
```

### 4.3 Patch architecture/development docs only if required

Allowed:

```text
update module ownership map
update test path references
update developer workflow command references
```

Forbidden:

```text
rewriting full docs
adding roadmap content
changing public user docs without need
```

### 4.4 Verify docs consistency

Check:

```text
AGENTS.md does not conflict with architecture docs
docs do not reference old paths incorrectly
stage lifecycle remains clear
```

---

## 5. REQUIRED DOCS

Required:

```text
docs/stages/reports/STAGE_4C_1_ARCHITECTURE_RULES_SYNC_AFTER_AUDIT_REPORT.md
```

Conditional:

```text
AGENTS.md only if Stage 4C.0 says needed
docs/architecture/ only if Stage 4C.0 says needed
docs/development/ only if Stage 4C.0 says needed
docs/stages/README.md when lifecycle cleanup happens
```

Do not update docs just to restate the stage.

---

## 6. TESTS / VERIFICATION

Docs-only stage.

Run:

```bash
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
```

If docs reference test commands and those commands changed, verify the referenced command or document why not.

Do not claim checks passed unless actually run.

---

## 7. REPORT

Create:

```text
docs/stages/reports/STAGE_4C_1_ARCHITECTURE_RULES_SYNC_AFTER_AUDIT_REPORT.md
```

Report must record:

```text
whether Stage 4C.0 required sync
files changed
rules/docs updated
rules/docs intentionally not changed
checks run
what was not run and why
completion status
```

---

## 8. COMPLETION CRITERIA

This stage is complete when:

```text
Stage 4C.0 findings were followed exactly
AGENTS.md/docs were updated only if required
no runtime code was changed
checks were run or inability documented
required report exists
lifecycle cleanup is completed according to AGENTS.md
```

---

## 9. OUTPUT LIMITS

Use AGENTS.md compact final response format.

Do not paste full diffs.
Do not include broad summaries.
