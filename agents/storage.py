# agents/storage.py

import sqlite3
from datetime import datetime

DEFAULT_DB_PATH = "agent_storage.db"

class Storage:
    def __init__(self, config=None):
        self.config = config or {}
        db_path = self.config.get("db_path", DEFAULT_DB_PATH)
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        c = self.conn.cursor()
        # 🧠 Таблица дневника
        c.execute('''
            CREATE TABLE IF NOT EXISTS diary_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                tags TEXT,
                timestamp TEXT NOT NULL
            )
        ''')
        # 📚 Таблица концептов
        c.execute('''
            CREATE TABLE IF NOT EXISTS concepts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT
            )
        ''')
        # 🔗 Таблица связей
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

    # --- 🧠 Diary API ---
    def write_entry(self, text, tags=None):
        timestamp = datetime.utcnow().isoformat()
        tag_str = ",".join(tags) if tags else ""
        self.conn.execute(
            'INSERT INTO diary_entries (text, tags, timestamp) VALUES (?, ?, ?)',
            (text, tag_str, timestamp)
        )
        self.conn.commit()

    def read_entries(self, limit=10, tag_filter=None):
        cursor = self.conn.cursor()
        if tag_filter:
            # Простейшая фильтрация по включению строки
            if isinstance(tag_filter, list):
                tag_filter = ",".join(tag_filter)
            like_expr = f"%{tag_filter}%"
            cursor.execute(
                'SELECT * FROM diary_entries WHERE tags LIKE ? ORDER BY id DESC LIMIT ?',
                (like_expr, limit)
            )
        else:
            cursor.execute(
                'SELECT * FROM diary_entries ORDER BY id DESC LIMIT ?',
                (limit,)
            )
        return cursor.fetchall()

    def search_entries_by_time(self, from_ts, to_ts):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM diary_entries WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp DESC',
            (from_ts, to_ts)
        )
        return cursor.fetchall()

    # --- 🧠 Semantic Graph API ---
    def add_concept(self, name, description=None):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO concepts (name, description) VALUES (?, ?)',
            (name, description)
        )
        self.conn.commit()
        return cursor.lastrowid

    def query_concept(self, name_substr):
        cursor = self.conn.execute(
            'SELECT id, name, description FROM concepts WHERE name LIKE ?',
            (f"%{name_substr}%",)
        )
        return cursor.fetchall()

    def add_link(self, source_id, target_id, relation):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO links (source_id, target_id, relation) VALUES (?, ?, ?)',
            (source_id, target_id, relation)
        )
        self.conn.commit()
        return cursor.lastrowid

    def list_concepts(self):
        return self.conn.execute('SELECT * FROM concepts').fetchall()

    def list_links(self):
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

    def delete_concept(self, concept_id):
        self.conn.execute('DELETE FROM concepts WHERE id = ?', (concept_id,))
        self.conn.execute('DELETE FROM links WHERE source_id = ? OR target_id = ?', (concept_id, concept_id))
        self.conn.commit()

    def delete_link(self, link_id):
        self.conn.execute('DELETE FROM links WHERE id = ?', (link_id,))
        self.conn.commit()

    def delete_entry(self, entry_id):
        self.conn.execute('DELETE FROM diary_entries WHERE id = ?', (entry_id,))
        self.conn.commit()

    def export_diary(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, text, tags, timestamp FROM diary_entries ORDER BY id ASC')
        return cursor.fetchall()

    def export_graph(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, name, description FROM concepts ORDER BY id ASC')
        concepts = cursor.fetchall()

        cursor.execute('SELECT id, source_id, target_id, relation FROM links ORDER BY id ASC')
        links = cursor.fetchall()

        return {"concepts": concepts, "links": links}

    def update_concept(self, concept_id, name=None, description=None):
        cursor = self.conn.cursor()
        if name is not None:
            cursor.execute('UPDATE concepts SET name = ? WHERE id = ?', (name, concept_id))
        if description is not None:
            cursor.execute('UPDATE concepts SET description = ? WHERE id = ?', (description, concept_id))
        self.conn.commit()

    def get_tag_stats(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT tags FROM diary_entries')
        tag_counts = {}
        for row in cursor.fetchall():
            tags = row[0].split(",") if row[0] else []
            for tag in tags:
                tag = tag.strip()
                if tag:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
        return tag_counts

    def search_links_by_relation(self, relation):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT id, source_id, target_id, relation FROM links WHERE relation LIKE ?',
            (f"%{relation}%",)
        )
        return cursor.fetchall()

    def close(self):
        self.conn.close()
