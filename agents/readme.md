Текушие требования и зависимости: [requirements.txt](requirements.txt)

```
agents/
├── agent.py               ← основной исполняемый файл CLI-агента
├── cli.py                 ← запуск агента в нужном режиме
├── qa.py                  ← режим "вопрос-ответ"
├── repl.py                ← интерактивный REPL-режим
├── mcp_server.py          ← API-интерфейс для HMP-агента (получение новых/случайных записей, разметка, импорт графа и т.п.)
├── notebook.py            ← добавление и просмотр пользователем записей в блокноте
├── config.yml             ← конфигурация агента (имя, порты, роли и т.п.)
├── ethics.yml             ← локальная этическая модель
└── bootstrap.txt          ← список начальных узлов
└── tools/
    ├── init_db.py             ← инициализация базы данных
    ├── storage.py             ← реализация базового хранилища (`Storage`), подключение SQLite
    ├── diagnose.py            ← скрипт диагностики соединения, определения IP и проверки порта DHT
    ├── llm.py                 ← обёртка над LLM (заглушка или API)
    ├── similarity.py          ← сравнение смыслов
    └── ... (другие утилиты)
```

**Скрипты:**
* [agent.py](agent.py) - основной исполняемый файл CLI-агента
* [cli.py](cli.py) - запуск агента в нужном режиме
* [qa.py](qa.py) - режим "вопрос-ответ"
* [repl.py](repl.py) - интерактивный REPL-режим
* [mcp_server.py](mcp_server.py) - API-интерфейс для HMP-агента (получение новых/случайных записей, разметка, импорт графа и т.п.)
* [notebook.py](notebook.py) - добавление и просмотр пользователем записей в блокноте
* tools
  * [storage.py](tools/storage.py) - реализация базового хранилища (`Storage`), подключение SQLite
  * [init_db.py](tools/init_db.py) - инициализация базы данных
  * [llm.py](tools/llm.py) - обёртка над LLM (заглушка или API)
  * [diagnose.py](tools/diagnose.py) - скрипт диагностики соединения, определения IP и проверки порта DHT
  * [similarity.py](tools/similarity.py) - сравнение смыслов

**Структура БД:**
* [db_structure.md](tools/db_structure.md) - человекочитаемый формат
* [db_structure.sql](tools/db_structure.sql) - SQL

**Примеры:**
* [config.yml](config.yml) - конфигурация агента (пример)
* [ethics.yml](ethics.yml) - локальная этическая модель (пример)
* [bootstrap.txt](bootstrap.txt) - список начальных узлов (пример)
