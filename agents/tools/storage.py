# agents/tools/storage.py

import sqlite3
import os
import json

from datetime import datetime, timedelta, UTC

SCRIPTS_BASE_PATH = "scripts"

class Storage:
    def __init__(self, config=None):
        self.config = config or {}
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agent_data.db"))
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        # Загружаем и выполняем весь SQL из файла db_structure.sql
        sql_file = os.path.join(os.path.dirname(__file__), "db_structure.sql")
        with open(sql_file, "r", encoding="utf-8") as f:
            sql_script = f.read()
        c = self.conn.cursor()
        c.executescript(sql_script)  # Выполнит все команды сразу
        self.conn.commit()

    # Методы для работы с дневником

    def write_diary_entry(self, text, tags=None):
        timestamp = datetime.now(UTC).isoformat()
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
        timestamp = datetime.now(UTC).isoformat()
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
        timestamp = datetime.now(UTC).isoformat()
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

    #def write_note(self, text, tags=None):
    # переехал в Web-интерфейс и API

    def get_notes_by_tags(self, limit=10, tag_filter=None):
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
        """Возвращает скрипт с подгруженным кодом из файла, если он был сохранён через @path"""
        c = self.conn.cursor()
        if version:
            c.execute("SELECT * FROM agent_scripts WHERE name = ? AND version = ?", (name, version))
        else:
            c.execute("""
                SELECT * FROM agent_scripts
                WHERE name = ?
                ORDER BY updated_at DESC
                LIMIT 1
            """, (name,))
        row = c.fetchone()
        if not row:
            return None

        row = list(row)
        code_entry = row[3]  # code

        if code_entry.strip().startswith("@path="):
            rel_path = code_entry.strip().split("=", 1)[1]
            full_path = os.path.join(SCRIPT_ROOT, rel_path)
            if os.path.isfile(full_path):
                with open(full_path, "r", encoding="utf-8") as f:
                    row[3] = f.read()
            else:
                row[3] = f"# Error: Script file not found at {full_path}"

        return tuple(row)

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
    
    # process_log — лог задач, ошибок и событий

    def log_process_event(self, name, value=None, tags=None, status='ok', priority=0, llm_id=None):
        c = self.conn.cursor()
        c.execute('''
            INSERT INTO process_log (name, value, tags, status, priority, llm_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, value, tags, status, priority, llm_id))
        self.conn.commit()

    def get_recent_logs(self, limit=50, status_filter=None):
        c = self.conn.cursor()
        query = 'SELECT * FROM process_log'
        params = []

        if status_filter:
            query += ' WHERE status = ?'
            params.append(status_filter)

        query += ' ORDER BY timestamp DESC LIMIT ?'
        params.append(limit)

        c.execute(query, tuple(params))
        return c.fetchall()

    # agent_tables — декларации пользовательских таблиц

    def register_agent_table(self, table_name, schema, description=None, llm_id=None):
        c = self.conn.cursor()
        c.execute('''
            INSERT OR IGNORE INTO agent_tables (table_name, description, schema, llm_id)
            VALUES (?, ?, ?, ?)
        ''', (table_name, description, schema, llm_id))
        self.conn.commit()

    def get_agent_tables(self):
        c = self.conn.cursor()
        c.execute('SELECT * FROM agent_tables ORDER BY created_at DESC')
        return c.fetchall()

    # agent_scripts — код скриптов, которыми может пользоваться агент

    def delete_script_file(name, version):
        """Удаляет файл скрипта, если он существует"""
        path = os.path.join(SCRIPT_ROOT, name, f"v{version}", "script.py")
        if os.path.isfile(path):
            os.remove(path)
    
    def resolve_script_path(name, version):
        return os.path.join(SCRIPTS_BASE_PATH, name, f"v{version}", "script.py")

    def register_agent_script(self, name, version, code, language='python', description=None, tags=None, llm_id=None):
        c = self.conn.cursor()

        if code.strip().startswith("@path="):
            # сохраняем только путь как метку
            path = code.strip().split("=", 1)[1]
            code_entry = f"@path={path}"
        else:
            # сохраняем и файл
            path = resolve_script_path(name, version)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(code)
            code_entry = f"@path={name}/v{version}/script.py"

        c.execute('''
            INSERT OR REPLACE INTO agent_scripts (name, version, code, language, description, tags, llm_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, version, code_entry, language, description, tags, llm_id))
        self.conn.commit()

    def get_agent_script_code(self, name, version=None):
        """Возвращает только код (из БД или файла)"""
        row = self.get_agent_script_by_name(name, version)
        if not row:
            return None
        code_entry = row["code_or_path"]
        if code_entry.strip().startswith("@path="):
            rel_path = code_entry.strip().split("=", 1)[1]
            full_path = os.path.join(SCRIPTS_BASE_PATH, rel_path)
            if os.path.isfile(full_path):
                with open(full_path, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                return f"# Error: File not found at path: {full_path}"
        return code_entry

    def list_agent_scripts(limit=50):
        c = self.conn.cursor()
        c.execute("SELECT * FROM agent_scripts ORDER BY updated_at DESC LIMIT ?", (limit,))
        return c.fetchall()    

    def get_latest_agent_script(self, name):
        c = self.conn.cursor()
        c.execute('''
            SELECT * FROM agent_scripts
            WHERE name = ?
            ORDER BY updated_at DESC
            LIMIT 1
        ''', (name,))
        return c.fetchone()

    def search_agent_scripts_by_tag(self, tag):
        c = self.conn.cursor()
        c.execute("SELECT * FROM agent_scripts WHERE tags LIKE ?", (f"%{tag}%",))
        return c.fetchall()

    def ensure_script_path(name, version):
        """Создаёт папку scripts/{name}/v{version}/ если не существует"""
        path = os.path.join(SCRIPT_ROOT, name, f"v{version}")
        os.makedirs(path, exist_ok=True)
        return os.path.join(path, "script.py")

    def save_script_to_file(code, name, version):
        """Сохраняет скрипт в файл и возвращает путь"""
        file_path = ensure_script_path(name, version)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
        return file_path

    def update_agent_script(self, name, version, code=None, description=None, tags=None, mode="inline"):
        """
        mode: 'inline' (сохранять код в БД), 'file' (в файл, в БД — @path=...)
        """
        c = self.conn.cursor()

        # Получаем текущий code, чтобы понять, был ли путь к файлу
        c.execute("SELECT code FROM agent_scripts WHERE name = ? AND version = ?", (name, version))
        result = c.fetchone()
        if not result:
            return False
        old_code = result[0]

        fields = []
        values = []

        # Обработка поля code
        if code is not None:
            old_is_file = old_code.strip().startswith("@path=")

            if mode == "file":
                file_path = save_script_to_file(code, name, version)
                rel_path = os.path.relpath(file_path, SCRIPT_ROOT)
                code_ref = f"@path={rel_path}"
                fields.append("code = ?")
                values.append(code_ref)

                # если раньше был inline — ничего не делаем, если файл — перезаписываем

            else:  # inline
                fields.append("code = ?")
                values.append(code)

                # если раньше был файл — удалить его
                if old_is_file:
                    delete_script_file(name, version)

        if description is not None:
            fields.append("description = ?")
            values.append(description)

        if tags is not None:
            fields.append("tags = ?")
            values.append(tags)

        if not fields:
            return False

        fields.append("updated_at = ?")
        values.append(datetime.now(UTC).isoformat())

        values.extend([name, version])
        query = f"""
            UPDATE agent_scripts
            SET {', '.join(fields)}
            WHERE name = ? AND version = ?
        """

        c.execute(query, values)
        self.conn.commit()
        return c.rowcount > 0
    
    # llm_registry — реестр LLM-агентов

    def register_llm(self, llm_id, name=None, description=None):
        c = self.conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO llm_registry (id, name, description)
            VALUES (?, ?, ?)
        ''', (llm_id, name, description))
        self.conn.commit()

    def get_registered_llms(self):
        c = self.conn.cursor()
        c.execute('SELECT * FROM llm_registry ORDER BY registered_at DESC')
        return c.fetchall()

    # diary_graph_index — быстрые индексы по смысловой карте и дневнику

    def add_diary_relation(self, source_id, target_id, relation, strength=1.0, context=None):
        c = self.conn.cursor()
        c.execute('''
            INSERT INTO diary_graph_index (source_entry_id, target_entry_id, relation, strength, context)
            VALUES (?, ?, ?, ?, ?)
        ''', (source_id, target_id, relation, strength, context))
        self.conn.commit()

    def get_diary_relations(self, entry_id):
        c = self.conn.cursor()
        c.execute('''
            SELECT * FROM diary_graph_index
            WHERE source_entry_id = ? OR target_entry_id = ?
            ORDER BY timestamp DESC
        ''', (entry_id, entry_id))
        return c.fetchall()

    # Инициализация
    def set_config(self, key, value):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO config (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
        ''', (key, value))
        self.conn.commit()

    def add_identity(self, identity):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO identity (id, name, pubkey, privkey, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            identity['id'],
            identity['name'],
            identity['pubkey'],
            identity['privkey'],
            identity.get('metadata', ''),
            identity['created_at'],
            identity['updated_at']
        ))
        self.conn.commit()

    def add_llm(self, llm):
        cursor = self.conn.cursor()
        config_json = json.dumps(llm, ensure_ascii=False)
        cursor.execute('''
            INSERT OR REPLACE INTO llm_registry (id, name, description, config_json)
            VALUES (?, ?, ?, ?)
        ''', (
            llm['name'],  # используем name как id
            llm['name'],
            llm.get('description', ''),
            config_json
        ))
        self.conn.commit()

    def clear_llm_registry(self):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM llm_registry')
        self.conn.commit()

    def add_user(self, user):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users (
                username, did, mail, password_hash,
                info, contacts, language, operator, ban
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user.get('username'),
            user.get('did'),
            user.get('mail'),
            user.get('password_hash'),
            user.get('info'),
            user.get('contacts'),
            user.get('language'),
            int(user.get('operator', 0)),
            user.get('ban')
        ))
        self.conn.commit()
        return cursor.lastrowid

    # Управление основными процессами
    def update_heartbeat(self, name: str):
        now = datetime.now(UTC).isoformat()
        self.conn.execute(
            "INSERT INTO main_process (name, heartbeat, stop) VALUES (?, ?, 0) "
            "ON CONFLICT(name) DO UPDATE SET heartbeat = excluded.heartbeat",
            (name, now)
        )
        self.conn.commit()

    def check_stop_flag(self, name: str) -> bool:
        cursor = self.conn.execute("SELECT stop FROM main_process WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row and row[0] == 1:
            self.conn.execute("UPDATE main_process SET stop = 0 WHERE name = ?", (name,))
            self.conn.commit()
            return True
        return False

    def is_process_alive(self, name: str, max_delay=180):
        cursor = self.conn.execute("SELECT heartbeat FROM main_process WHERE name=?", (name,))
        row = cursor.fetchone()
        if row:
            try:
                last_beat = datetime.fromisoformat(row[0])
                return (datetime.now(UTC) - last_beat).total_seconds() < max_delay
            except:
                return False
        return False

    # Чтение параметра конфигурации из БД
    def get_config_value(self, key: str, default=None):
        cursor = self.conn.execute("SELECT value FROM config WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else default

    # Web-интерфейс и API
    def write_note(self, content, role="user", user_did="anon", source="web"):
        timestamp = datetime.now(UTC).isoformat()
        self.conn.execute("""
            INSERT INTO notes (text, role, user_did, source, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (content, role, user_did, source, timestamp))
        self.conn.commit()

    def get_notes(self, limit=50):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT text, role, source, user_did, timestamp FROM notes
            WHERE hidden = 0
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

    # Утилиты

    def close(self):
        self.conn.close()
