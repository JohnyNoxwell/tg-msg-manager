import unittest

from tg_msg_manager.services.channel_export.media_filename import (
    FILENAME_STRATEGY_FALLBACK,
    FILENAME_STRATEGY_MAGIC,
    FILENAME_STRATEGY_MIME,
    FILENAME_STRATEGY_ORIGINAL,
    extension_from_magic_bytes,
    resolve_media_filename,
    sanitize_original_filename,
)


class TestChannelExportMediaFilename(unittest.TestCase):
    def test_original_filename_with_extension_is_preserved_safely(self):
        decision = resolve_media_filename(
            message_id=58947,
            media_index=1,
            original_filename="video.MP4",
            mime_type=None,
        )

        self.assertEqual(decision.filename, "0000058947_01_video.mp4")
        self.assertEqual(decision.extension, ".mp4")
        self.assertEqual(decision.strategy, FILENAME_STRATEGY_ORIGINAL)
        self.assertEqual(decision.original_filename, "video.MP4")

    def test_unsafe_filename_is_sanitized_and_path_traversal_is_blocked(self):
        self.assertEqual(sanitize_original_filename("../bad/name.mov"), "bad_name.mov")

        decision = resolve_media_filename(
            message_id=58991,
            media_index=1,
            original_filename="../bad/name.mov",
            mime_type=None,
        )

        self.assertEqual(decision.filename, "0000058991_01_bad_name.mov")
        self.assertNotIn("/", decision.filename)
        self.assertNotIn("..", decision.filename)

    def test_mime_type_resolves_known_video_document_audio_image_extensions(self):
        cases = {
            "video/mp4": ".mp4",
            "video/quicktime": ".mov",
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
            "image/gif": ".gif",
            "application/pdf": ".pdf",
            "audio/mpeg": ".mp3",
            "audio/mp4": ".m4a",
            "audio/ogg": ".ogg",
            "audio/wav": ".wav",
            "application/zip": ".zip",
            "application/x-rar-compressed": ".rar",
            "application/x-7z-compressed": ".7z",
        }

        for mime_type, extension in cases.items():
            with self.subTest(mime_type=mime_type):
                decision = resolve_media_filename(
                    message_id=1,
                    media_index=1,
                    original_filename=None,
                    mime_type=mime_type,
                )
                self.assertEqual(decision.extension, extension)
                self.assertEqual(decision.strategy, FILENAME_STRATEGY_MIME)

    def test_magic_byte_detection_maps_required_signatures(self):
        cases = {
            b"\x00\x00\x00\x18ftypisom\x00\x00\x00\x00": ".mp4",
            b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00": ".mp4",
            b"\x00\x00\x00\x14ftypqt  \x00\x00\x00\x00": ".mov",
            b"\xff\xd8\xff\xe0": ".jpg",
            b"\x89PNG\r\n\x1a\n": ".png",
            b"GIF87a": ".gif",
            b"GIF89a": ".gif",
            b"%PDF-1.7": ".pdf",
            b"PK\x03\x04": ".zip",
        }

        for header, extension in cases.items():
            with self.subTest(extension=extension):
                self.assertEqual(extension_from_magic_bytes(header), extension)

    def test_unknown_bytes_fall_back_to_bin(self):
        self.assertIsNone(extension_from_magic_bytes(b"not a known signature"))

        decision = resolve_media_filename(
            message_id=59036,
            media_index=1,
            original_filename=None,
            mime_type="application/octet-stream",
            header=b"not a known signature",
        )

        self.assertEqual(decision.filename, "0000059036_01.bin")
        self.assertEqual(decision.extension, ".bin")
        self.assertEqual(decision.strategy, FILENAME_STRATEGY_FALLBACK)

    def test_generic_mime_with_magic_bytes_uses_magic_strategy(self):
        decision = resolve_media_filename(
            message_id=58948,
            media_index=1,
            original_filename=None,
            mime_type="application/octet-stream",
            header=b"\x00\x00\x00\x18ftypisom\x00\x00\x00\x00",
        )

        self.assertEqual(decision.filename, "0000058948_01.mp4")
        self.assertEqual(decision.extension, ".mp4")
        self.assertEqual(decision.strategy, FILENAME_STRATEGY_MAGIC)


if __name__ == "__main__":
    unittest.main()
