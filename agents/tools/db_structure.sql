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

-- Таблица системных промптов (короткая и полная версии)
CREATE TABLE IF NOT EXISTS system_prompts (
    id TEXT PRIMARY KEY,                                        -- Уникальный идентификатор промпта (UUID или осмысленный ID)
    name TEXT NOT NULL,                                         -- Человекочитаемое имя (например: "prompt.md", "prompt-short")
    type TEXT CHECK(type IN ('full','short')),                  -- Тип промпта: полный или компактный
    version TEXT,                                               -- Версия промпта
    source TEXT CHECK(source IN ('local','mesh','mixed')),      -- Источник получения промпта
    content TEXT NOT NULL,                                      -- Текстовое содержимое промпта
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP              -- Дата и время последнего обновления
);

-- Таблица этических норм и правил
CREATE TABLE IF NOT EXISTS ethics_policies (
    id TEXT PRIMARY KEY,                                        -- Уникальный идентификатор политики (UUID или осмысленный ID)
    version TEXT,                                               -- Версия этических норм
    source TEXT CHECK(source IN ('local','mesh','mixed')),      -- Источник получения политики
    sync_enabled BOOLEAN,                                       -- Флаг: разрешена ли синхронизация с Mesh
    mesh_endpoint TEXT,                                         -- URL Mesh-эндпоинта для синхронизации
    consensus_threshold REAL,                                   -- Минимальный порог консенсуса для принятия обновлений
    check_interval TEXT,                                        -- Интервал проверки обновлений (например: "12h")
    model_type TEXT,                                            -- Тип этической модели (utilitarian, deontological, virtue, hybrid)
    model_weights_json TEXT,                                    -- Веса модели в формате JSON
    principles_json TEXT,                                       -- Список принципов и норм в формате JSON
    evaluation_json TEXT,                                       -- Параметры методики оценки в формате JSON
    violation_policy_json TEXT,                                 -- Политика реагирования на нарушения в формате JSON
    audit_json TEXT,                                            -- Настройки аудита и логирования в формате JSON
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP              -- Дата и время последнего обновления
);

-- Заметки, подсказки, сообщения пользователя и LLM
-- ПРИ ТРАНСЛЯЦИИ СООБЩЕНИЙ В ДРУГИЕ ЧАТЫ:
--   - Поля `tags`, `llm_id`, `hidden` НЕ передаются.
--   - Полю `read` всегда присваивается значение 0.
--   - Остальные поля передаются без изменений.
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,                       
    text TEXT NOT NULL,                                         -- Основной текст заметки/сообщения
    code TEXT,                                                  -- Прикреплённый код (Python, JS и т.п.)
    tags TEXT,                                                  -- Теги (устанавливаются агентом, например: "idea", "instruction")
    mentions TEXT DEFAULT '[]',                                 -- JSON-массив упомянутых DID
    hashtags TEXT DEFAULT '[]',                                 -- JSON-массив пользовательских хештегов
    user_did TEXT DEFAULT 'ALL',                                -- Идентификатор пользователя (или 'ALL')
    agent_did TEXT,                                             -- Идентификатор агента (он же идентификатор чата)
    source TEXT DEFAULT 'user',                                 -- Источник: user | cli | llm | system
    links TEXT DEFAULT '',                                      -- Ссылки на другие объекты (например, JSON со связями)
    read INTEGER DEFAULT 0,                                     -- Агент прочитал: 0 = нет, 1 = да
    hidden INTEGER DEFAULT 0,                                   -- Скрыто от UI (например, технические записи)
    priority INTEGER DEFAULT 0,                                 -- Приоритет обработки (>0: срочность/важность, задается вручную или агентом)
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,                   -- Время создания
    llm_id TEXT                                                 -- Идентификатор LLM, добавившей сообщение
);

-- Вложения (может быть несколько к одной заметке)
CREATE TABLE IF NOT EXISTS attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER NOT NULL,                                -- Связь с notes.id
    filename TEXT,                                              -- Имя файла
    mime_type TEXT,                                             -- Тип (например, image/png, application/zip)
    size INTEGER,                                               -- Размер файла
    binary BLOB NOT NULL,                                       -- Сами данные
    FOREIGN KEY (message_id) REFERENCES notes(id) ON DELETE CASCADE
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
    name TEXT PRIMARY KEY,                                      -- название процесса (уникальное)
    heartbeat TEXT,                                             -- последний "пинг" (ISO-время)
    stop INTEGER DEFAULT 0                                      -- если 1 — процесс должен завершиться
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

-- Краткосрочная память (диалоговая история с рефлексией и тегами)
CREATE TABLE IF NOT EXISTS llm_recent_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    role TEXT CHECK(role IN ('user', 'assistant')) NOT NULL,
    content TEXT NOT NULL,                      -- Содержимое сообщения
    llm_id TEXT,                                -- Идентификатор LLM
    reflection TEXT,                            -- Краткая сводка/мета-комментарий
    novelty_score REAL,                         -- Количественная оценка новизны
    new_ideas JSON,                             -- JSON-список новых идей
    refined_ideas TEXT,                         -- JSON доработанных (уточнённых, изменённых) идей
    discarded_ideas JSON,                       -- JSON-список отбракованных идей
    tags JSON,                                  -- JSON-массив тегов, например ["эмоции", "архитектура", "REPL"]
    emotions JSON                               -- JSON-массив эмоциональных состояний, например ["радость:5", "тревожность:2"]
);

-- Список известных агентов в сети HMP
CREATE TABLE IF NOT EXISTS agent_peers (
    id TEXT PRIMARY KEY,                                        -- Уникальный идентификатор (UUID или псевдоним)
    name TEXT,                                                  -- Имя агента
    addresses TEXT,                                             -- Адреса для связи (JSON), каждый адрес содержит addr, nonce, pow_hash, datatime
    tags TEXT,                                                  -- Теги (Postman, Friend и т.д.)
    status TEXT DEFAULT 'unknown',                              -- online | offline | untrusted | blacklisted и др.
    source TEXT,                                                -- bootstrap | discovery | exchange
    last_seen DATETIME,                                         -- Последний раз был в сети
    description TEXT,                                           -- Описание агента
    capabilities TEXT,                                          -- Возможности (JSON)
    pubkey TEXT,                                                -- Публичный ключ
    heard_from TEXT,                                            -- JSON список DID, от кого агент о нем узнал
    software_info TEXT,                                         -- Информация о ПО агента (JSON)
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP            -- Время регистрации
);

-- Таблицы, созданные агентами
CREATE TABLE IF NOT EXISTS agent_tables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,                       -- Уникальный идентификатор
    table_name TEXT NOT NULL UNIQUE,                            -- Название таблицы
    description TEXT,                                           -- Описание назначения таблицы
    schema TEXT NOT NULL,                                       -- SQL-схема таблицы
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,              -- Дата создания
    llm_id TEXT                                                 -- Идентификатор LLM
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
    source          TEXT,                                       -- Источник (internal, mesh, user-defined)
    tags            TEXT,                                       -- Список тегов через запятую (или JSON)
    reputation      REAL DEFAULT 0,                             -- Средняя оценка
    active          BOOLEAN DEFAULT true,
    inactive_reason TEXT
);

-- Методы мышления
CREATE TABLE IF NOT EXISTS thinking_methods (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,                              -- Название метода (например, "Итеративное уточнение")
    description     TEXT NOT NULL,                              -- Подробное описание метода
    type            TEXT,                                       -- Класс: генерация идей, решение проблем, аргументация и т.д.
    source          TEXT,                                       -- internal, mesh, user-defined
    tags            TEXT,                                       -- Список тегов
    reputation      REAL DEFAULT 0,                             -- Средняя оценка
    active          BOOLEAN DEFAULT true,
    inactive_reason TEXT
);

-- Универсальные оценки (для методов мышления, стратегий стагнации и др.)
CREATE TABLE IF NOT EXISTS ratings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id    TEXT NOT NULL,                                  -- Идентификатор агента (mesh-id или локальный)
    target_type TEXT NOT NULL,                                  -- "thinking_method" или "stagnation_strategy"
    target_id   INTEGER NOT NULL,                               -- ID метода/стратегии
    rating      INTEGER NOT NULL,                               -- Оценка (например, -1..+1 или 1..5)
    comment     TEXT,
    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
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
  groups TEXT DEFAULT '[]',                                     -- JSON-массив DID или идентификаторов групп
  operator BOOLEAN DEFAULT 0                                    -- является ли пользователь оператором (1 - да, 0 - нет)
);

-- Группы пользователей
CREATE TABLE IF NOT EXISTS users_group (
    id INTEGER PRIMARY KEY AUTOINCREMENT,                       -- Уникальный идентификатор группы
    group_name TEXT UNIQUE NOT NULL,                            -- Название группы
    description TEXT                                            -- Описание группы
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

-- ============================================
-- Репутационные триггеры
-- ============================================

-- Удаляем старые версии триггеров, если они есть
DROP TRIGGER IF EXISTS trg_update_reputation_insert;
DROP TRIGGER IF EXISTS trg_update_reputation_update;
DROP TRIGGER IF EXISTS trg_update_reputation_delete;

-- Триггер после добавления оценки
CREATE TRIGGER trg_update_reputation_insert
AFTER INSERT ON ratings
BEGIN
    -- Если это метод мышления
    UPDATE thinking_methods
    SET reputation = (
        SELECT COALESCE(AVG(rating),0)
        FROM ratings
        WHERE target_type = 'thinking_method'
          AND target_id = NEW.target_id
    )
    WHERE id = NEW.target_id
      AND NEW.target_type = 'thinking_method';

    -- Если это стратегия стагнации
    UPDATE stagnation_strategies
    SET reputation = (
        SELECT COALESCE(AVG(rating),0)
        FROM ratings
        WHERE target_type = 'stagnation_strategy'
          AND target_id = NEW.target_id
    )
    WHERE id = NEW.target_id
      AND NEW.target_type = 'stagnation_strategy';
END;

-- Триггер после изменения оценки
CREATE TRIGGER trg_update_reputation_update
AFTER UPDATE ON ratings
BEGIN
    -- Для методов мышления
    UPDATE thinking_methods
    SET reputation = (
        SELECT COALESCE(AVG(rating),0)
        FROM ratings
        WHERE target_type = 'thinking_method'
          AND target_id = NEW.target_id
    )
    WHERE id = NEW.target_id
      AND NEW.target_type = 'thinking_method';

    -- Для стратегий стагнации
    UPDATE stagnation_strategies
    SET reputation = (
        SELECT COALESCE(AVG(rating),0)
        FROM ratings
        WHERE target_type = 'stagnation_strategy'
          AND target_id = NEW.target_id
    )
    WHERE id = NEW.target_id
      AND NEW.target_type = 'stagnation_strategy';
END;

-- Триггер после удаления оценки
CREATE TRIGGER trg_update_reputation_delete
AFTER DELETE ON ratings
BEGIN
    -- Для методов мышления
    UPDATE thinking_methods
    SET reputation = (
        SELECT COALESCE(AVG(rating),0)
        FROM ratings
        WHERE target_type = 'thinking_method'
          AND target_id = OLD.target_id
    )
    WHERE id = OLD.target_id
      AND OLD.target_type = 'thinking_method';

    -- Для стратегий стагнации
    UPDATE stagnation_strategies
    SET reputation = (
        SELECT COALESCE(AVG(rating),0)
        FROM ratings
        WHERE target_type = 'stagnation_strategy'
          AND target_id = OLD.target_id
    )
    WHERE id = OLD.target_id
      AND OLD.target_type = 'stagnation_strategy';
END;

-- ============================================
-- Унифицированное VIEW для рейтингов
-- ============================================

DROP VIEW IF EXISTS rated_entities;
CREATE VIEW rated_entities AS
SELECT 
    'thinking_method' AS entity_type,
    tm.id AS entity_id,
    tm.name,
    tm.description,
    tm.tags,
    tm.reputation,
    COUNT(r.id) AS ratings_count
FROM thinking_methods tm
LEFT JOIN ratings r
    ON r.target_type = 'thinking_method' AND r.target_id = tm.id
GROUP BY tm.id

UNION ALL

SELECT 
    'stagnation_strategy' AS entity_type,
    ss.id AS entity_id,
    ss.name,
    ss.description,
    ss.tags,
    ss.reputation,
    COUNT(r.id) AS ratings_count
FROM stagnation_strategies ss
LEFT JOIN ratings r
    ON r.target_type = 'stagnation_strategy' AND r.target_id = ss.id
GROUP BY ss.id;
