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
