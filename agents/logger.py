# agents/logger.py

import json
import os
from datetime import datetime, UTC

LOG_FILE = "logs/repl_log.jsonl"

def log_event(event_type, message, extra=None):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "event": event_type,  # например: 'thought', 'input', 'error', 'action'
        "message": message,
    }

    if extra:
        entry["extra"] = extra

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def log_repl_snapshot(snapshot: dict):
    """
    Запись полной структуры REPL-контекста в лог, с возможностью последующего анализа.
    """
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "event": "repl_snapshot",
        "message": "Полный REPL-контекст",
        "context": snapshot,
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
