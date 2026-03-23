"""
utils.py — Utility functions for logging, formatting, etc.
"""

import json
import os
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
LOG_FILE = os.path.join(LOG_DIR, "audit.jsonl")


def ensure_log_dir():
    """Create logs/ directory if it doesn't exist."""
    os.makedirs(LOG_DIR, exist_ok=True)


def append_log(record: dict):
    """
    Append a single JSON record to the audit log.
    Uses JSONL format (one JSON object per line, append-only).
    """
    ensure_log_dir()
    record["timestamp"] = datetime.now().isoformat(timespec="seconds")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_logs() -> list:
    """Read all log records. Returns list of dicts."""
    if not os.path.exists(LOG_FILE):
        return []
    records = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def clear_logs():
    """Clear the audit log file (for demo reset)."""
    ensure_log_dir()
    with open(LOG_FILE, "w") as f:
        pass  # truncate


def format_pct(value: float) -> str:
    """Format a float as percentage string."""
    return f"{value:.1%}"


def format_weights_inline(weights: dict) -> str:
    """Format weights dict as a single-line string."""
    parts = [f"{k}: {v:.0%}" for k, v in weights.items()]
    return " | ".join(parts)
