import json
import os
from typing import Any, Dict, List, Optional

from ...core.models.message import MessageData


def manifest_dir(output_dir: str) -> str:
    return os.path.join(output_dir, ".export_state")


def manifest_path(output_dir: str, user_id: int) -> str:
    return os.path.join(manifest_dir(output_dir), f"{user_id}.json")


def build_export_fingerprint(
    user_id: int,
    messages: List[MessageData],
    *,
    as_json: bool,
    include_date: bool,
    json_profile: str,
) -> Dict[str, Any]:
    first = messages[0]
    last = messages[-1]
    return {
        "user_id": user_id,
        "message_count": len(messages),
        "first_message_id": first.message_id,
        "last_message_id": last.message_id,
        "first_timestamp": int(first.timestamp.timestamp()),
        "last_timestamp": int(last.timestamp.timestamp()),
        "as_json": as_json,
        "include_date": include_date,
        "json_profile": json_profile,
    }


def load_export_manifest(output_dir: str, user_id: int) -> Optional[Dict[str, Any]]:
    path = manifest_path(output_dir, user_id)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        return loaded if isinstance(loaded, dict) else None
    except Exception:
        return None


def expected_export_paths(output_path: str, part_count: int) -> List[str]:
    if part_count <= 1:
        return [output_path]
    root, ext = os.path.splitext(output_path)
    paths = [output_path]
    for part in range(2, part_count + 1):
        paths.append(f"{root}_part{part}{ext}")
    return paths
