# agents/tools/notebook_store.py

import sqlite3
from datetime import datetime
from pathlib import Path

DB_FILE = "notepad.db"

class Notebook:
    def __init__(self, db_path=DB_FILE):
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        c = self.conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                source TEXT DEFAULT 'user',  -- например, 'user', 'imported', 'agent'
                timestamp TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def add_note(self, text, source="user"):
        ts = datetime.utcnow().isoformat()
        self.conn.execute(
            'INSERT INTO notes (text, source, timestamp) VALUES (?, ?, ?)',
            (text.strip(), source, ts)
        )
        self.conn.commit()

    def get_latest_notes(self, limit=10):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT id, text, source, timestamp FROM notes ORDER BY id DESC LIMIT ?',
            (limit,)
        )
        return cursor.fetchall()

    def get_notes_after(self, since_ts):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT id, text, source, timestamp FROM notes WHERE timestamp > ? ORDER BY timestamp',
            (since_ts,)
        )
        return cursor.fetchall()

    def close(self):
        self.conn.close()
