# Development Documentation

## Purpose

Development docs define how changes are made. They do not define product roadmap by themselves.

## Development rules

- [`PR_CHECKLIST.md`](PR_CHECKLIST.md) - review checklist and boundary checks.
- [`FACADE_SIZE_BASELINE.md`](FACADE_SIZE_BASELINE.md) - facade size guardrail baseline.
- [`PRIVACY_AND_SENSITIVE_ARTIFACTS.md`](PRIVACY_AND_SENSITIVE_ARTIFACTS.md) - handling rules for local credentials, sessions, databases, exports, logs, fixtures, reports, and screenshots.
- [`PACKAGE_IDENTITY_AND_VERSION_POLICY.md`](PACKAGE_IDENTITY_AND_VERSION_POLICY.md) - package/module/script identity and version source policy.
- [`../architecture/ARCHITECTURE_RULES.md`](../architecture/ARCHITECTURE_RULES.md) - architecture rules that development must preserve.

## Testing

- [`LIVE_SMOKE_CHECKLIST.md`](LIVE_SMOKE_CHECKLIST.md) - manual live Telegram smoke checklist.
- Stage reports under [`../stages/reports/`](../stages/reports/) record verification results for completed stages.

Routine verification commands are defined by the active task. Do not claim unrun checks passed.

## CLI contracts

- [`CLI_CONTRACT.md`](CLI_CONTRACT.md) - CLI contract inventory.
- [`SAFE_FIRST_CHANNEL_EXPORT.md`](SAFE_FIRST_CHANNEL_EXPORT.md) - safe first channel dataset export quickstart.
- [`../../COMMANDS.md`](../../COMMANDS.md) - user-facing command reference.

Do not change command names, arguments, defaults, output formats, or state semantics without explicit instruction and documentation updates.

## Agent workflow

Default workflow:

1. Read [`../../AGENTS.md`](../../AGENTS.md).
2. Read the active task under [`../stages/active/`](../stages/active/).
3. Read only referenced architecture/development docs.
4. Implement the smallest scoped change.
5. Run the checks requested by the active task.
6. Update docs and reports in the same change when required.

## Documentation rules

Docs are part of implementation. Update docs when changing:

- CLI commands or flags;
- output files, dataset schemas, manifests, state files;
- media, discussion, incremental, force, or no-new-work behavior;
- architecture boundaries or developer workflow;
- testing commands, stage status, or known limitations.

A task is not complete while required docs are stale.
