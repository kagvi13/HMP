import json
import os
import sys
import time
import sqlite3

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
from tools.peers import refresh_peer_list, check_peer_statuses
from agents.init import main as run_init
from agents.config import load_config

config = load_config("agents/config.yml")
db_path = config.get("db_path", "./data/agent_storage.db")

def is_db_initialized(path):
    if not os.path.exists(path):
        return False
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='identity'")
        exists = cursor.fetchone() is not None
        conn.close()
        return exists
    except Exception:
        return False

if not is_db_initialized(db_path):
    print("[*] Не инициализирована БД. Выполняется init.py...")
    try:
        run_init()
    except Exception as e:
        print(f"[!] Ошибка при инициализации: {e}")
        sys.exit(1)

def run_repl(config=None):
    print("[🧠 HMP-Agent] Запуск REPL-режима (v2)")
    config = config or {}
    db = Storage(config=config)

    try:
        while True:
            tick_start = datetime.utcnow().isoformat()
            print(f"\n=== [🌀 Новый тик REPL] {tick_start} ===")

            # 0. Обновление информации о пирах
            refresh_peer_list(db)
            check_peer_statuses(db)

            # 1. Построение контекстов
            contexts = build_contexts(db=db, config=config)

            # 2. Формирование запроса и вызов LLM
            prompt = build_prompt(contexts)
            llm_response = call_llm(prompt, config=config)
            repl_log_entry = {
                "timestamp": tick_start,
                "prompt": prompt.strip(),
                "llm_response": llm_response.strip(),
            }

            # 3. Проверка на стагнацию
            is_stagnant = detect_stagnation(db, llm_response)
            repl_log_entry["stagnation_detected"] = is_stagnant
            if is_stagnant:
                print("⚠️ Стагнация выявлена. Активирован Anti-Stagnation Reflex.")
                llm_response = activate_anti_stagnation(db, config=config)

            # 4. Обновление памяти
            update_llm_memory(db, llm_response)

            # 5. Извлечение и выполнение команд
            commands = extract_commands(llm_response)
            repl_log_entry["commands_extracted"] = commands
            execute_commands(commands, db=db, config=config)

            # 6. Логирование полной итерации в файл
            log_path = config.get("repl_log_path", "logs/repl_log.jsonl")
            os.makedirs(os.path.dirname(log_path), exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(repl_log_entry, ensure_ascii=False) + "\n")
            db.write_llm_response(llm_response)
            db.update_agent_log(timestamp=tick_start)

            # 7. Переход в idle-режим или задержка
            if config.get("idle_mode"):
                print("💤 Idle-mode активен. Ожидание события...")
                time.sleep(config.get("idle_check_interval", 30))
            else:
                time.sleep(config.get("repl_interval", 5))

    except KeyboardInterrupt:
        print("\n[!] Завершение работы REPL по сигналу пользователя.")
