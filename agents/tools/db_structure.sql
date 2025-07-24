-- Таблица дневниковых записей: размышления, наблюдения, воспоминания
CREATE TABLE IF NOT EXISTS diary_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    tags TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Таблица концептов (понятий, сущностей, идей)
CREATE TABLE IF NOT EXISTS concepts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Семантические связи между концептами
CREATE TABLE IF NOT EXISTS links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_concept_id INTEGER,
    to_concept_id INTEGER,
    relation_type TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(from_concept_id) REFERENCES concepts(id),
    FOREIGN KEY(to_concept_id) REFERENCES concepts(id)
);

-- Произвольные заметки пользователя (наброски, идеи, подсказки)
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    tags TEXT,
    source TEXT DEFAULT 'user',
    read INTEGER DEFAULT 0,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);
