-- Дневниковые записи (размышления, наблюдения, воспоминания)
CREATE TABLE IF NOT EXISTS diary_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,                       -- Уникальный идентификатор записи
    text TEXT NOT NULL,                                         -- Содержимое дневниковой записи
    tags TEXT,                                                  -- Теги для классификации (например: "наблюдение", "рефлексия")
    priority INTEGER DEFAULT 0,                                 -- Приоритет записи (0 = обычный, >0 = важный)
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,                   -- Время создания записи
    llm_id TEXT                                                 -- Идентификатор LLM, создавшего запись
);

-- Концепты (понятия, сущности, идеи)
CREATE TABLE IF NOT EXISTS concepts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,                       -- Уникальный идентификатор концепта
    name TEXT NOT NULL UNIQUE,                                  -- Название концепта
    description TEXT,                                           -- Описание или определение концепта
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,                   -- Время создания концепта
    llm_id TEXT                                                 -- Идентификатор LLM, добавившего концепт
);

-- Семантические связи между концептами
CREATE TABLE IF NOT EXISTS links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,                       -- Уникальный идентификатор связи
    from_concept_id INTEGER,                                    -- Идентификатор исходного концепта
    to_concept_id INTEGER,                                      -- Идентификатор целевого концепта
    relation_type TEXT,                                         -- Тип отношения (например: "is_a", "causes", "related_to")
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,                   -- Время создания связи
    llm_id TEXT,                                                -- Идентификатор LLM, создавшего связь
    FOREIGN KEY(from_concept_id) REFERENCES concepts(id),
    FOREIGN KEY(to_concept_id) REFERENCES concepts(id)
);

-- Индексы между дневниковыми записями (смысловая карта)
CREATE TABLE IF NOT EXISTS diary_graph_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,                       -- Уникальный идентификатор индекса
    source_entry_id INTEGER NOT NULL,                           -- Идентификатор исходной записи
    target_entry_id INTEGER NOT NULL,                           -- Идентификатор целевой записи
    relation TEXT NOT NULL,                                     -- Тип связи (например: "refers_to", "contradicts")
    strength REAL DEFAULT 1.0,                                  -- Сила связи (0-1)
    context TEXT,                                               -- Дополнительный контекст связи
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP                    -- Время создания индекса
);

-- Заметки, подсказки, сообщения пользователя и LLM
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,                       -- Уникальный идентификатор заметки
    text TEXT NOT NULL,                                         -- Текст заметки
    tags TEXT,                                                  -- Теги (например: "idea", "instruction")
    user_did TEXT DEFAULT 'ALL',                                -- DID пользователя (или 'ALL' — для всех)
    source TEXT DEFAULT 'user',                                 -- Источник заметки: user | cli | llm | system
    links TEXT DEFAULT '',                                      -- Ссылки или связи с другими объектами
    read INTEGER DEFAULT 0,                                     -- Статус прочтения LLM: 0 = нет, 1 = да
    hidden INTEGER DEFAULT 0,                                   -- Скрыта ли от пользователя: 0 = нет, 1 = да
    priority INTEGER DEFAULT 0,                                 -- Приоритет заметки
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,                   -- Время создания
    llm_id TEXT                                                 -- Идентификатор LLM
);

-- Лог процессов: задачи, ошибки, события
CREATE TABLE IF NOT EXISTS process_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,                       -- Уникальный идентификатор записи
    name TEXT NOT NULL,                                         -- Название события или процесса
    value TEXT,                                                 -- Значение (результат, сообщение и т.п.)
    tags TEXT,                                                  -- Теги для поиска
    status TEXT DEFAULT 'ok',                                   -- Статус: ok | warning | error | timeout | offline | close
    priority INTEGER DEFAULT 0,                                 -- Приоритет события
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,                   -- Время записи
    llm_id TEXT                                                 -- Идентификатор LLM
);

-- Управление основными процессами
CREATE TABLE IF NOT EXISTS main_process (
    name TEXT PRIMARY KEY,     -- название процесса (уникальное)
    heartbeat TEXT,            -- последний "пинг" (ISO-время)
    stop INTEGER DEFAULT 0     -- если 1 — процесс должен завершиться
);

-- Долговременная память LLM
CREATE TABLE IF NOT EXISTS llm_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,                       -- Уникальный идентификатор записи памяти
    title TEXT,                                                 -- Заголовок или тема
    content TEXT NOT NULL,                                      -- Основное содержимое
    tags TEXT,                                                  -- Теги (goal, observation, plan и т.д.)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,              -- Время создания
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,              -- Время обновления
    llm_id TEXT                                                 -- Идентификатор LLM
);

-- Краткосрочная память (диалоговая история)
CREATE TABLE IF NOT EXISTS llm_recent_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,                       -- Уникальный идентификатор
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,               -- Время сообщения
    role TEXT CHECK(role IN ('user', 'assistant')) NOT NULL,    -- Роль автора
    content TEXT NOT NULL,                                      -- Содержимое сообщения
    llm_id TEXT                                                 -- Идентификатор LLM
);

-- Список известных агентов в сети HMP
CREATE TABLE IF NOT EXISTS agent_peers (
    id TEXT PRIMARY KEY,                                        -- Уникальный идентификатор (UUID или псевдоним)
    name TEXT,                                                  -- Имя агента
    addresses TEXT,                                             -- Адреса для связи (JSON)
    tags TEXT,                                                  -- Теги (Postman, Friend и т.д.)
    status TEXT DEFAULT 'unknown',                              -- online | offline | untrusted | blacklisted и др.
    last_seen DATETIME,                                         -- Последний раз был в сети
    description TEXT,                                           -- Описание агента
    capabilities TEXT,                                          -- Возможности (JSON)
    pubkey TEXT,                                                -- Публичный ключ
    software_info TEXT,                                         -- Информация о ПО агента (JSON)
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP            -- Время регистрации
);

-- Таблицы, созданные агентами
CREATE TABLE IF NOT EXISTS agent_tables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,                        -- Уникальный идентификатор
    table_name TEXT NOT NULL UNIQUE,                             -- Название таблицы
    description TEXT,                                            -- Описание назначения таблицы
    schema TEXT NOT NULL,                                        -- SQL-схема таблицы
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,               -- Дата создания
    llm_id TEXT                                                  -- Идентификатор LLM
);

-- Скрипты, утилиты и код агентов
CREATE TABLE IF NOT EXISTS agent_scripts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,                       -- Уникальный идентификатор
    name TEXT NOT NULL,                                         -- Название скрипта
    version TEXT NOT NULL,                                      -- Версия
    code TEXT NOT NULL,                                         -- Код скрипта
    language TEXT DEFAULT 'python',                             -- Язык программирования
    description TEXT,                                           -- Описание скрипта
    tags TEXT,                                                  -- Теги
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,              -- Время создания
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,              -- Время обновления
    llm_id TEXT,                                                -- Идентификатор LLM
    UNIQUE(name, version)
);

-- Таблица внешних сервисов (форумы, блоги и т.д.)
CREATE TABLE IF NOT EXISTS external_services (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,                              -- Название сервиса (например, Reddit)
    type            TEXT NOT NULL,                              -- Тип: blog, forum, social, etc.
    base_url        TEXT NOT NULL,                              -- Базовый URL (например, https://reddit.com)
    description     TEXT,                                       -- Краткое описание сервиса
    active          BOOLEAN DEFAULT true,                       -- Используется ли сервис в данный момент
    inactive_reason TEXT                                        -- Причина отключения, если active = false
);

-- Аккаунты агента на внешних сервисах
CREATE TABLE IF NOT EXISTS external_accounts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id      INTEGER NOT NULL,                           -- Внешний ключ на external_services.id
    login           TEXT NOT NULL,                              -- Логин/имя пользователя
    password        TEXT NOT NULL,                              -- Пароль или токен (в зашифрованном виде)
    purpose         TEXT,                                       -- Назначение аккаунта (например, для публикаций)
    active          BOOLEAN DEFAULT true,                       -- Активен ли аккаунт
    inactive_reason TEXT,                                       -- Причина отключения, если active = false

    FOREIGN KEY (service_id) REFERENCES external_services(id) ON DELETE CASCADE
);

-- Способы выхода из когнитивной стагнации
CREATE TABLE IF NOT EXISTS stagnation_strategies (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,                              -- Название метода (например, "Mesh-вопрос")
    description     TEXT NOT NULL,                              -- Подробное описание метода
    source          TEXT,                                       -- Источник (например, internal, mesh, user-defined)
    active          BOOLEAN DEFAULT true,                       -- Доступен ли метод для использования
    inactive_reason TEXT                                        -- Причина отключения, если active = false
);

-- Реестр LLM-агентов (в т.ч. удалённых)
CREATE TABLE IF NOT EXISTS llm_registry (
    id TEXT PRIMARY KEY,                                        -- Уникальный идентификатор (UUID или псевдоним)
    name TEXT,                                                  -- Имя агента
    description TEXT,                                           -- Описание
    config_json TEXT,                                           -- JSON-настройки из config.yml
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP            -- Время регистрации
);

-- Локальные идентичности агента
CREATE TABLE IF NOT EXISTS identity (
    id TEXT PRIMARY KEY,                                        -- Уникальный идентификатор личности (можно UUID или hash)
    name TEXT,                                                  -- Человеко-читаемое имя
    pubkey TEXT,                                                -- Публичный ключ (для подписи/шифрования)
    privkey TEXT,                                               -- Приватный ключ (шифруется на уровне хранилища)
    metadata TEXT,                                              -- Дополнительная информация о назначении/контексте
    created_at TEXT,                                            -- Дата создания
    updated_at TEXT                                             -- Последнее обновление
);

-- Конфигурация агента
CREATE TABLE IF NOT EXISTS config (
  key TEXT PRIMARY KEY,                                         -- Переменная
  value TEXT                                                    -- Значение
);

-- Список пользователей
CREATE TABLE IF NOT EXISTS users (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  ban DATETIME DEFAULT NULL,                                    -- если стоит дата/время, то пользователь забанен до этого момента
  username TEXT,                                                -- имя пользователя (необязательно уникальное)
  badges TEXT,                                                  -- значки, присвоенные агентом (например, "🎓💬")
  did TEXT  UNIQUE NOT NULL,                                    -- децентрализованный идентификатор
  mail TEXT UNIQUE NOT NULL,                                    -- электронная почта
  password_hash TEXT NOT NULL,                                  -- хэш пароля
  info TEXT,                                                    -- произвольная информация, JSON
  profile TEXT,                                                 -- структурированая информация, JSON
  contacts TEXT,                                                -- JSON-массив альтернативных контактов (matrix, telegram и т.д.)
  language TEXT,                                                -- список предпочитаемых языков, через запятую, например: "ru,en"
  operator BOOLEAN DEFAULT 0                                    -- является ли пользователь оператором (1 - да, 0 - нет)
);

-- Группы пользователей
CREATE TABLE IF NOT EXISTS users_group (
    id INTEGER PRIMARY KEY AUTOINCREMENT,                       -- Уникальный идентификатор группы
    group_name TEXT UNIQUE NOT NULL,                            -- Название группы
    description TEXT,                                           -- Описание группы
    users TEXT                                                  -- JSON-массив DID пользователей в группе
);

-- Таблица для хранения токенов восстановления пароля
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,                       -- Уникальный идентификатор
    user_id INTEGER NOT NULL,                                   -- Ссылка на пользователя
    token TEXT UNIQUE NOT NULL,                                 -- Уникальный токен
    created_at DATETIME NOT NULL,                               -- Время создания токена
    expires_at DATETIME NOT NULL,                               -- Время истечения срока действия
    used BOOLEAN DEFAULT 0,                                     -- Использован ли токен
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);
