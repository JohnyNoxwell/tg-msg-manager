import logging
import json
import os
from contextlib import contextmanager
from dataclasses import dataclass, field
from time import perf_counter
from typing import Dict

logger = logging.getLogger(__name__)

@dataclass
class TelemetryData:
    api_requests_total: int = 0
    messages_processed_total: int = 0
    errors_total: int = 0
    flood_wait_seconds_total: float = 0.0
    counters: Dict[str, int] = field(default_factory=dict)
    timings_total_seconds: Dict[str, float] = field(default_factory=dict)
    timings_samples: Dict[str, int] = field(default_factory=dict)

class TelemetryTracker:
    """
    Singleton class to track application metrics.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TelemetryTracker, cls).__new__(cls)
            cls._instance.data = TelemetryData()
        return cls._instance

    def track_request(self):
        self.data.api_requests_total += 1

    def track_messages(self, count: int):
        self.data.messages_processed_total += count

    def track_error(self):
        self.data.errors_total += 1

    def track_flood_wait(self, seconds: float):
        self.data.flood_wait_seconds_total += seconds

    def track_counter(self, name: str, amount: int = 1):
        self.data.counters[name] = self.data.counters.get(name, 0) + amount

    def track_duration(self, name: str, seconds: float):
        self.data.timings_total_seconds[name] = self.data.timings_total_seconds.get(name, 0.0) + seconds
        self.data.timings_samples[name] = self.data.timings_samples.get(name, 0) + 1

    @contextmanager
    def time_block(self, name: str):
        started_at = perf_counter()
        try:
            yield
        finally:
            self.track_duration(name, perf_counter() - started_at)

    def reset(self):
        self.data = TelemetryData()

    def get_summary(self) -> Dict:
        avg_timings_ms = {}
        for name, total_seconds in self.data.timings_total_seconds.items():
            samples = self.data.timings_samples.get(name, 0)
            avg_timings_ms[name] = round((total_seconds * 1000.0 / samples), 3) if samples else 0.0

        return {
            "api_requests": self.data.api_requests_total,
            "messages_processed": self.data.messages_processed_total,
            "errors": self.data.errors_total,
            "flood_wait_seconds": round(self.data.flood_wait_seconds_total, 3),
            "counters": dict(sorted(self.data.counters.items())),
            "timings_seconds": {
                name: round(total, 6)
                for name, total in sorted(self.data.timings_total_seconds.items())
            },
            "timing_samples": dict(sorted(self.data.timings_samples.items())),
            "timing_avg_ms": dict(sorted(avg_timings_ms.items())),
        }

    def write_summary(self, path: str = "LOGS/telemetry_latest.json") -> str:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.get_summary(), f, ensure_ascii=False, indent=2)
        return path

    def log_summary(self, label: str = "Execution Summary"):
        summary = self.get_summary()
        summary_path = self.write_summary()
        logger.info(label, extra={"event": "telemetry_summary", "metrics": summary, "summary_path": summary_path})

# Global instance
telemetry = TelemetryTracker()
