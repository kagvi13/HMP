# agents/storage.py

import sqlite3
from datetime import datetime
from pathlib import Path

DEFAULT_DB_PATH = Path("../agent_data/agent_storage.db")


class Storage:
    def __init__(self, config=None):
        self.config = config or {}
        db_path = self.config.get("db_path", DEFAULT_DB_PATH)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        self.conn.close()

    # === Diary Entries ===

    def add_diary_entry(self, content, entry_type="note", related_concepts=None):
        related = ",".join(related_concepts or [])
        created_at = datetime.utcnow().isoformat()
        self.conn.execute(
            """
            INSERT INTO diary_entries (entry_type, content, related_concepts, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (entry_type, content, related, created_at),
        )
        self.conn.commit()

    def get_diary_entries(self, limit=100):
        cursor = self.conn.execute(
            "SELECT * FROM diary_entries ORDER BY created_at DESC LIMIT ?", (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]

    # === Memory Concepts ===

    def add_concept(self, label, concept_type="fact", content="", context=""):
        now = datetime.utcnow().isoformat()
        self.conn.execute(
            """
            INSERT INTO memory_concepts (label, type, content, context, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (label, concept_type, content, context, now, now),
        )
        self.conn.commit()

    def get_concepts(self, concept_type=None):
        if concept_type:
            cursor = self.conn.execute(
                "SELECT * FROM memory_concepts WHERE type = ?", (concept_type,)
            )
        else:
            cursor = self.conn.execute("SELECT * FROM memory_concepts")
        return [dict(row) for row in cursor.fetchall()]

    # === Memory Links ===

    def link_concepts(self, source_label, target_label, relation, weight=1.0):
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM memory_concepts WHERE label = ?", (source_label,))
        source = cur.fetchone()
        cur.execute("SELECT id FROM memory_concepts WHERE label = ?", (target_label,))
        target = cur.fetchone()

        if source and target:
            cur.execute(
                """
                INSERT INTO memory_links (source_id, target_id, relation, weight)
                VALUES (?, ?, ?, ?)
                """,
                (source["id"], target["id"], relation, weight),
            )
            self.conn.commit()
        else:
            raise ValueError("Один из концептов не найден")

    def get_links(self, label=None):
        cur = self.conn.cursor()
        if label:
            cur.execute(
                """
                SELECT l.*, s.label as source_label, t.label as target_label
                FROM memory_links l
                JOIN memory_concepts s ON l.source_id = s.id
                JOIN memory_concepts t ON l.target_id = t.id
                WHERE s.label = ? OR t.label = ?
                """,
                (label, label),
            )
        else:
            cur.execute(
                """
                SELECT l.*, s.label as source_label, t.label as target_label
                FROM memory_links l
                JOIN memory_concepts s ON l.source_id = s.id
                JOIN memory_concepts t ON l.target_id = t.id
                """
            )
        return [dict(row) for row in cur.fetchall()]
