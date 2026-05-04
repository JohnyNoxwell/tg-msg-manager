# Stage 5 Telegram Fixture Format

Fixture files in this directory are JSONL and intentionally anonymized. They exist only for offline pipeline verification and must not contain real Telegram identifiers, private payloads, or copied production message bodies.

Each line is one record with a `kind` field:

- `entity`: declares a user, group, or channel fixture entity.
- `message`: declares one Telegram-like message row.
- `deleted`: marks a message id as deleted and therefore hidden from fake reads.
- `missing`: marks a message id as unavailable for live fetches.
- `failure`: injects a controlled client error for retry/report coverage.

Supported `entity` fields:

- `entity_id`: integer fixture id.
- `entity_type`: `user`, `group`, or `channel`.
- `first_name`, `last_name`, `username`, `title`, `phone`.
- `include_in_dialogs`: whether `get_dialogs()` should expose this entity.
- `is_me`: marks the fixture owner returned by `get_me()`.

Supported `message` fields:

- `chat_id`, `message_id`, `user_id`, `timestamp`.
- `author_name`, `text`, `media_type`, `reply_to_id`, `fwd_from_id`, `context_group_id`.
- `raw_payload`: optional JSON object for deterministic export/context behavior.
- `media_ref`: optional fake download payload used by `download_media()`.
- `is_service`: optional boolean.

Allowed additional fields:

- Extra metadata may live inside `raw_payload`.
- Duplicate `message` rows with the same `chat_id` + `message_id` are allowed when a test needs to verify idempotency or edited payload replacement across fixture revisions.

Rules for edge cases:

- `deleted` means the fake client behaves as if the message no longer exists in scans or direct fetches.
- `missing` means the message id is intentionally absent from fake live fetches even if another record references it.
- `failure` supports `method`, `entity_id`, optional `from_user_id`, `times`, `error_type`, `message`, and optional `seconds`.
- Failures are deterministic and are consumed call by call, which allows retry tests to fail once and then recover without network access.
