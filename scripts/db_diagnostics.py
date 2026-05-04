#!/usr/bin/env python3

import argparse
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


KEY_TABLES = [
    "messages",
    "users",
    "chats",
    "sync_targets",
    "sync_state",
    "message_context_links",
    "message_target_links",
    "export_targets",
    "export_runs",
    "missing_reply_refs",
    "retry_queue",
    "user_identity_history",
]


@dataclass(frozen=True)
class QueryCheck:
    label: str
    sql: str


QUALITY_CHECKS = [
    QueryCheck(
        "messages_without_user_id",
        "SELECT COUNT(*) AS value FROM messages WHERE user_id IS NULL OR user_id = 0",
    ),
    QueryCheck(
        "messages_without_text_and_media",
        """
        SELECT COUNT(*) AS value
        FROM messages
        WHERE COALESCE(TRIM(text), '') = ''
          AND COALESCE(TRIM(media_type), '') = ''
        """,
    ),
    QueryCheck(
        "duplicate_chat_message_pairs",
        """
        SELECT COUNT(*) AS value
        FROM (
            SELECT chat_id, message_id
            FROM messages
            GROUP BY chat_id, message_id
            HAVING COUNT(*) > 1
        )
        """,
    ),
    QueryCheck(
        "duplicate_payload_hashes",
        """
        SELECT COUNT(*) AS value
        FROM (
            SELECT payload_hash
            FROM messages
            WHERE COALESCE(TRIM(payload_hash), '') != ''
            GROUP BY payload_hash
            HAVING COUNT(*) > 1
        )
        """,
    ),
    QueryCheck(
        "missing_reply_references",
        """
        SELECT COUNT(*) AS value
        FROM messages m
        WHERE m.reply_to_id IS NOT NULL
          AND NOT EXISTS (
              SELECT 1
              FROM messages parent
              WHERE parent.chat_id = m.chat_id
                AND parent.message_id = m.reply_to_id
          )
        """,
    ),
    QueryCheck(
        "tracked_missing_reply_refs",
        """
        SELECT COUNT(*) AS value
        FROM missing_reply_refs
        WHERE status = 'missing'
        """,
    ),
    QueryCheck(
        "dangling_target_links_missing_message",
        """
        SELECT COUNT(*) AS value
        FROM message_target_links l
        WHERE NOT EXISTS (
            SELECT 1
            FROM messages m
            WHERE m.chat_id = l.chat_id
              AND m.message_id = l.message_id
        )
        """,
    ),
    QueryCheck(
        "dangling_target_links_missing_user",
        """
        SELECT COUNT(*) AS value
        FROM message_target_links l
        WHERE NOT EXISTS (
            SELECT 1
            FROM users u
            WHERE u.user_id = l.target_user_id
        )
        """,
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect SQLite schema and data quality for TG_MSG_MNGR storage."
    )
    parser.add_argument(
        "db_path",
        nargs="?",
        default="messages.db",
        help="Path to the SQLite database. Defaults to ./messages.db",
    )
    return parser.parse_args()


def connect_readonly(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def fetch_scalar(conn: sqlite3.Connection, sql: str) -> Any:
    row = conn.execute(sql).fetchone()
    if row is None:
        return None
    return row[0]


def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def collect_tables(conn: sqlite3.Connection) -> list[str]:
    rows = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name ASC
        """
    ).fetchall()
    return [str(row["name"]) for row in rows]


def collect_columns(conn: sqlite3.Connection, table_name: str) -> list[dict[str, Any]]:
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return [
        {
            "cid": int(row["cid"]),
            "name": row["name"],
            "type": row["type"],
            "notnull": int(row["notnull"]),
            "default": row["dflt_value"],
            "pk": int(row["pk"]),
        }
        for row in rows
    ]


def collect_indexes(conn: sqlite3.Connection, table_name: str) -> list[dict[str, Any]]:
    indexes = []
    rows = conn.execute(f"PRAGMA index_list({table_name})").fetchall()
    for row in rows:
        index_name = row["name"]
        columns = conn.execute(f"PRAGMA index_info({index_name})").fetchall()
        indexes.append(
            {
                "name": index_name,
                "unique": bool(int(row["unique"])),
                "origin": row["origin"],
                "columns": [column["name"] for column in columns],
            }
        )
    return indexes


def collect_key_counts(conn: sqlite3.Connection) -> dict[str, int | None]:
    counts: dict[str, int | None] = {}
    for table_name in KEY_TABLES:
        if table_exists(conn, table_name):
            counts[table_name] = int(fetch_scalar(conn, f"SELECT COUNT(*) FROM {table_name}") or 0)
        else:
            counts[table_name] = None
    return counts


def collect_message_range(conn: sqlite3.Connection) -> dict[str, Any]:
    if not table_exists(conn, "messages"):
        return {"min_timestamp": None, "max_timestamp": None}
    row = conn.execute(
        """
        SELECT
            MIN(timestamp) AS min_timestamp,
            MAX(timestamp) AS max_timestamp
        FROM messages
        """
    ).fetchone()
    return {
        "min_timestamp": int(row["min_timestamp"]) if row["min_timestamp"] is not None else None,
        "max_timestamp": int(row["max_timestamp"]) if row["max_timestamp"] is not None else None,
    }


def collect_quality_checks(conn: sqlite3.Connection) -> dict[str, int | str]:
    results: dict[str, int | str] = {}
    for check in QUALITY_CHECKS:
        try:
            results[check.label] = int(fetch_scalar(conn, check.sql) or 0)
        except sqlite3.OperationalError as exc:
            results[check.label] = f"unavailable: {exc}"
    try:
        results["dangling_context_links"] = int(
            fetch_scalar(conn, build_dangling_context_links_sql(conn)) or 0
        )
    except sqlite3.OperationalError as exc:
        results["dangling_context_links"] = f"unavailable: {exc}"
    return results


def build_dangling_context_links_sql(conn: sqlite3.Connection) -> str:
    if not table_exists(conn, "message_context_links"):
        return "SELECT 0"
    columns = {column["name"] for column in collect_columns(conn, "message_context_links")}
    if "chat_id" in columns:
        return """
            SELECT COUNT(*) AS value
            FROM message_context_links l
            WHERE NOT EXISTS (
                      SELECT 1
                      FROM messages src
                      WHERE src.chat_id = l.chat_id
                        AND src.message_id = l.message_id
                  )
               OR NOT EXISTS (
                      SELECT 1
                      FROM messages ctx
                      WHERE ctx.chat_id = l.chat_id
                        AND ctx.message_id = l.context_message_id
                  )
        """
    return """
        SELECT COUNT(*) AS value
        FROM message_context_links l
        WHERE NOT EXISTS (
                  SELECT 1
                  FROM messages src
                  WHERE src.message_id = l.message_id
              )
           OR NOT EXISTS (
                  SELECT 1
                  FROM messages ctx
                  WHERE ctx.message_id = l.context_message_id
              )
    """


def format_ts(value: int | None) -> str:
    if value is None:
        return "n/a"
    return datetime.fromtimestamp(value, tz=timezone.utc).isoformat()


def collect_report(conn: sqlite3.Connection, db_path: Path) -> dict[str, Any]:
    tables = collect_tables(conn)
    return {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "database": str(db_path),
        "pragma": {
            "integrity_check": fetch_scalar(conn, "PRAGMA integrity_check;"),
            "journal_mode": fetch_scalar(conn, "PRAGMA journal_mode;"),
            "user_version": int(fetch_scalar(conn, "PRAGMA user_version;") or 0),
        },
        "tables": {
            table_name: {
                "columns": collect_columns(conn, table_name),
                "indexes": collect_indexes(conn, table_name),
            }
            for table_name in tables
        },
        "key_counts": collect_key_counts(conn),
        "messages": {
            **collect_message_range(conn),
            "message_count": int(fetch_scalar(conn, "SELECT COUNT(*) FROM messages") or 0)
            if table_exists(conn, "messages")
            else 0,
            "reply_links": int(
                fetch_scalar(
                    conn,
                    "SELECT COUNT(*) FROM messages WHERE reply_to_id IS NOT NULL",
                )
                or 0
            )
            if table_exists(conn, "messages")
            else 0,
        },
        "quality_checks": collect_quality_checks(conn),
    }


def render_report(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# SQLite Diagnostics")
    lines.append("")
    lines.append(f"- generated_at: {report['generated_at']}")
    lines.append(f"- database: {report['database']}")
    lines.append(
        f"- integrity_check: {report['pragma']['integrity_check']}"
    )
    lines.append(f"- journal_mode: {report['pragma']['journal_mode']}")
    lines.append(f"- user_version: {report['pragma']['user_version']}")
    lines.append("")
    lines.append("## Key Counts")
    for table_name, value in report["key_counts"].items():
        lines.append(f"- {table_name}: {value if value is not None else 'missing table'}")
    lines.append("")
    lines.append("## Message Range")
    lines.append(f"- min_timestamp: {format_ts(report['messages']['min_timestamp'])}")
    lines.append(f"- max_timestamp: {format_ts(report['messages']['max_timestamp'])}")
    lines.append(f"- message_count: {report['messages']['message_count']}")
    lines.append(f"- reply_links: {report['messages']['reply_links']}")
    lines.append("")
    lines.append("## Quality Checks")
    for label, value in report["quality_checks"].items():
        lines.append(f"- {label}: {value}")
    lines.append("")
    lines.append("## Tables")
    for table_name, table_data in report["tables"].items():
        lines.append(f"### {table_name}")
        lines.append("columns:")
        for column in table_data["columns"]:
            default = column["default"] if column["default"] is not None else "NULL"
            lines.append(
                f"- {column['name']} {column['type']} pk={column['pk']} notnull={column['notnull']} default={default}"
            )
        lines.append("indexes:")
        if table_data["indexes"]:
            for index in table_data["indexes"]:
                cols = ", ".join(index["columns"])
                lines.append(
                    f"- {index['name']} unique={str(index['unique']).lower()} origin={index['origin']} columns=[{cols}]"
                )
        else:
            lines.append("- none")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    db_path = Path(args.db_path).expanduser().resolve()
    with connect_readonly(db_path) as conn:
        report = collect_report(conn, db_path)
    print(render_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
