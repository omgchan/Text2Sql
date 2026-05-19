import json
import os
from datetime import datetime


LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs", "agent.log"))


def log_entry(entry: dict):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    entry = dict(entry)
    entry.setdefault("timestamp", datetime.utcnow().isoformat() + "Z")
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
