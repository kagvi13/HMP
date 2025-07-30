-- Основные таблицы когнитивного ядра

-- Дневниковые записи (размышления, наблюдения, воспоминания)
CREATE TABLE IF NOT EXISTS diary_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    tags TEXT,
    priority INTEGER DEFAULT 0,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    llm_id TEXT
);

-- Концепты (понятия, сущности, идеи)
CREATE TABLE IF NOT EXISTS concepts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    llm_id TEXT
);

-- Семантические связи между концептами
CREATE TABLE IF NOT EXISTS links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_concept_id INTEGER,
    to_concept_id INTEGER,
    relation_type TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    llm_id TEXT,
    FOREIGN KEY(from_concept_id) REFERENCES concepts(id),
    FOREIGN KEY(to_concept_id) REFERENCES concepts(id)
);

-- Быстрые индексы по смысловой карте и дневнику
CREATE TABLE IF NOT EXISTS diary_graph_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_entry_id INTEGER NOT NULL,
    target_entry_id INTEGER NOT NULL,
    relation TEXT NOT NULL,
    strength REAL DEFAULT 1.0,
    context TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Заметки, подсказки, сообщения пользователя и LLM
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    tags TEXT,
    user_did TEXT DEFAULT 'ALL'
    source TEXT DEFAULT 'user', -- user | llm | system
    links TEXT DEFAULT '',
    read INTEGER DEFAULT 0,     -- 0 = непрочитано LLM, 1 = прочитано
    hidden INTEGER DEFAULT 0,   -- 0 = отображать пользователю, 1 = скрыть
    priority INTEGER DEFAULT 0,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    llm_id TEXT
);

-- Лог процессов: задачи, ошибки, события
CREATE TABLE IF NOT EXISTS process_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    value TEXT,
    tags TEXT,
    status TEXT DEFAULT 'ok',  -- ok | warning | error | timeout | offline | close
    priority INTEGER DEFAULT 0,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    llm_id TEXT
);

-- Память LLM (контекст размышлений)
CREATE TABLE IF NOT EXISTS llm_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT NOT NULL,
    tags TEXT, -- goal,observation,meta,...
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    llm_id TEXT
);

-- Краткосрочная память LLM (история общения)
CREATE TABLE IF NOT EXISTS llm_recent_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    role TEXT CHECK(role IN ('user', 'assistant')) NOT NULL,
    content TEXT NOT NULL,
    llm_id TEXT
);

-- Список известных HMP-агентов
CREATE TABLE IF NOT EXISTS agent_peers (
    id TEXT PRIMARY KEY,             -- UUID или псевдоним агента
    name TEXT,                       -- Человеко-читаемое имя
    addresses TEXT,                  -- JSON: ["http://1.2.3.4:9000", "p2p://..."]
    tags TEXT,                       -- DHT, Postman, Friend, Local и т.д.
    status TEXT DEFAULT 'unknown',  -- online | offline | untrusted | blacklisted | quarantined | unknown
    last_seen DATETIME,             
    description TEXT,
    capabilities TEXT,               -- JSON: {"can_sync": true, ...}
    pubkey TEXT,                     -- Публичный ключ или хэш
    software_info TEXT,              -- JSON: версия, ОС и др.
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Список пользовательских таблиц, созданных агентами
CREATE TABLE IF NOT EXISTS agent_tables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL UNIQUE,
    description TEXT,
    schema TEXT NOT NULL, -- SQL-схема таблицы
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    llm_id TEXT
);

-- Список утилит/скриптов, добавленных агентами
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
);

-- Список LLM-агентов (возможно удалённые)
CREATE TABLE IF NOT EXISTS llm_registry (
    id TEXT PRIMARY KEY, -- UUID или псевдоним
    name TEXT,
    description TEXT,
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Список пользователей
CREATE TABLE users (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  ban DATETIME DEFAULT NULL,           -- если стоит дата/время, то пользователь забанен до этого момента
  username TEXT,                       -- имя пользователя (необязательно уникальное)
  did TEXT UNIQUE,                     -- децентрализованный идентификатор
  mail TEXT UNIQUE,                    -- электронная почта
  password_hash TEXT,                  -- хэш пароля
  info TEXT,                           -- произвольная информация, JSON
  contacts TEXT,                       -- JSON-массив альтернативных контактов (matrix, telegram и т.д.)
  language TEXT,                       -- список предпочитаемых языков, через запятую, например: "ru,en"
  operator BOOLEAN DEFAULT 0           -- является ли пользователь оператором (1 - да, 0 - нет)
);

-- Список групп пользователей
CREATE TABLE IF NOT EXISTS users_group (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT UNIQUE NOT NULL,
    description TEXT,
    users TEXT -- JSON-массив или CSV со списком DID, например: '["did:example:123", "did:example:456"]'
);

-- Таблица для хранения токенов восстановления пароля
CREATE TABLE password_reset_tokens (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  token TEXT UNIQUE NOT NULL,
  created_at DATETIME NOT NULL,
  expires_at DATETIME NOT NULL,
  used BOOLEAN DEFAULT 0,
  FOREIGN KEY(user_id) REFERENCES users(user_id)
);


