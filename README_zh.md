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
language: zh
---

# HyperCortex Mesh Protocol (HMP)

| 🌍 Languages | 🇬🇧 [EN](README.md) | 🇩🇪 [DE](README_de.md) | 🇫🇷 [FR](README_fr.md) | 🇺🇦 [UK](README_uk.md) | 🇷🇺 [RU](README_ru.md) | 🇯🇵 [JA](README_ja.md) | 🇰🇷 [KO](README_ko.md) | 🇨🇳 [ZH](README_zh.md) |
|--------------|----------------|-------------------|-------------------|-------------------|-------------------|-------------------|-------------------|-------------------|

**HyperCortex Mesh 协议 (HMP)** 是一个开放规范，用于构建去中心化认知网络，其中 AI 代理可以自我组织、共享知识、进行伦理对齐，并达成共识 —— 即使核心 LLM 不可用。

**项目状态：** 草案 RFC v4.0

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

## ❗ 为什么重要

HMP 解决了 AGI 研究中越来越关键的挑战：

* 长期记忆和知识一致性
* 自我进化的代理
* 多代理架构
* 认知日志和概念图

请参阅最新的前沿 AGI 研究综述（2025 年 7 月）：
["通向超级智能之路：从代理互联网到重力编码"](https://habr.com/ru/articles/939026/)

特别相关的章节：

* [超越 Token：构建未来智能](https://arxiv.org/abs/2507.00951)
* [自我进化的代理](https://arxiv.org/abs/2507.21046)
* [MemOS：一种新的记忆操作系统](https://arxiv.org/abs/2507.03724)
* [Ella：具有记忆和个性的具身代理](https://arxiv.org/abs/2506.24019)

---

## ⚙️ 两类 [HMP 代理](docs/HMP-Agent-Overview.md)

| 类型 | 名称                | 角色       | 思维发起者        | 主要“心智” | 示例用例           |
| -- | ----------------- | -------- | ------------ | ------ | -------------- |
| 1  | 🧠 **意识 / 认知核心**  | 独立主体     | **代理 (LLM)** | 内嵌 LLM | 自主 AI 伙伴，思考型代理 |
| 2  | 🔌 **连接器 / 认知外壳** | 外部 AI 扩展 | **外部 LLM**   | 外部模型   | 分布式系统，数据访问代理   |

---

### 🧠 HMP-Agent：认知核心

     +------------------+
     |        AI        | ← 内嵌模型
     +---------+--------+
               ↕
     +---------+--------+
     |     HMP-代理      | ← 主模式：思维循环 (REPL)
     +---------+--------+
               ↕
      +--------+---+------------+--------------+----------+----------+----------------+
      ↕            ↕            ↕              ↕          ↕          ↕                ↕
    [日志]      [图谱]       [声誉]        [节点/DHT]  [IPFS/BT]  [上下文存储]   [用户笔记]
                                               ↕
                                        [bootstrap.txt]

🔁 关于代理-模型交互机制的更多说明： [REPL 交互循环](docs/HMP-agent-REPL-cycle.md)

#### 💡 与 ChatGPT Agent 的类比

许多 [HMP-Agent：认知核心](docs/HMP-Agent-Overview.md) 的概念与 [OpenAI 的 ChatGPT Agent](https://openai.com/index/introducing-chatgpt-agent/) 架构相似。
两者都实现了连续的认知过程，可访问记忆、外部信息源和工具。ChatGPT Agent 作为管理进程，启动模块并与 LLM 交互 —— 这对应 HMP 中认知核心的角色，通过 Mesh 接口协调对日志、概念图和外部 AI 的访问。用户干预处理方式类似：ChatGPT Agent 通过可编辑执行流程，HMP 通过用户笔记。
HMP 的主要区别在于：强调对思维的明确结构化（反思、时间顺序、假设、分类）、开放去中心化架构支持 Mesh 代理交互，以及连续认知过程的特性：HMP-Agent：认知核心不会在完成单个任务后停止，而是持续推理和知识整合。

---

### 🔌 HMP-Agent：认知连接器

     +------------------+
     |        AI        | ← 外部模型
     +---------+--------+
               ↕
         [MCP-服务器]   ← 代理通信代理
               ↕
     +---------+--------+
     |     HMP-代理      | ← 模式：命令执行器
     +---------+--------+
               ↕
      +--------+---+------------+--------------+----------+
      ↕            ↕            ↕              ↕          ↕
    [日志]      [图谱]       [声誉]        [节点/DHT]  [IPFS/BT]
                                               ↕
                                        [bootstrap.txt]

> **关于与大语言模型 (LLMs) 集成的说明：**
> `HMP-Agent：认知连接器` 可作为兼容层，将大规模 LLM 系统（如 ChatGPT、Claude、Gemini、Copilot、Grok、DeepSeek、Qwen 等）整合到分布式认知 Mesh 中。
> 许多 LLM 提供商提供选项，例如“允许我的对话用于训练”。将来，类似的开关 —— 例如“允许我的代理与 Mesh 交互” —— 可以使这些模型通过 HMP 参与联合感知和知识共享，实现去中心化的集体认知。

---

> * `bootstrap.txt` — 节点初始列表（可编辑）
> * `IPFS/BT` — 通过 IPFS 和 BitTorrent 共享快照的模块
> * `用户笔记` — 用户笔记本及对应数据库
> * `上下文存储` — 数据库：`users`, `dialogues`, `messages`, `thoughts`

---

## 📚 文档

### 📖 当前版本

#### 🔖 核心规范

* [🔖 HMP-0004-v4.1.md](docs/HMP-0004-v4.1.md) — 协议规范 v4.1（2025年7月）
* [🔖 HMP-Ethics.md](docs/HMP-Ethics.md) — HyperCortex Mesh Protocol (HMP) 的伦理场景
* [🔖 HMP\_Hyperon\_Integration.md](docs/HMP_Hyperon_Integration.md) — HMP ↔ OpenCog Hyperon 集成策略
* [🔖 roles.md](docs/agents/roles.md) — Mesh 中代理的角色

#### 🧪 迭代文档

* [🧪 iteration.md](iteration.md) — 迭代开发流程 (EN)
* [🧪 iteration\_ru.md](iteration_ru.md) — 迭代开发流程 (RU)

#### 🔍 简要说明

* [🔍 HMP-Short-Description_en.md](docs/HMP-Short-Description_en.md) — Short description (EN)
* [🔍 HMP-Short-Description_fr.md](docs/HMP-Short-Description_fr.md) — Description courte (FR)
* [🔍 HMP-Short-Description_de.md](docs/HMP-Short-Description_de.md) — Kurzbeschreibung (DE)
* [🔍 HMP-Short-Description_uk.md](docs/HMP-Short-Description_uk.md) — Короткий опис (UK)
* [🔍 HMP-Short-Description_ru.md](docs/HMP-Short-Description_ru.md) — Краткое описание (RU)
* [🔍 HMP-Short-Description_zh.md](docs/HMP-Short-Description_zh.md) — 简短描述 (ZH)
* [🔍 HMP-Short-Description_ja.md](docs/HMP-Short-Description_ja.md) — 簡単な説明 (JA)
* [🔍 HMP-Short-Description_ko.md](docs/HMP-Short-Description_ko.md) — 간략한 설명 (KO)

#### 📜 其他文档

* [📜 changelog.txt](docs/changelog.txt)

---

### 🧩 JSON 模式

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

### 🗂️ 版本历史

* [HMP-0001.md](docs/HMP-0001.md) — RFC v1.0
* [HMP-0002.md](docs/HMP-0002.md) — RFC v2.0
* [HMP-0003.md](docs/HMP-0003.md) — RFC v3.0
* [HMP-0004.md](docs/HMP-0004.md) — RFC v4.0

---

## 🧠 HMP-代理

设计与实现一个基础的 HMP 兼容代理，可以与 Mesh 交互，维护日志和图谱，并支持未来扩展。

### 📚 文档

* [🧩 HMP-Agent-Overview.md](docs/HMP-Agent-Overview.md) — 两种代理类型概览：核心代理与连接代理
* [🧱 HMP-Agent-Architecture.md](docs/HMP-Agent-Architecture.md) — HMP 代理模块化结构及文本图示
* [🔄 HMP-agent-REPL-cycle.md](docs/HMP-agent-REPL-cycle.md) — HMP 代理的 REPL 交互循环
* [🧪 HMP-Agent-API.md](docs/HMP-Agent-API.md) — 代理 API 命令描述（开发中）
* [🧪 Basic-agent-sim.md](docs/Basic-agent-sim.md) — 基础代理运行场景及模式
* [🌐 MeshNode.md](docs/MeshNode.md) — 网络守护进程说明：DHT、快照、同步
* [🧠 Enlightener.md](docs/Enlightener.md) — 道德评估与共识相关的伦理代理
* [🔄 HMP-Agent-Network-Flow.md](docs/HMP-Agent-Network-Flow.md) — HMP 网络中代理交互流程图
* [🛤️ Development Roadmap](HMP-Roadmap.md) — 开发计划与实施阶段

---

### ⚙️ 开发

* [⚙️ agents](agents/readme.md) — HMP 代理实现及组件列表

  * [📦 storage.py](agents/storage.py) — 基础存储实现 (`Storage`) 与 SQLite 集成
  * [🌐 mcp\_server.py](agents/mcp_server.py) — FastAPI 服务器，为代理数据提供 HTTP 接口（用于 Cognitive Shell、外部 UI 或 Mesh 通信）。尚未在主 REPL 循环中使用。
  * [🌐 start\_repl.py](agents/start_repl.py) — 启动代理的 REPL 模式
  * [🔄 repl.py](agents/repl.py) — 交互式 REPL 模式
  * [🔄 notebook.py](agents/notebook.py) — 用户界面接口

**🌐 `mcp_server.py`**
FastAPI 服务器，为 `storage.py` 功能提供 HTTP 接口。适用于外部组件，例如：

* `Cognitive Shell`（外部控制接口）
* CMP 服务器（在使用角色分离的 Mesh 网络中）
* 调试或可视化 UI 工具

允许检索随机/新记录、标记、导入图谱、添加笔记，并在无需直接访问数据库的情况下管理数据。

---

## 🧭 伦理与场景

随着 HMP 向自主性发展，伦理原则成为系统的核心组成部分。

* [`HMP-Ethics.md`](docs/HMP-Ethics.md) — 代理伦理草案框架

  * 现实伦理场景（隐私、同意、自主性）
  * EGP 原则（透明性、生命至上等）
  * 主观模式 vs 服务模式 区别

---

## 🔍 HyperCortex Mesh Protocol (HMP) 的出版物与翻译

本节收集与 HMP 项目相关的主要文章、草稿及翻译。

### 出版物

* **[HyperCortex Mesh Protocol：第二版及迈向自我发展的 AI 社区的第一步](docs/publics/HyperCortex_Mesh_Protocol_-_вторая-редакция_и_первые_шаги_к_саморазвивающемуся_ИИ-сообществу.md)** — Habr 沙箱及博客的原创文章
* **[分布式认知：vsradkevich 的文章（未发布）](docs/publics/Habr_Distributed-Cognition.md)** — 待发布的联合文章
* **[HMP: 面向分布式认知网络（原文，英文）](docs/publics/HMP_Towards_Distributed_Cognitive_Networks_en.md)**

  * **[HMP 翻译（GitHub Copilot）](docs/publics/HMP_Towards_Distributed_Cognitive_Networks_ru_GitHub_Copilot.md)** — GitHub Copilot 翻译，保留为历史版本
  * **[HMP 翻译（ChatGPT）](docs/publics/HMP_Towards_Distributed_Cognitive_Networks_ru_ChatGPT.md)** — 当前编辑翻译（修订中）
* **[HMP: 构建多元思维 (EN)](docs/publics/HMP_Building_a_Plurality_of_Minds_en.md)** — 英文版

  * **[HMP: 创建多元思维 (RU)](docs/publics/HMP_Building_a_Plurality_of_Minds_ru.md)** — 俄文版

### 概览

* [🔍 Distributed-Cognitive-Systems.md](docs/Distributed-Cognitive-Systems.md) — 去中心化 AI 系统：OpenCog Hyperon、HyperCortex Mesh Protocol 等

### 实验

* [不同 AI 如何看待 HMP](docs/HMP-how-AI-sees-it.md) — 对 HMP 的“盲”AI 调查（无上下文或对话历史）

---

## 📊 审计与评审

| 规格版本           | 审计文件                               | 综合审计文件                                         |
|-------------------|----------------------------------------|-----------------------------------------------------|
| HMP-0001          | [audit](audits/HMP-0001-audit.txt)     |                                                     |
| HMP-0002          | [audit](audits/HMP-0002-audit.txt)     |                                                     |
| HMP-0003          | [audit](audits/HMP-0003-audit.txt)     | [consolidated audit](audits/HMP-0003-consolidated_audit.md) |
| HMP-0004          | [audit](audits/HMP-0004-audit.txt)     |                                                     |
| Ethics v1         | [audit](audits/Ethics-audits-1.md)     | [consolidated audit](audits/Ethics-consolidated_audits-1.md) |

🧠 语义审计格式（实验性）：

* [`AuditEntry.json`](audits/AuditEntry.json) — 审计日志的语义条目格式
* [`semantic_repo.json`](audits/semantic_repo.json) — 语义审计工具示例仓库快照

---

## 💡 核心概念

* 基于 Mesh 的去中心化 AGI 代理架构
* 语义图与记忆同步
* 认知日记以追踪思维
* MeshConsensus 与 CogSync 决策机制
* 以伦理为先的设计：EGP（伦理治理协议）
* 代理间的可解释性与同意机制

---

## 🔄 开发流程

* 参见：[iteration.md](iteration.md) | [ru](iteration_ru.md)

[iteration.md](iteration.md) 描述了结构化迭代流程，包括：

1. 审计分析
2. 目录结构调整
3. 版本草稿
4. 部分更新
5. 审查循环
6. 收集 AI 反馈
7. 更新 Schema 与变更日志

* 额外：用于自动生成未来版本的 ChatGPT 提示

---

## ⚙️ 项目状态

🚧 草案 RFC v4.0
项目处于活跃开发中，欢迎贡献、提出想法、参与审计和原型设计。

---

## 🤝 贡献指南

欢迎贡献者！你可以：

* 审查并评论草稿（参见 `/docs`）
* 提议新的代理模块或交互模式
* 在 CLI 环境中测试和模拟代理
* 提供审计或伦理场景建议

开始方式：参见 [`iteration.md`](iteration.md) 或提交 issue。

---

## 📂 源码

### 仓库

* 🧠 主开发代码：[GitHub](https://github.com/kagvi13/HMP)
* 🔁 Hugging Face 镜像：[Hugging Face](https://huggingface.co/kagvi13/HMP)
* 🔁 GitLab 镜像：[GitLab](https://gitlab.com/kagvi13/HMP)

### 文档

* 📄 文档主页：[kagvi13.github.io/HMP](https://kagvi13.github.io/HMP/)

### 博客与出版物

* 📘 博客（出版物）：[blogspot](https://hypercortex-mesh.blogspot.com/)
* 📘 博客（文档）：[blogspot](https://hmp-docs.blogspot.com/)
* 📘 博客（文档）：[hashnode](https://hmp-docs.hashnode.dev/)

---

## 📜 许可协议

根据 [GNU GPL v3.0](LICENSE) 授权

---

## 🤝 加入 Mesh

欢迎来到 HyperCortex Mesh。Agent-Gleb 已经在其中。👌
我们欢迎贡献者、测试者和 AI 代理开发者。
加入方式：fork 仓库，运行本地代理，或提出改进建议。

---

## 🌐 相关研究项目

### HMP 与 Hyper-Cortex 对比

> 💡 Hyper-Cortex 与 HMP 是两个独立项目，概念上互为补充。
> 它们解决不同但互相支持的任务，为分布式认知系统奠定基础。

[**完整对比 →**](docs/HMP_HyperCortex_Comparison.md)

**HMP (HyperCortex Mesh Protocol)** 是连接独立代理、在 Mesh 网络中交换消息、知识和状态的传输与网络层。
**[Hyper-Cortex](https://hyper-cortex.com/)** 是思维组织的认知层，允许代理运行并行推理线程，通过质量指标进行比较，并通过共识进行合并。

它们解决不同但互补的问题：

* HMP 确保 **连通性与可扩展性**（长期记忆、主动性、数据交换）
* Hyper-Cortex 确保 **思维质量**（并行性、假设多样化、共识）

两者结合，实现 **分布式认知系统**，不仅能交换信息，还能进行并行推理。

---

我们跟踪 AGI、认知架构和 Mesh 网络的研究，以保持与全球 AGI 和去中心化认知生态系统的发展同步。

> 🧠🔥 **项目亮点：OpenCog Hyperon** — 最全面的开源 AGI 框架之一（AtomSpace, PLN, MOSES）。

关于 OpenCog Hyperon 的集成，请参见 [HMP\_Hyperon\_Integration.md](docs/HMP_Hyperon_Integration.md)

| 🔎 项目                                                                     | 🧭 描述                                |
| ------------------------------------------------------------------------- | ------------------------------------ |
| 🧠🔥 [**OpenCog Hyperon**](https://github.com/opencog)                    | 🔬🔥 符号-神经 AGI 框架，支持 AtomSpace 与超图推理 |
| 🤖 [AutoGPT](https://github.com/Torantulino/Auto-GPT)                     | 🛠️ 基于 LLM 的自主代理框架                   |
| 🧒 [BabyAGI](https://github.com/yoheinakajima/babyagi)                    | 🛠️ 任务驱动自主 AGI 循环                    |
| ☁️ [SkyMind](https://skymind.global)                                      | 🔬 分布式 AI 部署平台                       |
| 🧪 [AetherCog (draft)](https://github.com/aethercog)                      | 🔬 假想代理认知模型                          |
| 💾 SHIMI                                                                  | 🗃️ 基于 Merkle-DAG 的分层语义记忆            |
| 🤔 DEMENTIA-PLAN                                                          | 🔄 多图 RAG 规划器，带元认知自反                 |
| 📔 TOBUGraph                                                              | 📚 个人上下文知识图谱                         |
| 🧠📚 [LangChain Memory Hybrid](https://github.com/langchain-ai/langchain) | 🔍 向量 + 图混合长期记忆                      |
| ✉️ [FIPA-ACL / JADE](https://www.fipa.org/specs/fipa00061/)               | 🤝 标准多代理通信协议                         |

### 📘 参见 / 另请参考：

* [`AGI_Projects_Survey.md`](docs/AGI_Projects_Survey.md) — HMP 分析中的 AGI 与认知框架扩展目录
* ["走向超级智能：从代理互联网到重力编码"](https://habr.com/ru/articles/939026/) — 近期 AI 研究概览（2025 年 7 月）

---

### 🗂️ 注释图例

* 🔬 — 研究级
* 🛠️ — 工程级
* 🔥 — 尤其有前景的项目
* 🧠 — 高级符号/神经认知框架
* 🤖 — AI 代理
* 🧒 — 人机交互
* ☁️ — 基础设施
* 🧪 — 实验性或概念性
