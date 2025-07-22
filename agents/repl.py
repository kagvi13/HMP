# agents/repl.py

import sys
import time
import select
from datetime import datetime
from storage import Storage
from tools.notebook_store import Notebook
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
    repl_timeout = config.get("repl_timeout", 10)

    db = Storage(config=config)
    notebook = Notebook()
    thoughts = [f"Привет, я {agent_name}."]
    last_check_time = datetime.utcnow().isoformat()

    while True:
        # Сгенерировать новую мысль
        last = thoughts[-1]
        next_thought = llm.generate_thought(last, config=config)

        if not thoughts_are_similar(last, next_thought):
            print_thought(next_thought)
            db.write_entry(next_thought, tags=["thought"])
            thoughts.append(next_thought)
        else:
            print("🤔 Мысль повторяется. Проверяю блокнот...")

        # Проверка новых пользовательских заметок
        new_notes = notebook.get_notes_after(last_check_time)
        if new_notes:
            print(f"📓 Новые записи в блокноте: {len(new_notes)}")
            for nid, text, source, ts in new_notes:
                print_thought(text, prefix="📝")
                db.write_entry(text, tags=["notepad"])
                thoughts.append(text)
                last_check_time = ts  # обновляем момент последней обработки

        # Ожидание пользовательского ввода
        user_input = wait_for_input(timeout=repl_timeout)
        if user_input:
            if user_input.strip().lower() in ("exit", "quit"):
                print("👋 Выход из REPL. До связи!")
                break
            else:
                db.write_entry(user_input, tags=["user"])
                thoughts.append(user_input)

    db.close()
    notebook.close()
