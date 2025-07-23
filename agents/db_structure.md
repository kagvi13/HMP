sql```
-- Хранение концептов (единиц когнитивной памяти): понятий, фактов, образов, внутренних конструкций и внешних знаний.
CREATE TABLE memory_concepts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT NOT NULL,
    type TEXT,
    content TEXT,               -- JSON-данные или сериализованный объект
    context TEXT,               -- Дополнительный контекст
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Определение связей между концептами — формирование когнитивного графа.
CREATE TABLE memory_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_id INTEGER,
    to_id INTEGER,
    relation TEXT,              -- Тип связи (e.g., 'causes', 'associated_with')
    weight REAL DEFAULT 1.0,
    FOREIGN KEY(from_id) REFERENCES memory_concepts(id),
    FOREIGN KEY(to_id) REFERENCES memory_concepts(id)
);

-- Журнал восприятия, действий и входящих/исходящих сообщений.
CREATE TABLE cognitive_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT,            -- e.g., 'input', 'action', 'message'
    payload TEXT,               -- JSON-строка или сериализованный объект
    source TEXT,                -- Откуда пришло (если применимо)
    target TEXT,                -- Кому отправлено (если применимо)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Управление гипотезами: недоказанными или частично сформированными утверждениями.
CREATE TABLE hypotheses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    status TEXT DEFAULT 'active',  -- 'active', 'rejected', 'confirmed'
    relevance_score REAL DEFAULT 0.5,
    evidence TEXT,                 -- JSON (ссылки на события, концепты)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Управление целями агента — формулировка намерений и задач.
CREATE TABLE goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT,
    priority INTEGER DEFAULT 5,        -- 1 = high priority
    status TEXT DEFAULT 'pending',     -- 'pending', 'in_progress', 'completed', 'abandoned'
    context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Лог входящих и исходящих сообщений в Mesh-среде.
CREATE TABLE hmp_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    direction TEXT,                    -- 'inbound' | 'outbound'
    peer TEXT,                         -- ID или адрес другого агента
    payload TEXT,                      -- JSON
    topic TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- История reasoning-процессов: единиц когнитивной активности, отражающих ход размышлений.
CREATE TABLE cognitive_cycles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cycle_number INTEGER,
    thoughts TEXT,                     -- JSON-массив мыслей
    new_concepts TEXT,
    actions_taken TEXT,
    context_snapshot TEXT,
    started_at TIMESTAMP,
    ended_at TIMESTAMP
);

-- Хранение версии артефактов: конфигураций, моделей, API-структур.
CREATE TABLE versioned_artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,                         -- например, 'api_structure', 'cognitive_core_config'
    version TEXT,
    content TEXT,                      -- JSON или Markdown
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Хранение деклараций, этических норм, стратегий и ограничений поведения агента.
CREATE TABLE IF NOT EXISTS agent_policies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    policy_type TEXT NOT NULL,
    name TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Отслеживание состояния и локальной памяти когнитивных модулей (например, рефлексии, генерации гипотез, плана).
CREATE TABLE IF NOT EXISTS modules_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_name TEXT NOT NULL,
    status TEXT NOT NULL,
    memory TEXT,
    last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Журнал размышлений, наблюдений, воспоминаний или метакомментариев, созданных агентом или пользователем.
CREATE TABLE IF NOT EXISTS diary_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_type TEXT NOT NULL,
    content TEXT NOT NULL,
    related_concepts TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
