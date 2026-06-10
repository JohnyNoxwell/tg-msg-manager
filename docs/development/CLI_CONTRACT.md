# CLI Contract

Last verified: 2026-06-10

Console script:

- `tg-msg-manager = tg_msg_manager.cli:main`

Primary Python entrypoint:

- `python3 -m tg_msg_manager.cli`

## Commands

| Command | Required args | Optional args / defaults | Expected effect |
| --- | --- | --- | --- |
| `export` | `--user-id` | `--chat-id=None`, `--deep=True`, `--flat`, `--force-resync=False`, `--context-window=3`, `--max-cluster=10`, `--depth=2`, `--limit=None`, `--json=False`, `--txt-profile=context-readable` | Sync target messages, then optionally build DB export artifact |
| `update` | none | none | Refresh tracked targets |
| `retry` | none | `--limit=10`, `--list=False`, `--cleanup=False` | List or run retry queue tasks |
| `report` | none | `--json=False` | Print DB/reporting summary |
| `clean` | none | `--dry-run=None`, `--apply=False`, `--yes=False` | Delete own Telegram messages with safety gates |
| `export-pm` | `--user-id` | none | Archive private dialog |
| `delete` | `--user-id` | none | Delete local DB/filesystem data for target |
| `schedule` | none | none | Configure scheduler integration |
| `setup` | none | none | Install aliases / setup shell helpers |
| `db-export` | `--user-id` | `--json=False`, `--txt-profile=context-readable` | Export already-synced local DB data |
| `validate-dataset` | `--path` | `--json=False` | Validate an exported channel dataset from local files only |
| `inspect-dataset` | `--path` | `--json=False`, `--doctor=False` | Summarize deterministic counts/statuses, or emit a read-only doctor report for an exported channel dataset |
| `target names` | `<target>` | `--field=all`, `--format=text` | Show locally stored username/display-name/title history for a known target without Telegram access |
| `export-channel` | `--channel` | `--limit=None`, `--media=metadata`, `--max-media-size=None`, `--media-types=None`, `--discussion=none`, `--max-comments-per-post=100`, `--output-dir=None`, `--force=False` | Export broadcast-channel posts into the filesystem dataset layout |

## Contract Tests

Protected by:

- `tests.cli.test_cli.TestCLIParser.test_build_cli_parser_preserves_stage0_command_surface`
- `tests.cli.test_cli.TestCLIParser.test_help_lists_stage0_commands_and_export_args`
- `tests.cli.test_cli.TestCLIContext.test_run_cli_without_command_in_non_tty_prints_help`
- `tests.cli.test_channel_export_cli.TestChannelExportCLIParser`
- `tests.services.dataset_validation.test_dataset_validation_contracts.TestDatasetValidationCLI`
