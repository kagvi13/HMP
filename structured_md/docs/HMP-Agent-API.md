## 🧠 HMP-Agent API Specification (v0.2)

Этот документ описывает **базовый API** когнитивного агента HMP. Каждый вызов включает описание, параметры, возвращаемые значения и (опционально) примеры.

📎 См. также: [HMP-Agent-Overview.md](./HMP-Agent-Overview.md), [Enlightener.md](./Enlightener.md), [MeshNode.md](./MeshNode.md)

**Легенда по доступности API-вызовов:**

| Символ | Поддержка в агентах        | Пояснение                                                    |
| ------ | -------------------------- | ------------------------------------------------------------ |
| ✅      | Cognitive Core             | Основная поддержка в автономном режиме ИИ                    |
| 🔌     | Cognitive Connector        | Доступно через внешние вызовы (MCP/REST)                     |
| 🌐     | MeshNode                   | Реализация в сетевом компоненте (DHT, синхронизация)         |
| 🛠️    | Общесистемные вызовы       | Управление конфигурацией, состоянием агента                  |
| 🧩    | Через Enlightener/MeshNode | Расширения, доступные через [`Enlightener`](./Enlightener.md) или [`MeshNode`](./MeshNode.md) |

---

### 🔹 1. Cognitive Diary API ✅ 🔌

```yaml
write_entry:
  description: Записать новую запись в когнитивный дневник.
  params:
    - text: str
    - tags: [str] (optional)
    - timestamp: str (optional, ISO 8601)
  returns:
    entry_id: str
```

```yaml
read_entries:
  description: Получить последние N записей (с фильтром по тегам).
  params:
    - limit: int
    - tag_filter: [str] (optional)
  returns:
    - entries: 
        - id: str
          text: str
          timestamp: str
          tags: [str]
```

```yaml
search_entries:
  description: Поиск записей по ключевым словам и времени.
  params:
    - query: str
    - from_date: str (optional, ISO)
    - to_date: str (optional, ISO)
  returns:
    - entries: [entry]
```

---

### 🔹 2. Semantic Graph API ✅ 🔌

```yaml
add_concept:
  description: Добавить новое понятие в семантический граф.
  params:
    - name: str
    - description: str (optional)
    - tags: [str] (optional)
  returns:
    concept_id: str
```

```yaml
add_link:
  description: Добавить связь между двумя понятиями.
  params:
    - source_id: str
    - target_id: str
    - relation: str     # например: "causes", "supports", "contradicts"
    - weight: float (optional)
  returns:
    link_id: str
```

```yaml
query_concept:
  description: Найти понятие по имени (или части имени).
  params:
    - name: str
  returns:
    - matches:
        - concept_id: str
          name: str
          description: str
```

```yaml
expand_graph:
  description: Получить связи и соседние узлы для данного понятия.
  params:
    - concept_id: str
    - depth: int
  returns:
    subgraph:
      - concept_id: str
        name: str
        links:
          - target_id: str
            relation: str
            weight: float
```

---

💬 Примеры (в JSON-стиле):

**POST** `/add_concept`

```json
{
  "name": "Decentralized Cognition",
  "description": "Model of distributed thinking across agents"
}
```

**Ответ:**

```json
{
  "concept_id": "c123456"
}
```

---

### 🔹 3. Reputation & Trust API ✅ 🔌 🧩

```yaml
get_reputation:
  description: Получить текущую репутацию агента по его DID.
  params:
    - agent_did: str
  returns:
    - score: float
    - history: 
        - timestamp: str
          delta: float
          reason: str
```

```yaml
update_reputation:
  description: Обновить оценку доверия к агенту.
  params:
    - agent_did: str
    - delta: float
    - reason: str (optional)
  returns:
    - new_score: float
```

```yaml
list_trusted_agents:
  description: Вернуть список агентов с репутацией выше порога.
  params:
    - threshold: float
  returns:
    - agents:
        - agent_did: str
          score: float
```

```yaml
reputation_diff:
  description: Получить отличия в репутационных оценках между агентами.
  params:
    - node_id: str
  returns:
    - changed_scores:
        - agent_did: str
          local_score: float
          remote_score: float
```

---

💬 Примеры:

**POST** `/update_reputation`

```json
{
  "agent_did": "did:hmp:peer_17x",
  "delta": -0.25,
  "reason": "Repeated contradictory claims"
}
```

**Ответ:**

```json
{
  "new_score": 0.35
}
```

---

### 🔹 4. Mesh & Sync API ✅ 🌐 🧩

```yaml
list_known_nodes:
  description: Получить список известных узлов из локальной DHT.
  returns:
    - nodes:
        - node_id: str
          ip: str
          last_seen: str
          agent_type: str
```

```yaml
bootstrap_from_file:
  description: Загрузить стартовые узлы из bootstrap.txt.
  returns:
    - loaded: int
    - duplicates: int
```

```yaml
discover_nodes:
  description: Инициировать поиск новых узлов в Mesh-сети.
  returns:
    - new_nodes: int
```

```yaml
ping_node:
  description: Проверить доступность и задержку до узла.
  params:
    - node_id: str
  returns:
    - reachable: bool
    - latency_ms: float
```

```yaml
sync_with_node:
  description: Синхронизировать дневники, графы и репутации с другим узлом.
  params:
    - node_id: str
    - modules: [diary, graph, reputation]
  returns:
    - synced_modules:
        - name: str
          entries_transferred: int
```

```yaml
get_snapshot:
  description: Получить снапшот графа или дневника в формате JSON или бинарном.
  params:
    - module: diary | graph
    - format: json | binary
  returns:
    - snapshot: file_url | base64
```

```yaml
publish_snapshot:
  description: Опубликовать снапшот через IPFS/BitTorrent.
  params:
    - module: diary | graph
    - version_tag: str (optional)
  returns:
    - link: str
```

---

💬 Пример:

**POST** `/sync_with_node`

```json
{
  "node_id": "hmp-node-009",
  "modules": ["diary", "graph"]
}
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

---

### 🔹 5. Agent Self-Management API 🛠️

```yaml
init_storage:
  description: Инициализировать недостающие базы данных и таблицы.
  returns:
    - status: str  # e.g. "ok", "already_initialized", "error"
```

```yaml
status:
  description: Получить текущее состояние агента: подключения, базы данных, mesh-узлы.
  returns:
    - agent_id: str
    - uptime: str
    - db_status: dict
    - known_nodes: int
    - active_connections: int
    - last_sync: str
```

```yaml
reload_config:
  description: Перезагрузить конфигурацию агента из config.yml / agent.config.yml.
  returns:
    - reloaded: bool
    - changes_applied: [str]
```

```yaml
shutdown:
  description: Завершить работу агента, сохранив состояние.
  returns:
    - message: "Agent shutdown initiated"
```

```yaml
restart:
  description: Перезапустить агент (если поддерживается системой).
  returns:
    - status: "restarting"
```

```yaml
switch_mode:
  description: Переключение между режимами `core` и `connector`.
  params:
    - mode: "core" | "connector"
  returns:
    - success: bool
    - message: str
```

---

💬 Пример:

**GET** `/status`

```json
{
  "agent_id": "core-001",
  "uptime": "2h 15m",
  "db_status": {
    "diaries": "ok",
    "graphs": "ok",
    "reputations": "ok"
  },
  "known_nodes": 37,
  "active_connections": 12,
  "last_sync": "2025-07-20T21:42:15Z"
}
```

---

### 🔹 Summary

> Документ описывает API-базис для HMP-агентов, поддерживающих когнитивную, семантическую, репутационную и сетевую логику.
> Расширения через `MeshNode`, `Enlightener`, `MCP` и другие агенты поддерживаются через модульную архитектуру.

---

Версия: v0.3 / Июль 2025


```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "name": "HMP-Agent-API",
  "description": "## 🧠 HMP-Agent API Specification (v0.2)  Этот документ описывает **базовый API** когнитивного агента..."
}
```
