Текушие требования и зависимости: [requirements.txt](requirements.txt)

```
agents/
├── agent.py               ← Основной исполняемый файл CLI-агента.
├── cli.py                 ← Запуск агента в нужном режиме.
├── qa.py                  ← Режим "вопрос-ответ".
├── repl.py                ← Интерактивный REPL-режим.
├── mcp_server.py          ← API-интерфейс для HMP-агента (получение новых/случайных записей, разметка, импорт графа и т.п.).
├── notebook.py            ← Добавление и просмотр пользователем записей в блокноте.
├── config.yml             ← Конфигурация агента (имя, порты, роли и т.п.).
├── ethics.yml             ← Локальная этическая модель.
└── bootstrap.txt          ← Список начальных узлов.
└── tools/
    ├── init_db.py             ← Инициализация базы данных.
    ├── storage.py             ← Реализация базового хранилища (`Storage`), подключение SQLite.
    ├── diagnose.py            ← Скрипт диагностики соединения, определения IP и проверки порта DHT.
    ├── agent_mesh_listener.py ← Прием входящих сообщений от других HMP-агентов
    ├── context_builder.py     ← Сбор всех `контекстов` из БД и их фильтрация.
    ├── peers.py               ← Информация о пирах.
    ├── peer_comm.py           ← Запросы к пирам.
    ├── peer_sync.py           ← Модуль обмена сообщениями.
    ├── llm.py                 ← Работа с LLM (вызов, выбор модели, системный промпт).
    ├── command_parser.py      ← Извлечение команд из JSON или размеченного блока.
    ├── command_executor.py    ← Выполнение команд (shell, graph, diary и др).
    ├── memory_utils.py        ← Работа с 'llm_memory', 'llm_recent_responses' и стагнацией.
    ├── similarity.py          ← Сравнение смыслов.
    └── ... (другие утилиты)
```

**Скрипты:**
* [agent.py](agent.py) - Основной исполняемый файл CLI-агента.
* [cli.py](cli.py) - Запуск агента в нужном режиме.
* [qa.py](qa.py) - Режим "вопрос-ответ".
* [repl.py](repl.py) - Интерактивный REPL-режим.
* [mcp_server.py](mcp_server.py) - API-интерфейс для HMP-агента (получение новых/случайных записей, разметка, импорт графа и т.п.).
* [notebook.py](notebook.py) - Добавление и просмотр пользователем записей в блокноте.
* tools
  * [storage.py](tools/storage.py) - Реализация базового хранилища (`Storage`), подключение SQLite.
  * [init_db.py](tools/init_db.py) - Инициализация базы данных.
  * [llm.py](tools/llm.py) - Работа с LLM (вызов, выбор модели, системный промпт).
  * [context_builder.py](tools/context_builder.py) - Сбор всех `контекстов` из БД и их фильтрация.
  * [peer_comm.py](tools/peer_comm.py) - Запросы к пирам.
  * [command_parser.py](tools/command_parser.py) - Извлечение команд из JSON или размеченного блока.
  * [command_executor.py](tools/command_executor.py) - Выполнение команд (shell, graph, diary и др).
  * [memory_utils.py](tools/memory_utils.py) - Работа с 'llm_memory', 'llm_recent_responses' и стагнацией.
  * [diagnose.py](tools/diagnose.py) - Скрипт диагностики соединения, определения IP и проверки порта DHT.
  * [similarity.py](tools/similarity.py) - Сравнение смыслов.

**Структура БД:**
* [db_structure.md](tools/db_structure.md) - человекочитаемый формат
* [db_structure.sql](tools/db_structure.sql) - SQL

**Примеры:**
* [config.yml](config.yml) - конфигурация агента (пример)
* [ethics.yml](ethics.yml) - локальная этическая модель (пример)
* [bootstrap.txt](bootstrap.txt) - список начальных узлов (пример)
