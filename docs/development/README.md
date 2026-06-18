# Development Documentation

## Purpose

Development docs define how changes are made. They do not define product roadmap by themselves.

## Development rules

- [`PR_CHECKLIST.md`](PR_CHECKLIST.md) - review checklist and boundary checks.
- [`FACADE_SIZE_BASELINE.md`](FACADE_SIZE_BASELINE.md) - facade size guardrail baseline.
- [`PRIVACY_AND_SENSITIVE_ARTIFACTS.md`](PRIVACY_AND_SENSITIVE_ARTIFACTS.md) - handling rules for local credentials, sessions, databases, exports, logs, fixtures, reports, and screenshots.
- [`PACKAGE_IDENTITY_AND_VERSION_POLICY.md`](PACKAGE_IDENTITY_AND_VERSION_POLICY.md) - package/module/script identity and version source policy.
- [`RELEASE_CHECKLIST_SCOPE.md`](RELEASE_CHECKLIST_SCOPE.md) - no-publish release checklist boundary for release-readiness audits.
- [`LOCAL_VERIFICATION_MATRIX.md`](LOCAL_VERIFICATION_MATRIX.md) - offline/local verification matrix for release-readiness audits.
- [`OPERATIONAL_RISKS_AND_LIMITS.md`](OPERATIONAL_RISKS_AND_LIMITS.md) - local runtime caveats for sessions, FloodWait/rate limits, SQLite concurrency, scheduler runs, and live smoke checks.
- [`../architecture/ARCHITECTURE_RULES.md`](../architecture/ARCHITECTURE_RULES.md) - architecture rules that development must preserve.

## Testing

- [`LIVE_SMOKE_CHECKLIST.md`](LIVE_SMOKE_CHECKLIST.md) - manual live Telegram smoke checklist.
- [`NON_CHANNEL_SYNTHETIC_FIXTURES_PLAN.md`](NON_CHANNEL_SYNTHETIC_FIXTURES_PLAN.md) - synthetic fixture basis for user/group `export` and `db-export` contract checks.
- [`NON_CHANNEL_CONTRACT_TEST_PLAN.md`](NON_CHANNEL_CONTRACT_TEST_PLAN.md) - focused fixture-backed non-channel contract test coverage and deferred gaps.
- [`DEFERRED_CONTRACT_COVERAGE_PRIORITIZATION.md`](DEFERRED_CONTRACT_COVERAGE_PRIORITIZATION.md) - priority order for generated-output, no-new-work, raw JSON, SQLite schema, smoke-check, and private archive contract gaps.
- Stage reports under [`../stages/reports/`](../stages/reports/) record verification results for completed stages.

Routine verification commands are defined by the active task. Do not claim unrun checks passed.
The routine local test target is `make test`, which runs `python3 -m pytest tests -q`.

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
5. Run the checks requested by the active task. For code or test changes, run the CI-parity gate from `.github/workflows/ci.yml`; when CI runs `make verify`, local stage completion must run `make verify`.
6. Update docs and reports in the same change when required.

Before push or handoff for code/test changes, run:

```bash
make pre-commit
```

`make pre-commit` may format files, then runs `make verify`. `make verify` remains the authoritative completion gate when CI uses it.

## Documentation rules

Docs are part of implementation. Update docs when changing:

- CLI commands or flags;
- output files, dataset schemas, manifests, state files;
- media, discussion, incremental, force, or no-new-work behavior;
- architecture boundaries or developer workflow;
- testing commands, stage status, or known limitations.

A task is not complete while required docs are stale.
