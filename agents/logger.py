import json
import os
from datetime import datetime

LOG_FILE = "logs/repl_log.jsonl"

def log_event(event_type, message, extra=None):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_type,       # например: 'thought', 'input', 'error', 'action'
        "message": message,        # краткое описание или фраза
    }

    if extra:
        entry["extra"] = extra     # например: {"node_id": "xyz", "reasoning": "..."}
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
