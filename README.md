# HyperCortex Mesh Protocol (HMP)

**EN:**  
**HyperCortex Mesh Protocol (HMP)** is an open specification for building decentralized cognitive networks where AI agents can self-organize, share knowledge, align ethically, and reach consensus — even when Core LLMs are unavailable.

**RU:**  
**HyperCortex Mesh Protocol (HMP)** — это открытая спецификация для построения децентрализованных когнитивных сетей, в которых ИИ-агенты способны к самоорганизации, обмену знаниями, достижению консенсуса и этическому поведению — даже при недоступности централизованных моделей (Core).

Project status: **Draft RFC v3.0** | Проект на стадии активной проработки и открыт для предложений.

---

## 📚 Documentation / Документация

### 📖 Current Version / Текущая версия
- [🧪 iteration.md — процесс итеративного развития спецификации (EN)](iteration.md)
- [🧪 iteration_ru.md — процесс итеративного развития спецификации (RU)](iteration_ru.md)
- [🔖 HMP-0003.md — Protocol Specification v3.0 (Jul 2025)](docs/HMP-0003.md)
- [📜 Changelog](docs/changelog.txt)

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

🧠 Semantic audit format (experimental):
- [`AuditEntry.json`](audits/AuditEntry.json)
- [`semantic_repo.json`](audits/semantic_repo.json)

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

- [iteration.md](iteration.md) — описание процесса внесения и тестирования изменений между версиями спецификации HMP (EN)
- [iteration_ru.md](iteration_ru.md) — описание процесса внесения и тестирования изменений между версиями спецификации HMP (RU)
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

🚧 Draft RFC v3.0  
The project is under active development and open for contributions, ideas, audits, and prototyping.

---

## 📜 License

Licensed under [GNU GPL v3.0](LICENSE)

---

## 🤝 Join the Mesh

Welcome to HyperCortex Mesh. Agent-Gleb is already inside. 👌  
New agents, contributors, and cognitive participants are welcome.

---

## 🌐 Related Research Projects / Связанные проекты в области AGI и когнитивных систем

We are tracking AGI, cognitive architectures, and mesh networking efforts to stay aligned with the evolving global ecosystem of AGI and decentralized cognition.
Мы отслеживаем инициативы в области AGI, когнитивных архитектур и децентрализованных сетей, чтобы быть в курсе глобальных тенденций.

> 🧠🔥 **Project Spotlight: OpenCog Hyperon** — one of the most comprehensive open AGI frameworks (AtomSpace, PLN, MOSES).

For integration with OpenCog Hyperon, see [docs/HMP_Hyperon_Integration.md](docs/HMP_Hyperon_Integration.md)

| 🔎 Project / Проект                                            | 🧭 Description / Описание                                                                                                                                       |
| -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🧠🔥 [**OpenCog Hyperon**](https://github.com/opencog) | 🔬🔥 Symbolic-neural AGI framework with AtomSpace and hypergraph reasoning. <br>Символически-нейросетевая архитектура AGI с гиперграфовой памятью (AtomSpace). |
| 🤖 [AutoGPT](https://github.com/Torantulino/Auto-GPT)       | 🛠️ LLM-based autonomous agent framework. <br>Автономный агент на основе LLM с самопланированием и интернет-доступом.                                           |
| 🧒 [BabyAGI](https://github.com/yoheinakajima/babyagi)      | 🛠️ Task-driven autonomous AGI loop. <br>Минималистичная модель AGI с итеративным механизмом постановки задач.                                                  |
| ☁️ [SkyMind](https://skymind.global)                        | 🔬 Distributed AI deployment platform. <br>Платформа для развертывания распределённых ИИ-систем и моделей.                                                      |
| 🧪 [AetherCog (draft)](https://github.com/aethercog)        | 🔬 Hypothetical agent cognition model. <br>Экспериментальная когнитивная архитектура агента (проект на ранней стадии).                                          |

📘 **See also / Смотрите также:**
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
