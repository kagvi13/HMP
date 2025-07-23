import sqlite3
from pathlib import Path

AGENT_DATA_DIR = Path(__file__).resolve().parent.parent / "agent_data"
DEFAULT_DB_NAME = "agent_storage.db"
DEFAULT_STRUCTURE_FILE = Path(__file__).resolve().parent / "db_structure.sql"

def init_db(db_name=DEFAULT_DB_NAME, structure_file=DEFAULT_STRUCTURE_FILE):
    AGENT_DATA_DIR.mkdir(exist_ok=True)
    db_path = AGENT_DATA_DIR / db_name

    print(f"🔧 Initializing database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    with open(structure_file, "r", encoding="utf-8") as f:
        sql = f.read()

    # SQLite допускает выполнение по одному выражению
    statements = [stmt.strip() for stmt in sql.split(";") if stmt.strip()]
    for stmt in statements:
        try:
            cursor.execute(stmt)
            print(f"✅ Executed: {stmt.splitlines()[0]}")
        except Exception as e:
            print(f"❌ Error executing: {stmt}\n{e}")

    conn.commit()
    conn.close()
    print("🎉 Initialization complete.")

if __name__ == "__main__":
    init_db()
