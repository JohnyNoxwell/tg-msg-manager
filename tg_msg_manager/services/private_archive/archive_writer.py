import os

from ...core.models.message import MessageData
from ..file_writer import FileRotateWriter


class PrivateArchiveWriter:
    def ensure_archive_dirs(self, media_dir: str) -> None:
        for sub in ("photos", "videos", "voices", "documents"):
            os.makedirs(os.path.join(media_dir, sub), exist_ok=True)

    def create_log_writer(self, chat_log_path: str) -> FileRotateWriter:
        return FileRotateWriter(chat_log_path, as_json=False, max_msgs=5000)

    async def append_message(
        self, writer: FileRotateWriter, message: MessageData
    ) -> None:
        await writer.write_block(
            self.format_pm_log(message) + "\n\n" + "-" * 40 + "\n\n", 1
        )

    def format_pm_log(self, message: MessageData) -> str:
        dt_str = message.timestamp.strftime("%Y-%m-%d][%H:%M")
        author = message.author_name or f"User_{message.user_id}"
        header = f"[{dt_str}] <{author}> (ID: {message.user_id}):"
        media_note = f" <Attached {message.media_type}>" if message.media_type else ""
        return f"{header}{media_note}\n{message.text or '(empty)'}"
