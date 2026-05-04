# Stage 0 CLI Surface Inventory

Date: 2026-05-04

## 1. Top-Level Commands

| Command | Arguments / flags | Visible defaults | Requires Telegram client | Read DB only | Mutates Telegram | Mutates local DB/files |
| --- | --- | --- | --- | --- | --- | --- |
| `export` | `--user-id` required, `--chat-id`, `--deep`, `--flat`, `--force-resync`, `--context-window`, `--max-cluster`, `--depth`, `--limit`, `--json` | `deep=True`, `context_window=3`, `max_cluster=10`, `depth=2`, `limit=None`, `json=False` | yes | no | no | yes |
| `update` | none | none | yes | no | no | yes |
| `retry` | `--limit`, `--list`, `--cleanup` | `limit=10`, `list=False`, `cleanup=False` | yes | mixed | no | yes |
| `report` | `--json` | `json=False` | no | yes | no | no |
| `clean` | `--dry-run`, `--apply`, `--yes/-y` | `dry_run=None`, `apply=False`, `yes=False` | yes | no | yes when not dry-run | yes |
| `export-pm` | `--user-id` required | none | yes | no | no | yes |
| `delete` | `--user-id` required | none | yes in current runtime wiring | no | no | yes |
| `schedule` | none | none | no | no | no | yes |
| `setup` | none | none | no | no | no | yes |
| `db-export` | `--user-id` required, `--json` | `json=False` | no | yes | no | yes |

Notes:

- `report` and `db-export` are explicitly read-only against Telegram.
- `delete` currently boots the normal cleaner/runtime path, but the command intent is local purge only.
- `retry` can stay read-mostly or re-run ingestion work depending on task type.

## 2. Interactive Menu Entry Points

Primary entry points:

- `main_menu()`
- `_dispatch_main_menu_choice()`

Main menu hotkeys:

- `1` -> export target
- `2` -> update tracked targets
- `3` -> clean own Telegram messages
- `4` -> export PM
- `5` -> delete local target data
- `6` -> setup scheduler
- `7` -> install aliases
- `8` -> about
- `9` -> DB export
- `R` -> retry queue
- `P` -> report
- `L` -> toggle language
- `0` -> exit
- `ESC` -> back/cancel in prompt flows

Back/cancel behavior:

- `ESC` returns from prompt-driven menu flows without action.
- In export flow, entering `0` at target prompt also returns.
- `0` from the main menu exits the menu loop.

Service routing:

- export menu -> `ExportService` + `DBExportService`
- update menu -> `ExportService` + `DBExportService`
- clean menu -> `CleanerService`
- export PM menu -> `PrivateArchiveService`
- delete menu -> `CleanerService.purge_user_data()`
- DB export menu -> `DBExportService`
- retry menu -> `RetryWorker` / retry read-side
- report menu -> `ReportCollector`
- schedule menu -> `setup_scheduler()`
- setup menu -> `AliasManager`

## 3. Output-Sensitive Behavior

Behavior treated as output-sensitive during Stage 0:

- top-level help usage blocks and command names;
- export progress/event rendering via `render_service_event()`;
- final export summary block from `UI.print_final_summary()`;
- update summary rendering from `print_update_summary()`;
- retry queue textual list and retry summary line;
- report output format selection (`markdown` vs `json`);
- interactive menu hotkeys and labels rendered by `render_main_menu()`.

Stage 0 rule:

- internal handler/parser extraction is allowed;
- user-visible command names, flags, defaults, and help semantics must remain unchanged.
