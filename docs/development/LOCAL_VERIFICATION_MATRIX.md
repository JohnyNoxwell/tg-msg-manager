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

If a command cannot run, record the exact command, result, and reason in the
active stage report.

## Optional Local Checks

These may be useful for deeper local confidence, but they are not mandatory for
the offline release checklist unless a future active stage makes them required:

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
