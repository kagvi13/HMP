## 📦 HMP-Agent: Структура БД (v0.3, человекочитаемый формат)

---

### 🧠 Когнитивная память (Concept Graph)

#### 🧠 `memory_concepts`

**Назначение:**
Хранение концептов (единиц когнитивной памяти): понятий, фактов, образов, внутренних конструкций и внешних знаний.

**Поля:**

* `id: INTEGER` — первичный ключ.
* `label: TEXT` — человекочитаемое имя концепта.
* `type: TEXT` — тип концепта (`idea`, `object`, `goal`, `fact`, `memory_snapshot`, `mesh_entity`, …).
* `content: TEXT` — JSON-объект с содержанием концепта (например, описание, параметры, вложенные идеи).
* `context: TEXT` — дополнительный контекст (например, источник, ссылка на событие).
* `created_at: TIMESTAMP` — дата создания.
* `updated_at: TIMESTAMP` — дата последнего обновления.

**Ключевые поля:** `id`, `label`

**Связи:**

* Ссылается из `memory_links.from_id` и `to_id`
* Используется в `cognitive_cycles`, `hypotheses`, `reflections`, `reasoning_traces`

---

#### 🔗 `memory_links`

**Назначение:**
Определение связей между концептами — формирование когнитивного графа.

**Поля:**

* `id: INTEGER` — первичный ключ.
* `from_id: INTEGER` — ID исходного концепта.
* `to_id: INTEGER` — ID связанного концепта.
* `relation: TEXT` — тип связи (`causes`, `associated_with`, `contradicts`, …).
* `weight: REAL` — значимость или сила связи (по умолчанию 1.0).

**Ключевые поля:** `id`, `from_id`, `to_id`

**Связи:**

* `from_id`, `to_id → memory_concepts(id)`

---

## 📜 События, действия, сообщения

#### 🧩 `cognitive_events`

**Назначение:**
Журнал восприятия, действий и входящих/исходящих сообщений.

**Поля:**

* `id: INTEGER` — первичный ключ.
* `event_type: TEXT` — тип события (`input`, `output`, `message`, `action`, `mesh`, `internal`).
* `payload: TEXT` — сериализованные данные (обычно JSON).
* `source: TEXT` — источник события (например, ID mesh-пира).
* `target: TEXT` — целевая система или компонент.
* `created_at: TIMESTAMP` — время события.

**Ключевые поля:** `id`, `event_type`

**Связи:**

* Используется в `reflections.trigger_event_id`

---
#### 📬 `hmp_messages`

**Назначение:**
Лог входящих и исходящих сообщений в Mesh-среде.

**Поля:**

* `id: INTEGER`
* `direction: TEXT` — `inbound` или `outbound`
* `peer: TEXT` — адрес или идентификатор узла
* `payload: TEXT` — сериализованные данные (обычно JSON)
* `topic: TEXT` — категория сообщения
* `created_at: TIMESTAMP`

**Примечание:**
Адаптация к спецификации HMP должна производиться на уровне сериализации перед отправкой, а не на уровне хранения.

---

### 🔍 Гипотезы, цели, reasoning

#### 🧠 `hypotheses`

**Назначение:**
Управление гипотезами: недоказанными или частично сформированными утверждениями.

**Поля:**

* `id: INTEGER` — первичный ключ.
* `title: TEXT` — краткое описание гипотезы.
* `description: TEXT` — расширенное описание.
* `status: TEXT` — состояние (`active`, `rejected`, `confirmed`, `stale`).
* `relevance_score: REAL` — оценка актуальности (0.0–1.0).
* `evidence: TEXT` — JSON-массив ссылок на концепты, события и факты.
* `created_at: TIMESTAMP`

**Связи:**

* Может ссылаться на `memory_concepts`, `cognitive_events`

---

#### 🎯 `goals`

**Назначение:**
Управление целями агента — формулировка намерений и задач.

**Поля:**

* `id: INTEGER` — первичный ключ.
* `description: TEXT` — формулировка цели.
* `priority: INTEGER` — приоритет (1 = максимальный).
* `status: TEXT` — текущее состояние (`pending`, `in_progress`, `completed`, `abandoned`).
* `context: TEXT` — дополнительная информация.
* `created_at`, `updated_at: TIMESTAMP`

---

#### 🔁 `cognitive_cycles`

**Назначение:**
История reasoning-процессов: единиц когнитивной активности, отражающих ход размышлений.

**Поля:**

* `id: INTEGER` — первичный ключ.
* `cycle_number: INTEGER` — порядковый номер итерации.
* `thoughts: TEXT` — массив мыслей в формате JSON.
* `new_concepts: TEXT` — ID новых концептов, сформированных в ходе цикла.
* `actions_taken: TEXT` — предпринятые действия.
* `context_snapshot: TEXT` — снимок состояния.
* `started_at`, `ended_at: TIMESTAMP`

**Связи:**

* Используется в `reflections`, `reasoning_traces`, `agent_state_snapshots`

---

### 🧬 Версионирование, артефакты, кодексы

#### 📦 `versioned_artifacts`

**Назначение:**
Хранение версии артефактов: конфигураций, моделей, API-структур.

**Поля:**

* `id: INTEGER`
* `name: TEXT` — идентификатор артефакта (`api_structure`, `core_config`, `agent_traits`)
* `version: TEXT` — версионирование (e.g., `2025-07-22.1`)
* `content: TEXT` — JSON или Markdown
* `created_at: TIMESTAMP`

Отлично! Текущий `db_structure.md` уже хорошо структурирован, и его можно расширить, добавив недостающие таблицы. Вот предложения по доработке:

---

### 🧬 Версионирование, артефакты, кодексы

#### 🧾 `agent_policies`

**Назначение:**
Хранение деклараций, этических норм, стратегий и ограничений поведения агента.

**Поля:**

* `id: INTEGER` — первичный ключ.
* `policy_type: TEXT` — тип (`ethics`, `exploration`, `safety`, `prioritization`, …).
* `name: TEXT` — краткое название политики.
* `content: TEXT` — Markdown или JSON-содержимое.
* `created_at: TIMESTAMP` — дата создания.

**Примечание:**
Может быть использована при принятии решений или фильтрации гипотез/действий.

---

### ⚙️ Модули и состояния

#### 🧩 `modules_state`

**Назначение:**
Отслеживание состояния и локальной памяти когнитивных модулей (например, рефлексии, генерации гипотез, плана).

**Поля:**

* `id: INTEGER` — первичный ключ.
* `module_name: TEXT` — имя модуля (`reflection`, `planner`, `input_handler`, …).
* `status: TEXT` — текущее состояние (`idle`, `running`, `paused`, `error`).
* `memory: TEXT` — сериализованное состояние (JSON).
* `last_heartbeat: TIMESTAMP` — последнее обновление.

---

### 📓 Агентский дневник

#### 📖 `diary_entries`

**Назначение:**
Журнал размышлений, наблюдений, воспоминаний или метакомментариев, созданных агентом или пользователем.

**Поля:**

* `id: INTEGER` — первичный ключ.
* `entry_type: TEXT` — тип (`reflection`, `note`, `observation`, `self_report`, `dialog`, …).
* `content: TEXT` — основное содержимое записи.
* `related_concepts: TEXT` — JSON-массив `concept_id`, с которыми связана запись.
* `created_at: TIMESTAMP`
