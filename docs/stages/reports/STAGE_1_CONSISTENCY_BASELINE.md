# Stage 1 Consistency Baseline

## 1. Commit

- Branch: `main`
- Commit: `31b78b342fe8129149dcd13dfa434eb352558640`

## 2. Git state before changes

```text
git status --short
(clean working tree)
```

## 3. Baseline verification

### `make test`

- Status: passed
- Result: `Ran 186 tests in 24.327s`

### `make verify`

- Status: passed
- Result: verification pipeline completed successfully on the pre-pass tree

### `python3 -m compileall tg_msg_manager`

- Status: passed
- Result: package compiled without syntax/import errors

### import smoke

Command:

```bash
python3 - <<'PY'
import tg_msg_manager
import tg_msg_manager.services.export
import tg_msg_manager.services.context
import tg_msg_manager.services.db_export
import tg_msg_manager.services.private_archive
import tg_msg_manager.infrastructure.storage.contracts
import tg_msg_manager.core.models.payloads
print("imports ok")
PY
```

- Status: passed
- Result: `imports ok`

## 4. Known consistency gaps before the pass

- Internal code still had a few stale imports pointing at legacy DB export and storage aggregator entrypoints.
- `PrivateArchiveService` still carried message-stream and media-download operational logic inline.
- Compatibility import coverage for Stage 1 entrypoints was missing.
- Stage 1 audit/baseline/report documents for the consistency close-out were not yet present.
