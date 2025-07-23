# agents/storage.py

import sqlite3
from datetime import datetime

DEFAULT_DB_PATH = "agent_data.db"

class Storage:
    def __init__(self, config=None):
        self.config = config or {}
        db_path = self.config.get("db_path", DEFAULT_DB_PATH)
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        c = self.conn.cursor()

        # Таблица дневников
        c.execute('''
            CREATE TABLE IF NOT EXISTS diary_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                tags TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Таблица концептов
        c.execute('''
            CREATE TABLE IF NOT EXISTS concepts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Таблица связей
        c.execute('''
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_concept_id INTEGER,
                to_concept_id INTEGER,
                relation_type TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(from_concept_id) REFERENCES concepts(id),
                FOREIGN KEY(to_concept_id) REFERENCES concepts(id)
            )
        ''')

        # Таблица пользовательских заметок
        c.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                tags TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.commit()

    # Методы для работы с дневником
    def write_diary_entry(self, text, tags=None):
        timestamp = datetime.utcnow().isoformat()
        tag_str = ",".join(tags) if tags else ""
        self.conn.execute(
            'INSERT INTO diary_entries (text, tags, timestamp) VALUES (?, ?, ?)',
            (text, tag_str, timestamp)
        )
        self.conn.commit()

    def read_diary_entries(self, limit=10, tag_filter=None):
        cursor = self.conn.cursor()
        if tag_filter:
            if isinstance(tag_filter, list):
                tag_filter = ",".join(tag_filter)
            like_expr = f"%{tag_filter}%"
            cursor.execute(
                'SELECT * FROM diary_entries WHERE tags LIKE ? ORDER BY id DESC LIMIT ?',
                (like_expr, limit)
            )
        else:
            cursor.execute('SELECT * FROM diary_entries ORDER BY id DESC LIMIT ?', (limit,))
        return cursor.fetchall()

    # Методы для работы с концептами
    def create_concept(self, name, description=None):
        timestamp = datetime.utcnow().isoformat()
        self.conn.execute(
            'INSERT INTO concepts (name, description, timestamp) VALUES (?, ?, ?)',
            (name, description, timestamp)
        )
        self.conn.commit()

    def get_concept_by_name(self, name):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM concepts WHERE name = ?', (name,))
        return cursor.fetchone()

    def list_concepts(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM concepts ORDER BY id ASC')
        return cursor.fetchall()

    # Методы для работы с связями
    def link_concepts(self, from_name, to_name, relation_type):
        from_concept = self.get_concept_by_name(from_name)
        to_concept = self.get_concept_by_name(to_name)
        if not from_concept or not to_concept:
            raise ValueError("Один или оба концепта не найдены")
        from_id = from_concept[0]
        to_id = to_concept[0]
        timestamp = datetime.utcnow().isoformat()
        self.conn.execute(
            'INSERT INTO links (from_concept_id, to_concept_id, relation_type, timestamp) VALUES (?, ?, ?, ?)',
            (from_id, to_id, relation_type, timestamp)
        )
        self.conn.commit()

    def get_links_for_concept(self, concept_name):
        concept = self.get_concept_by_name(concept_name)
        if not concept:
            return []
        concept_id = concept[0]
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM links WHERE from_concept_id = ? OR to_concept_id = ?',
            (concept_id, concept_id)
        )
        return cursor.fetchall()

    # Методы для заметок
    def write_note(self, text, tags=None):
        timestamp = datetime.utcnow().isoformat()
        tag_str = ",".join(tags) if tags else ""
        self.conn.execute(
            'INSERT INTO notes (text, tags, timestamp) VALUES (?, ?, ?)',
            (text, tag_str, timestamp)
        )
        self.conn.commit()

    def read_notes(self, limit=10, tag_filter=None):
        cursor = self.conn.cursor()
        if tag_filter:
            if isinstance(tag_filter, list):
                tag_filter = ",".join(tag_filter)
            like_expr = f"%{tag_filter}%"
            cursor.execute(
                'SELECT * FROM notes WHERE tags LIKE ? ORDER BY id DESC LIMIT ?',
                (like_expr, limit)
            )
        else:
            cursor.execute('SELECT * FROM notes ORDER BY id DESC LIMIT ?', (limit,))
        return cursor.fetchall()
