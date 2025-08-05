# agents/check_agents.py

import os
import sys
from datetime import datetime, UTC

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.storage import Storage

storage = Storage()

def print_config():
    print("⚙️ Конфигурация:")
    rows = storage.conn.execute("SELECT key, value FROM config").fetchall()
    if not rows:
        print(" • (таблица config пуста)")
    for key, value in rows:
        print(f" • {key:20} = {value}")
    print()

def check_all_processes():
    print_config()
    print(f"🗄️ Путь к базе данных: {storage.db_path}\n")

    processes = storage.conn.execute("SELECT name, heartbeat FROM main_process").fetchall()
    if not processes:
        print("⛔ В базе нет активных процессов.")
        return

    print("📋 Статус процессов:")
    now = datetime.now(UTC)
    for name, heartbeat in processes:
        try:
            hb_time = datetime.fromisoformat(heartbeat)
            delta = (now - hb_time).total_seconds()
            status = "🟢 Активен" if delta < 180 else "🔴 Не отвечает"
            print(f" • {name:20} — {status} (обновлён {int(delta)} сек. назад)")
        except Exception as e:
            print(f" • {name:20} — ⚠️ Ошибка: {e}")

if __name__ == "__main__":
    check_all_processes()
