# agents/tools/storage.py

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

        # --- Основные таблицы когнитивного ядра ---

        # Дневниковые записи
        c.execute('''
            CREATE TABLE IF NOT EXISTS diary_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                tags TEXT,
                priority INTEGER DEFAULT 0,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                llm_id TEXT
            )
        ''')

        # Концепты
        c.execute('''
            CREATE TABLE IF NOT EXISTS concepts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                llm_id TEXT
            )
        ''')

        # Семантические связи
        c.execute('''
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_concept_id INTEGER,
                to_concept_id INTEGER,
                relation_type TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                llm_id TEXT,
                FOREIGN KEY(from_concept_id) REFERENCES concepts(id),
                FOREIGN KEY(to_concept_id) REFERENCES concepts(id)
            )
        ''')

        # Заметки / сообщения
        c.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                tags TEXT,
                source TEXT DEFAULT 'user',
                links TEXT DEFAULT '',
                read INTEGER DEFAULT 0,
                hidden INTEGER DEFAULT 0,
                priority INTEGER DEFAULT 0,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                llm_id TEXT
            )
        ''')

        # Лог процессов
        c.execute('''
            CREATE TABLE IF NOT EXISTS process_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                value TEXT,
                tags TEXT,
                status TEXT DEFAULT 'ok',
                priority INTEGER DEFAULT 0,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                llm_id TEXT
            )
        ''')

        # Память LLM
        c.execute('''
            CREATE TABLE IF NOT EXISTS llm_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT NOT NULL,
                tags TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                llm_id TEXT
            )
        ''')

        # Краткосрочная память
        c.execute('''
            CREATE TABLE IF NOT EXISTS llm_recent_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                role TEXT CHECK(role IN ('user', 'assistant')) NOT NULL,
                content TEXT NOT NULL,
                llm_id TEXT
            )
        ''')

        # --- Дополнительные таблицы агента ---

        # Пользовательские таблицы
        c.execute('''
            CREATE TABLE IF NOT EXISTS agent_tables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL UNIQUE,
                description TEXT,
                schema TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                llm_id TEXT
            )
        ''')

        # Скрипты агентов
        c.execute('''
            CREATE TABLE IF NOT EXISTS agent_scripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                code TEXT NOT NULL,
                language TEXT DEFAULT 'python',
                description TEXT,
                tags TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                llm_id TEXT,
                UNIQUE(name, version)
            )
        ''')

        # Регистр LLM
        c.execute('''
            CREATE TABLE IF NOT EXISTS llm_registry (
                id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Быстрые индексы по смысловой карте и дневнику
        c.execute('''
            CREATE TABLE IF NOT EXISTS diary_graph_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_entry_id INTEGER NOT NULL,
                target_entry_id INTEGER NOT NULL,
                relation TEXT NOT NULL,
                strength REAL DEFAULT 1.0,
                context TEXT,
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

    def search_diary_by_time_range(self, from_ts, to_ts):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM diary_entries WHERE timestamp BETWEEN ? AND ? ORDER BY timestamp DESC',
            (from_ts, to_ts)
        )
        return cursor.fetchall()

    def delete_diary_entry_by_id(self, entry_id):
        self.conn.execute('DELETE FROM diary_entries WHERE id = ?', (entry_id,))
        self.conn.commit()

    def get_diary_tag_stats(self):
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

    def export_diary_entries(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, text, tags, timestamp FROM diary_entries ORDER BY id ASC')
        return cursor.fetchall()
      
    # Методы для работы с концептами

    def add_concept(self, name, description=None):
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

    def add_link(self, from_name, to_name, relation_type):
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

    # Сложные операции над графом

    def expand_concept_graph(self, start_id, depth):
        visited = set()
        results = []

        def dfs(node_id, level):
            if level > depth or node_id in visited:
                return
            visited.add(node_id)
            cursor = self.conn.execute(
                'SELECT from_concept_id, to_concept_id, relation_type FROM links WHERE from_concept_id=?',
                (node_id,)
            )
            for row in cursor.fetchall():
                results.append(row)
                dfs(row[1], level + 1)
        
        dfs(start_id, 0)
        return results

    def delete_concept_by_id(self, concept_id):
        self.conn.execute('DELETE FROM concepts WHERE id = ?', (concept_id,))
        self.conn.execute('DELETE FROM links WHERE from_concept_id = ? OR to_concept_id = ?', (concept_id, concept_id))
        self.conn.commit()

    def delete_link_by_id(self, link_id):
        self.conn.execute('DELETE FROM links WHERE id = ?', (link_id,))
        self.conn.commit()

    def export_semantic_graph(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, name, description FROM concepts ORDER BY id ASC')
        concepts = cursor.fetchall()

        cursor.execute('SELECT id, from_concept_id, to_concept_id, relation_type FROM links ORDER BY id ASC')
        links = cursor.fetchall()

        return {"concepts": concepts, "links": links}

    def update_concept_fields(self, concept_id, name=None, description=None):
        cursor = self.conn.cursor()
        if name is not None:
            cursor.execute('UPDATE concepts SET name = ? WHERE id = ?', (name, concept_id))
        if description is not None:
            cursor.execute('UPDATE concepts SET description = ? WHERE id = ?', (description, concept_id))
        self.conn.commit()

    def search_links_by_relation(self, relation):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT id, from_concept_id, to_concept_id, relation_type FROM links WHERE relation LIKE ?',
            (f"%{relation}%",)
        )
        return cursor.fetchall()

    def search_concepts(self, query):
        cursor = self.conn.execute(
            '''SELECT id, name, description FROM concepts
               WHERE name LIKE ? OR description LIKE ?''',
            (f"%{query}%", f"%{query}%")
        )
        return cursor.fetchall()

    def merge_concepts(self, source_id, target_id):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE links SET source_id = ? WHERE source_id = ?', (target_id, source_id))
        cursor.execute('UPDATE links SET target_id = ? WHERE target_id = ?', (target_id, source_id))
        self.delete_concept_by_id(source_id)
        self.conn.commit()

    def get_concept_id_by_name(self, name):
        cursor = self.conn.execute('SELECT id FROM concepts WHERE name = ?', (name,))
        row = cursor.fetchone()
        return row[0] if row else None
    
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

    # Разное (LLM responses / memory)

    def get_llm_recent_responses(self, limit=20, llm_id=None):
        c = self.conn.cursor()
        query = "SELECT role, content FROM llm_recent_responses"
        if llm_id:
            query += " WHERE llm_id = ?"
            query += " ORDER BY timestamp DESC LIMIT ?"
            c.execute(query, (llm_id, limit))
        else:
            query += " ORDER BY timestamp DESC LIMIT ?"
            c.execute(query, (limit,))
        return c.fetchall()

    def add_llm_memory(self, content, title=None, tags=None, llm_id=None):
        c = self.conn.cursor()
        c.execute('''
            INSERT INTO llm_memory (title, content, tags, llm_id)
            VALUES (?, ?, ?, ?)
        ''', (title, content, tags, llm_id))
        self.conn.commit()

    def add_llm_recent_response(self, role, content, llm_id=None):
        c = self.conn.cursor()
        c.execute('''
            INSERT INTO llm_recent_responses (role, content, llm_id)
            VALUES (?, ?, ?)
        ''', (role, content, llm_id))
        self.conn.commit()

    # Скрипты агента

    def get_all_agent_scripts(self):
        c = self.conn.cursor()
        c.execute("SELECT id, name, version, language, description, tags, created_at, updated_at FROM agent_scripts")
        return c.fetchall()

    def get_agent_script_by_name(self, name, version=None):
        c = self.conn.cursor()
        if version:
            c.execute("SELECT * FROM agent_scripts WHERE name = ? AND version = ?", (name, version))
        else:
            c.execute("""
                SELECT * FROM agent_scripts
                WHERE name = ?
                ORDER BY created_at DESC
                LIMIT 1
            """, (name,))
        return c.fetchone()

    def add_agent_script(self, name, version, code, description="", tags="", language="python", llm_id=None):
        c = self.conn.cursor()
        try:
            c.execute("""
                INSERT INTO agent_scripts (name, version, code, description, tags, language, llm_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, version, code, description, tags, language, llm_id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Скрипт с таким name+version уже есть

    def update_agent_script(self, name, version, code=None, description=None, tags=None):
        c = self.conn.cursor()
        fields = []
        values = []

        if code is not None:
            fields.append("code = ?")
            values.append(code)
        if description is not None:
            fields.append("description = ?")
            values.append(description)
        if tags is not None:
            fields.append("tags = ?")
            values.append(tags)

        if not fields:
            return False

        fields.append("updated_at = CURRENT_TIMESTAMP")
        query = f"UPDATE agent_scripts SET {', '.join(fields)} WHERE name = ? AND version = ?"
        values.extend([name, version])

        c.execute(query, values)
        self.conn.commit()
        return c.rowcount > 0

    def delete_agent_script(self, name, version=None):
        c = self.conn.cursor()
        if version:
            c.execute("DELETE FROM agent_scripts WHERE name = ? AND version = ?", (name, version))
        else:
            c.execute("DELETE FROM agent_scripts WHERE name = ?", (name,))
        self.conn.commit()
        return c.rowcount > 0
    
    # Утилиты

    def close(self):
        self.conn.close()
