import sys
import os
import shutil
import tempfile
import unittest
import json
from unittest.mock import patch

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tg_msg_manager.services.file_writer import FileRotateWriter


class TestFileRotateWriter(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="tg_writer_test_")

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    async def test_txt_resume_uses_persisted_state(self):
        base_path = os.path.join(self.tmpdir, "chat_log.txt")

        writer = FileRotateWriter(base_path, as_json=False, max_msgs=2, overwrite=True)
        await writer.write_block("first\n", 1)

        resumed = FileRotateWriter(base_path, as_json=False, max_msgs=2, overwrite=False)
        await resumed.write_block("second\n", 1)
        await resumed.write_block("third\n", 1)

        self.assertTrue(os.path.exists(base_path))
        self.assertTrue(os.path.exists(os.path.join(self.tmpdir, "chat_log_part2.txt")))

    async def test_overwrite_cleans_state(self):
        base_path = os.path.join(self.tmpdir, "chat_log.txt")

        writer = FileRotateWriter(base_path, as_json=False, max_msgs=2, overwrite=True)
        await writer.write_block("first\n", 1)
        state_path = os.path.join(self.tmpdir, ".writer_state", "chat_log.json")
        self.assertTrue(os.path.exists(state_path))

        FileRotateWriter(base_path, as_json=False, max_msgs=2, overwrite=True)
        with open(state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
        self.assertEqual(state["current_part"], 1)
        self.assertEqual(state["current_count"], 0)

    async def test_legacy_state_is_migrated_to_state_dir(self):
        base_path = os.path.join(self.tmpdir, "chat_log.txt")
        legacy_state_path = os.path.join(self.tmpdir, ".chat_log.writer_state.json")
        with open(base_path, "w", encoding="utf-8") as f:
            f.write("first\n")
        with open(legacy_state_path, "w", encoding="utf-8") as f:
            json.dump({"current_part": 1, "current_count": 1}, f)

        resumed = FileRotateWriter(base_path, as_json=False, max_msgs=2, overwrite=False)
        await resumed.write_block("second\n", 1)

        new_state_path = os.path.join(self.tmpdir, ".writer_state", "chat_log.json")
        self.assertTrue(os.path.exists(new_state_path))
        self.assertFalse(os.path.exists(legacy_state_path))

    async def test_finalize_persists_state_when_persist_is_batched(self):
        base_path = os.path.join(self.tmpdir, "chat_log.txt")

        writer = FileRotateWriter(base_path, as_json=False, max_msgs=10, overwrite=True, persist_every_writes=5)
        await writer.write_block("first\n", 1)

        state_path = os.path.join(self.tmpdir, ".writer_state", "chat_log.json")
        with open(state_path, "r", encoding="utf-8") as f:
            state_before = json.load(f)
        self.assertEqual(state_before["current_count"], 0)

        await writer.finalize()
        with open(state_path, "r", encoding="utf-8") as f:
            state_after = json.load(f)
        self.assertEqual(state_after["current_count"], 1)

    async def test_write_block_and_finalize_offload_disk_io_to_threads(self):
        base_path = os.path.join(self.tmpdir, "chat_log.txt")
        writer = FileRotateWriter(base_path, as_json=False, max_msgs=10, overwrite=True, persist_every_writes=5)

        async def run_inline(func, *args, **kwargs):
            return func(*args, **kwargs)

        with patch("tg_msg_manager.services.file_writer.asyncio.to_thread", side_effect=run_inline) as mocked_to_thread:
            await writer.write_block("first\n", 1)
            await writer.finalize()

        called_funcs = [call.args[0].__name__ for call in mocked_to_thread.await_args_list]
        self.assertIn("_append_content_sync", called_funcs)
        self.assertIn("_persist_state_sync", called_funcs)
        self.assertTrue(os.path.exists(base_path))


if __name__ == "__main__":
    unittest.main()
