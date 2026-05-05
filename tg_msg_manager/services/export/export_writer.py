from typing import Optional

from ..db_exporter import DBExportService


class ExportArtifactWriter:
    """
    Dedicated boundary for DB-backed export artifact writes.

    Stage 0 keeps file-format behavior inside DBExportService but exposes the
    boundary through a focused adapter module so future export work does not
    grow the sync orchestrator again.
    """

    def __init__(self, service: DBExportService):
        self.service = service

    async def export_user_messages(
        self,
        user_id: int,
        *,
        as_json: bool = False,
        include_date: bool = True,
        output_path: Optional[str] = None,
    ) -> Optional[str]:
        return await self.service.export_user_messages(
            user_id,
            as_json=as_json,
            include_date=include_date,
            output_path=output_path,
        )
