import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from tg_msg_manager.services.channel_export.errors import ChannelExportStateError
from tg_msg_manager.services.channel_export.models import (
    CHANNEL_EXPORT_RUN_MODE_FORCE_FULL,
    CHANNEL_EXPORT_RUN_MODE_FULL,
    CHANNEL_EXPORT_RUN_MODE_INCREMENTAL,
    ChannelExportState,
    ChannelIdentity,
)
from tg_msg_manager.services.channel_export.state_manager import (
    ChannelExportStateManager,
)


class TestChannelExportStateManager(unittest.TestCase):
    def setUp(self):
        self.manager = ChannelExportStateManager()
        self.channel = ChannelIdentity(
            channel_id=123,
            title="Daily",
            username="daily",
        )

    def _state(self) -> ChannelExportState:
        now = datetime(2026, 5, 7, 12, 0, tzinfo=timezone.utc)
        return ChannelExportState(
            schema_version="1.0",
            channel_id=123,
            channel_username="daily",
            channel_title="Daily",
            last_exported_message_id=77,
            last_exported_at=now,
            message_count_total=10,
            media_count_total=3,
            downloaded_media_count_total=0,
            already_existing_media_count_total=0,
            skipped_media_count_total=0,
            skipped_by_size_count_total=0,
            skipped_by_type_count_total=0,
            failed_media_count_total=0,
            last_run_status="completed",
            updated_at=now,
            date_from=now,
            date_to=now,
            last_manifest_path="manifest.json",
        )

    def test_load_missing_state_returns_none(self):
        with tempfile.TemporaryDirectory(prefix="tg_channel_state_missing_") as tmpdir:
            self.assertIsNone(self.manager.load(Path(tmpdir) / "missing.json"))

    def test_save_then_load_round_trip(self):
        with tempfile.TemporaryDirectory(
            prefix="tg_channel_state_roundtrip_"
        ) as tmpdir:
            path = Path(tmpdir) / "channel_export_state.json"
            self.manager.save(path, self._state())

            loaded = self.manager.load(path)

            self.assertEqual(loaded, self._state())

    def test_validate_state_for_channel_rejects_channel_id_mismatch(self):
        state = self._state()

        with self.assertRaises(ChannelExportStateError):
            self.manager.validate_state_for_channel(
                state,
                ChannelIdentity(channel_id=999, title="Other", username="other"),
            )

    def test_determine_run_mode_respects_force_and_existing_state(self):
        self.assertEqual(
            self.manager.determine_run_mode(self._state(), force=True),
            CHANNEL_EXPORT_RUN_MODE_FORCE_FULL,
        )
        self.assertEqual(
            self.manager.determine_run_mode(self._state(), force=False),
            CHANNEL_EXPORT_RUN_MODE_INCREMENTAL,
        )
        self.assertEqual(
            self.manager.determine_run_mode(None, force=False),
            CHANNEL_EXPORT_RUN_MODE_FULL,
        )

    def test_determine_run_mode_without_last_message_id_falls_back_to_full(self):
        state = self._state()
        state = ChannelExportState(
            schema_version=state.schema_version,
            channel_id=state.channel_id,
            channel_username=state.channel_username,
            channel_title=state.channel_title,
            last_exported_message_id=None,
            last_exported_at=state.last_exported_at,
            message_count_total=state.message_count_total,
            media_count_total=state.media_count_total,
            downloaded_media_count_total=state.downloaded_media_count_total,
            already_existing_media_count_total=state.already_existing_media_count_total,
            skipped_media_count_total=state.skipped_media_count_total,
            skipped_by_size_count_total=state.skipped_by_size_count_total,
            skipped_by_type_count_total=state.skipped_by_type_count_total,
            failed_media_count_total=state.failed_media_count_total,
            last_run_status=state.last_run_status,
            updated_at=state.updated_at,
            date_from=state.date_from,
            date_to=state.date_to,
            last_manifest_path=state.last_manifest_path,
        )

        self.assertEqual(
            self.manager.determine_run_mode(state, force=False),
            CHANNEL_EXPORT_RUN_MODE_FULL,
        )

    def test_corrupt_json_raises_clear_error(self):
        with tempfile.TemporaryDirectory(prefix="tg_channel_state_corrupt_") as tmpdir:
            path = Path(tmpdir) / "channel_export_state.json"
            path.write_text("{not-json", encoding="utf-8")

            with self.assertRaises(ChannelExportStateError):
                self.manager.load(path)

    def test_missing_optional_fields_are_tolerated(self):
        with tempfile.TemporaryDirectory(prefix="tg_channel_state_optional_") as tmpdir:
            path = Path(tmpdir) / "channel_export_state.json"
            path.write_text(
                (
                    '{"channel_id": 123, "message_count_total": 1, '
                    '"media_count_total": 0, "last_run_status": "completed", '
                    '"updated_at": "2026-05-07T12:00:00+00:00"}'
                ),
                encoding="utf-8",
            )

            loaded = self.manager.load(path)

            self.assertEqual(loaded.channel_id, 123)
            self.assertIsNone(loaded.channel_username)
            self.assertEqual(loaded.downloaded_media_count_total, 0)


if __name__ == "__main__":
    unittest.main()
