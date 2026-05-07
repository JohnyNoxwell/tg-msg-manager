from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional, Tuple

from .jsonl_renderer import ChannelJsonlRenderer
from .media_manifest_writer import ChannelMediaManifestWriter
from .models import ChannelExportPlan, ChannelPostRecord
from .txt_renderer import ChannelTxtRenderer


class ChannelPayloadWriter:
    def write_records(
        self,
        *,
        plan: ChannelExportPlan,
        records: Iterable[ChannelPostRecord],
        jsonl_renderer: ChannelJsonlRenderer,
        txt_renderer: ChannelTxtRenderer,
        media_manifest_writer: ChannelMediaManifestWriter,
        include_jsonl: bool = True,
        include_txt: bool = True,
    ) -> Tuple[int, int, Optional[datetime], Optional[datetime]]:
        plan.output_dir.mkdir(parents=True, exist_ok=True)
        jsonl_path = Path(plan.messages_jsonl_path)
        txt_path = Path(plan.messages_txt_path)
        media_manifest_path = Path(plan.media_manifest_path)

        with (
            jsonl_path.open("w", encoding="utf-8") as jsonl_handle,
            txt_path.open("w", encoding="utf-8") as txt_handle,
            media_manifest_path.open("w", encoding="utf-8") as media_handle,
        ):
            message_count = 0
            media_count = 0
            date_from = None
            date_to = None

            for record in records:
                message_count += 1
                if date_from is None or record.timestamp < date_from:
                    date_from = record.timestamp
                if date_to is None or record.timestamp > date_to:
                    date_to = record.timestamp

                if include_jsonl:
                    jsonl_handle.write(jsonl_renderer.render_line(record) + "\n")
                if include_txt:
                    txt_handle.write(txt_renderer.render_block(record) + "\n")
                for media_record in record.media:
                    media_count += 1
                    media_handle.write(
                        media_manifest_writer.render_line(media_record) + "\n"
                    )

            return message_count, media_count, date_from, date_to
