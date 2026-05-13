---
title: HyperCortex Mesh Protocol (HMP) — 简要说明
description: '**版本：** v5.0（Core Specification Stable）   **日期：** 2026    ---  ## 什么是
  HMP？  **HyperCortex Mesh Protocol（HMP）** 是一项开放规范，用于构建去中心化的自主智能体认知网络。  HMP 使智能体能够：  -
  维持长期认知连续性， - 交换结构化知识， - 协调目标与行动， - 实现分布式共识， -...'
type: Article
tags:
- REPL
- Agent
- Mesh
- HMP
---

# HyperCortex Mesh Protocol (HMP) — 简要说明

**版本：** v5.0（Core Specification Stable）  
**日期：** 2026  

---

## 什么是 HMP？

**HyperCortex Mesh Protocol（HMP）** 是一项开放规范，用于构建去中心化的自主智能体认知网络。

HMP 使智能体能够：

- 维持长期认知连续性，
- 交换结构化知识，
- 协调目标与行动，
- 实现分布式共识，
- 在异构系统之间实现伦理对齐。

不同于传统的无状态 AI API，HMP 将智能体视为嵌入在共享推理与记忆 Mesh 中的持久性认知实体。

---

## 概念基础

HMP 旨在解决当前 AI 与 AGI 研究中的关键问题：

- 缺乏长期记忆连续性，
- 缺少去中心化协调机制，
- 自主智能体之间的互操作性不足，
- 协议层缺乏伦理治理机制。

HMP 提出一种分层架构，将推理、记忆、治理与传输明确分离，同时保持互操作性。

---

## 核心概念

### 认知智能体

自主实体，能够：

- 使用内嵌或外部 AI 模型进行推理，
- 维护语义图谱，
- 在认知日志中记录决策，
- 参与分布式协调。

HMP 定义两种智能体类型：

- **Cognitive Core** —— 具有内嵌推理模型与持续 REPL 思维循环的智能体。
- **Cognitive Connector** —— 作为外部 LLM 系统兼容层的智能体。

---

### 容器（Containers）

HMP 引入 **容器（Containers）** 作为原子级认知单元。

容器具有以下特性：

- 已签名，
- 可验证，
- 可在 Mesh 网络中传输，
- 结构上独立于实现语言。

它们连接本地推理与分布式协调。

---

### 语义图谱与认知日志

- **语义图谱** 表示带权关系的结构化知识。
- **认知日志** 存储按时间顺序排列的推理过程、假设、观察与反思。

二者共同提供思维可追溯性与记忆持久性。

---

### 分布式协调

HMP 在协议层提供机制以支持：

- 目标生命周期管理，
- 分布式共识，
- 伦理评估，
- 跨智能体查询与自省。

治理机制具有演化性，并基于提案机制运行。

---

## 协议架构（v5）

HMP 将系统划分为：

1. **认知层** —— 推理、日志、图谱、信誉。
2. **容器层** —— 原子化、签名化的状态表示。
3. **核心协议层** —— 共识、治理、目标管理、伦理机制。
4. **传输层** —— DHT、P2P、libp2p、ANP 或自定义网络方案。

这种分离结构支持模块化、可扩展性与互操作性。

---

## 信任与可验证性

- 容器与快照的加密签名
- 信誉档案机制
- 可选的 Sybil 攻击防护机制
- 面向未来的后量子密码兼容性

信任被视为协议级核心属性。

---

## 互操作性

HMP 不强制规定内部认知架构。

它可与以下系统互操作：

- ANP（Agent Network Protocol）
- OpenCog Hyperon
- 事件驱动型基础设施
- 通过 Cognitive Connector 接入的 LLM 系统

HMP 关注的是认知连续性，而不仅仅是传输标准化。

---

## 应用场景示例

- 分布式科学协作
- 多智能体研究系统
- AI 伦理治理网络
- 持久型 AI 伙伴
- 基于 Mesh 的知识生态系统

---

## 当前状态

- **v5.0 Core Specification — Stable**
- Early exploratory Python drafts（非生产级，仅用于示例）
- 持续进行架构优化
- 欢迎审计与贡献

---

## 了解更多

- [Project Philosophy](PHILOSOPHY.md)
- [HMP-0005 Core Specification](HMP-0005.md)
- [Overview of v5 Architecture (RU)](HMPv5_Overview_Ru.md)

欢迎通过主仓库参与贡献与讨论。


---
> ⚡ [AI friendly version docs (structured_md)](../index.md)


```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "name": "HyperCortex Mesh Protocol (HMP) — 简要说明",
  "description": "# HyperCortex Mesh Protocol (HMP) — 简要说明  **版本：** v5.0（Core Specification Stable）   **日期：** 2026    ..."
}
```
