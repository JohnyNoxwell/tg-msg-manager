# Export Smoke Scenarios

Date: 2026-05-04

Purpose:

- verify that SQLite/schema hardening work does not change public export behavior;
- keep checks runnable without changing the CLI surface;
- make missing-reply and renamed-user cases explicit before further migrations.

## 1. Export one target by `user_id`

- command:
  `python3 -m tg_msg_manager.cli export --user-id <USER_ID>`
- expected artifact:
  one file in `DB_EXPORTS/` for the target
- expected result:
  export completes successfully and prints a sync summary
- checks:
  output file exists
  output file is non-empty
  exported rows/messages belong to the requested target plus allowed context

## 2. Export target with reply context

- command:
  `python3 -m tg_msg_manager.cli export --user-id <USER_ID> --chat-id <CHAT_ID> --deep`
- expected artifact:
  one target export file in `DB_EXPORTS/`
- expected result:
  target messages are present and reply-related context messages are included when locally available or fetchable
- checks:
  output file exists
  output file is non-empty
  at least one exported message has `reply_to_id`

## 3. Export target with context window

- command:
  `python3 -m tg_msg_manager.cli export --user-id <USER_ID> --chat-id <CHAT_ID> --context-window 3`
- expected artifact:
  one target export file in `DB_EXPORTS/`
- expected result:
  export succeeds with surrounding context behavior unchanged from pre-migration baseline
- checks:
  output file exists
  output file is non-empty
  message count does not drop unexpectedly versus the same scenario before migration

## 4. Repeat export/update without new messages

- commands:
  `python3 -m tg_msg_manager.cli export --user-id <USER_ID> --chat-id <CHAT_ID>`
  `python3 -m tg_msg_manager.cli update`
- expected result:
  second run should not behave like a first sync
- checks:
  no crash
  no duplicate-message explosion in DB counts
  exported artifact is either skipped or refreshed deterministically, depending on DB-backed artifact fingerprint state

## 5. Repeat export/update with new messages

- commands:
  run a normal export/update
  add or expose newer messages for the same target
  rerun the same command
- expected result:
  only new head messages should be appended/synced
- checks:
  `last_msg_id` advances
  old messages are not duplicated
  export artifact remains readable and non-empty

## 6. Export user who changed nickname

- command:
  `python3 -m tg_msg_manager.cli export --user-id <USER_ID>`
- expected result:
  historical rows keep their original `messages.author_name`
  current target naming resolves from `users.current_author_name` / tracked target metadata
- checks:
  filename/display name follows the current resolved target name
  older exported rows may still contain older `author_name` values
  no retroactive rewrite of historical message rows

## 7. Export target with missing `reply_to_id`

- command:
  `python3 -m tg_msg_manager.cli export --user-id <USER_ID> --chat-id <CHAT_ID> --deep`
- expected result:
  export completes even if some parent reply messages are absent from local storage
- checks:
  no crash
  exported artifact exists
  missing parent links degrade gracefully instead of aborting the export

## Fixture-backed offline verification

- command:
  `python3 -m unittest tests.test_fixture_e2e -q`
- expected result:
  fixture-backed sync/context/export/retry/report scenarios pass without Telegram access

## CLI help smoke checks

- commands:
  `python3 -m tg_msg_manager.cli --help`
  `python3 -m tg_msg_manager.cli export --help`
  `python3 -m tg_msg_manager.cli update --help`
  `python3 -m tg_msg_manager.cli db-export --help`
- expected result:
  all commands exit successfully and preserve the Stage 0 command surface
