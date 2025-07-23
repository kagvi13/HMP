## 📦 HMP-Agent SQL Schema (черновик v0.1)

```sql
-- Сущности когнитивной памяти
CREATE TABLE memory_concepts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT NOT NULL,
    type TEXT,
    content TEXT,               -- JSON-данные или сериализованный объект
    context TEXT,               -- Дополнительный контекст
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Связи между концептами (граф)
CREATE TABLE memory_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_id INTEGER,
    to_id INTEGER,
    relation TEXT,              -- Тип связи (e.g., 'causes', 'associated_with')
    weight REAL DEFAULT 1.0,
    FOREIGN KEY(from_id) REFERENCES memory_concepts(id),
    FOREIGN KEY(to_id) REFERENCES memory_concepts(id)
);

-- Журнал событий восприятия и действий
CREATE TABLE cognitive_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT,            -- e.g., 'input', 'action', 'message'
    payload TEXT,               -- JSON-строка или сериализованный объект
    source TEXT,                -- Откуда пришло (если применимо)
    target TEXT,                -- Кому отправлено (если применимо)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Гипотезы (временно активные конструкции)
CREATE TABLE hypotheses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    description TEXT,
    status TEXT DEFAULT 'active',  -- 'active', 'rejected', 'confirmed'
    relevance_score REAL DEFAULT 0.5,
    evidence TEXT,                 -- JSON (ссылки на события, концепты)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Цели агента
CREATE TABLE goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT,
    priority INTEGER DEFAULT 5,        -- 1 = high priority
    status TEXT DEFAULT 'pending',     -- 'pending', 'in_progress', 'completed', 'abandoned'
    context TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- HMP-месседжи (mesh-коммуникация)
CREATE TABLE hmp_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    direction TEXT,                    -- 'inbound' | 'outbound'
    peer TEXT,                         -- ID или адрес другого агента
    payload TEXT,                      -- JSON
    topic TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Журнал reasoning-циклов (когнитивных итераций)
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

-- Версионирование моделей (структура API, конфиг, гипотезы)
CREATE TABLE versioned_artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,                         -- например, 'api_structure', 'cognitive_core_config'
    version TEXT,
    content TEXT,                      -- JSON или Markdown
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### 🧠 Примечания

* Базовая структура памяти строится на двух таблицах: `memory_concepts` и `memory_links`, формируя ориентированный граф концептов.
* `cognitive_events` и `cognitive_cycles` обеспечивают журнал восприятия и размышлений.
* HMP-сообщения фиксируются отдельно для анализа взаимодействия между агентами.
* Слой гипотез и целей предоставляет средства для ведения reasoning, планирования и работы с неопределённостью.
* В `versioned_artifacts` можно хранить конфигурации, API-структуры и черновики моделей, связанных с агентом.
