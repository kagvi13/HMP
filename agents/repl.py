# agents/repl.py

import sys
import time
import select
from datetime import datetime
from storage import Storage
from tools import llm  # генератор мыслей
# from tools.similarity import is_similar  # можно подключить позже

def print_thought(thought, prefix="💡"):
    print(f"{prefix} {thought}")

def wait_for_input(timeout=10):
    print(f"⌛ Ожидание ввода пользователя ({timeout} сек)... (введите `exit` для выхода)")
    rlist, _, _ = select.select([sys.stdin], [], [], timeout)
    if rlist:
        return sys.stdin.readline().strip()
    else:
        print("⏱️ Нет ввода. Продолжаю размышления...")
        return None

def thoughts_are_similar(t1, t2):
    return t1.strip() == t2.strip()  # временная заглушка

def run_repl(config=None):
    print("[🧠 HMP-Agent] Запуск REPL-режима.")
    config = config or {}
    agent_name = config.get("agent_name", "Unnamed-Agent")

    db = Storage(config=config)
    thoughts = [f"Привет, я {agent_name}."]

    while True:
        last = thoughts[-1]
        next_thought = llm.generate_thought(last, config=config)

        if thoughts_are_similar(last, next_thought):
            print("🤔 Мысль повторяется. Ожидаю пользовательский ввод...")
        else:
            print_thought(next_thought)
            db.write_entry(next_thought, tags=["thought"])
            thoughts.append(next_thought)

        user_input = wait_for_input(timeout=config.get("repl_timeout", 10))

        if user_input:
            if user_input.strip().lower() in ("exit", "quit"):
                print("👋 Выход из REPL. До связи!")
                break
            else:
                db.write_entry(user_input, tags=["user"])
                thoughts.append(user_input)

    db.close()
