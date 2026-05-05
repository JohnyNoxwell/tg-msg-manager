# Live Smoke Checklist

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

- command exits `0`
- help output contains main commands

### 2. Minimal sync

Command:

```bash
python3 -m tg_msg_manager.cli export --user-id <TEST_USER_ID> --chat-id <TEST_CHAT_ID> --flat --limit 1
```

Expected:

- no crash
- DB receives a new or known message
- sync checkpoint updates correctly

### 3. Flat export

Command:

```bash
python3 -m tg_msg_manager.cli export --user-id <TEST_USER_ID> --chat-id <TEST_CHAT_ID> --flat --limit 1
```

Expected:

- output file created
- target user's message appears
- no unrelated messages included

### 4. Deep context export

Command:

```bash
python3 -m tg_msg_manager.cli export --user-id <TEST_USER_ID> --chat-id <TEST_CHAT_ID> --depth 2 --limit 1
```

Expected:

- output file created
- target message included
- context messages included
- separators preserved

### 5. DB export

Command:

```bash
python3 -m tg_msg_manager.cli db-export --user-id <TEST_USER_ID> --json
```

Expected:

- output created
- export target state updates
- unchanged second run is skipped or handled as designed

### 6. Private archive

Command:

```bash
python3 -m tg_msg_manager.cli export-pm --user-id <TEST_USER_ID>
```

Expected:

- no crash
- archive output created
- checkpoint/state updated

### 7. Retry/report

Command:

```bash
python3 -m tg_msg_manager.cli retry --list
python3 -m tg_msg_manager.cli report
```

Expected:

- commands exit `0`
- report contains expected sections

## Result table

| Date | Commit | Tester | Scenario | Result | Notes |
|---|---|---|---|---|---|
