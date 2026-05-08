import unittest

from tg_msg_manager.services.channel_export.media_policy import (
    MEDIA_MODE_FULL,
    MEDIA_MODE_METADATA,
    MEDIA_MODE_NONE,
    build_media_relative_path,
    extension_for_media,
    full_mode_pre_download_status,
    initial_download_status,
    is_media_type_allowed,
    media_category,
    media_category_for_extension,
    should_skip_by_size,
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

    def test_media_category_prefers_concrete_mime_over_document_container(self):
        self.assertEqual(media_category("Document", "video/mp4"), "videos")
        self.assertEqual(media_category("Document", "image/jpeg"), "photos")
        self.assertEqual(media_category("Document", "audio/mpeg"), "audio")

    def test_media_category_for_extension_maps_detected_video_to_videos(self):
        self.assertEqual(
            media_category_for_extension(".mp4", fallback="documents"),
            "videos",
        )
        self.assertEqual(
            media_category_for_extension(".mov", fallback="documents"),
            "videos",
        )
        self.assertEqual(
            media_category_for_extension(".bin", fallback="documents"),
            "documents",
        )

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

    def test_build_media_relative_path_preserves_safe_original_filename(self):
        path = build_media_relative_path(
            message_id=12345,
            media_index=1,
            media_type="Photo",
            mime_type="image/jpeg",
            file_name="image.jpg",
        )

        self.assertEqual(path, "media/photos/0000012345_01_image.jpg")

    def test_initial_download_status_follows_media_mode(self):
        self.assertEqual(initial_download_status("none"), "skipped_by_mode")
        self.assertEqual(initial_download_status("metadata"), "metadata_only")
        self.assertEqual(initial_download_status("full"), "pending")

    def test_full_mode_pre_download_status_respects_size_and_type(self):
        self.assertEqual(
            full_mode_pre_download_status(
                media_type="photo",
                mime_type="image/jpeg",
                file_size=2048,
                max_media_size=1024,
                allowed_media_types=None,
            ),
            "skipped_by_size",
        )
        self.assertEqual(
            full_mode_pre_download_status(
                media_type="document",
                mime_type="application/pdf",
                file_size=512,
                max_media_size=None,
                allowed_media_types=("photo",),
            ),
            "skipped_by_type",
        )
        self.assertEqual(
            full_mode_pre_download_status(
                media_type="photo",
                mime_type="image/jpeg",
                file_size=512,
                max_media_size=1024,
                allowed_media_types=("photo",),
            ),
            "pending",
        )

    def test_media_type_allowlist_and_size_helpers(self):
        self.assertTrue(
            is_media_type_allowed(
                media_type="photo",
                mime_type="image/jpeg",
                allowed_media_types=("photo",),
            )
        )
        self.assertFalse(
            is_media_type_allowed(
                media_type="thumbnail",
                mime_type="image/jpeg",
                allowed_media_types=None,
            )
        )
        self.assertTrue(should_skip_by_size(file_size=200, max_media_size=100))
        self.assertFalse(should_skip_by_size(file_size=None, max_media_size=100))


if __name__ == "__main__":
    unittest.main()
