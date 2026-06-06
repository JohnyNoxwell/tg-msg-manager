import sys
import os
import unittest
import tempfile
import json
from contextlib import contextmanager
from unittest.mock import patch

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tg_msg_manager.core.config import Settings, load_settings
from tg_msg_manager.core.runtime import build_app_runtime


@contextmanager
def temporary_cwd(path):
    previous_cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous_cwd)


class TestConfig(unittest.TestCase):
    def test_missing_required_fields(self):
        # Should fail if api_id is missing
        with self.assertRaises(Exception):
            Settings(api_hash="hash")

    def test_env_override(self):
        with patch.dict(os.environ, {"TG_API_ID": "12345", "TG_API_HASH": "abcde"}):
            settings = Settings()
            self.assertEqual(settings.api_id, 12345)
            self.assertEqual(settings.api_hash, "abcde")

    def test_explicit_init_values_override_environment_values(self):
        with patch.dict(
            os.environ,
            {
                "TG_API_ID": "12345",
                "TG_API_HASH": "env-hash",
                "TG_DB_PATH": "env.db",
            },
            clear=True,
        ):
            settings = Settings(api_id=1, api_hash="init-hash", db_path="init.db")

        self.assertEqual(settings.api_id, 1)
        self.assertEqual(settings.api_hash, "init-hash")
        self.assertEqual(settings.db_path, "init.db")

    def test_whitelist_casting(self):
        # Verify it handles set of strings
        settings = Settings(api_id=1, api_hash="h", whitelist_chats=["123", "user1"])
        self.assertIn(123, settings.whitelist_chats)
        self.assertIn("user1", settings.whitelist_chats)

    def test_language_aliases_normalize_and_fallback(self):
        settings = Settings(api_id=1, api_hash="h", language="EN")
        self.assertEqual(settings.lang, "en")

        fallback = Settings(api_id=1, api_hash="h", ui_language="de")
        self.assertEqual(fallback.lang, "ru")

    def test_load_settings_maps_legacy_exclude_chats_alias_from_config_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            with open(config_path, "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "api_id": 1,
                        "api_hash": "h",
                        "exclude_chats": [-1001700453512],
                    },
                    fh,
                )

            with patch.dict(os.environ, {}, clear=True), temporary_cwd(tmpdir):
                settings = load_settings(config_path)

        self.assertEqual(settings.whitelist_chats, {-1001700453512})

    def test_load_settings_preserves_env_config_and_default_precedence(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            with open(config_path, "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "api_id": 1,
                        "api_hash": "config-hash",
                        "db_path": "config.db",
                        "max_rps": 4.5,
                    },
                    fh,
                )

            with patch.dict(
                os.environ,
                {"TG_API_HASH": "env-hash", "TG_DB_PATH": "env.db"},
                clear=True,
            ), temporary_cwd(tmpdir):
                settings = load_settings(config_path)

        self.assertEqual(settings.api_id, 1)
        self.assertEqual(settings.api_hash, "env-hash")
        self.assertEqual(settings.db_path, "env.db")
        self.assertEqual(settings.max_rps, 4.5)
        self.assertEqual(settings.log_level, "INFO")

    def test_load_settings_does_not_leak_config_values_to_environment(self):
        config_env_keys = {
            "TG_API_ID",
            "TG_API_HASH",
            "TG_DB_PATH",
            "TG_WHITELIST_CHATS",
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            success_path = os.path.join(tmpdir, "success.json")
            with open(success_path, "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "api_id": 1,
                        "api_hash": "h",
                        "db_path": "local.db",
                        "whitelist_chats": [123],
                    },
                    fh,
                )

            with patch.dict(os.environ, {}, clear=True), temporary_cwd(tmpdir):
                load_settings(success_path)
                self.assertFalse(config_env_keys.intersection(os.environ))

            failure_path = os.path.join(tmpdir, "failure.json")
            with open(failure_path, "w", encoding="utf-8") as fh:
                json.dump({"api_id": "bad", "api_hash": "h"}, fh)

            with patch.dict(os.environ, {}, clear=True), temporary_cwd(tmpdir):
                with self.assertRaises(Exception):
                    load_settings(failure_path)
                self.assertFalse(config_env_keys.intersection(os.environ))

    def test_load_settings_can_skip_api_credentials_for_local_read_commands(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            with open(config_path, "w", encoding="utf-8") as fh:
                json.dump({"db_path": "local.db", "lang": "en_US.UTF-8"}, fh)

            with patch.dict(os.environ, {}, clear=True), temporary_cwd(tmpdir):
                settings = load_settings(
                    config_path,
                    require_api_credentials=False,
                )

        self.assertEqual(settings.api_id, 0)
        self.assertEqual(settings.api_hash, "")
        self.assertEqual(settings.db_path, "local.db")
        self.assertEqual(settings.lang, "ru")

    @patch("tg_msg_manager.core.runtime.load_settings")
    def test_build_app_runtime_resolves_project_relative_paths(
        self, mock_load_settings
    ):
        mock_load_settings.return_value = Settings(
            api_id=1,
            api_hash="h",
            db_path="data/messages.db",
        )

        runtime = build_app_runtime(
            project_root="/tmp/tg-msg-manager",
            python_executable="/usr/bin/python3",
        )

        self.assertEqual(runtime.paths.project_root, "/tmp/tg-msg-manager")
        self.assertEqual(runtime.paths.db_path, "/tmp/tg-msg-manager/data/messages.db")
        self.assertEqual(runtime.paths.db_exports_dir, "/tmp/tg-msg-manager/DB_EXPORTS")
        self.assertEqual(runtime.python_executable, "/usr/bin/python3")
        mock_load_settings.assert_called_once_with(
            "/tmp/tg-msg-manager/config.json",
            require_api_credentials=True,
        )


if __name__ == "__main__":
    unittest.main()
