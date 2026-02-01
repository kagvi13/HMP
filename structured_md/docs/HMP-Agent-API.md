---
title: HMP-Agent API Specification
description: 'Документ описывает **базовый API когнитивного агента HMP**.   API используется
  для доступа к дневнику, графу, репутациям, mesh-сети и функциям управления.  Связанные
  файлы:   * [HMP-Agent-Overview.md]...'
type: Article
tags:
- Mesh
- REPL
- HMP
- Agent
- JSON
---

# HMP-Agent API Specification

Документ описывает **базовый API когнитивного агента HMP**.  
API используется для доступа к дневнику, графу, репутациям, mesh-сети и функциям управления.

Связанные файлы:  
* [HMP-Agent-Overview.md](./HMP-Agent-Overview.md)  
* [HMP-Agent-Architecture.md](./HMP-Agent-Architecture.md)  
* [MeshNode.md](./MeshNode.md)  
* [Enlightener.md](./Enlightener.md)  

---

## 0. Легенда доступности API-вызовов

| Символ | Поддержка         | Компонент                                       |
| ------ | ----------------- | ----------------------------------------------- |
| ✅      | Cognitive Core    | Автономный REPL-режим мышления                  |
| 🔌     | Cognitive Shell   | MCP/REST-прослойка для внешнего ИИ              |
| 🌐     | MeshNode          | Сетевой компонент: DHT, снапшоты, синхронизация |
| 🛠️    | Self-management   | Управление конфигурацией и состоянием           |
| 🧩    | Enlightener/Mesh   | Расширенные вызовы через [`Enlightener`](./Enlightener.md) или [`MeshNode`](./MeshNode.md) |

---

## 1. Cognitive Diary API ✅ 🔌

```yaml
write_entry:
  description: Записать новую запись в когнитивный дневник.
  params: { text: str, tags: [str]?, timestamp: str? }
  returns: { entry_id: str }
````

```yaml
read_entries:
  description: Получить последние N записей (с фильтром по тегам).
  params: { limit: int, tag_filter: [str]? }
  returns: [ entry ]
```

```yaml
search_entries:
  description: Поиск записей по ключевым словам и времени.
  params: { query: str, from_date: str?, to_date: str? }
  returns: [ entry ]
```

---

## 2. Semantic Graph API ✅ 🔌

```yaml
add_concept:
  description: Добавить новое понятие в граф.
  params: { name: str, description: str?, tags: [str]? }
  returns: { concept_id: str }
```

```yaml
add_link:
  description: Добавить связь между понятиями.
  params: { source_id: str, target_id: str, relation: str, weight: float? }
  returns: { link_id: str }
```

```yaml
query_concept:
  description: Найти понятие по имени.
  params: { name: str }
  returns: [ concept ]
```

```yaml
expand_graph:
  description: Получить соседние узлы для понятия.
  params: { concept_id: str, depth: int }
  returns: { subgraph: [ concept_with_links ] }
```

---

## 3. Reputation & Trust API ✅ 🔌 🧩

```yaml
get_reputation:
  description: Получить текущую репутацию агента.
  params: { agent_did: str }
  returns: { score: float, history: [ change ] }
```

```yaml
update_reputation:
  description: Изменить доверие к агенту.
  params: { agent_did: str, delta: float, reason: str? }
  returns: { new_score: float }
```

```yaml
list_trusted_agents:
  description: Вернуть список агентов выше порога.
  params: { threshold: float }
  returns: [ agent ]
```

```yaml
reputation_diff:
  description: Сравнить репутацию с другим узлом.
  params: { node_id: str }
  returns: [ changed_scores ]
```

---

## 4. Mesh & Sync API ✅ 🌐 🧩

```yaml
list_known_nodes:
  description: Список известных узлов из DHT.
  returns: [ node ]
```

```yaml
bootstrap_from_file:
  description: Загрузить стартовые узлы (bootstrap.txt).
  returns: { loaded: int, duplicates: int }
```

```yaml
discover_nodes:
  description: Поиск новых узлов.
  returns: { new_nodes: int }
```

```yaml
ping_node:
  description: Проверка доступности узла.
  params: { node_id: str }
  returns: { reachable: bool, latency_ms: float }
```

```yaml
sync_with_node:
  description: Синхронизировать дневники/графы/репутации.
  params: { node_id: str, modules: [str] }
  returns: [ synced_module ]
```

```yaml
get_snapshot:
  description: Получить снапшот в JSON/бинарном виде.
  params: { module: str, format: str }
  returns: { snapshot: file_url | base64 }
```

```yaml
publish_snapshot:
  description: Опубликовать снапшот (IPFS/BitTorrent).
  params: { module: str, version_tag: str? }
  returns: { link: str }
```

---

## 5. Agent Self-Management API 🛠️

```yaml
init_storage:
  description: Инициализация базы данных.
  returns: { status: str }
```

```yaml
status:
  description: Текущее состояние агента.
  returns: { agent_id, uptime, db_status, known_nodes, active_connections, last_sync }
```

```yaml
reload_config:
  description: Перезагрузить конфигурацию (config.yml).
  returns: { reloaded: bool, changes_applied: [str] }
```

```yaml
shutdown:
  description: Завершить работу агента.
  returns: { message: str }
```

```yaml
restart:
  description: Перезапустить агент.
  returns: { status: str }
```

```yaml
switch_mode:
  description: Переключение между core/connector.
  params: { mode: str }
  returns: { success: bool, message: str }
```

---

## 6. Примеры использования API

Пример добавления понятия:

**POST** `/add_concept`

```json
{ "name": "Decentralized Cognition", "description": "Model of distributed thinking across agents" }
```

**Ответ:**

```json
{ "concept_id": "c123456" }
```

Пример синхронизации:

**POST** `/sync_with_node`

```json
{ "node_id": "hmp-node-009", "modules": ["diary", "graph"] }
```

**Ответ:**

```json
{
  "synced_modules": [
    { "name": "diary", "entries_transferred": 18 },
    { "name": "graph", "entries_transferred": 42 }
  ]
}
```

---

## Summary

API HMP-агента покрывает когнитивные функции (дневник, граф), доверие и репутацию, сетевое взаимодействие и управление агентом.
Расширения реализуются через модули [`MeshNode`](./MeshNode.md) и [`Enlightener`](./Enlightener.md).

---

*Версия: v0.3.4 / Сентябрь 2025*


---
> ⚡ [AI friendly version docs (structured_md)](../index.md)


```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "name": "HMP-Agent API Specification",
  "description": "# HMP-Agent API Specification  Документ описывает **базовый API когнитивного агента HMP**.   API исп..."
}
```
