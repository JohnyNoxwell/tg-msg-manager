# Live Smoke Checklist

## Variables

Use real local values:

- `TEST_USER_ID`: target Telegram user ID for export/archive checks
- `TEST_CHAT_ID`: chat/dialog ID that contains known messages from `TEST_USER_ID`

## Preconditions

- Valid Telegram session exists.
- Test chat/dialog is available.
- Test user ID is known.
- DB backup created.
- Network available.

## Commands

### 1. Basic CLI help

Command:

```bash
python3 -m tg_msg_manager.cli --help
```

Expected:

- exit code `0`
- command exits `0`
- help output contains main commands

Failure:

- non-zero exit code
- traceback
- missing `export`, `db-export`, `export-pm`, `retry`, or `report` commands

### 2. Minimal sync

Command:

```bash
python3 -m tg_msg_manager.cli export --user-id "$TEST_USER_ID" --chat-id "$TEST_CHAT_ID" --flat --limit 1
```

Expected:

- exit code `0`
- no crash
- DB receives a new or known message
- sync checkpoint updates correctly

Failure:

- non-zero exit code
- no message persistence for a known live message
- checkpoint not updated after a successful run

### 3. Flat export

Command:

```bash
python3 -m tg_msg_manager.cli export --user-id "$TEST_USER_ID" --chat-id "$TEST_CHAT_ID" --flat --limit 1
```

Expected:

- exit code `0`
- output file created
- target user's message appears
- no unrelated messages included

Failure:

- non-zero exit code
- output file missing
- target message absent
- unexpected unrelated context appears in flat mode

### 4. Deep context export

Command:

```bash
python3 -m tg_msg_manager.cli export --user-id "$TEST_USER_ID" --chat-id "$TEST_CHAT_ID" --depth 2 --limit 1
```

Expected:

- exit code `0`
- output file created
- target message included
- context messages included
- separators preserved

Failure:

- non-zero exit code
- output file missing
- context not rendered in deep mode
- formatting separators differ unexpectedly

### 5. DB export

Command:

```bash
python3 -m tg_msg_manager.cli db-export --user-id "$TEST_USER_ID" --json
```

Expected:

- exit code `0`
- output created
- export target state updates
- unchanged second run is skipped or handled as designed

Failure:

- non-zero exit code
- JSON/JSONL artifact missing
- target export state not updated
- repeated unchanged run rewrites output unexpectedly

### 6. Private archive

Command:

```bash
python3 -m tg_msg_manager.cli export-pm --user-id "$TEST_USER_ID"
```

Expected:

- exit code `0`
- no crash
- archive output created
- checkpoint/state updated

Failure:

- non-zero exit code
- chat log or media directories missing
- target checkpoint not updated after a successful archive

### 7. Retry/report

Command:

```bash
python3 -m tg_msg_manager.cli retry --list
python3 -m tg_msg_manager.cli report
```

Expected:

- commands exit `0`
- report contains expected sections
- retry listing renders without traceback

Failure:

- non-zero exit code
- missing retry/report sections
- traceback in either command

## Result table

| Date | Commit | Tester | Scenario | Result | Notes |
|---|---|---|---|---|---|
