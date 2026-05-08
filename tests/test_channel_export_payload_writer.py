import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from tg_msg_manager.services.channel_export.jsonl_renderer import ChannelJsonlRenderer
from tg_msg_manager.services.channel_export.media_manifest_writer import (
    ChannelMediaManifestWriter,
)
from tg_msg_manager.services.channel_export.models import (
    CHANNEL_EXPORT_RUN_MODE_FULL,
    CHANNEL_EXPORT_RUN_MODE_INCREMENTAL,
    ChannelExportPlan,
    ChannelMediaRecord,
    ChannelPostRecord,
)
from tg_msg_manager.services.channel_export.payload_writer import (
    WRITE_MODE_APPEND,
    ChannelPayloadWriter,
)
from tg_msg_manager.services.channel_export.txt_renderer import ChannelTxtRenderer


def make_post(*, message_id, text, timestamp, media=()):
    return ChannelPostRecord(
        message_id=message_id,
        channel_id=7,
        channel_title="Updates",
        channel_username="updates",
        timestamp=timestamp,
        text=text,
        views=None,
        forwards=None,
        replies_count=None,
        reactions={},
        media=media,
        raw_payload={},
    )


class TestChannelPayloadWriter(unittest.TestCase):
    def _build_plan(self, tmpdir: str) -> ChannelExportPlan:
        output_dir = Path(tmpdir) / "channel"
        return ChannelExportPlan(
            output_dir=output_dir,
            manifest_path=output_dir / "manifest.json",
            messages_jsonl_path=output_dir / "messages.jsonl",
            messages_txt_path=output_dir / "messages.txt",
            media_manifest_path=output_dir / "media_manifest.jsonl",
            state_path=output_dir / "channel_export_state.json",
            media_dir=output_dir / "media",
        )

    def _media_record(self) -> ChannelMediaRecord:
        return ChannelMediaRecord(
            media_id="1_01",
            message_id=1,
            media_index=1,
            media_type="photo",
            mime_type="image/jpeg",
            file_name="a.jpg",
            file_size=10,
            width=100,
            height=50,
            duration=None,
            local_path="media/photos/0000000001_01.jpg",
            sha256=None,
            download_status="metadata_only",
            error=None,
        )

    def test_write_session_writes_files_and_counts_messages_and_media(self):
        with tempfile.TemporaryDirectory(prefix="tg_channel_writer_") as tmpdir:
            plan = self._build_plan(tmpdir)
            progress_events = []
            session = ChannelPayloadWriter().open_session(
                plan=plan,
                jsonl_renderer=ChannelJsonlRenderer(),
                txt_renderer=ChannelTxtRenderer(),
                media_manifest_writer=ChannelMediaManifestWriter(),
                run_mode=CHANNEL_EXPORT_RUN_MODE_FULL,
                progress_callback=progress_events.append,
                progress_interval=1,
            )

            with session:
                session.write_record(
                    make_post(
                        message_id=1,
                        text="Привіт",
                        timestamp=datetime(2026, 5, 7, 10, 0, tzinfo=timezone.utc),
                        media=(self._media_record(),),
                    )
                )
                session.write_record(
                    make_post(
                        message_id=2,
                        text="World",
                        timestamp=datetime(2026, 5, 7, 11, 0, tzinfo=timezone.utc),
                    )
                )
                stats = session.finish()

            self.assertEqual(stats.posts_exported, 2)
            self.assertEqual(stats.media_records_added, 1)
            self.assertEqual(stats.already_existing_media_count, 0)
            self.assertEqual(stats.failed_media_count, 0)
            self.assertEqual(stats.date_from.isoformat(), "2026-05-07T10:00:00+00:00")
            self.assertEqual(stats.date_to.isoformat(), "2026-05-07T11:00:00+00:00")
            jsonl_lines = plan.messages_jsonl_path.read_text(
                encoding="utf-8"
            ).splitlines()
            self.assertEqual(len(jsonl_lines), 2)
            self.assertEqual(json.loads(jsonl_lines[0])["text"], "Привіт")
            self.assertIn("Привіт", plan.messages_txt_path.read_text(encoding="utf-8"))
            self.assertEqual(
                len(plan.media_manifest_path.read_text(encoding="utf-8").splitlines()),
                1,
            )
            self.assertEqual(progress_events[-1]["processed_posts"], 2)

    def test_write_session_append_mode_appends_without_overwriting(self):
        with tempfile.TemporaryDirectory(prefix="tg_channel_writer_append_") as tmpdir:
            plan = self._build_plan(tmpdir)
            writer = ChannelPayloadWriter()

            with writer.open_session(
                plan=plan,
                jsonl_renderer=ChannelJsonlRenderer(),
                txt_renderer=ChannelTxtRenderer(),
                media_manifest_writer=ChannelMediaManifestWriter(),
                run_mode=CHANNEL_EXPORT_RUN_MODE_FULL,
            ) as session:
                session.write_record(
                    make_post(
                        message_id=1,
                        text="First",
                        timestamp=datetime(2026, 5, 7, 10, 0, tzinfo=timezone.utc),
                    )
                )
                session.finish()

            with writer.open_session(
                plan=plan,
                jsonl_renderer=ChannelJsonlRenderer(),
                txt_renderer=ChannelTxtRenderer(),
                media_manifest_writer=ChannelMediaManifestWriter(),
                run_mode=CHANNEL_EXPORT_RUN_MODE_INCREMENTAL,
                write_mode=WRITE_MODE_APPEND,
            ) as session:
                session.write_record(
                    make_post(
                        message_id=2,
                        text="Second",
                        timestamp=datetime(2026, 5, 7, 11, 0, tzinfo=timezone.utc),
                    )
                )
                session.finish()

            jsonl_lines = plan.messages_jsonl_path.read_text(
                encoding="utf-8"
            ).splitlines()
            txt_content = plan.messages_txt_path.read_text(encoding="utf-8")
            self.assertEqual(len(jsonl_lines), 2)
            self.assertEqual(json.loads(jsonl_lines[0])["message_id"], 1)
            self.assertEqual(json.loads(jsonl_lines[1])["message_id"], 2)
            self.assertIn("message_id=1", txt_content)
            self.assertIn("message_id=2", txt_content)

    def test_write_session_handles_empty_channel_and_creates_files(self):
        with tempfile.TemporaryDirectory(prefix="tg_channel_writer_empty_") as tmpdir:
            plan = self._build_plan(tmpdir)

            with ChannelPayloadWriter().open_session(
                plan=plan,
                jsonl_renderer=ChannelJsonlRenderer(),
                txt_renderer=ChannelTxtRenderer(),
                media_manifest_writer=ChannelMediaManifestWriter(),
                run_mode=CHANNEL_EXPORT_RUN_MODE_FULL,
            ) as session:
                stats = session.finish()

            self.assertEqual(stats.posts_exported, 0)
            self.assertEqual(plan.messages_jsonl_path.read_text(encoding="utf-8"), "")
            self.assertEqual(plan.messages_txt_path.read_text(encoding="utf-8"), "")
            self.assertEqual(plan.media_manifest_path.read_text(encoding="utf-8"), "")

    def test_write_session_tracks_media_status_counters(self):
        downloaded = ChannelMediaRecord(
            **{**self._media_record().__dict__, "download_status": "downloaded"}
        )
        already_exists = ChannelMediaRecord(
            **{
                **downloaded.__dict__,
                "media_id": "2_01",
                "download_status": "already_exists",
            }
        )
        skipped_by_size = ChannelMediaRecord(
            **{
                **downloaded.__dict__,
                "media_id": "3_01",
                "download_status": "skipped_by_size",
            }
        )
        failed = ChannelMediaRecord(
            **{
                **downloaded.__dict__,
                "media_id": "4_01",
                "download_status": "failed",
                "error": "boom",
            }
        )

        with tempfile.TemporaryDirectory(prefix="tg_channel_writer_status_") as tmpdir:
            plan = self._build_plan(tmpdir)
            with ChannelPayloadWriter().open_session(
                plan=plan,
                jsonl_renderer=ChannelJsonlRenderer(),
                txt_renderer=ChannelTxtRenderer(),
                media_manifest_writer=ChannelMediaManifestWriter(),
                run_mode=CHANNEL_EXPORT_RUN_MODE_FULL,
            ) as session:
                session.write_record(
                    make_post(
                        message_id=1,
                        text="Hello",
                        timestamp=datetime(2026, 5, 7, 10, 0, tzinfo=timezone.utc),
                        media=(downloaded, already_exists, skipped_by_size, failed),
                    )
                )
                stats = session.finish()

            self.assertEqual(stats.downloaded_media_count, 1)
            self.assertEqual(stats.already_existing_media_count, 1)
            self.assertEqual(stats.skipped_by_size_count, 1)
            self.assertEqual(stats.failed_media_count, 1)


if __name__ == "__main__":
    unittest.main()
