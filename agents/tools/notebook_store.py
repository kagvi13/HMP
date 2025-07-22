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
                source TEXT DEFAULT 'user',
                timestamp TEXT NOT NULL,
                read INTEGER DEFAULT 0,
                tags TEXT
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

    def get_first_unread_note(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, text, source, timestamp, tags FROM notes WHERE read = 0 ORDER BY id ASC LIMIT 1"
        )
        return cursor.fetchone()

    def mark_note_as_read(self, note_id: int):
        self.conn.execute(
            "UPDATE notes SET read = 1 WHERE id = ?",
            (note_id,)
        )
        self.conn.commit()

    def set_tags(self, note_id: int, tags: list[str]):
        tag_str = ",".join(tags)
        self.conn.execute(
            "UPDATE notes SET tags = ? WHERE id = ?",
            (tag_str, note_id)
        )
        self.conn.commit()

    def get_random_note_by_tags(self, include_tags: list[str]):
        cursor = self.conn.cursor()
        like_clauses = " OR ".join(["tags LIKE ?"] * len(include_tags))
        values = [f"%{tag}%" for tag in include_tags]
        query = f"""
            SELECT id, text, source, timestamp, tags
            FROM notes
            WHERE ({like_clauses})
            ORDER BY RANDOM()
            LIMIT 1
        """
        cursor.execute(query, values)
        return cursor.fetchone()

    def close(self):
        self.conn.close()
