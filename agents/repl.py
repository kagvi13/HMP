# agents/repl.py

import time
from datetime import datetime
from tools.context_builder import build_contexts, build_prompt
from tools.llm import call_llm
from tools.command_parser import extract_commands
from tools.command_executor import execute_commands
from tools.memory_utils import (
    detect_stagnation,
    activate_anti_stagnation,
    update_llm_memory
)
from tools.storage import Storage


def run_repl(config=None):
    print("[🧠 HMP-Agent] Запуск REPL-режима (v2)")
    config = config or {}
    db = Storage(config=config)

    while True:
        tick_start = datetime.utcnow().isoformat()
        print(f"\n=== [🌀 Новый тик REPL] {tick_start} ===")

        # 0. Обновление информации о пирах
        from tools.peers import refresh_peer_list, check_peer_statuses
        refresh_peer_list(db)
        check_peer_statuses(db)

        # 1. Построение контекстов
        contexts = build_contexts(db=db, config=config)

        # 2. Формирование запроса и вызов LLM
        prompt = build_prompt(contexts)
        llm_response = call_llm(prompt, config=config)

        # 3. Проверка на стагнацию
        if detect_stagnation(db, llm_response):
            print("⚠️ Стагнация выявлена. Активирован Anti-Stagnation Reflex.")
            llm_response = activate_anti_stagnation(db, config=config)

        # 4. Обновление памяти
        update_llm_memory(db, llm_response)

        # 5. Извлечение и выполнение команд
        commands = extract_commands(llm_response)
        execute_commands(commands, db=db, config=config)

        # 6. Сохранение истории и завершение итерации
        db.write_llm_response(llm_response)
        db.update_agent_log(timestamp=tick_start)

        # 7. Переход в idle-режим или задержка
        if config.get("idle_mode"):
            # TODO: реализовать проверку условий выхода из idle
            print("💤 Idle-mode активен. Ожидание события...")
            time.sleep(config.get("idle_check_interval", 30))
        else:
            time.sleep(config.get("repl_interval", 5))
