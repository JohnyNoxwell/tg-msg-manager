from typing import List

from ...core.models.message import MessageData
from ...infrastructure.storage.records import UserExportRow
from ..rendering.txt_profiles import TXT_PROFILE_LEGACY
from .summary import (
    DBExportPlan,
    DBExportSource,
    prepare_export_plan,
    resolve_export_author_name,
    resolve_export_author_name_from_rows,
)


class DBExportPlanBuilder:
    def __init__(self, storage: object):
        self.storage = storage

    def prepare_plan(
        self,
        *,
        user_id: int,
        output_dir: str,
        source: DBExportSource,
        as_json: bool,
        include_date: bool,
        json_profile: str,
        txt_profile: str = TXT_PROFILE_LEGACY,
    ) -> DBExportPlan:
        return prepare_export_plan(
            self.storage,
            user_id=user_id,
            output_dir=output_dir,
            source=source,
            as_json=as_json,
            include_date=include_date,
            json_profile=json_profile,
            txt_profile=txt_profile,
        )

    def resolve_author_name(self, user_id: int, messages: List[MessageData]) -> str:
        return resolve_export_author_name(self.storage, user_id, messages)

    def resolve_author_name_from_rows(
        self, user_id: int, rows: List[UserExportRow]
    ) -> str:
        return resolve_export_author_name_from_rows(self.storage, user_id, rows)
