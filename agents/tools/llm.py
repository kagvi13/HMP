# tools/llm.py

from datetime import datetime
import random

def generate_thought(previous_text, config=None):
    """
    Генерация новой мысли на основе предыдущей.
    Пока — заглушка (можно заменить на вызов OpenAI, LLaMA и др.)
    """
    config = config or {}
    mode = config.get("llm_mode", "mock")

    if mode == "mock":
        return mock_thought(previous_text)
    
    elif mode == "api":
        # TODO: подключение к OpenAI, LM Studio, Ollama...
        return "[API] (здесь могла быть ваша мысль)"

    return "[!] Неизвестный режим генерации."

def mock_thought(previous_text):
    samples = [
        "А что если рассмотреть это с другой стороны?",
        "Мне кажется, это связано с предыдущим опытом.",
        "Нужно уточнить границы понятия.",
        "А есть ли более эффективный путь решения?",
        "Я всё ещё думаю о предыдущей мысли..."
    ]
    return f"[{datetime.utcnow().isoformat()}] {random.choice(samples)}"

def summarize(text, config=None):
    """
    Заглушка для краткого резюме текста.
    """
    return f"Резюме: {text[:40]}..."

def ask_question(question, config=None):
    """
    Заглушка для режима QA.
    """
    return f"Ответ на вопрос «{question}»: заглушка."
