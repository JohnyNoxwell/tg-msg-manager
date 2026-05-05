from ...infrastructure.storage.interface import PrivateArchiveStorage


class PrivateArchiveStateManager:
    def __init__(self, storage: PrivateArchiveStorage):
        self.storage = storage

    def get_last_msg_id(self, user_id: int) -> int:
        return self.storage.get_last_msg_id(user_id)

    def register_target(self, *, user_id: int, target_name: str) -> None:
        self.storage.register_target(user_id, target_name, user_id)

    def mark_synced(self, user_id: int) -> None:
        if hasattr(self.storage, "update_last_sync_at"):
            self.storage.update_last_sync_at(user_id, user_id)
