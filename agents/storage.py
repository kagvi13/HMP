# agents/storage.py

import sqlite3
from datetime import datetime

DB_FILE = "agent_storage.db"

class Storage:
    def __init__(self, db_path=DB_FILE):
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        c = self.conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS diary_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                tags TEXT,
                timestamp TEXT NOT NULL
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS concepts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER,
                target_id INTEGER,
                relation TEXT,
                FOREIGN KEY(source_id) REFERENCES concepts(id),
                FOREIGN KEY(target_id) REFERENCES concepts(id)
            )
        ''')
        self.conn.commit()

    # --- Diary API ---
    def write_entry(self, text, tags=None):
        ts = datetime.utcnow().isoformat()
        tag_str = ",".join(tags) if tags else ""
        self.conn.execute(
            'INSERT INTO diary_entries (text, tags, timestamp) VALUES (?, ?, ?)',
            (text, tag_str, ts)
        )
        self.conn.commit()

    def read_entries(self, limit=10, tag_filter=None):
        cursor = self.conn.cursor()
        if tag_filter:
            like_expr = f"%{tag_filter}%"
            cursor.execute(
                'SELECT * FROM diary_entries WHERE tags LIKE ? ORDER BY id DESC LIMIT ?',
                (like_expr, limit)
            )
        else:
            cursor.execute('SELECT * FROM diary_entries ORDER BY id DESC LIMIT ?', (limit,))
        return cursor.fetchall()

    def search_entries_by_time(self, from_ts, to_ts):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM diary_entries WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp DESC',
            (from_ts, to_ts)
        )
        return cursor.fetchall()

    # --- Graph API ---
    def add_concept(self, name, description=None):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO concepts (name, description) VALUES (?, ?)',
            (name, description)
        )
        self.conn.commit()
        return cursor.lastrowid

    def add_link(self, source_id, target_id, relation):
        self.conn.execute(
            'INSERT INTO links (source_id, target_id, relation) VALUES (?, ?, ?)',
            (source_id, target_id, relation)
        )
        self.conn.commit()

    def get_concepts(self):
        return self.conn.execute('SELECT * FROM concepts').fetchall()

    def get_links(self):
        return self.conn.execute('SELECT * FROM links').fetchall()

    def expand_graph(self, start_id, depth):
        visited = set()
        results = []

        def dfs(node_id, level):
            if level > depth or node_id in visited:
                return
            visited.add(node_id)
            cursor = self.conn.execute(
                'SELECT source_id, target_id, relation FROM links WHERE source_id=?',
                (node_id,)
            )
            for row in cursor.fetchall():
                results.append(row)
                dfs(row[1], level + 1)

        dfs(start_id, 0)
        return results

    def close(self):
        self.conn.close()
