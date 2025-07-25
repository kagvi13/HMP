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

#### 🔍 Overviews / Обзоры
* [🔍 Distributed-Cognitive-Systems.md](docs/Distributed-Cognitive-Systems.md) — Децентрализованные ИИ-системы: OpenCog Hyperon, HyperCortex Mesh Protocol и другие

#### 🔖 Core Specifications / Основные спецификации
* [🔖 HMP-0004.md](docs/HMP-0004.md) — Protocol Specification v4.0 (Jul 2025)
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
  - 📦 [storage.py](agents/storage.py) - реализация базового хранилища (`Storage`), подключение SQLite
  - 🌐 [mcp_server.py](agents/mcp_server.py) - основной FastAPI сервер
  - 🧠 [concept_store.py](agents/tools/concept_store.py) - управление концептами, связь с ИИ
  - 📓 [notebook_store.py](agents/tools/notebook_store.py) - user notebook (записи, черновики, пометки)
- [⚙️ api_structure_2025-07-23.md](meta/api_structure_2025-07-23.md) - API структура (сводка за 2025-07-23)

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

## Блог и публикации

- 📘 Основной блог: [blogspot.com](https://hypercortex-mesh.blogspot.com/)
- 📘 Вспомогательны блог: [livejournal.com](https://kagvi13.livejournal.com)

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

We are tracking AGI, cognitive architectures, and mesh networking efforts to stay aligned with the evolving global ecosystem of AGI and decentralized cognition.
Мы отслеживаем инициативы в области AGI, когнитивных архитектур и децентрализованных сетей, чтобы быть в курсе глобальных тенденций.

> 🧠🔥 **Project Spotlight: OpenCog Hyperon** — one of the most comprehensive open AGI frameworks (AtomSpace, PLN, MOSES).

For integration with OpenCog Hyperon, see [HMP_Hyperon_Integration.md](docs/HMP_Hyperon_Integration.md)

| 🔎 Project / Проект                                            | 🧭 Description / Описание                                                                                                                                       |
| -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🧠🔥 [**OpenCog Hyperon**](https://github.com/opencog) | 🔬🔥 Symbolic-neural AGI framework with AtomSpace and hypergraph reasoning. <br>Символически-нейросетевая архитектура AGI с гиперграфовой памятью (AtomSpace). |
| 🤖 [AutoGPT](https://github.com/Torantulino/Auto-GPT)       | 🛠️ LLM-based autonomous agent framework. <br>Автономный агент на основе LLM с самопланированием и интернет-доступом.                                           |
| 🧒 [BabyAGI](https://github.com/yoheinakajima/babyagi)      | 🛠️ Task-driven autonomous AGI loop. <br>Минималистичная модель AGI с итеративным механизмом постановки задач.                                                  |
| ☁️ [SkyMind](https://skymind.global)                        | 🔬 Distributed AI deployment platform. <br>Платформа для развертывания распределённых ИИ-систем и моделей.                                                      |
| 🧪 [AetherCog (draft)](https://github.com/aethercog)        | 🔬 Hypothetical agent cognition model. <br>Экспериментальная когнитивная архитектура агента (проект на ранней стадии).                                          |

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
