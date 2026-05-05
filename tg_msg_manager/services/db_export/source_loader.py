from typing import Optional

from .summary import DBExportSource, load_export_source, load_incremental_export_source


class DBExportSourceLoader:
    def __init__(self, storage: object):
        self.storage = storage

    def load_full_source(
        self,
        *,
        user_id: int,
        as_json: bool,
        json_profile: str,
    ) -> Optional[DBExportSource]:
        return load_export_source(
            self.storage,
            user_id=user_id,
            as_json=as_json,
            json_profile=json_profile,
        )

    def load_incremental_source(
        self,
        *,
        user_id: int,
        last_exported_message_ts: int,
        last_exported_message_id: int,
        as_json: bool,
        json_profile: str,
    ) -> Optional[DBExportSource]:
        return load_incremental_export_source(
            self.storage,
            user_id=user_id,
            last_exported_message_ts=last_exported_message_ts,
            last_exported_message_id=last_exported_message_id,
            as_json=as_json,
            json_profile=json_profile,
        )
