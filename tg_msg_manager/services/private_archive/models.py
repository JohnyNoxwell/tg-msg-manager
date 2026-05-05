from dataclasses import dataclass


@dataclass(frozen=True)
class ArchiveContext:
    user_id: int
    target_name: str
    user_dir: str
    media_dir: str
    chat_log_path: str
