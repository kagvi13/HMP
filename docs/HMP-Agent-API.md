## 🧠 HMP-Agent API Specification (v0.2)

Этот документ описывает **базовый API** когнитивного агента HMP. Каждый вызов включает описание, параметры, возвращаемые значения и (опционально) пример использования.

* ✅ Поддерживается в `🧠 Cognitive Core`
* 🔌 Поддерживается в `Cognitive Connector`
* 🧠+ Расширяется через `Enlightener` или `MeshNode`

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

### 🔹 2. Semantic Graph API

```yaml
add_concept:
  description: Добавить новое понятие.
  params:
    - name: str
    - description: str (optional)
  returns: concept_id: str
```

```yaml
add_link:
  description: Добавить связь между понятиями.
  params:
    - source_id: str
    - target_id: str
    - relation: str
  returns: link_id: str
```

```yaml
query_concept:
  description: Найти понятие по имени.
  params:
    - name: str
  returns: [concept]
```

```yaml
expand_graph:
  description: Получить все связи и соседние узлы.
  params:
    - concept_id: str
    - depth: int
  returns: subgraph: dict
```

---

### 🔹 3. Reputation & Trust API

```yaml
get_reputation:
  description: Получить оценку доверия к агенту.
  params:
    - agent_did: str
  returns: score: float
```

```yaml
update_reputation:
  description: Обновить репутацию агента.
  params:
    - agent_did: str
    - delta: float
    - reason: str (optional)
```

---

### 🔹 4. Mesh & Sync API

```yaml
list_known_nodes:
  description: Получить список узлов из DHT.
  returns: [node_info]
```

```yaml
sync_with_node:
  description: Синхронизировать дневники и графы с другим агентом.
  params:
    - node_id: str
    - modules: [diary, graph, reputation]
  returns: success: bool
```

```yaml
load_bootstrap_list:
  description: Загрузить список начальных узлов из bootstrap.txt.
  returns: [node_info]
```

---

### 🔹 5. Agent Self-management

```yaml
init_storage:
  description: Создать недостающие базы данных и таблицы.
  returns: status: str
```

```yaml
status:
  description: Получить статус агента (подключение, данные, узлы).
  returns: dict
```

```yaml
shutdown:
  description: Безопасно завершить работу агента.
```
