# agents/repl.py

import time
from datetime import datetime
from tools.context_builder import build_contexts
from tools.llm import call_llm
from tools.command_parser import extract_commands
from tools.command_executor import execute_commands
from tools.memory_utils import update_llm_memory, detect_stagnation
from storage import Storage

def run_repl(config=None):
    print("[🧠 HMP-Agent] Запуск REPL-режима (v2).")
    config = config or {}
    db = Storage(config=config)
    
    while True:
        tick_start = datetime.utcnow().isoformat()
        print(f"\n=== [🌀 Новый тик REPL] {tick_start} ===")

        # 1. Построение контекстов
        contexts = build_contexts(db=db, config=config)

        # 2. Формирование запроса к LLM
        prompt = build_prompt(contexts)
        llm_response = call_llm(prompt, config=config)

        # 3. Обнаружение стагнации
        if detect_stagnation(db, llm_response):
            print("⚠️ Стагнация выявлена. Активирован Anti-Stagnation Reflex.")
            llm_response = activate_anti_stagnation(db, config=config)

        # 4. Обновление памяти
        update_llm_memory(db, llm_response)

        # 5. Извлечение и выполнение команд
        commands = extract_commands(llm_response)
        execute_commands(commands, db=db, config=config)

        # 6. Сохранение истории
        db.write_llm_response(llm_response)

        # 7. Управление режимами ожидания
        if check_idle_mode(config):
            wait_idle_trigger(config)
        else:
            time.sleep(config.get("repl_interval", 5))
