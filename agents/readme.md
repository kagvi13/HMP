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

agents/
├── start_repl.bat                   ← Запуск агента в REPL-режиме (bat)
├── start_repl.sh                    ← Запуск агента в REPL-режиме (sh)
├── start_repl.py                    ← Запуск агента в REPL-режиме (py)
├── init.py                          ← Инициализация БД
├── logger.py                        ← Ведение логов
├── add_message.py                   ← Ручная отправка сообщений для агента
├── requirements.txt                 ← Зависимости
├── tools/
│   ├── db_structure.sql             ← БД SQL
│   ├── db_structure.md              ← Описание БД SQL
│   ├── storage.py                   ← Реализация базового хранилища (`Storage`), подключение SQLite
│   ├── check_init.py                ← Проверка инициализации БД
│   ├── config_utils.py              ← Обновляет JSON-файл конфигурации указанными значениями
│   ├── crypto.py                    ← Создание и шифрование ключей RSA/Ed25519
│   ├── identity.py                  ← Генерация DiD
│   ├── llm.py                       ← Работа с LLM (вызов, выбор модели, системный промпт)
│   ├── agent_mesh_listener.py       ← Прием входящих сообщений от других HMP-агентов
│   ├── peer_comm.py                 ← Низкоуровневые P2P-запросы (отправка, ping, мета)
│   ├── peer_sync.py                 ← Фоновая синхронизация с другими пирам
│   ├── peers.py                     ← Реестр известных пиров (id, ключи, адреса)
│   ├── memory_utils.py              ← Работа с 'llm_memory', 'llm_recent_responses' и стагнацией
│   ├── context_builder.py           ← Сбор всех `контекстов` из БД и их фильтрация
│   ├── command_parser.py            ← Извлечение команд из JSON или размеченного блока
│   ├── command_executor.py          ← Выполнение команд (shell, graph, diary и др)
│   ├── similarity.py                ← Сравнение смыслов
│   ├── diagnose.py                  ← Скрипт диагностики соединения, определения IP и проверки порта DHT
├── notebook/
│   ├── auth.py                      ← Регистрация, вход, восстановление
│   ├── views.py                     ← Общий и приватный чаты
│   ├── mailer.py                    ← Простая синхронная отправка email
│   ├── templates/
│       ├── index.html               ← Основа
│       ├── private.html             ← Общий и приватный чат
│       ├── login.html               ← Вход
│       ├── register.html            ← Регистрация или сброс пароля
│       ├── style.css                ← Таблица стилей
├── config.yml                       ← Конфигурация агента (имя, порты, роли и т.п.)
├── bootstrap.txt                    ← Локальная этическая модель
├── ethics.yml                       ← Список начальных узлов