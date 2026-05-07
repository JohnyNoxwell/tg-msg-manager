import argparse


def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TG_MSG_MNGR CLI")
    subparsers = parser.add_subparsers(dest="command")

    export_parser = subparsers.add_parser("export")
    export_parser.add_argument("--user-id", required=True)
    export_parser.add_argument("--chat-id", default=None)
    export_parser.add_argument("--deep", action="store_true", default=True)
    export_parser.add_argument("--flat", action="store_false", dest="deep")
    export_parser.add_argument("--force-resync", action="store_true")
    export_parser.add_argument("--context-window", type=int, default=3)
    export_parser.add_argument("--max-cluster", type=int, default=10)
    export_parser.add_argument("--depth", type=int, default=2)
    export_parser.add_argument("--limit", type=int, default=None)
    export_parser.add_argument("--json", action="store_true")

    subparsers.add_parser("update")
    retry_parser = subparsers.add_parser("retry")
    retry_parser.add_argument("--limit", type=int, default=10)
    retry_parser.add_argument("--list", action="store_true")
    retry_parser.add_argument("--cleanup", action="store_true")
    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("--json", action="store_true")

    clean_parser = subparsers.add_parser("clean")
    clean_parser.add_argument("--dry-run", action="store_true", default=None)
    clean_parser.add_argument("--apply", action="store_true")
    clean_parser.add_argument("--yes", "-y", action="store_true")

    subparsers.add_parser("export-pm").add_argument("--user-id", required=True)
    subparsers.add_parser("delete").add_argument("--user-id", required=True)
    subparsers.add_parser("schedule")
    subparsers.add_parser("setup")

    db_parser = subparsers.add_parser("db-export")
    db_parser.add_argument("--user-id", required=True)
    db_parser.add_argument("--json", action="store_true", default=False)

    export_channel_parser = subparsers.add_parser("export-channel")
    export_channel_parser.add_argument("--channel", required=True)
    export_channel_parser.add_argument("--limit", type=int, default=None)
    export_channel_parser.add_argument(
        "--media",
        choices=("none", "metadata", "full"),
        default="metadata",
    )
    export_channel_parser.add_argument("--output-dir", default=None)
    export_channel_parser.add_argument("--force", action="store_true", default=False)
    return parser
