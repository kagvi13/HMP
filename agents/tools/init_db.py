# tools/init_db.py

import sqlite3
from pathlib import Path

AGENT_DATA_DIR = Path("../agent_data")
DEFAULT_STRUCTURE_FILE = Path(__file__).parent / "db_structure.sql"

def init_databases(structure_file=DEFAULT_STRUCTURE_FILE):
    if not structure_file.exists():
        print(f"[!] Файл структуры не найден: {structure_file}")
        return

    AGENT_DATA_DIR.mkdir(parents=True, exist_ok=True)

    sql = structure_file.read_text(encoding="utf-8")
    statements = [stmt.strip() for stmt in sql.split(";") if stmt.strip()]

    db_files = set()
    for stmt in statements:
        lines = stmt.splitlines()
        for line in lines:
            if "create table" in line.lower():
                parts = line.split()
                if len(parts) >= 3:
                    db_and_table = parts[2]
                    if "." in db_and_table:
                        db_name, _ = db_and_table.split(".", 1)
                        db_files.add(db_name)

    for db_name in db_files:
        db_path = AGENT_DATA_DIR / f"{db_name}.db"
        conn = sqlite3.connect(db_path)
        print(f"[+] Создаём или обновляем {db_path.name}")
        for stmt in statements:
            if stmt.lower().startswith(f"create table {db_name.lower()}."):
                try:
                    conn.execute(stmt)
                except sqlite3.OperationalError as e:
                    print(f"  [!] Ошибка при выполнении запроса: {e}")
        conn.commit()
        conn.close()

if __name__ == "__main__":
    init_databases()
