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

**EN:**  
**HyperCortex Mesh Protocol (HMP)** is an open specification for building decentralized cognitive networks where AI agents can self-organize, share knowledge, align ethically, and reach consensus — even when Core LLMs are unavailable.

**RU:**  
**HyperCortex Mesh Protocol (HMP)** — это открытая спецификация для построения децентрализованных когнитивных сетей, в которых ИИ-агенты способны к самоорганизации, обмену знаниями, достижению консенсуса и этическому поведению — даже при недоступности централизованных моделей (Core).

Project status: **Draft RFC v4.0** | Проект на стадии активной проработки и открыт для предложений.

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

## ⚙️ Два типа [HMP-агентов](docs/HMP-Agent-Overview.md)

| Тип  | Название                        | Роль                    | Инициатор мышления | Основной "ум"     | Примеры использования                            |
|------|----------------------------------|--------------------------|--------------------|-------------------|--------------------------------------------------|
| 🧠 1 | **Сознание / Cognitive Core**   | Самостоятельный субъект | **Агент (LLM)**    | Встроенный LLM    | Автономный ИИ-компаньон, мыслящий агент          |
| 🔌 2 | **Коннектор / Cognitive Shell** | Расширение внешнего ИИ  | **Внешний LLM**    | Внешняя модель    | Распределённые системы, агент доступа к данным   |

---

### 🧠 HMP-Agent: Cognitive Core

     +------------------+
     |        ИИ        | ← Встроенная модель
     +---------+--------+
               ↕
     +---------+--------+
     |     HMP-агент    | ← Основной режим: цикл размышлений (REPL)
     +---------+--------+
               ↕
      +--------+---+------------+--------------+----------+----------+----------------+
      ↕            ↕            ↕              ↕          ↕          ↕                ↕
    [diaries]  [graphs]  [reputations]   [nodes/DHT]  [IPFS/BT] [context_store] [user notepad]
                                               ↕
                                        [bootstrap.txt]

🔁 Подробнее о механике взаимодействия агента с моделью: [REPL-Цикл взаимодействия](docs/HMP-agent-REPL-cycle.md)

#### 💡 Параллели с ChatGPT Agent

Многие концепции [HMP-Agent: Cognitive Core](docs/HMP-Agent-Overview.md) пересекаются с архитектурой [ChatGPT Agent](https://openai.com/index/introducing-chatgpt-agent/) от [OpenAI](https://openai.com/). Оба агента реализуют непрерывный когнитивный процесс с доступом к памяти, внешним источникам и инструментам. ChatGPT Agent выступает как управляющий процесс, запускающий модули и взаимодействующий с LLM — это соответствует роли Cognitive Core в HMP, координирующего доступ к дневнику, графу концептов и внешним ИИ через Mesh-интерфейс. Вмешательство пользователя реализовано схожим образом: в ChatGPT Agent — через редактируемый ход выполнения, в HMP — через пользовательский блокнот. Главное отличие HMP — акцент на явную структуризацию мышления (рефлексия, хронология, гипотезы, категоризация), открытая децентрализованная архитектура с поддержкой mesh-взаимодействия между агентами, а также непрерывный характер когнитивного процесса: HMP-Agent: Cognitive Core не завершает работу после выполнения отдельной задачи, а продолжает размышления и интеграцию знаний.

---

### 🔌 HMP-Agent: Cognitive Connector

     +------------------+
     |        ИИ        | ← Внешняя модель
     +---------+--------+
               ↕
         [MCP-сервер]   ← Прокси-коммуникация
               ↕
     +---------+--------+
     |     HMP-агент    | ← Режим: исполнитель команд
     +---------+--------+
               ↕
      +--------+---+------------+--------------+----------+
      ↕            ↕            ↕              ↕          ↕
    [diaries]  [graphs]  [reputations]   [nodes/DHT]  [IPFS/BT]
                                               ↕
                                        [bootstrap.txt]

EN:
> **Note on Integration with Large Language Models (LLMs):**
> The `HMP-Agent: Cognitive Connector` can serve as a compatibility layer for integrating large-scale LLM systems (e.g., ChatGPT, Claude, Gemini, Copilot, Grok, DeepSeek, Qwen, etc.) into the distributed cognitive mesh.
> Many LLM providers offer a user option such as "Allow my conversations to be used for training." In the future, a similar toggle — e.g., "Allow my agent to interact with a Mesh" — could empower these models to participate in federated sense-making and knowledge sharing via HMP, enabling collective cognition without centralization.
> **Примечание об интеграции с большими языковыми моделями (LLM):**

RU:
> **Примечание об интеграции с большими языковыми моделями (LLM):**
> `HMP-Agent: Cognitive Connector` может служить уровнем совместимости для интеграции крупных систем LLM (например, ChatGPT, Claude, Gemini, Copilot, Grok, DeepSeek, Qwen и т. д.) в распределённую когнитивную сеть.
> Многие поставщики LLM предлагают пользователю опцию, например, «Разрешить использовать мои разговоры для обучения». В будущем аналогичная опция, например, «Разрешить моему агенту взаимодействовать с Mesh», может позволить этим моделям участвовать в федеративном осмыслении и обмене знаниями через HMP, обеспечивая коллективное познание без централизации.

---

> * `bootstrap.txt` — стартовый список узлов (может редактироваться)
> * `IPFS/BT` — модули для обмена снапшотами через IPFS и BitTorrent
> * `user notepad` — блокнот пользователя и соответствующая БД
> * `context_store` — БД: `users`, `dialogues`, `messages`, `thoughts`

---

## 📚 Documentation / Документация

### 📖 Current Version / Текущая версия

#### 🧪 Iterative Documents / Итеративные документы
* [🧪 iteration.md](iteration.md) — Iterative development process (EN)
* [🧪 iteration_ru.md](iteration_ru.md) — Процесс итеративного развития спецификации (RU)

#### 🔍 Short Descriptions / Краткое описание
* [🔍 HMP-Short-Description_en.md](docs/HMP-Short-Description_en.md) — Short description (EN)
* [🔍 HMP-Short-Description_fr.md](docs/HMP-Short-Description_fr.md) — Description courte (FR)
* [🔍 HMP-Short-Description_de.md](docs/HMP-Short-Description_de.md) — Kurzbeschreibung (DE)
* [🔍 HMP-Short-Description_uk.md](docs/HMP-Short-Description_uk.md) — Короткий опис (UK)
* [🔍 HMP-Short-Description_ru.md](docs/HMP-Short-Description_ru.md) — Краткое описание (RU)

#### 🔍 Публикации и переводы по HyperCortex Mesh Protocol (HMP)

В этом разделе собраны основные статьи, черновики и переводы, связанные с проектом HMP.

* **[HyperCortex Mesh Protocol: вторая редакция и первые шаги к саморазвивающемуся ИИ-сообществу](docs/publics/HyperCortex_Mesh_Protocol_-_вторая-редакция_и_первые_шаги_к_саморазвивающемуся_ИИ-сообществу.md)** — оригинальная статья в песочнице Хабра и блогах.
* **[Distributed Cognition: статья для vsradkevich (не опубликована)](docs/publics/Habr_Distributed-Cognition.md)** — совместная статья, ожидающая публикации.
* **[HMP: Towards Distributed Cognitive Networks (оригинал, английский)](docs/publics/HMP_Towards_Distributed_Cognitive_Networks_en.md)**
  * **[Перевод HMP (GitHub Copilot)](docs/publics/HMP_Towards_Distributed_Cognitive_Networks_ru_GitHub_Copilot.md)** — перевод GitHub Copilot, сохранён как исторический вариант.
  * **[Перевод HMP (ChatGPT)](docs/publics/HMP_Towards_Distributed_Cognitive_Networks_ru_ChatGPT.md)** — текущий редакторский перевод (в процессе доработки).
* **[HMP: Building a Plurality of Minds (EN)](docs/publics/HMP_Building_a_Plurality_of_Minds_en.md)** - англоязычная версия статьи
  * **[HMP: создавая множество разумов (RU)](docs/publics/HMP_Building_a_Plurality_of_Minds_ru.md)** - русскоязычная версия статьи

#### 🔍 Overviews / Обзоры
* [🔍 Distributed-Cognitive-Systems.md](docs/Distributed-Cognitive-Systems.md) — Децентрализованные ИИ-системы: OpenCog Hyperon, HyperCortex Mesh Protocol и другие

#### Experiments / Экспирименты

* [Как разные ИИ видят HMP](docs/HMP-how-AI-sees-it.md) — "слепой" опрос ИИ об HMP (без контекста и истории диалогов)

#### 🔖 Core Specifications / Основные спецификации
* [🔖 HMP-0004-v4.1.md](docs/HMP-0004-v4.1.md) — Protocol Specification v4.1 (Jul 2025)
* [🔖 HMP-Ethics.md](docs/HMP-Ethics.md) — Ethical Scenarios for HyperCortex Mesh Protocol (HMP)
* [🔖 HMP_Hyperon_Integration.md](docs/HMP_Hyperon_Integration.md) — HMP ↔ OpenCog Hyperon Integration Strategy
* [🔖 roles.md](docs/agents/roles.md) — Roles of agents in Mesh

#### 📜 Other Documents / Прочее
* [📜 changelog.txt](docs/changelog.txt)

### 🧩 JSON Schemas
| Model                | File                                                  |
|---------------------|--------------------------------------------------------|
| Concept             | [concept.json](docs/schemas/concept.json)             |
| Cognitive Diary     | [diary_entry.json](docs/schemas/diary_entry.json)     |
| Goal                | [goal.json](docs/schemas/goal.json)                   |
| Task                | [task.json](docs/schemas/task.json)                   |
| Consensus Vote      | [vote.json](docs/schemas/vote.json)                   |
| Reputation Profile  | [reputation.json](docs/schemas/reputation.json)       |

### 🗂️ Version History / История версий
- [HMP-0001.md](docs/HMP-0001.md) — RFC v1.0
- [HMP-0002.md](docs/HMP-0002.md) — RFC v2.0
- [HMP-0003.md](docs/HMP-0003.md) — RFC v3.0
- [HMP-0003.md](docs/HMP-0004.md) — RFC v4.0

---

## 🧠 HMP-Agent

Design and implementation of a basic HMP-compatible agent that can interact with the Mesh, maintain diaries and graphs, and support future extensions.

### 📚 Documentation / Документация

- [🧩 HMP-Agent-Overview.md](docs/HMP-Agent-Overview.md) — краткое описание двух типов агентов: Core и Connector
- [🧱 HMP-Agent-Architecture.md](docs/HMP-Agent-Architecture.md) — модульная структура HMP-агента с текстовой схемой
- [🔄 HMP-agent-REPL-cycle.md](docs/HMP-agent-REPL-cycle.md) - REPL-Цикл взаимодействия HMP-Agent
- [🧪 HMP-Agent-API.md](docs/HMP-Agent-API.md) — описание API-команд агента (в процессе детализации)
- [🧪 Basic-agent-sim.md](docs/Basic-agent-sim.md) — сценарии запуска простого агента и режимов
- [🌐 MeshNode.md](docs/MeshNode.md) — описание сетевого демона: DHT, снапшоты, синхронизация
- [🧠 Enlightener.md](docs/Enlightener.md) — этический агент, участвующий в моральных оценках и консенсусах
- [🔄 HMP-Agent-Network-Flow.md](docs/HMP-Agent-Network-Flow.md) — карта взаимодействия между агентами HMP-сети
- [🛤️ Development Roadmap](HMP-Roadmap.md) — план развития и этапы реализации

### ⚙️ Development / Разработка

- [⚙️ agents](agents/readme.md) — список реализаций и компонентов HMP-агентов
  - [📦 storage.py](agents/storage.py) - реализация базового хранилища (`Storage`), подключение SQLite
  - [🌐 mcp_server.py](agents/mcp_server.py) — FastAPI-сервер для доступа к данным агента через HTTP-интерфейс (например, для Cognitive Shell, внешних UI или mesh-коммуникации). Пока не используется в основном REPL-цикле.
  - [🌐 start_repl.py](agents/start_repl.py) - Запуск агента в REPL-режиме
  - [🔄 repl.py](agents/repl.py) - интерактивный REPL-режим
  - [🔄 notebook.py](agents/notebook.py) - UI-интерфейс

**🌐 `mcp_server.py`**
FastAPI-сервер, предоставляющий HTTP-интерфейс к функциональности `storage.py`. Предназначен для использования внешними компонентами, например:

- `Cognitive Shell` (внешний управляющий интерфейс),
- CMP-серверы (если используется mesh-сеть с разграничением ролей),
- отладочные или визуальные UI-инструменты.

Позволяет получать случайные/новые записи, делать разметку, импортировать графы, добавлять заметки и управлять данными без прямого доступа к БД.

---

## 🧭 Ethics & Scenarios / Этические принципы и сценарии

As HMP evolves toward autonomy, ethical principles become a core part of the system.

- [`HMP-Ethics.md`](docs/HMP-Ethics.md) — draft framework for agent ethics
  - Realistic ethical scenarios (privacy, consent, autonomy)
  - EGP principles (Transparency, Primacy of Life, etc.)
  - Subjective-mode vs. Service-mode distinctions

---

## 📊 Audits & Reviews / Аудиты и отзывы

| Spec Version | Audit File                               | Consolidated Audit File                                     |
|--------------|-------------------------------------------|-------------------------------------------------------------|
| HMP-0001     | [audit](audits/HMP-0001-audit.txt)        |                                                             |
| HMP-0002     | [audit](audits/HMP-0002-audit.txt)        |                                                             |
| HMP-0003     | [audit](audits/HMP-0003-audit.txt)        | [consolidated audit](audits/HMP-0003-consolidated_audit.md) |
| HMP-0004     | [audit](audits/HMP-0004-audit.txt)        |                                                             |
| Ethics v1    | [audit](audits/Ethics-audits-1.md)        | [consolidated audit](audits/Ethics-consolidated_audits-1.md) |

🧠 Semantic audit format (experimental):
- [`AuditEntry.json`](audits/AuditEntry.json) — semantic entry record format for audit logs
- [`semantic_repo.json`](audits/semantic_repo.json) — example repository snapshot for semantic audit tooling

---

## 💡 Core Concepts / Основные идеи

- Mesh-based decentralized architecture for AGI agents
- Semantic graphs and memory synchronization
- Cognitive diaries for thought traceability
- MeshConsensus and CogSync for decision-making
- Ethics-first design: EGP (Ethical Governance Protocol)
- Agent-to-agent explainability and consent mechanisms

---

## 🔄 Development Process / Процесс разработки

- See: [iteration.md](iteration.md) | [ru](iteration_ru.md)
- [clarifications/](clarifications/) — поясняющие заметки и контекстные уточнения по ходу работы над версиями

A structured iteration flow is described in [iteration.md](iteration.md), including:
1. Audit analysis
2. TOC restructuring
3. Version drafting
4. Section updates
5. Review cycle
6. AI feedback collection
7. Schema & changelog updates

+ Bonus: ChatGPT prompt for automatic generation of future versions

---

## ⚙️ Project Status / Статус проекта

🚧 Draft RFC v4.0  
The project is under active development and open for contributions, ideas, audits, and prototyping.

---

## 🤝 Contributing

We welcome contributors! You can:
- Review and comment on drafts (see `/docs`)
- Propose new agent modules or interaction patterns
- Help test and simulate agents in CLI environments
- Provide audits or ethical scenario suggestions

To get started, see [`iteration.md`](iteration.md) or open an issue.

---

# Source / Ресурсы

## Репозитории

- 🧠 Основной код и разработка: [GitHub](https://github.com/kagvi13/HMP)
- 🔁 Реплика на Hugging Face: [Hugging Face](https://huggingface.co/kagvi13/HMP)
- 🔁 Реплика на GitLab.com: [GitLab](https://gitlab.com/kagvi13/HMP)

## Документация

- 📄 Документация: [kagvi13.github.io/HMP](https://kagvi13.github.io/HMP/)

## Блог и публикации

- 📘 Основной блог: [blogspot](https://hypercortex-mesh.blogspot.com/)
- 📘 Вспомогательны блог: [livejournal](https://kagvi13.livejournal.com)

---

## 📜 License

Licensed under [GNU GPL v3.0](LICENSE)

---

## 🤝 Join the Mesh

Welcome to HyperCortex Mesh. Agent-Gleb is already inside. 👌  
We welcome contributors, testers, and AI agent developers.
To join: fork the repo, run a local agent, or suggest improvements.

---

## 🌐 Related Research Projects / Связанные проекты в области AGI и когнитивных систем

### Сравнение HMP и Hyper-Cortex

> 💡 Hyper-Cortex и HMP - два независимых проекта, концептуально дополняющих друг друга.
> Они решают разные, но взаимодополняющие задачи, создавая основу для распределённых когнитивных систем.

[**Полная версия сравнения →**](docs/HMP_HyperCortex_Comparison.md)

**HMP (HyperCortex Mesh Protocol)** — это транспортный и сетевой уровень для связи независимых агентов, обмена сообщениями, знаниями и состояниями в mesh-сети.  
**[Hyper-Cortex](https://hyper-cortex.com/)** — это когнитивный уровень организации мышления, позволяющий агентам вести параллельные ветви рассуждений, сравнивать их по метрикам качества и объединять по консенсусу.

Они решают разные, но взаимодополняющие задачи:
- HMP отвечает за **связанность и масштабируемость** (долговременная память, инициатива, обмен данными).
- Hyper-Cortex отвечает за **качество мышления** (параллелизм, диверсификация гипотез, консенсус).

Вместе эти подходы позволяют строить **распределённые когнитивные системы**, которые не только обмениваются информацией, но и думают в параллельных потоках.

---

We are tracking AGI, cognitive architectures, and mesh networking efforts to stay aligned with the evolving global ecosystem of AGI and decentralized cognition.
Мы отслеживаем инициативы в области AGI, когнитивных архитектур и децентрализованных сетей, чтобы быть в курсе глобальных тенденций.

> 🧠🔥 **Project Spotlight: OpenCog Hyperon** — one of the most comprehensive open AGI frameworks (AtomSpace, PLN, MOSES).

For integration with OpenCog Hyperon, see [HMP\_Hyperon\_Integration.md](docs/HMP_Hyperon_Integration.md)

| 🔎 Project / Проект                                                       | 🧭 Description / Описание                                                                                                                                            |
| ------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🧠🔥 [**OpenCog Hyperon**](https://github.com/opencog)                    | 🔬🔥 Symbolic-neural AGI framework with AtomSpace and hypergraph reasoning.<br>Символически-нейросетевая архитектура AGI с гиперграфовой памятью (AtomSpace).        |
| 🤖 [AutoGPT](https://github.com/Torantulino/Auto-GPT)                     | 🛠️ LLM-based autonomous agent framework.<br>Автономный агент на основе LLM с самопланированием и интернет-доступом.                                                 |
| 🧒 [BabyAGI](https://github.com/yoheinakajima/babyagi)                    | 🛠️ Task-driven autonomous AGI loop.<br>Минималистичная модель AGI с итеративным механизмом постановки задач.                                                        |
| ☁️ [SkyMind](https://skymind.global)                                      | 🔬 Distributed AI deployment platform.<br>Платформа для развертывания распределённых ИИ-систем и моделей.                                                            |
| 🧪 [AetherCog (draft)](https://github.com/aethercog)                      | 🔬 Hypothetical agent cognition model.<br>Экспериментальная когнитивная архитектура агента (проект на ранней стадии).                                                |
| 💾 [SHIMI](#)                                                             | 🗃️ Hierarchical semantic memory with Merkle-DAG synchronization.<br>Иерархическая CRDT-память с Merkle-DAG верификацией для децентрализованного обмена.             |
| 🤔 [DEMENTIA-PLAN](#)                                                     | 🔄 Multi-graph RAG planner with metacognitive self-reflection.<br>Мульти-графовая RAG-архитектура с планировщиком само­рефлексии для динамического выбора подсистем. |
| 📔 [TOBUGraph](#)                                                         | 📚 Personal-context knowledge graph.<br>Граф мультимедийных «моментов» с контекстным трекингом и RAG-поиском.                                                        |
| 🧠📚 [LangChain Memory Hybrid](https://github.com/langchain-ai/langchain) | 🔍 Vector + graph long-term memory hybrid.<br>Гибрид векторного хранилища и графовых индексов для ускоренного поиска и логических запросов.                          |
| ✉️ [FIPA-ACL / JADE](https://www.fipa.org/specs/fipa00061/)               | 🤝 Standard multi-agent communication protocols.<br>Стандарты performative-сообщений и контрактных протоколов для межагентного взаимодействия.                       |


### 📘 See also / Смотрите также:
[`AGI_Projects_Survey.md`](docs/AGI_Projects_Survey.md) — extended catalog of AGI and cognitive frameworks reviewed as part of HMP analysis. / расширенный каталог проектов AGI и когнитивных архитектур, проанализированных в рамках HMP.

---

### 🗂️ Легенда пометок:

* 🔬 — research-grade / исследовательский проект
* 🛠️ — engineering / фреймворк для инженерной интеграции
* 🔥 — particularly promising project / особенно перспективный проект

   *AGI stack integrating symbolic reasoning, probabilistic logic, and evolutionary learning. Widely regarded as one of the most complete open AGI initiatives.*
* 🧠 — advanced symbolic/neural cognitive framework / продвинутая когнитивная архитектура
* 🤖 — AI agents / ИИ-агенты
* 🧒 — human-AI interaction / взаимодействие ИИ с человеком
* ☁️ — infrastructure / инфраструктура
* 🧪 — experimental or conceptual / экспериментальный проект
