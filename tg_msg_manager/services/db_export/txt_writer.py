from typing import Any, Dict, Optional

from ...core.models.message import MessageData
from ..rendering import format_legacy_txt_export_block


def format_txt_export_block(
    *,
    message: MessageData,
    msg_lookup: Dict[int, MessageData],
    last_date: Any,
    last_author_id: Optional[int],
) -> tuple[str, Any, Optional[int]]:
    return format_legacy_txt_export_block(
        message=message,
        msg_lookup=msg_lookup,
        last_date=last_date,
        last_author_id=last_author_id,
    )
