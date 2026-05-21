import sys
import os
import io
import json
import unittest
import logging

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tg_msg_manager.core.logging import JSONFormatter
from tg_msg_manager.core.context import set_chat_id
from tg_msg_manager.core.telemetry import telemetry


class TestObservability(unittest.TestCase):
    def test_json_formatter(self):
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setFormatter(JSONFormatter())

        logger = logging.getLogger("test_json")
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.propagate = False

        # Set context
        set_chat_id(999)
        logger.info("Test message")

        output = log_capture.getvalue().strip()
        data = json.loads(output)

        self.assertEqual(data["message"], "Test message")
        self.assertEqual(data["chat_id"], 999)
        self.assertIn("timestamp", data)

    def test_telemetry_counters(self):
        telemetry.reset()
        telemetry.track_request()
        telemetry.track_request()
        telemetry.track_counter("sync.flat_batches", 3)
        with telemetry.time_block("sync.chat.total"):
            pass

        summary = telemetry.get_summary()
        self.assertEqual(summary["api_requests"], 2)
        self.assertEqual(summary["counters"]["sync.flat_batches"], 3)
        self.assertEqual(summary["timing_samples"]["sync.chat.total"], 1)
        self.assertIn("sync.chat.total", summary["timing_avg_ms"])

    def test_json_formatter_includes_custom_extra_fields(self):
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setFormatter(JSONFormatter())

        logger = logging.getLogger("test_json_extra")
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.propagate = False

        logger.info(
            "Metrics message", extra={"event": "telemetry_summary", "metrics": {"x": 1}}
        )

        output = log_capture.getvalue().strip()
        data = json.loads(output)
        self.assertEqual(data["event"], "telemetry_summary")
        self.assertEqual(data["metrics"]["x"], 1)


if __name__ == "__main__":
    unittest.main()
