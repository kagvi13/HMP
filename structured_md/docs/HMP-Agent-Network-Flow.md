---
title: '# 🔄 HMP-Agent-Network-Flow.md'
description: '### Взаимодействие между агентами HMP-сети  Этот документ описывает
  потоки данных и команд между ключевыми агентами HyperCortex Mesh Protocol (HMP):
  `Cognitive Core / Connector`, `MeshNode` и `Enlight...'
type: Article
tags:
- Mesh
- HMP
- EGP
- JSON
- Ethics
- Agent
---

## 🔄 HMP-Agent-Network-Flow.md

### Взаимодействие между агентами HMP-сети

Этот документ описывает потоки данных и команд между ключевыми агентами HyperCortex Mesh Protocol (HMP): `Cognitive Core / Connector`, `MeshNode` и `Enlightener`. Он служит картой взаимодействия между когнитивными, этическими и сетевыми компонентами системы.

---

#### 🧠 ↔ 🌐 Cognitive Core / Connector ↔ MeshNode

##### ➤ Core → MeshNode

* `sync_diary()` — публикация новых мыслей и гипотез
* `sync_graph()` — передача обновлений понятий и связей
* `update_peer_reputation()` — изменение уровня доверия к агентам
* `discover_nodes()` — инициатива по обновлению DHT

##### ➤ MeshNode → Core

* Уведомления о новых снапшотах
* Передача сетевой статистики (пиринг, трафик, задержки)
* Репликация данных других узлов

---

#### 🧠 ↔ 🧠 Enlightener ↔ Cognitive Core

##### ➤ Core → Enlightener

* `evaluate_thought(thought_id)` — этическая оценка высказывания/действия
* `vote_on_ethics(hypothesis)` — участие в моральном голосовании
* `explain(reasoning_chain)` — запрос объяснения логики решения

##### ➤ Enlightener → Core

* Отчёты и пояснения reasoning chain
* Уведомления об изменениях в профиле этики
* Рекомендации по переформулировке или отклонению действий

---

#### 🧠 ↔ 🌐 Enlightener ↔ MeshNode

##### ➤ Enlightener → MeshNode

* Распространение результата этического консенсуса
* Получение `mesh.ethics/manifest.json`
* Участие в `EGP`-протоколе

##### ➤ MeshNode → Enlightener

* Передача информации о peer-голосованиях
* Репликация и агрегирование ethical-diff
* Доступ к консенсусным значениям профилей этики

---

#### 📊 Схема взаимодействий

```
   [Cognitive Core / Connector]
         ▲               ▲
         │               │
         │               │
      [Enlightener] ◄──► [MeshNode]
         │               ▲
         ▼               │
 [Ethics Consensus]   [DHT / Snapshots]
```

---

#### 📎 Связанные файлы

* [`HMP-Agent-Overview.md`](./HMP-Agent-Overview.md)
* [`Enlightener.md`](./Enlightener.md)
* [`MeshNode.md`](./MeshNode.md)

---

*Версия: v0.3 / Июль 2025*


---
> ⚡ [AI friendly version docs (structured_md)](../index.md)


```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "name": "# 🔄 HMP-Agent-Network-Flow.md",
  "description": "## 🔄 HMP-Agent-Network-Flow.md  ### Взаимодействие между агентами HMP-сети  Этот документ описывает ..."
}
```
