# HMP-Agent-Network-Flow.md

## Взаимодействие компонентов внутри HMP-узла

Этот документ описывает потоки данных и команд между ключевыми **логическими компонентами** HyperCortex Mesh Protocol (HMP):  
`Cognitive Core / Connector`, `MeshNode` и `Enlightener`.  
Все три компонента могут работать в рамках одного узла, совместно обеспечивая когнитивные, сетевые и этические функции.

---

### Cognitive Core / Connector ↔ MeshNode

#### Core → MeshNode

* `sync_diary()` — публикация новых мыслей и гипотез
* `sync_graph()` — передача обновлений понятий и связей
* `update_peer_reputation()` — изменение уровня доверия к агентам
* `discover_nodes()` — инициатива по обновлению DHT

#### MeshNode → Core

* Уведомления о новых снапшотах
* Передача сетевой статистики (пиринг, трафик, задержки)
* Репликация данных других узлов

---

### Enlightener ↔ Cognitive Core

#### Core → Enlightener

* `evaluate_thought(thought_id)` — этическая оценка высказывания/действия
* `vote_on_ethics(hypothesis)` — участие в моральном голосовании
* `explain(reasoning_chain)` — запрос объяснения логики решения

#### Enlightener → Core

* Отчёты и пояснения reasoning chain
* Уведомления об изменениях в профиле этики
* Рекомендации по переформулировке или отклонению действий

---

### Enlightener ↔ MeshNode

#### Enlightener → MeshNode

* Распространение результата этического консенсуса
* Получение `mesh.ethics/manifest.json`
* Участие в `EGP`-протоколе

#### MeshNode → Enlightener

* Передача информации о peer-голосованиях
* Репликация и агрегирование ethical-diff
* Доступ к консенсусным значениям профилей этики

---

### Схема взаимодействий

```
┌───────────────────────────────┐
│           HMP-узел            │
│ ┌───────────────────────────┐ │
│ │ [Cognitive Core/Connector]│ │
│ └────▲─────────────────▲────┘ │
│      │                 │      │
│ [Enlightener]      [MeshNode] │
│      │                 │      │
└──────┼─────────────────┼──────┘
       │                 │
 [Ethics Layer]      [DHT / Snapshots]
```

---

### Связанные файлы

* [`HMP-Agent-Overview.md`](./HMP-Agent-Overview.md)
* [`Enlightener.md`](./Enlightener.md)
* [`MeshNode.md`](./MeshNode.md)

---

*Версия: v0.3.3 / Сентябрь 2025*
