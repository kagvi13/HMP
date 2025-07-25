-- Таблица дневниковых записей: размышления, наблюдения, воспоминания
CREATE TABLE IF NOT EXISTS diary_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    tags TEXT,
    priority INTEGER DEFAULT 0,  -- приоритет записи (0 — обычный, >0 — важнее)
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
    links TEXT DEFAULT '',
    read INTEGER DEFAULT 0,             -- 0 = непрочитанное LLM, 1 = прочитано
    priority INTEGER DEFAULT 0,         -- приоритет записи
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Журнал процессов: запуски, завершения, ошибки
CREATE TABLE IF NOT EXISTS process_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    value TEXT,
    tags TEXT,
    status TEXT DEFAULT 'ok',           -- ok | warning | error | timeout | offline | close
    priority INTEGER DEFAULT 0,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Память LLM (временные сообщения в её контексте)
CREATE TABLE IF NOT EXISTS llm_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT NOT NULL,
    tags TEXT, -- через запятую: "goal,observation,meta"
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Краткосрочной памяти LLM
CREATE TABLE IF NOT EXISTS llm_recent_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    role TEXT CHECK(role IN ('user', 'assistant')) NOT NULL,
    content TEXT NOT NULL
);
