from typing import Optional

from ..db_export import DBExportService


class ExportArtifactWriter:
    """
    Dedicated boundary for DB-backed export artifact writes.

    File-format behavior stays inside DBExportService while the sync/export
    orchestration depends on a focused adapter boundary.
    """

    def __init__(self, service: DBExportService):
        self.service = service

    async def export_user_messages(
        self,
        user_id: int,
        *,
        as_json: bool = False,
        include_date: bool = True,
        output_dir: Optional[str] = None,
        txt_profile: Optional[str] = None,
    ) -> Optional[str]:
        kwargs = {
            "as_json": as_json,
            "include_date": include_date,
            "output_dir": output_dir,
        }
        if txt_profile is not None:
            kwargs["txt_profile"] = txt_profile
        return await self.service.export_user_messages(user_id, **kwargs)
