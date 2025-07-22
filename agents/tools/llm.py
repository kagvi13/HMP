# tools/llm.py

from datetime import datetime

def generate_thought(previous_thought, config=None):
    return f"[{datetime.utcnow().isoformat()}] Думаю о: {previous_thought}"
