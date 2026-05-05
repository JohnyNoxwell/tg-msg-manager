from ...core.models.message import MessageData
from ...infrastructure.storage.records import UserExportRow
from .jsonl_writer import serialize_json_message, serialize_row_as_ai_jsonl


class DBExportJsonlRenderer:
    def render_message(self, message: MessageData, *, profile: str = "ai") -> str:
        return serialize_json_message(message, profile=profile)

    def render_row(self, row: UserExportRow) -> str:
        return serialize_row_as_ai_jsonl(row)
