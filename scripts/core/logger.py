"""Append-only JSONL logger. Each line is a self-contained JSON object.

Thread-safe via append mode."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


class JsonlLogger:
    """Append-only JSONL file writer."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, event_type: str, data: dict[str, Any]) -> None:
        record = {
            "ts": time.time(),
            "type": event_type,
            **data,
        }
        with open(self.file_path, "a") as f:
            f.write(json.dumps(record) + "\n")

    def read_all(self, max_records: int = 10000) -> list[dict]:
        """Read all records. Most recent last."""
        if not self.file_path.exists():
            return []

        records = []
        with open(self.file_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
                if len(records) >= max_records:
                    break
        return records

    def read_since(self, since_ts: float) -> list[dict]:
        """Read records newer than a timestamp."""
        return [r for r in self.read_all() if r.get("ts", 0) > since_ts]