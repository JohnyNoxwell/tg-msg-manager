import unittest

from tg_msg_manager.cli_parser import build_cli_parser
from tg_msg_manager.services.rendering import DEFAULT_TXT_PROFILE


class TestNonChannelContractCliScope(unittest.TestCase):
    def test_contract_scoped_commands_keep_context_readable_default(self):
        parser = build_cli_parser()

        export_args = parser.parse_args(["export", "--user-id", "5001"])
        db_export_args = parser.parse_args(["db-export", "--user-id", "5001"])

        self.assertEqual(export_args.txt_profile, DEFAULT_TXT_PROFILE)
        self.assertEqual(db_export_args.txt_profile, DEFAULT_TXT_PROFILE)

    def test_contract_scoped_commands_accept_legacy_profile(self):
        parser = build_cli_parser()

        export_args = parser.parse_args(
            ["export", "--user-id", "5001", "--txt-profile", "legacy"]
        )
        db_export_args = parser.parse_args(
            ["db-export", "--user-id", "5001", "--txt-profile", "legacy"]
        )

        self.assertEqual(export_args.txt_profile, "legacy")
        self.assertEqual(db_export_args.txt_profile, "legacy")

    def test_export_pm_is_not_a_user_group_or_db_export_contract_command(self):
        contract_commands = {"export", "db-export"}

        self.assertNotIn("export-pm", contract_commands)


if __name__ == "__main__":
    unittest.main()
