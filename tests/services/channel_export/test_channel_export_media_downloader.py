import hashlib
import tempfile
import unittest
from pathlib import Path

from tg_msg_manager.services.channel_export.media_downloader import (
    ChannelMediaDownloader,
    compute_file_sha256,
)
from tg_msg_manager.services.channel_export.models import ChannelMediaRecord


class FakeDownloaderClient:
    def __init__(self, *, content="hello", fail=False, return_none=False):
        self.content = content
        self.fail = fail
        self.return_none = return_none
        self.calls = []

    async def download_media(self, media, file=None):
        self.calls.append((media, file))
        if self.fail:
            raise RuntimeError("boom")
        if self.return_none:
            return None
        path = Path(file)
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(self.content, bytes):
            path.write_bytes(self.content)
        else:
            path.write_text(self.content, encoding="utf-8")
        return str(path)


def make_record(**overrides):
    payload = {
        "media_id": "1_01",
        "message_id": 1,
        "media_index": 1,
        "media_type": "photo",
        "mime_type": "image/jpeg",
        "file_name": "a.jpg",
        "file_size": 10,
        "width": 10,
        "height": 10,
        "duration": None,
        "local_path": "media/photos/0000000001_01.jpg",
        "sha256": None,
        "download_status": "pending",
        "error": None,
    }
    payload.update(overrides)
    return ChannelMediaRecord(**payload)


class TestChannelMediaDownloader(unittest.IsolatedAsyncioTestCase):
    async def test_download_saves_file_and_sha256(self):
        client = FakeDownloaderClient(content="hello")
        downloader = ChannelMediaDownloader(client)

        with tempfile.TemporaryDirectory(prefix="tg_channel_downloader_") as tmpdir:
            record = await downloader.download(
                record=make_record(),
                media_ref={"content": "hello"},
                output_dir=Path(tmpdir),
                max_media_size=None,
                allowed_media_types=None,
            )

            self.assertEqual(record.download_status, "downloaded")
            self.assertEqual(
                record.sha256,
                hashlib.sha256(b"hello").hexdigest(),
            )
            self.assertEqual(record.final_path, "media/photos/0000000001_01.jpg")

    async def test_download_marks_existing_file_without_redownload(self):
        client = FakeDownloaderClient(content="fresh")
        downloader = ChannelMediaDownloader(client)

        with tempfile.TemporaryDirectory(
            prefix="tg_channel_downloader_existing_"
        ) as tmpdir:
            existing_path = Path(tmpdir) / "media/photos/0000000001_01.jpg"
            existing_path.parent.mkdir(parents=True, exist_ok=True)
            existing_path.write_text("existing", encoding="utf-8")

            record = await downloader.download(
                record=make_record(),
                media_ref={"content": "fresh"},
                output_dir=Path(tmpdir),
                max_media_size=None,
                allowed_media_types=None,
            )

            self.assertEqual(record.download_status, "already_exists")
            self.assertEqual(record.sha256, compute_file_sha256(existing_path))
            self.assertEqual(client.calls, [])

    async def test_download_marks_existing_mime_resolved_mp4_without_redownload(self):
        client = FakeDownloaderClient(content=b"fresh")
        downloader = ChannelMediaDownloader(client)

        with tempfile.TemporaryDirectory(
            prefix="tg_channel_downloader_existing_mp4_"
        ) as tmpdir:
            existing_path = Path(tmpdir) / "media/videos/0000058947_01.mp4"
            existing_path.parent.mkdir(parents=True, exist_ok=True)
            existing_path.write_bytes(b"existing mp4")

            record = await downloader.download(
                record=make_record(
                    message_id=58947,
                    media_id="58947_01",
                    media_type="video",
                    mime_type="video/mp4",
                    file_name=None,
                    local_path="media/videos/0000058947_01.mp4",
                    detected_extension=".mp4",
                    filename_strategy="mime_type",
                    final_filename="0000058947_01.mp4",
                    final_path="media/videos/0000058947_01.mp4",
                ),
                media_ref={"content": "fresh"},
                output_dir=Path(tmpdir),
                max_media_size=None,
                allowed_media_types=None,
            )

            self.assertEqual(record.download_status, "already_exists")
            self.assertEqual(record.local_path, "media/videos/0000058947_01.mp4")
            self.assertEqual(record.sha256, compute_file_sha256(existing_path))
            self.assertEqual(client.calls, [])

    async def test_download_renames_generic_mp4_magic_bytes_to_final_mp4(self):
        content = b"\x00\x00\x00\x18ftypisom\x00\x00\x00\x00payload"
        client = FakeDownloaderClient(content=content)
        downloader = ChannelMediaDownloader(client)

        with tempfile.TemporaryDirectory(prefix="tg_channel_downloader_mp4_") as tmpdir:
            record = await downloader.download(
                record=make_record(
                    message_id=58947,
                    media_id="58947_01",
                    media_type="document",
                    mime_type="application/octet-stream",
                    file_name=None,
                    local_path="media/documents/0000058947_01.bin",
                    detected_extension=".bin",
                    filename_strategy="fallback_bin",
                    final_filename="0000058947_01.bin",
                    final_path="media/documents/0000058947_01.bin",
                ),
                media_ref={"content": content},
                output_dir=Path(tmpdir),
                max_media_size=None,
                allowed_media_types=None,
            )

            final_path = Path(tmpdir) / "media/videos/0000058947_01.mp4"
            old_path = Path(tmpdir) / "media/documents/0000058947_01.bin"
            self.assertEqual(record.download_status, "downloaded")
            self.assertEqual(record.local_path, "media/videos/0000058947_01.mp4")
            self.assertEqual(record.final_path, "media/videos/0000058947_01.mp4")
            self.assertEqual(record.detected_extension, ".mp4")
            self.assertEqual(record.filename_strategy, "magic_bytes")
            self.assertTrue(final_path.exists())
            self.assertFalse(old_path.exists())
            self.assertEqual(record.sha256, hashlib.sha256(content).hexdigest())

    async def test_download_renames_generic_quicktime_magic_bytes_to_final_mov(self):
        content = b"\x00\x00\x00\x14ftypqt  \x00\x00\x00\x00payload"
        client = FakeDownloaderClient(content=content)
        downloader = ChannelMediaDownloader(client)

        with tempfile.TemporaryDirectory(prefix="tg_channel_downloader_mov_") as tmpdir:
            record = await downloader.download(
                record=make_record(
                    message_id=58991,
                    media_id="58991_01",
                    media_type="document",
                    mime_type="application/octet-stream",
                    file_name=None,
                    local_path="media/documents/0000058991_01.bin",
                    detected_extension=".bin",
                    filename_strategy="fallback_bin",
                    final_filename="0000058991_01.bin",
                    final_path="media/documents/0000058991_01.bin",
                ),
                media_ref={"content": content},
                output_dir=Path(tmpdir),
                max_media_size=None,
                allowed_media_types=None,
            )

            self.assertEqual(record.download_status, "downloaded")
            self.assertEqual(record.local_path, "media/videos/0000058991_01.mov")
            self.assertTrue((Path(tmpdir) / "media/videos/0000058991_01.mov").exists())
            self.assertFalse(
                (Path(tmpdir) / "media/documents/0000058991_01.bin").exists()
            )

    async def test_download_keeps_unknown_content_as_bin(self):
        content = b"unknown payload"
        client = FakeDownloaderClient(content=content)
        downloader = ChannelMediaDownloader(client)

        with tempfile.TemporaryDirectory(
            prefix="tg_channel_downloader_unknown_"
        ) as tmpdir:
            record = await downloader.download(
                record=make_record(
                    media_type="document",
                    mime_type="application/octet-stream",
                    file_name=None,
                    local_path="media/documents/0000000001_01.bin",
                    detected_extension=".bin",
                    filename_strategy="fallback_bin",
                    final_filename="0000000001_01.bin",
                    final_path="media/documents/0000000001_01.bin",
                ),
                media_ref={"content": content},
                output_dir=Path(tmpdir),
                max_media_size=None,
                allowed_media_types=None,
            )

            self.assertEqual(record.download_status, "downloaded")
            self.assertEqual(record.local_path, "media/documents/0000000001_01.bin")
            self.assertTrue(
                (Path(tmpdir) / "media/documents/0000000001_01.bin").exists()
            )

    async def test_download_respects_size_and_type_policy(self):
        client = FakeDownloaderClient()
        downloader = ChannelMediaDownloader(client)

        with tempfile.TemporaryDirectory(
            prefix="tg_channel_downloader_policy_"
        ) as tmpdir:
            skipped_by_size = await downloader.download(
                record=make_record(file_size=2048),
                media_ref={"content": "hello"},
                output_dir=Path(tmpdir),
                max_media_size=1024,
                allowed_media_types=None,
            )
            skipped_by_type = await downloader.download(
                record=make_record(media_type="document", mime_type="application/pdf"),
                media_ref={"content": "hello"},
                output_dir=Path(tmpdir),
                max_media_size=None,
                allowed_media_types=("photo",),
            )

            self.assertEqual(skipped_by_size.download_status, "skipped_by_size")
            self.assertEqual(skipped_by_type.download_status, "skipped_by_type")
            self.assertEqual(client.calls, [])

    async def test_download_failure_returns_failed_status(self):
        client = FakeDownloaderClient(fail=True)
        downloader = ChannelMediaDownloader(client)

        with tempfile.TemporaryDirectory(
            prefix="tg_channel_downloader_fail_"
        ) as tmpdir:
            record = await downloader.download(
                record=make_record(),
                media_ref={"content": "hello"},
                output_dir=Path(tmpdir),
                max_media_size=None,
                allowed_media_types=None,
            )

            self.assertEqual(record.download_status, "failed")
            self.assertEqual(record.error, "boom")
