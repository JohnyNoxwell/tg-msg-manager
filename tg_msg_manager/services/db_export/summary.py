import re
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Iterable, List, Optional

from ...core.models.message import MessageData
from ...infrastructure.storage.records import (
    StoredUser,
    UserExportRow,
    UserExportSummary,
)
from ...utils.ui import UI
from .manifest import build_export_fingerprint
from ..rendering.txt_profiles import TXT_PROFILE_LEGACY


@dataclass
class DBExportSource:
    export_summary: Optional[UserExportSummary]
    export_rows: Optional[List[UserExportRow]]
    export_row_iter_factory: Optional[Callable[[], Iterable[UserExportRow]]]
    messages: Optional[List[MessageData]]
    source_count: int


@dataclass
class DBExportPlan:
    target_author: str
    output_path: str
    ext: str
    fingerprint: dict


def resolve_export_author_name(
    storage: object, user_id: int, messages: List[MessageData]
) -> str:
    db_user = StoredUser.coerce(storage.get_user(user_id))
    if db_user:
        formatted = UI.format_name(db_user)
        if formatted and formatted != "Unknown" and not formatted.startswith("ID:"):
            return formatted

    for message in messages:
        if (
            message.user_id == user_id
            and message.author_name
            and message.author_name.strip()
        ):
            return message.author_name.strip()

    return f"User_{user_id}"


def resolve_export_author_name_from_rows(
    storage: object, user_id: int, rows: List[UserExportRow]
) -> str:
    db_user = StoredUser.coerce(storage.get_user(user_id))
    if db_user:
        formatted = UI.format_name(db_user)
        if formatted and formatted != "Unknown" and not formatted.startswith("ID:"):
            return formatted

    for row in rows:
        if row.user_id == user_id and row.author_name:
            return str(row.author_name).strip()

    return f"User_{user_id}"


def resolve_export_author_name_from_summary(
    storage: object, user_id: int, summary: UserExportSummary
) -> str:
    db_user = StoredUser.coerce(storage.get_user(user_id))
    if db_user:
        formatted = UI.format_name(db_user)
        if formatted and formatted != "Unknown" and not formatted.startswith("ID:"):
            return formatted

    author_name = summary.target_author_name
    if isinstance(author_name, str) and author_name.strip():
        return author_name.strip()

    return f"User_{user_id}"


def load_export_source(
    storage: object,
    *,
    user_id: int,
    as_json: bool,
    json_profile: str,
) -> Optional[DBExportSource]:
    export_summary = None
    export_rows = None
    if as_json and json_profile == "ai":
        summary_getter = getattr(storage, "get_user_export_summary", None)
        iter_getter = getattr(storage, "iter_user_export_rows", None)
        if callable(summary_getter):
            export_summary = UserExportSummary.coerce(summary_getter(user_id))
            if export_summary and callable(iter_getter):
                return DBExportSource(
                    export_summary=export_summary,
                    export_rows=None,
                    export_row_iter_factory=lambda: (
                        UserExportRow.coerce(row) for row in iter_getter(user_id)
                    ),
                    messages=None,
                    source_count=export_summary.message_count,
                )

        getter = getattr(storage, "get_user_export_rows", None)
        if callable(getter):
            raw_rows = getter(user_id)
            if raw_rows is not None:
                export_rows = [UserExportRow.coerce(row) for row in raw_rows]

    messages = None if export_rows is not None else storage.get_user_messages(user_id)
    if export_summary:
        source_count = export_summary.message_count
    elif export_rows is not None:
        source_count = len(export_rows)
    elif messages is not None:
        source_count = len(messages)
    else:
        source_count = 0

    if source_count <= 0:
        return None

    return DBExportSource(
        export_summary=export_summary,
        export_rows=export_rows,
        export_row_iter_factory=None,
        messages=messages,
        source_count=source_count,
    )


def load_incremental_export_source(
    storage: object,
    *,
    user_id: int,
    last_exported_message_ts: int,
    last_exported_message_id: int,
    as_json: bool,
    json_profile: str,
) -> Optional[DBExportSource]:
    export_summary = None
    export_rows = None
    if as_json and json_profile == "ai":
        summary_getter = getattr(storage, "get_user_export_summary_since", None)
        iter_getter = getattr(storage, "iter_user_export_rows_since", None)
        if callable(summary_getter):
            export_summary = UserExportSummary.coerce(
                summary_getter(
                    user_id,
                    last_exported_message_ts,
                    last_exported_message_id,
                )
            )
            if export_summary and callable(iter_getter):
                return DBExportSource(
                    export_summary=export_summary,
                    export_rows=None,
                    export_row_iter_factory=lambda: (
                        UserExportRow.coerce(row)
                        for row in iter_getter(
                            user_id,
                            last_exported_message_ts,
                            last_exported_message_id,
                        )
                    ),
                    messages=None,
                    source_count=export_summary.message_count,
                )

        getter = getattr(storage, "get_user_export_rows_since", None)
        if callable(getter):
            raw_rows = getter(
                user_id,
                last_exported_message_ts,
                last_exported_message_id,
            )
            if raw_rows is not None:
                export_rows = [UserExportRow.coerce(row) for row in raw_rows]

    if export_summary:
        source_count = export_summary.message_count
    elif export_rows is not None:
        source_count = len(export_rows)
    else:
        messages = []
        for message in storage.get_user_messages(user_id):
            message_ts = int(message.timestamp.timestamp())
            if message_ts > last_exported_message_ts or (
                message_ts == last_exported_message_ts
                and message.message_id > last_exported_message_id
            ):
                messages.append(message)
        source_count = len(messages)
        if source_count <= 0:
            return None
        return DBExportSource(
            export_summary=None,
            export_rows=None,
            export_row_iter_factory=None,
            messages=messages,
            source_count=source_count,
        )

    if source_count <= 0:
        return None

    return DBExportSource(
        export_summary=export_summary,
        export_rows=export_rows,
        export_row_iter_factory=None,
        messages=None,
        source_count=source_count,
    )


def prepare_export_plan(
    storage: object,
    *,
    user_id: int,
    output_dir: str,
    source: DBExportSource,
    as_json: bool,
    include_date: bool,
    json_profile: str,
    txt_profile: str = TXT_PROFILE_LEGACY,
) -> DBExportPlan:
    if source.export_summary is not None:
        summary = source.export_summary
        target_author = resolve_export_author_name_from_summary(
            storage, user_id, summary
        )
        fingerprint = {
            "user_id": user_id,
            "message_count": summary.message_count,
            "first_message_id": summary.first_message_id,
            "last_message_id": summary.last_message_id,
            "first_timestamp": summary.first_timestamp,
            "last_timestamp": summary.last_timestamp,
            "as_json": as_json,
            "include_date": include_date,
            "json_profile": json_profile,
            "txt_profile": None if as_json else txt_profile,
        }
    elif source.export_rows is not None:
        target_author = resolve_export_author_name_from_rows(
            storage, user_id, source.export_rows
        )
        fingerprint = {
            "user_id": user_id,
            "message_count": len(source.export_rows),
            "first_message_id": source.export_rows[0]["message_id"],
            "last_message_id": source.export_rows[-1]["message_id"],
            "first_timestamp": source.export_rows[0]["timestamp"],
            "last_timestamp": source.export_rows[-1]["timestamp"],
            "as_json": as_json,
            "include_date": include_date,
            "json_profile": json_profile,
            "txt_profile": None if as_json else txt_profile,
        }
    else:
        messages = list(source.messages or [])
        messages.sort(key=lambda message: (message.timestamp, message.message_id))
        target_author = resolve_export_author_name(storage, user_id, messages)
        fingerprint = build_export_fingerprint(
            user_id,
            messages,
            as_json=as_json,
            include_date=include_date,
            json_profile=json_profile,
            txt_profile=txt_profile,
        )

    safe_name = re.sub(r"[^\w\s-]", "", target_author).strip()
    safe_name = re.sub(r"[-\s]+", "_", safe_name)
    date_suffix = f"_date({datetime.now().strftime('%m-%d')})" if include_date else ""
    ext = ".jsonl" if as_json else ".txt"
    filename = f"{safe_name}_{user_id}{date_suffix}{ext}"
    return DBExportPlan(
        target_author=target_author,
        output_path=f"{output_dir}/{filename}",
        ext=ext,
        fingerprint=fingerprint,
    )
