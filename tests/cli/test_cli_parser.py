import unittest

from tg_msg_manager.cli import build_cli_parser


class TestCLIParser(unittest.TestCase):
    def test_build_cli_parser_preserves_stage0_command_surface(self):
        parser = build_cli_parser()
        parsed = parser.parse_args(["export", "--user-id", "42"])
        clean = parser.parse_args(["clean"])
        retry = parser.parse_args(["retry"])

        self.assertEqual(
            set(parser._subparsers._group_actions[0].choices.keys()),
            {
                "export",
                "update",
                "retry",
                "report",
                "clean",
                "export-pm",
                "export-channel",
                "update-channels",
                "delete",
                "schedule",
                "setup",
                "db-export",
                "validate-dataset",
                "inspect-dataset",
                "target",
            },
        )
        self.assertTrue(parsed.deep)
        self.assertEqual(parsed.depth, 2)
        self.assertEqual(parsed.context_window, 3)
        self.assertEqual(parsed.max_cluster, 10)
        self.assertIsNone(parsed.limit)
        self.assertFalse(parsed.json)
        self.assertIsNone(clean.dry_run)
        self.assertFalse(clean.apply)
        self.assertFalse(clean.yes)
        self.assertEqual(retry.limit, 10)
        self.assertFalse(retry.list)
        self.assertFalse(retry.cleanup)

    def test_help_lists_stage0_commands_and_export_args(self):
        parser = build_cli_parser()
        root_help = parser.format_help()
        export_help = (
            parser._subparsers._group_actions[0].choices["export"].format_help()
        )

        self.assertIn("export", root_help)
        self.assertIn("update", root_help)
        self.assertIn("retry", root_help)
        self.assertIn("report", root_help)
        self.assertIn("export-channel", root_help)
        self.assertIn("update-channels", root_help)
        self.assertIn("validate-dataset", root_help)
        self.assertIn("inspect-dataset", root_help)
        self.assertIn("target", root_help)
        self.assertIn("--user-id", export_help)
        self.assertIn("--chat-id", export_help)
        self.assertIn("--depth", export_help)
        self.assertIn("--context-window", export_help)
        self.assertIn("--max-cluster", export_help)
        self.assertIn("--json", export_help)


if __name__ == "__main__":
    unittest.main()
