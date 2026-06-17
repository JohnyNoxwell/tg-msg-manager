# Local Verification Matrix

Status: offline release-checklist verification matrix.

This matrix defines local checks for release-readiness audits. It does not
authorize publishing, version bumps, tags, package builds/uploads, live Telegram
checks, private artifact reads, or behavior changes.

## Required Offline Checks

Run when the environment has the project development tools available:

```bash
git diff --check
make lint
make format-check
make test
make verify
python3 -m unittest discover tests -p '*non_channel*contract*.py'
```

For stages that change code or tests, local completion must match the
repository CI gate in `.github/workflows/ci.yml`. When CI runs `make verify`,
the stage cannot be marked complete unless `make verify` passed after the
code/test changes. Focused checks do not replace this gate.

If a command cannot run, record the exact command, result, and reason in the
active stage report.

## Optional Local Checks

These may be useful for deeper local confidence. For code/test changes,
`make pre-commit` is the local pre-push/handoff guardrail, but `make verify`
remains authoritative when CI uses it:

```bash
make pre-commit
python3 -m unittest tests.e2e.test_fixture_e2e -q
```

`make pre-commit` may format files before verification. Do not run it in an
audit-only stage unless formatting changes are explicitly acceptable or the
stage requests it.

## Manual / Live Checks

Manual live Telegram smoke checks require credentials, sessions, and
privacy-safe reporting. They are outside the offline release checklist and must
not be claimed as passed unless a future active stage explicitly scopes and runs
them.

## Never Required For Offline Checklist

- Package publish/upload.
- Git tag creation.
- Version bump.
- Release artifact build unless a future stage explicitly scopes a local dry-run.
- Reading private exports, sessions, SQLite databases, logs, screenshots,
  runtime state, or real Telegram data.
- Network access or Telegram credentials.
