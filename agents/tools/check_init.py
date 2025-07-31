# tools/check_init.py

import os
import sqlite3
import sys
from agents.init import main as run_init
from agents.config import load_config

def is_db_initialized(db_path):
    if not os.path.exists(db_path):
        return False
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='identity'")
            return cursor.fetchone() is not None
    except Exception:
        return False

def ensure_db_initialized(config_path="agents/config.yml"):
    config = load_config(config_path)
    db_path = config.get("db_path", "./data/agent_storage.db")
    
    if not is_db_initialized(db_path):
        print("[*] Не инициализирована БД. Выполняется init.py...")
        try:
            run_init()
        except Exception as e:
            print(f"[!] Ошибка при инициализации: {e}")
            sys.exit(1)
    else:
        print("[=] БД уже инициализирована.")

    return config
