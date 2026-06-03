import json
from typing import Optional

from .models import TARGET_NAME_FIELDS, TargetNamesResult


def render_target_names_text(result: TargetNamesResult, *, field: str = "all") -> str:
    lines = [
        f"Target: {result.target}",
        f"Type: {result.target_type}",
        "",
    ]
    if result.current and field == "all":
        current_lines = _render_current_lines(result)
        if current_lines:
            lines.append("Current:")
            lines.extend(current_lines)
            lines.append("")

    lines.append(f"{_history_title(field)}:")
    history = [
        item
        for item in result.history
        if field == "all" or item.field == field
    ]
    if not history:
        lines.append("  No changes recorded.")
        return "\n".join(lines)

    for item in history:
        if field == "all":
            lines.append(
                "  "
                f"{item.observed_at}  {item.field:<12}  "
                f"{_display_value(item.old_value, item.field):<16} -> "
                f"{_display_value(item.new_value, item.field)}"
            )
        else:
            lines.append(
                "  "
                f"{item.observed_at}  "
                f"{_display_value(item.old_value, item.field):<16} -> "
                f"{_display_value(item.new_value, item.field)}"
            )
    return "\n".join(lines)


def render_target_names_json(result: TargetNamesResult, *, field: str = "all") -> str:
    fields = TARGET_NAME_FIELDS if field == "all" else (field,)
    payload = {
        "target": result.target,
        "target_type": result.target_type,
        "current": _current_payload(result, fields),
        "history": [
            {
                "observed_at": item.observed_at,
                "field": item.field,
                "old_value": _json_value(item.old_value, item.field),
                "new_value": _json_value(item.new_value, item.field),
            }
            for item in result.history
            if field == "all" or item.field == field
        ],
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=False)


def render_target_names_error(
    *, code: str, target: str, json_output: bool = False
) -> str:
    if code == "ambiguous_target":
        message = "Target matches more than one local record."
        text = f"Error: target is ambiguous in local metadata: {target}"
    else:
        code = "target_not_found"
        message = "Target not found in local metadata."
        text = f"Error: target not found in local metadata: {target}"

    if not json_output:
        return text
    return json.dumps(
        {
            "error": {
                "code": code,
                "message": message,
                "target": target,
            }
        },
        ensure_ascii=False,
        sort_keys=False,
    )


def _render_current_lines(result: TargetNamesResult) -> list[str]:
    if result.current is None:
        return []
    lines = []
    for field in TARGET_NAME_FIELDS:
        value = getattr(result.current, field)
        if value is not None:
            lines.append(f"  {field}: {_display_value(value, field)}")
    if result.current.first_seen is not None:
        lines.append(f"  first_seen: {result.current.first_seen}")
    if result.current.last_seen is not None:
        lines.append(f"  last_seen: {result.current.last_seen}")
    return lines


def _current_payload(result: TargetNamesResult, fields: tuple[str, ...]) -> dict:
    if result.current is None:
        return {}
    return {
        field: _json_value(getattr(result.current, field), field)
        for field in fields
    }


def _history_title(field: str) -> str:
    if field == "username":
        return "Username history"
    if field == "display_name":
        return "Display name history"
    if field == "title":
        return "Title history"
    return "Name history"


def _display_value(value: Optional[str], field: str) -> str:
    if value is None:
        return "-"
    if field == "username":
        return _format_username(value) or "-"
    return value


def _json_value(value: Optional[str], field: str):
    if value is None:
        return None
    if field == "username":
        return _format_username(value)
    return value


def _format_username(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if text.startswith("@"):
        return text
    return f"@{text}"
