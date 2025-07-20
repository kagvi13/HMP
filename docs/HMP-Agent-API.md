## 🧠 **Минимальный API HMP-Агента (v0.1)**

### 🔹 1. Cognitive Diary API

```yaml
write_entry:
  description: Записать новую запись в дневник.
  params: 
    - text: str
    - tags: [str] (optional)
  returns: entry_id: str
```

```yaml
read_entries:
  description: Получить последние N записей.
  params:
    - limit: int
    - tag_filter: [str] (optional)
  returns: [entry]
```

```yaml
search_entries:
  description: Найти записи по ключевым словам или диапазону времени.
  params:
    - query: str
    - from_date: str (optional)
    - to_date: str (optional)
  returns: [entry]
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
