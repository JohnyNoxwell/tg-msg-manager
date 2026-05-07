import unittest

from tg_msg_manager.services.channel_export.media_policy import (
    MEDIA_MODE_FULL,
    MEDIA_MODE_METADATA,
    MEDIA_MODE_NONE,
    build_media_relative_path,
    extension_for_media,
    initial_download_status,
    media_category,
    validate_media_mode,
)


class TestChannelExportMediaPolicy(unittest.TestCase):
    def test_validate_media_mode_accepts_supported_values(self):
        self.assertEqual(validate_media_mode("none"), MEDIA_MODE_NONE)
        self.assertEqual(validate_media_mode("metadata"), MEDIA_MODE_METADATA)
        self.assertEqual(validate_media_mode("full"), MEDIA_MODE_FULL)

    def test_validate_media_mode_rejects_invalid_value(self):
        with self.assertRaises(ValueError):
            validate_media_mode("archive")

    def test_media_category_maps_photo_video_document_and_unknown(self):
        self.assertEqual(media_category("Photo", None), "photos")
        self.assertEqual(media_category("Video", None), "videos")
        self.assertEqual(media_category("Document", None), "documents")
        self.assertEqual(media_category(None, None), "unknown")

    def test_extension_for_media_prefers_file_name_then_mime_type(self):
        self.assertEqual(
            extension_for_media(
                media_type=None,
                mime_type="application/pdf",
                file_name="report.PDF",
            ),
            ".pdf",
        )
        self.assertEqual(
            extension_for_media(
                media_type=None,
                mime_type="image/jpeg",
                file_name=None,
            ),
            ".jpg",
        )

    def test_build_media_relative_path_is_stable_and_zero_padded(self):
        path = build_media_relative_path(
            message_id=12345,
            media_index=1,
            media_type="Photo",
            mime_type="image/jpeg",
            file_name="image.jpg",
        )

        self.assertEqual(path, "media/photos/0000012345_01.jpg")

    def test_initial_download_status_follows_media_mode(self):
        self.assertEqual(initial_download_status("none"), "skipped_by_mode")
        self.assertEqual(initial_download_status("metadata"), "metadata_only")
        self.assertEqual(initial_download_status("full"), "pending")


if __name__ == "__main__":
    unittest.main()
