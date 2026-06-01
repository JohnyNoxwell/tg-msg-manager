# STAGE 5F.1 — USER DOCUMENTATION NAVIGATION AUDIT / QUICKSTART CONSOLIDATION

Status: active task
Stage: 5F.1
Type: docs
Depends on: `docs/stages/reports/STAGE_5F_0_CURRENT_ARCHITECTURE_CONTEXT_REFRESH_REPORT.md`, `README.md`, `COMMANDS.md`, `docs/README.md`, `docs/development/README.md`, `docs/development/SAFE_FIRST_CHANNEL_EXPORT.md`, and `tg_msg_manager/cli_parser.py` for command example verification only.

---

## 0. CODEX ENTRY CONTRACT

Before editing:

1. Read `AGENTS.md`.
2. Read and apply `.skills/stage-reviewer/SKILL.md`.
3. Read and apply `.skills/architecture-guard/SKILL.md`.
4. Inspect only files listed in this stage, plus directly linked docs needed to verify a claim.
5. Write a compact plan with no more than 5 bullets.

During execution:

- Implement only this stage.
- Do not start Stage 5F.2 or later work.
- Create the factual report before lifecycle cleanup.
- After the report exists, read and apply `.skills/stage-completion-auditor/SKILL.md`.
- Complete lifecycle cleanup according to `AGENTS.md`.

If any required skill is unavailable as a tool, manually read and apply the matching `.skills/<skill-name>/SKILL.md` before reporting it missing.

## 1. PURPOSE

Audit and consolidate user-facing documentation navigation after Stage 5F.0.

Determine whether current docs already cover the user journey or whether a minimal navigational quickstart is needed.

The final conclusion must be exactly one of:

```text
NO_NEW_QUICKSTART_NEEDED
CREATE_CANONICAL_QUICKSTART
```

If `CREATE_CANONICAL_QUICKSTART` is chosen, create only a minimal navigational quickstart. Do not duplicate the command reference from `COMMANDS.md`.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `docs/architecture/CURRENT_PROJECT_CONTEXT.md`
- `docs/architecture/README.md`
- `README.md`
- `COMMANDS.md`
- `docs/README.md`
- `docs/development/README.md`
- `docs/development/SAFE_FIRST_CHANNEL_EXPORT.md`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_5F_0_CURRENT_ARCHITECTURE_CONTEXT_REFRESH_REPORT.md`

Conditional:

- `tg_msg_manager/cli_parser.py` only when command examples are added or changed.
- Directly linked docs from the required files only when needed to verify a navigation claim.

Do not inspect archive files, private artifacts, or existing `docs/stages/reports/` files unrelated to this stage.

## 3. HARD PROHIBITIONS

Do not change:

- runtime code;
- CLI parser behavior, command names, flags, defaults, output, or exit behavior;
- tests;
- SQLite schema or storage behavior;
- dataset formats or Dataset Contract V1;
- services, exporters, validators, or doctor behavior;
- package version or runtime `__version__`;
- private artifacts.

Do not create a full command manual. `COMMANDS.md` remains the command reference.

Do not read, inspect, copy, summarize, or use real Telegram exports, ignored export directories, sessions, credentials, `.env`, SQLite databases, logs with private identifiers, screenshots, message text, real Telegram IDs/usernames/channels, or private media.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Map where the listed docs cover installation, configuration, first run, interactive menu, first user/group export, first `db-export`, first `export-channel`, `validate-dataset`, `inspect-dataset`, `inspect-dataset --doctor`, privacy, docs entrypoints, and command reference location.
2. Identify contradictions and duplicated guidance between `README.md`, `COMMANDS.md`, `docs/README.md`, `docs/development/README.md`, and `docs/development/SAFE_FIRST_CHANNEL_EXPORT.md`.
3. Choose `NO_NEW_QUICKSTART_NEEDED` or `CREATE_CANONICAL_QUICKSTART`.
4. Update only navigation links or minimal entrypoint text needed to make the user entrypoint clear.
5. If the conclusion is `CREATE_CANONICAL_QUICKSTART`, create `docs/user/QUICKSTART.md` as a short navigational page only.

## 5. REQUIRED DOCS

Allowed documentation changes:

- `README.md` only for precise navigation links.
- `COMMANDS.md` only for precise navigation links.
- `docs/README.md` for documentation entrypoint updates.
- `docs/development/README.md` for development-doc navigation updates.
- `docs/development/SAFE_FIRST_CHANNEL_EXPORT.md` only for precise navigation links.
- `docs/user/QUICKSTART.md` only if the report conclusion is `CREATE_CANONICAL_QUICKSTART`.
- `docs/stages/reports/STAGE_5F_1_USER_DOCUMENTATION_NAVIGATION_AUDIT_QUICKSTART_CONSOLIDATION_REPORT.md`.
- `docs/stages/README.md` and this stage file only during lifecycle cleanup after the report exists.

Do not update unrelated docs.

## 6. TESTS / VERIFICATION

Run:

```bash
git diff --check
```

If command examples are added or changed, verify them against:

- `tg_msg_manager/cli_parser.py`
- `README.md`
- `COMMANDS.md`

Do not claim unrun checks passed.

## 7. REPORT

Create:

```text
docs/stages/reports/STAGE_5F_1_USER_DOCUMENTATION_NAVIGATION_AUDIT_QUICKSTART_CONSOLIDATION_REPORT.md
```

The report must be written in Russian and include:

- status;
- final conclusion: `NO_NEW_QUICKSTART_NEEDED` or `CREATE_CANONICAL_QUICKSTART`;
- table-free summary of where each user journey topic is documented;
- contradictions or duplications found;
- files changed;
- checks run;
- skills applied;
- whether a quickstart was created and why;
- confirmation that CLI examples were checked against `tg_msg_manager/cli_parser.py` if examples were touched;
- confirmations for preserved behavior, CLI, SQLite, dataset formats, storage contracts, export behavior, validation/doctor behavior, and private-artifact boundary;
- lifecycle actions.

## 8. COMPLETION CRITERIA

This stage is complete only if:

- documentation navigation has one clear user entrypoint;
- no duplicate command reference was introduced;
- command examples, if changed, match the parser;
- no runtime, CLI, SQLite, dataset, service, export, validation, or doctor behavior changed;
- the factual report exists;
- `stage-completion-auditor` has been applied;
- lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`, stay under 1200 characters, and include only meaningful sections.

Do not include full diffs, large copied file content, markdown tables, generic summaries, speculation, or future recommendations.
