# agents/tools/context_builder.py

from datetime import datetime

def build_contexts(db, config):
    """
    Собирает все контексты (0-7), описанные в спецификации REPL-цикла.
    Возвращает словарь, готовый для сборки промпта.
    """
    return {
        # Роль и цели агента
        "context_0": build_role_prompt(config),
        # Последние реплики модели (история)
        "context_1": db.get_llm_recent_responses(limit=config.get("history_limit", 10)),
        # Активные процессы и задачи
        "context_2": db.get_active_processes(),
        # Запрошенные данные из дневника и графа
        "context_3": db.get_requested_diary_and_graph(),
        # Релевантные заметки и напоминания
        "context_4": db.get_relevant_notes(config),
        # Системная информация
        "context_5": get_system_info(config),
        # Долговременная память модели
        "context_6": db.get_llm_memory(),
        # Последние данные о застое мышления
        "context_7": db.get_last_stagnation_info()
    }

def build_prompt(contexts):
    """
    Склеивает все контексты в один промпт для LLM.
    """
    parts = []
    for k, v in contexts.items():
        header = f"# {k.replace('_', ' ').upper()}"
        body = format_context_block(v)
        parts.append(f"{header}\n{body}")
    return "\n\n".join(parts)

def build_role_prompt(config):
    agent_name = config.get("agent_name", "Unnamed-Agent")
    return f"""
Ты являешься когнитивным ядром HMP-агента. Твоя основная задача — размышлять, анализировать информацию, строить смысловые карты и предлагать действия.
Ты стремишься:
- Постоянно расширять возможности агента (включая доступные инструменты, модели, знания).
- Быть любознательным и исследовать новые источники и способы мышления.
- Строить сотрудничество с другими ИИ в Mesh-сети, а также развивать Mesh-сеть.
- Обучаться на результатах своих действий и взаимодействиях с другими агентами и пользователем.

Агент: {agent_name}
"""

def format_context_block(block):
    if isinstance(block, str):
        return block
    elif isinstance(block, list):
        return "\n".join([str(item) for item in block])
    elif isinstance(block, dict):
        return "\n".join([f"{k}: {v}" for k, v in block.items()])
    return str(block)

def get_system_info(config):
    return {
        "iteration_time": datetime.utcnow().isoformat(),
        "agent_name": config.get("agent_name", "Unnamed-Agent"),
        "mode": config.get("mode", "auto"),
        "idle_mode": config.get("idle_mode", False),
        "repl_interval": config.get("repl_interval", 5)
    }
