import unittest

from tg_msg_manager.infrastructure.storage.records import (
    TargetNameResolutionRecord,
    TargetNameSnapshotRecord,
    TargetNameTargetRecord,
)
from tg_msg_manager.services.target_names import query_target_names


class FakeTargetNamesStorage:
    def __init__(self, resolution, snapshots=()):
        self.resolution = resolution
        self.snapshots = list(snapshots)

    def resolve_target_name_target(self, target):
        return self.resolution

    def get_target_name_snapshots(self, target):
        return self.snapshots


class TestTargetNamesQuery(unittest.TestCase):
    def test_derives_old_values_and_filters_duplicate_consecutive_snapshots(self):
        target = TargetNameTargetRecord(
            target_id=1001,
            target_type="user",
            current_username="new_handle",
            current_display_name="Second Name",
            first_seen=1700000000,
            last_seen=1700000030,
        )
        storage = FakeTargetNamesStorage(
            TargetNameResolutionRecord(
                status="found", target="1001", matches=(target,)
            ),
            [
                TargetNameSnapshotRecord(
                    target_id=1001,
                    target_type="user",
                    observed_at=1700000000,
                    username="old_handle",
                    display_name="First Name",
                ),
                TargetNameSnapshotRecord(
                    target_id=1001,
                    target_type="user",
                    observed_at=1700000010,
                    username="old_handle",
                    display_name="Second Name",
                ),
                TargetNameSnapshotRecord(
                    target_id=1001,
                    target_type="user",
                    observed_at=1700000030,
                    username="new_handle",
                    display_name="Second Name",
                ),
            ],
        )

        result = query_target_names(storage, "1001")

        self.assertEqual(result.status, "found")
        self.assertEqual(result.current.username, "new_handle")
        self.assertEqual(
            [(item.field, item.old_value, item.new_value) for item in result.history],
            [
                ("username", None, "old_handle"),
                ("display_name", None, "First Name"),
                ("display_name", "First Name", "Second Name"),
                ("username", "old_handle", "new_handle"),
            ],
        )

    def test_filters_requested_field(self):
        target = TargetNameTargetRecord(target_id=1001, target_type="user")
        storage = FakeTargetNamesStorage(
            TargetNameResolutionRecord(
                status="found", target="1001", matches=(target,)
            ),
            [
                TargetNameSnapshotRecord(
                    target_id=1001,
                    target_type="user",
                    observed_at=1700000000,
                    username="old_handle",
                    display_name="First Name",
                ),
                TargetNameSnapshotRecord(
                    target_id=1001,
                    target_type="user",
                    observed_at=1700000030,
                    username="new_handle",
                    display_name="Second Name",
                ),
            ],
        )

        result = query_target_names(storage, "1001", field="username")

        self.assertEqual(
            [(item.old_value, item.new_value) for item in result.history],
            [(None, "old_handle"), ("old_handle", "new_handle")],
        )

    def test_chat_target_keeps_current_title_with_empty_history(self):
        target = TargetNameTargetRecord(
            target_id=-1002001,
            target_type="channel",
            current_title="Synthetic Channel",
        )
        storage = FakeTargetNamesStorage(
            TargetNameResolutionRecord(
                status="found", target="-1002001", matches=(target,)
            )
        )

        result = query_target_names(storage, "-1002001", field="title")

        self.assertEqual(result.status, "found")
        self.assertEqual(result.current.title, "Synthetic Channel")
        self.assertEqual(result.history, ())

    def test_returns_unknown_and_ambiguous_states(self):
        missing = query_target_names(
            FakeTargetNamesStorage(
                TargetNameResolutionRecord(status="not_found", target="missing")
            ),
            "missing",
        )
        target = TargetNameTargetRecord(target_id=1001, target_type="user")
        ambiguous = query_target_names(
            FakeTargetNamesStorage(
                TargetNameResolutionRecord(
                    status="ambiguous", target="shared", matches=(target, target)
                )
            ),
            "shared",
        )

        self.assertEqual(missing.status, "not_found")
        self.assertEqual(ambiguous.status, "ambiguous")
        self.assertEqual(len(ambiguous.matches), 2)


if __name__ == "__main__":
    unittest.main()
