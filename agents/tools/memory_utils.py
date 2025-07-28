# tools/memory_utils.py

from datetime import datetime, timedelta
from difflib import SequenceMatcher
from typing import Optional, List, Dict

STAGNATION_WINDOW = 5  # сколько последних записей сравнивать
STAGNATION_THRESHOLD = 0.95  # схожесть выше этого — считается стагнацией


def get_last_responses(db, limit=STAGNATION_WINDOW) -> List[str]:
    records = db.get_llm_recent_responses(limit=limit)
    return [r["content"] if isinstance(r, dict) else r for r in records]


def is_stagnant(responses: List[str]) -> bool:
    if len(responses) < 2:
        return False

    similarities = []
    for i in range(len(responses) - 1):
        sim = string_similarity(responses[i], responses[i + 1])
        similarities.append(sim)

    avg_sim = sum(similarities) / len(similarities)
    return avg_sim >= STAGNATION_THRESHOLD


def string_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.strip(), b.strip()).ratio()


def get_last_stagnation_info(db) -> Optional[Dict]:
    responses = get_last_responses(db)
    if is_stagnant(responses):
        return {
            "detected": True,
            "average_similarity": round(sum(
                string_similarity(responses[i], responses[i+1])
                for i in range(len(responses)-1)
            ) / (len(responses)-1), 4),
            "last_messages": responses
        }
    return {"detected": False}


def add_to_llm_memory(db, title: str, content: str, tags: str = "meta"):
    db.insert("llm_memory", {
        "title": title,
        "content": content,
        "tags": tags,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    })


def record_reflection_if_stagnant(db):
    stagnation = get_last_stagnation_info(db)
    if stagnation.get("detected"):
        content = f"Обнаружена стагнация размышлений. Последние сообщения были очень похожи.\n\n"
        content += "---\n" + "\n---\n".join(stagnation["last_messages"])
        add_to_llm_memory(db, "Стагнация размышлений", content, tags="meta,warning")
        return True
    return False
