Текушие требования и зависимости: [requirements.txt](requirements.txt)

```
agents/
├── agent.py               ← основной исполняемый файл CLI-агента
├── storage.py             ← хранилище дневника и графа (можно SQLite или JSON)
├── cli.py                 ← запуск агента в нужном режиме
├── qa.py                  ← режим "вопрос-ответ"
├── repl.py                ← интерактивный REPL-режим
├── mcp_server.py          ← FastAPI-сервер
├── notebook.py            ← добавление и просмотр пользователем записей в блокноте
├── config.yml             ← конфигурация агента (имя, порты, роли и т.п.)
├── ethics.yml             ← локальная этическая модель
└── bootstrap.txt          ← список начальных узлов
└── tools/
    ├── diagnose.py            ← скрипт диагностики соединения, определения IP и проверки порта DHT
    ├── llm.py                 ← обёртка над LLM (заглушка или API)
    ├── notebook_store.py      ← Хранилище пользовательских записей
    ├── similarity.py          ← Сравнение смыслов
    ├── llm.py                 ← Генерация мысли
    └── ... (другие утилиты)

```

**Скрипты:**
* [agent.py](agent.py) - основной исполняемый файл CLI-агента
* [storage.py](storage.py) - хранилище дневника и графа (можно SQLite или JSON)
* [cli.py](cli.py) - запуск агента в нужном режиме
* [qa.py](qa.py) - режим "вопрос-ответ"
* [repl.py](repl.py) - интерактивный REPL-режим
* [mcp_server.py](mcp_server.py) - FastAPI-сервер
* [notebook.py](notebook.py) - добавление и просмотр пользователем записей в блокноте
* tools
  * [llm.py](tools/llm.py) - обёртка над LLM (заглушка или API)
  * [diagnose.py](tools/diagnose.py) - скрипт диагностики соединения, определения IP и проверки порта DHT
  * [notebook_store.py](tools/notebook_store.py) - Хранилище пользовательских записей
  * [similarity.py](tools/similarity.py) - Сравнение смыслов

**Примеры:**
* [config.yml](config.yml) - конфигурация агента (пример)
* [ethics.yml](ethics.yml) - локальная этическая модель (пример)
* [bootstrap.txt](bootstrap.txt) - список начальных узлов (пример)
