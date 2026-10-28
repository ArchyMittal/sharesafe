"""
ShareSafe — Lightweight JSON-on-disk store with file locking.
Works perfectly for a single-process uvicorn server (hackathon scale).
"""
from __future__ import annotations
import json
import threading
from pathlib import Path
from typing import Any, List, Optional


class JsonStore:
    """
    Atomic read/write for a JSON file that holds a list of dicts.
    A single module-level lock per file prevents write races within one process.
    """

    _locks: dict[str, threading.Lock] = {}
    _locks_meta = threading.Lock()

    def __init__(self, filepath: str, seed: Optional[List[dict]] = None):
        self.path = Path(filepath)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        # Get or create a per-file lock
        key = str(self.path.resolve())
        with JsonStore._locks_meta:
            if key not in JsonStore._locks:
                JsonStore._locks[key] = threading.Lock()
        self._lock = JsonStore._locks[key]

        # Seed if file does not exist yet
        if not self.path.exists() and seed is not None:
            self._write(seed)
        elif not self.path.exists():
            self._write([])

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def all(self) -> List[dict]:
        """Return all records."""
        with self._lock:
            return self._read()

    def get(self, id_: str) -> Optional[dict]:
        """Return a single record by 'id' field, or None."""
        for record in self.all():
            if record.get("id") == id_:
                return record
        return None

    def insert(self, record: dict) -> dict:
        """Append a record and persist."""
        with self._lock:
            data = self._read()
            data.append(record)
            self._write(data)
        return record

    def update(self, id_: str, patch: dict) -> Optional[dict]:
        """Merge patch into the record with the given id. Returns updated record or None."""
        with self._lock:
            data = self._read()
            for i, record in enumerate(data):
                if record.get("id") == id_:
                    data[i] = {**record, **patch}
                    self._write(data)
                    return data[i]
        return None

    def filter(self, **kwargs: Any) -> List[dict]:
        """Return records whose fields match all given key=value pairs."""
        result = []
        for record in self.all():
            if all(record.get(k) == v for k, v in kwargs.items()):
                result.append(record)
        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _read(self) -> List[dict]:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write(self, data: List[dict]) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
