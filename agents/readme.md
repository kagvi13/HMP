Запуск: `start_repl.bat` или `start_repl.sh`

Установка зависимостей из `requirements.txt`
Конфигурационные файлы: `config.yml`, `bootstrap.txt`
Локальная этическая модель: `ethics.yml`

Проверка инициализации БД - если нет, инициализация (`tools/check_init.py`)

Запуск потоков (осуществляет start_repl.py):
| Поток                            | Назначение                                 |
| -------------------------------- | ------------------------------------------ |
| 🌐 `notebook.py` (FastAPI)       | UI-интерфейс                               |
| 🧠 `repl.py`                     | Агентная логика: REPL-цикл                 |
| 🌍 `agent_mesh_listener.py`      | Получение входящих сообщений               |
| 🌐 `peer_sync.py` или DHT-сервис | Поддержание связи с другими агентами / DHT |

---

**🌐 `mcp_server.py`**
FastAPI-сервер, предоставляющий HTTP-интерфейс к функциональности `storage.py`. Предназначен для использования внешними компонентами, например:

* `Cognitive Shell` (внешний управляющий интерфейс),
* CMP-серверы (если используется mesh-сеть с разграничением ролей),
* отладочные или визуальные UI-инструменты.

Позволяет получать случайные/новые записи, делать разметку, импортировать графы, добавлять заметки и управлять данными без прямого доступа к БД.

---

[agents/](/agents)  
├── [`start_repl.bat`](start_repl.bat) ← Запуск агента в REPL-режиме (bat)  
├── [`start_repl.sh`](start_repl.sh) ← Запуск агента в REPL-режиме (sh)  
├── [`start_repl.py`](start_repl.py) ← Запуск агента в REPL-режиме (py)  
├── [`repl.ru](repl.ru) ← REPL-цикл  
├── [`notebook.py](notebook.py) ← UI-интерфейс  
├── [`agent_mesh_listener.py`](tools/agent_mesh_listener.py) ← Прием входящих сообщений от других HMP-агентов  
├── [`peer_sync.py`](tools/peer_sync.py) ← Фоновая синхронизация с другими пирам  
├── [`mcp_server.py`](mcp_server.py) ← API-интерфейс к хранилищу (storage.py): получение/поиск записей, импорт графа, разметка и др. Используется внешними модулями (напр. Cognitive Shell или CMP).  
├── [`init.py`](init.py) ← Инициализация БД  
├── [`logger.py`](logger.py) ← Ведение логов  
├── [`add_message.py`](add_message.py) ← Ручная отправка сообщений для агента  
├── [`requirements.txt`](requirements.txt) ← Зависимости  
├── [tools/](tools/) ← Вспомогательные скрипты и модули  
│   ├── [`db_structure.sql`](tools/db_structure.sql) ← БД SQL  
│   ├── [`db_structure.md`](tools/db_structure.md) ← Описание БД SQL  
│   ├── [`storage.py`](tools/storage.py) ← Реализация базового хранилища (`Storage`), подключение SQLite  
│   ├── [`check_init.py`](tools/check_init.py) ← Проверка инициализации БД  
│   ├── [`config_utils.py`](tools/config_utils.py) ← Обновляет JSON-файл конфигурации указанными значениями  
│   ├── [`crypto.py`](tools/crypto.py) ← Создание и шифрование ключей RSA/Ed25519  
│   ├── [`identity.py`](tools/identity.py) ← Генерация DiD  
│   ├── [`llm.py`](tools/llm.py) ← Работа с LLM (вызов, выбор модели, системный промпт)  
│   ├── [`peer_comm.py`](tools/peer_comm.py) ← Низкоуровневые P2P-запросы (отправка, ping, мета)  
│   ├── [`peers.py`](tools/peers.py) ← Реестр известных пиров (id, ключи, адреса)  
│   ├── [`memory_utils.py`](tools/memory_utils.py) ← Работа с 'llm_memory', 'llm_recent_responses' и стагнацией  
│   ├── [`context_builder.py`](tools/context_builder.py) ← Сбор всех `контекстов` из БД и их фильтрация  
│   ├── [`command_parser.py`](tools/command_parser.py) ← Извлечение команд из JSON или размеченного блока  
│   ├── [`command_executor.py`](tools/command_executor.py) ← Выполнение команд (shell, graph, diary и др)  
│   ├── [`similarity.py`](tools/similarity.py) ← Сравнение смыслов  
│   ├── [`diagnose.py`](tools/diagnose.py) ← Скрипт диагностики соединения, определения IP и проверки порта DHT  
├── [notebook/](notebook/) ← Веб-интерфейс и связанные модули  
│   ├── [`auth.py`](notebook/auth.py) ← Регистрация, вход, восстановление  
│   ├── [`views.py`](notebook/views.py) ← Общий и приватный чаты  
│   ├── [`mailer.py`](notebook/mailer.py) ← Простая синхронная отправка email  
│   └── [templates/](notebook/templates/) ← HTML-шаблоны и стили  
│       ├── [`index.html`](notebook/templates/index.html) ← Основа  
│       ├── [`private.html`](notebook/templates/private.html) ← Общий и приватный чат  
│       ├── [`login.html`](notebook/templates/login.html) ← Вход  
│       ├── [`register.html`](notebook/templates/register.html) ← Регистрация или сброс пароля  
│       └── [`style.css`](notebook/templates/style.css) ← Таблица стилей  
├── [`config.yml`](config.yml) ← Конфигурация агента (имя, порты, роли и т.п.)  
├── [`bootstrap.txt`](bootstrap.txt) ← Локальная этическая модель  
└── [`ethics.yml`](ethics.yml) ← Список начальных узлов  '
