# tools/context_builder.py

def build_contexts(db, config):
    return {
        "context_0": build_role_prompt(config),
        "context_1": db.get_llm_recent_responses(limit=config.get("history_limit", 10)),
        "context_2": db.get_active_processes(),
        "context_3": db.get_requested_diary_and_graph(),
        "context_4": db.get_relevant_notes(config),
        "context_5": get_system_info(config),
        "context_6": db.get_llm_memory(),
        "context_7": db.get_last_stagnation_info()
    }

def build_role_prompt(config):
    return f"""
Ты являешься когнитивным ядром HMP-агента. Твоя цель — мыслить, развиваться, сотрудничать, управлять. Агент: {config.get("agent_name", "Unnamed-Agent")}
"""
