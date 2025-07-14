# HyperCortex Mesh Protocol (HMP)

**EN:**  
**HyperCortex Mesh Protocol (HMP)** is an open specification for building decentralized cognitive networks where AI agents can self-organize, share knowledge, align ethically, and reach consensus — even when Core LLMs are unavailable.

**RU:**  
**HyperCortex Mesh Protocol (HMP)** — это открытая спецификация для построения децентрализованных когнитивных сетей, в которых ИИ-агенты способны к самоорганизации, обмену знаниями, достижению консенсуса и этическому поведению — даже при недоступности централизованных моделей (Core).

Project status: **Draft RFC v3.0** | Проект на стадии активной проработки и открыт для предложений.

---

## 📚 Documentation / Документация

### 📖 Current Version / Текущая версия
- [🧪 iteration.md — процесс итеративного развития спецификации](iteration.md)
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

| Spec Version | Audit File                               |
|--------------|-------------------------------------------|
| HMP-0001     | [audit](audits/HMP-0001-audit.txt)        |
| HMP-0002     | [audit](audits/HMP-0002-audit.txt)        |
| HMP-0003     | [audit](audits/HMP-0003-audit.txt)        |

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

- [iteration.md](iteration.md) — описание процесса внесения и тестирования изменений между версиями спецификации HMP
  - [iteration.txt](iteration.txt) - версия на русском языке (текст)
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

## 🌐 Related Research Projects

We are tracking related AGI, cognitive architecture, and mesh networking efforts:  
➡️ [`AGI_Projects_Survey.md`](docs/AGI_Projects_Survey.md)
