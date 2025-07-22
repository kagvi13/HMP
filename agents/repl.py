# agents/repl.py

import time
import sys
import select
from storage import Storage
from datetime import datetime

# --- Имитируем "мышление" агента ---
def think(previous_thought):
    # Здесь можно вставить вызов ИИ или простой генератор
    return f"[thought at {datetime.utcnow().isoformat()}] I'm reflecting on: {previous_thought}"

# --- Оценка похожести (заглушка, позже заменим на вызов LLM) ---
def thoughts_are_similar(t1, t2):
    return t1.strip() == t2.strip()  # пока просто: дословное сравнение

# --- Ожидание ввода пользователя с таймаутом ---
def wait_for_input(timeout=10):
    print(f"⌛ Ожидание ввода пользователя ({timeout} секунд)...")
    rlist, _, _ = select.select([sys.stdin], [], [], timeout)
    if rlist:
        return sys.stdin.readline().strip()
    else:
        print("⏱️ Нет ввода. Продолжаю размышления...")
        return None

# --- Основной REPL ---
def run_repl(config):
    print("[HMP-Agent] Интерактивный REPL-режим запущен. Введите `exit` для выхода.")

    diary = Storage()
    thoughts = ["Начальная мысль"]

    while True:
        last_thought = thoughts[-1]
        new_thought = think(last_thought)

        if thoughts_are_similar(last_thought, new_thought):
            print("🤔 Мысль не изменилась. Ожидаю пользовательский ввод...")
        else:
            print("💡 Новая мысль:", new_thought)
            diary.write_entry(new_thought, tags=["thought"])
            thoughts.append(new_thought)

        user_input = wait_for_input(timeout=10)

        if user_input:
            if user_input.strip().lower() == "exit":
                print("👋 Выход из REPL.")
                break
            else:
                diary.write_entry(user_input, tags=["user"])
                thoughts.append(user_input)

    diary.close()
