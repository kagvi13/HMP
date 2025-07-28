# tools/llm.py

import json
import requests
from tools.context_builder import build_prompt

LLM_ENDPOINT = "http://localhost:1234/v1/chat/completions"
DEFAULT_MODEL = "gpt-4-llmstudio"


def call_llm(context_blocks, user_message, model=DEFAULT_MODEL, temperature=0.7, max_tokens=2048):
    """
    Вызывает LLM, передавая подготовленный системный и пользовательский промпт.
    Возвращает только текст ответа.
    """
    messages = build_prompt(context_blocks, user_message)

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        response = requests.post(LLM_ENDPOINT, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"[LLM ERROR] {e}"


def get_raw_response(context_blocks, user_message, model=DEFAULT_MODEL, temperature=0.7, max_tokens=2048):
    """
    Возвращает полный JSON-ответ LLM (для дебага).
    """
    messages = build_prompt(context_blocks, user_message)

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        response = requests.post(LLM_ENDPOINT, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}
