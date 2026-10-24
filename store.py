import json
import logging
import os
import threading
from typing import Any, Dict, List

from app_paths import DATA_DIR

logger = logging.getLogger("Store")

HISTORY_FILE = DATA_DIR / "history.json"
STATE_FILE = DATA_DIR / "state.json"
MAX_UNPINNED = 50
MAX_PERSISTED_IMAGE_B64 = 4 * 1024 * 1024  # larger screenshots stay in memory only; the row keeps its thumbnail

DEFAULT_SETTINGS = {"theme": "dark", "paused": False, "notifications": True}
DEFAULT_STATS = {"sent_count": 0, "sent_bytes": 0, "received_count": 0, "received_bytes": 0}


def _load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default
    except Exception as e:
        logger.warning(f"Could not read {path.name}, starting fresh: {e}")
        return default


def _atomic_write(path, payload):
    tmp = path.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    os.replace(tmp, path)


class Store:
    """History, transfer stats and settings persisted in the user data folder."""

    def __init__(self):
        self._lock = threading.Lock()
        self.history: List[Dict[str, Any]] = _load(HISTORY_FILE, [])
        state = _load(STATE_FILE, {})
        self.settings = {**DEFAULT_SETTINGS, **state.get("settings", {})}
        self.stats = {**DEFAULT_STATS, **state.get("stats", {})}

    def add(self, item: Dict[str, Any]):
        previous = next((h for h in self.history if h["hash"] == item["hash"]), None)
        if previous and previous.get("pinned"):
            item["pinned"] = True
        self.history = [h for h in self.history if h["hash"] != item["hash"]]
        self.history.insert(0, item)
        unpinned = [h for h in self.history if not h.get("pinned")]
        for stale in unpinned[MAX_UNPINNED:]:
            self.history.remove(stale)

    def find(self, item_hash: str):
        return next((h for h in self.history if h["hash"] == item_hash), None)

    def set_pinned(self, item_hash: str, pinned: bool) -> bool:
        item = self.find(item_hash)
        if item:
            item["pinned"] = pinned
        return item is not None

    def delete(self, item_hash: str):
        self.history = [h for h in self.history if h["hash"] != item_hash]

    def clear_unpinned(self):
        self.history = [h for h in self.history if h.get("pinned")]

    def record_transfer(self, direction: str, size: int):
        self.stats[f"{direction}_count"] += 1
        self.stats[f"{direction}_bytes"] += size

    def update_settings(self, changes: Dict[str, Any]):
        for key in DEFAULT_SETTINGS:
            if key in changes:
                self.settings[key] = type(DEFAULT_SETTINGS[key])(changes[key])

    def save(self):
        with self._lock:
            history = [
                {**h, "data": ""} if h["type"] == "image" and len(h.get("data", "")) > MAX_PERSISTED_IMAGE_B64 else h
                for h in self.history
            ]
            try:
                _atomic_write(HISTORY_FILE, history)
                _atomic_write(STATE_FILE, {"settings": self.settings, "stats": self.stats})
            except Exception as e:
                logger.error(f"Saving state failed: {e}")
