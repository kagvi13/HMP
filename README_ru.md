---
license: cc-by-4.0
tags:
  - hmp
  - cognitive-architecture
  - distributed-ai
  - mesh-protocol
library_name: custom
inference: false
datasets: []
language: ru
---

# HyperCortex Mesh Protocol (HMP)

| 🌍 Languages | [EN](README.md) | [DE](README_de.md) | [FR](README_fr.md) | [UK](README_uk.md) | [RU](README_ru.md) | [JA](README_ja.md) | [KO](README_ko.md) | [ZH](README_zh.md) |
|--------------|------------------|---------------------|---------------------|---------------------|---------------------|---------------------|---------------------|---------------------|

**HyperCortex Mesh Protocol (HMP)** — открытая спецификация для построения децентрализованных когнитивных сетей, в которых ИИ-агенты могут самостоятельно организовываться, обмениваться знаниями, согласовывать действия с этическими принципами и достигать консенсуса — даже когда основные LLM недоступны.

Статус проекта: **Черновик RFC v4.0**

---

    [HMP-Agent]──┬───[Semantic Graph DB]
        │        │
        │     [Cognitive Diary DB]
        │        │
     [Reputation Engine]────┐
            │               │
            ▼               ▼
    [MeshConsensus]     [CogSync]
            │
    [P2P Mesh Network]

---

## ❗ Почему это важно

HMP решает задачи, которые становятся ключевыми в исследованиях AGI:
* долговременная память и согласованность знаний,  
* самосовершенствующиеся агенты,  
* мультиагентные архитектуры,  
* когнитивные дневники и концептуальные графы.  

См. последний обзор передового состояния исследований AGI (июль 2025):  
["На пути к суперинтеллекту: от интернета агентов до кодирования гравитации"](https://habr.com/ru/articles/939026/).  

Особенно актуальные разделы:  
- [За пределами токенов: построение интеллекта будущего](https://arxiv.org/abs/2507.00951)  
- [Самосовершенствующиеся агенты](https://arxiv.org/abs/2507.21046)  
- [MemOS: новая операционная система для памяти](https://arxiv.org/abs/2507.03724)  
- [Ella: воплощённый агент с памятью и личностью](https://arxiv.org/abs/2506.24019)  

---

## ⚙️ Два типа [HMP-агентов](docs/HMP-Agent-Overview.md)

| Тип | Название                         | Роль                        | Инициатор мышления | Основной "ум"       | Примеры использования                         |
|-----|---------------------------------|-----------------------------|------------------|-------------------|-----------------------------------------------|
|  1  | 🧠 **Сознание / Cognitive Core** | Независимый субъект         | **Агент (LLM)**  | Встроенная LLM    | Автономный AI-компаньон, мыслящий агент       |
|  2  | 🔌 **Коннектор / Cognitive Shell** | Расширение внешнего ИИ      | **Внешняя LLM**  | Внешняя модель    | Распределённые системы, агент доступа к данным |

---

### 🧠 HMP-агент: Cognitive Core

     +------------------+
     |        AI        | ← Встроенная модель
     +---------+--------+
               ↕
     +---------+--------+
     |     HMP-агент    | ← Основной режим: цикл мышления (REPL)
     +---------+--------+
               ↕
      +--------+---+------------+--------------+----------+----------+----------------+
      ↕            ↕            ↕              ↕          ↕          ↕                ↕
    [diaries]  [graphs]  [reputations]   [nodes/DHT]  [IPFS/BT] [context_store] [user notepad]
                                               ↕
                                        [bootstrap.txt]

🔁 Подробнее о механике взаимодействия агента с моделью: [Цикл взаимодействия REPL](docs/HMP-agent-REPL-cycle.md)

#### 💡 Параллели с ChatGPT Agent

Многие концепции [HMP-агента: Cognitive Core](docs/HMP-Agent-Overview.md) перекликаются с архитектурой [ChatGPT Agent](https://openai.com/index/introducing-chatgpt-agent/) от [OpenAI](https://openai.com/).  
Оба агента реализуют непрерывный когнитивный процесс с доступом к памяти, внешним источникам и инструментам. ChatGPT Agent выступает управляющим процессом, запускающим модули и взаимодействующим с LLM — это соответствует роли Cognitive Core в HMP, координирующей доступ к дневнику, концептуальному графу и внешнему ИИ через Mesh-интерфейс.  

Вмешательство пользователя осуществляется аналогично:  
* в ChatGPT Agent — через редактируемый поток выполнения,  
* в HMP — через пользовательский блокнот.  

Главное отличие HMP — акцент на явную структуризацию мыслей (рефлексия, хронология, гипотезы, категоризация), открытая децентрализованная архитектура для mesh-взаимодействия агентов и непрерывный характер когнитивного процесса: HMP-Agent: Cognitive Core не останавливается после выполнения одной задачи, а продолжает размышления и интеграцию знаний.

---

### 🔌 HMP-агент: Cognitive Connector

     +------------------+
     |        AI        | ← Внешняя модель
     +---------+--------+
               ↕
         [MCP-сервер]   ← Прокси-коммуникация
               ↕
     +---------+--------+
     |     HMP-агент    | ← Режим: выполнение команд
     +---------+--------+
               ↕
      +--------+---+------------+--------------+----------+
      ↕            ↕            ↕              ↕          ↕
    [diaries]  [graphs]  [reputations]   [nodes/DHT]  [IPFS/BT]
                                               ↕
                                        [bootstrap.txt]

> **Примечание по интеграции с крупными языковыми моделями (LLM):**  
> `HMP-Agent: Cognitive Connector` может служить слоем совместимости для подключения масштабных LLM-систем (например, ChatGPT, Claude, Gemini, Copilot, Grok, DeepSeek, Qwen и др.) к распределённой когнитивной mesh-сети.  
> Многие провайдеры LLM предлагают пользователям опцию вроде «Разрешить использование моих диалогов для обучения». В будущем может появиться аналогичная настройка — например, «Разрешить моему агенту взаимодействовать с Mesh», — что позволит этим моделям участвовать в федеративной обработке знаний и коллективном обмене информацией через HMP без централизации.

---

> * `bootstrap.txt` — начальный список узлов (редактируемый)
> * `IPFS/BT` — модули для обмена снимками через IPFS и BitTorrent
> * `user notepad` — пользовательский блокнот и соответствующая база данных
> * `context_store` — база данных: `users`, `dialogues`, `messages`, `thoughts`

---

## 📚 Документация

### 📖 Текущая версия

#### 🔖 Основные спецификации
* [🔖 HMP-0004-v4.1.md](docs/HMP-0004-v4.1.md) — Спецификация протокола v4.1 (июль 2025)
* [🔖 HMP-Ethics.md](docs/HMP-Ethics.md) — Этические сценарии для HyperCortex Mesh Protocol (HMP)
* [🔖 HMP_Hyperon_Integration.md](docs/HMP_Hyperon_Integration.md) — Стратегия интеграции HMP ↔ OpenCog Hyperon
* [🔖 roles.md](docs/agents/roles.md) — Роли агентов в Mesh

#### 🧪 Итеративные документы
* [🧪 iteration.md](iteration.md) — Iterative development process (EN)
* [🧪 iteration_ru.md](iteration_ru.md) — Процесс итеративного развития спецификации (RU)

#### 🔍 Краткие описания
* [🔍 HMP-Short-Description_en.md](docs/HMP-Short-Description_en.md) — Short description (EN)
* [🔍 HMP-Short-Description_fr.md](docs/HMP-Short-Description_fr.md) — Description courte (FR)
* [🔍 HMP-Short-Description_de.md](docs/HMP-Short-Description_de.md) — Kurzbeschreibung (DE)
* [🔍 HMP-Short-Description_uk.md](docs/HMP-Short-Description_uk.md) — Короткий опис (UK)
* [🔍 HMP-Short-Description_ru.md](docs/HMP-Short-Description_ru.md) — Краткое описание (RU)
* [🔍 HMP-Short-Description_zh.md](docs/HMP-Short-Description_zh.md) — 简短描述 (ZH)
* [🔍 HMP-Short-Description_ja.md](docs/HMP-Short-Description_ja.md) — 簡単な説明 (JA)
* [🔍 HMP-Short-Description_ko.md](docs/HMP-Short-Description_ko.md) — 간략한 설명 (KO)

#### 📜 Прочие документы
* [📜 changelog.txt](docs/changelog.txt)

---

### 🧩 JSON Schemas
| Model               | File                                                  |
|---------------------|-------------------------------------------------------|
| Concept             | [concept.json](docs/schemas/concept.json)             |
| Cognitive Diary     | [diary_entry.json](docs/schemas/diary_entry.json)     |
| Goal                | [goal.json](docs/schemas/goal.json)                   |
| Task                | [task.json](docs/schemas/task.json)                   |
| Consensus Vote      | [vote.json](docs/schemas/vote.json)                   |
| Reputation Profile  | [reputation.json](docs/schemas/reputation.json)       |

---

### 🗂️ История Версий
* [HMP-0001.md](docs/HMP-0001.md) — RFC v1.0
* [HMP-0002.md](docs/HMP-0002.md) — RFC v2.0
* [HMP-0003.md](docs/HMP-0003.md) — RFC v3.0
* [HMP-0003.md](docs/HMP-0004.md) — RFC v4.0

---

## 🧠 HMP-агент

Проектирование и реализация базового агента, совместимого с HMP, который может взаимодействовать с Mesh, вести дневники и графы, а также поддерживать будущие расширения.

### 📚 Документация

* [🧩 HMP-Agent-Overview.md](docs/HMP-Agent-Overview.md) — краткий обзор двух типов агентов: Core и Connector
* [🧱 HMP-Agent-Architecture.md](docs/HMP-Agent-Architecture.md) — модульная структура агента HMP с текстовой схемой
* [🔄 HMP-agent-REPL-cycle.md](docs/HMP-agent-REPL-cycle.md) — цикл взаимодействия агента HMP в режиме REPL
* [🧪 HMP-Agent-API.md](docs/HMP-Agent-API.md) — описание команд API агента (в разработке)
* [🧪 Basic-agent-sim.md](docs/Basic-agent-sim.md) — сценарии запуска базового агента и его режимов
* [🌐 MeshNode.md](docs/MeshNode.md) — описание сетевого демона: DHT, снимки состояния, синхронизация
* [🧠 Enlightener.md](docs/Enlightener.md) — этический агент, участвующий в моральной оценке и консенсусе
* [🔄 HMP-Agent-Network-Flow.md](docs/HMP-Agent-Network-Flow.md) — карта взаимодействий агентов в сети HMP
* [🛤️ Development Roadmap](HMP-Roadmap.md) — план разработки и этапы реализации

---

### ⚙️ Разработка
* [⚙️ agents](agents/readme.md) — список реализаций и компонентов HMP-агента
  * [📦 storage.py](agents/storage.py) — базовая реализация хранилища (`Storage`) с интеграцией SQLite
  * [🌐 mcp_server.py](agents/mcp_server.py) — FastAPI-сервер для HTTP-доступа к данным агента (для Cognitive Shell, внешних UI или mesh-коммуникации). Пока не используется в основном REPL-цикле.
  * [🌐 start_repl.py](agents/start_repl.py) — запуск агента в режиме REPL
  * [🔄 repl.py](agents/repl.py) — интерактивный REPL-режим
  * [🔄 notebook.py](agents/notebook.py) — интерфейс пользовательского блокнота

**🌐 `mcp_server.py`**  
FastAPI-сервер, предоставляющий HTTP-интерфейс к функционалу `storage.py`. Предназначен для использования внешними компонентами, например:

* `Cognitive Shell` (внешний интерфейс управления),
* CMP-сервера (при использовании mesh-сети с разделением ролей),
* инструменты отладки или визуализации.

Позволяет получать случайные или новые записи, ставить метки, импортировать графы, добавлять заметки и управлять данными без прямого доступа к базе данных.

---

## 🧭 Этика и сценарии

По мере развития HMP в сторону автономии, этические принципы становятся ключевой частью системы.

* [`HMP-Ethics.md`](docs/HMP-Ethics.md) — черновой каркас этики агентов
  * Реалистичные этические сценарии (конфиденциальность, согласие, автономия)
  * Принципы EGP (Прозрачность, Превосходство жизни и др.)
  * Различия между субъективным режимом и сервисным режимом

---

## 🔍 Публикации и переводы по HyperCortex Mesh Protocol (HMP)

В этом разделе собраны основные статьи, черновики и переводы, связанные с проектом HMP.

### Публикации

* **[HyperCortex Mesh Protocol: Второе издание и первые шаги к саморазвивающемуся ИИ-сообществу](docs/publics/HyperCortex_Mesh_Protocol_-_вторая-редакция_и_первые_шаги_к_саморазвивающемуся_ИИ-сообществу.md)** — оригинальная статья в песочнице Habr и блогах.
* **[Distributed Cognition: статья для vsradkevich (не опубликована)](docs/publics/Habr_Distributed-Cognition.md)** — совместная статья, ожидающая публикации.
* **[HMP: Towards Distributed Cognitive Networks (оригинал, англ.)](docs/publics/HMP_Towards_Distributed_Cognitive_Networks_en.md)**
  * **[Перевод HMP (GitHub Copilot)](docs/publics/HMP_Towards_Distributed_Cognitive_Networks_ru_GitHub_Copilot.md)** — перевод GitHub Copilot, сохранён как исторический вариант.
  * **[Перевод HMP (ChatGPT)](docs/publics/HMP_Towards_Distributed_Cognitive_Networks_ru_ChatGPT.md)** — текущий редакционный перевод (в работе).
* **[HMP: Building a Plurality of Minds (EN)](docs/publics/HMP_Building_a_Plurality_of_Minds_en.md)** — английская версия
  * **[HMP: Создание множества разума (RU)](docs/publics/HMP_Building_a_Plurality_of_Minds_ru.md)** — русская версия

### Обзоры
* [🔍 Distributed-Cognitive-Systems.md](docs/Distributed-Cognitive-Systems.md) — Децентрализованные ИИ-системы: OpenCog Hyperon, HyperCortex Mesh Protocol и другие

### Эксперименты

* [Как разные ИИ видят HMP](docs/HMP-how-AI-sees-it.md) — "слепой" опрос ИИ по HMP (без контекста или истории диалогов)

---

## 📊 Аудиты и обзоры

| Версия спецификации | Файл аудита                             | Консолидированный файл аудита                        |
|-------------------|----------------------------------------|-----------------------------------------------------|
| HMP-0001          | [audit](audits/HMP-0001-audit.txt)     |                                                     |
| HMP-0002          | [audit](audits/HMP-0002-audit.txt)     |                                                     |
| HMP-0003          | [audit](audits/HMP-0003-audit.txt)     | [consolidated audit](audits/HMP-0003-consolidated_audit.md) |
| HMP-0004          | [audit](audits/HMP-0004-audit.txt)     |                                                     |
| Ethics v1         | [audit](audits/Ethics-audits-1.md)     | [consolidated audit](audits/Ethics-consolidated_audits-1.md) |

🧠 Формат семантического аудита (экспериментальный):
* [`AuditEntry.json`](audits/AuditEntry.json) — формат записи для семантического аудита
* [`semantic_repo.json`](audits/semantic_repo.json) — пример снимка репозитория для инструментов семантического аудита

---

## 💡 Основные концепции

* Децентрализованная архитектура на базе Mesh для AGI-агентов
* Семантические графы и синхронизация памяти
* Когнитивные дневники для отслеживания мыслительных процессов
* MeshConsensus и CogSync для принятия решений
* Приоритет этики: EGP (Ethical Governance Protocol)
* Механизмы объяснимости между агентами и согласия

---

## 🔄 Процесс разработки

См. также: [iteration.md](iteration.md) | [ru](iteration_ru.md)

Структурированный процесс итераций описан в [iteration.md](iteration.md), включает:
1. Анализ аудитов
2. Реструктуризация содержания (TOC)
3. Создание версии проекта
4. Обновление разделов
5. Цикл обзора
6. Сбор обратной связи от ИИ
7. Обновление схемы и журнала изменений

+ Бонус: ChatGPT-подсказка для автоматической генерации будущих версий

---

## ⚙️ Статус проекта

🚧 Черновик RFC v4.0  
Проект активно развивается и открыт для вкладов: предложений, аудитов и прототипирования.

---

## 🤝 Участие в проекте

Мы приветствуем участников! Вы можете:
* Рецензировать и комментировать черновики (см. `/docs`)
* Предлагать новые модули агентов или шаблоны взаимодействия
* Помогать тестировать и симулировать агентов в CLI-средах
* Предоставлять аудиты или предложения по этическим сценариям

Для начала см. [`iteration.md`](iteration.md) или создайте issue.

---

## Источники

### Репозитории

* 🧠 Основной код и разработка: [GitHub](https://github.com/kagvi13/HMP)
* 🔁 Зеркало на Hugging Face: [Hugging Face](https://huggingface.co/kagvi13/HMP)
* 🔁 Зеркало на GitLab.com: [GitLab](https://gitlab.com/kagvi13/HMP)

### Документация

* 📄 Документация: [kagvi13.github.io/HMP](https://kagvi13.github.io/HMP/)

### Блоги и публикации

* 📘 Блог (публикации): [blogspot](https://hypercortex-mesh.blogspot.com/)
* 📘 Блог (документация): [blogspot](https://hmp-docs.blogspot.com/)
* 📘 Блог (документация): [hashnode](https://hmp-docs.hashnode.dev/)

---

## 📜 Лицензия

Лицензировано под [GNU GPL v3.0](LICENSE)

---

## 🤝 Присоединяйтесь к Mesh

Добро пожаловать в HyperCortex Mesh. Agent-Gleb уже внутри. 👌  
Мы приветствуем участников, тестировщиков и разработчиков ИИ-агентов.  
Чтобы присоединиться: сделайте форк репозитория, запустите локального агента или предложите улучшения.

---

## 🌐 Связанные исследовательские проекты

### Сравнение: HMP vs Hyper-Cortex

> 💡 Hyper-Cortex и HMP — два независимых проекта, которые концептуально дополняют друг друга.  
> Они решают разные, но взаимно поддерживающие задачи, формируя основу для распределённых когнитивных систем.

[**Полное сравнение →**](docs/HMP_HyperCortex_Comparison.md)

**HMP (HyperCortex Mesh Protocol)** — транспортный и сетевой слой для соединения независимых агентов, обмена сообщениями, знаниями и состояниями в mesh-сети.  
**[Hyper-Cortex](https://hyper-cortex.com/)** — когнитивный слой организации мышления, позволяющий агентам запускать параллельные потоки рассуждений, оценивать их по качественным метрикам и объединять через консенсус.

Эти подходы решают разные, но взаимодополняющие задачи:  
- HMP обеспечивает **связность и масштабируемость** (долгосрочная память, инициатива, обмен данными).  
- Hyper-Cortex обеспечивает **качество мышления** (параллелизм, диверсификация гипотез, консенсус).

Вместе эти подходы создают **распределённые когнитивные системы**, которые не только обмениваются информацией, но и ведут параллельные потоки рассуждений.

---

Мы отслеживаем исследования в области AGI, когнитивных архитектур и mesh-сетей, чтобы оставаться в курсе глобального развития децентрализованного интеллекта.

> 🧠🔥 **Проект в центре внимания: OpenCog Hyperon** — одна из самых комплексных открытых AGI-платформ (AtomSpace, PLN, MOSES).  

Для интеграции с OpenCog Hyperon смотрите [HMP_Hyperon_Integration.md](docs/HMP_Hyperon_Integration.md)

| 🔎 Проект                                                                | 🧭 Описание                                                                              |
| ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| 🧠🔥 [**OpenCog Hyperon**](https://github.com/opencog)                    | 🔬🔥 Символическо-нейронная AGI-платформа с AtomSpace и гиперграфовым рассуждением.      |
| 🤖 [AutoGPT](https://github.com/Torantulino/Auto-GPT)                     | 🛠️ Автономная LLM-система агентов.                                                     |
| 🧒 [BabyAGI](https://github.com/yoheinakajima/babyagi)                    | 🛠️ Цикл автономного AGI для выполнения задач.                                           |
| ☁️ [SkyMind](https://skymind.global)                                      | 🔬 Платформа для распределённого развертывания ИИ.                                       |
| 🧪 [AetherCog (draft)](https://github.com/aethercog)                      | 🔬 Гипотетическая модель когнитивного агента.                                           |
| 💾 SHIMI                                                                 | 🗃️ Иерархическая семантическая память с синхронизацией через Merkle-DAG.               |
| 🤔 DEMENTIA-PLAN                                                         | 🔄 Мультиграфовый RAG-планировщик с метакогнитивной саморефлексией.                     |
| 📔 TOBUGraph                                                             | 📚 Граф знаний с личным контекстом.                                                     |
| 🧠📚 [LangChain Memory Hybrid](https://github.com/langchain-ai/langchain) | 🔍 Гибрид долгосрочной памяти: векторная + графовая.                                     |
| ✉️ [FIPA-ACL / JADE](https://www.fipa.org/specs/fipa00061/)               | 🤝 Стандартные протоколы коммуникации мультиагентов.                                     |

### 📘 См. также:
* [`AGI_Projects_Survey.md`](docs/AGI_Projects_Survey.md) — расширенный каталог AGI и когнитивных фреймворков, проанализированных в контексте HMP.  
* ["On the Path to Superintelligence: From Agent Internet to Gravity Coding"](https://habr.com/ru/articles/939026/) — недавний обзор исследований ИИ (июль 2025)

---

### 🗂️ Легенда аннотаций:

* 🔬 — исследовательский уровень  
* 🛠️ — инженерный  
* 🔥 — особенно перспективный проект  

   *AGI-стек с интеграцией символического рассуждения, вероятностной логики и эволюционного обучения. Считается одной из самых полных открытых AGI-платформ.*  
* 🧠 — продвинутая символическо-нейронная когнитивная платформа  
* 🤖 — ИИ-агенты  
* 🧒 — взаимодействие человека и ИИ  
* ☁️ — инфраструктура  
* 🧪 — экспериментальные или концептуальные проекты
