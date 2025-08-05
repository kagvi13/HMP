# agents/init.py

import os
import sys
import yaml
import json
import uuid
import sqlite3

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, UTC
from werkzeug.security import generate_password_hash
from tools.storage import Storage
from tools.identity import generate_did
from tools.crypto import generate_keypair

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yml")
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "agent_data.db"))  # фиксированный путь

def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def save_config(path, config):
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True)

def init_identity(storage, config):
    if not config.get("agent_id"):
        did = generate_did()
        pubkey, privkey = generate_keypair()
        identity_id = did.split(":")[-1]

        identity = {
            "id": identity_id,
            "name": config.get("agent_name", "Unnamed"),
            "pubkey": pubkey,
            "privkey": privkey,
            "metadata": json.dumps({"role": config.get("agent_role", "core")}),
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat()
        }
        storage.add_identity(identity)

        config["agent_id"] = did
        config["identity_agent"] = identity_id
        save_config(CONFIG_PATH, config)
        print(f"[+] Создана личность: {identity_id}")
    else:
        print("[=] agent_id уже задан, пропускаем генерацию DiD.")

def init_user(storage, config):
    user = config.get("default_user", {})
    if not user.get("email"):
        print("[-] Не указан email пользователя — пропуск.")
        return
    password = user.get("password")
    if not password:
        print("[-] Не указан пароль пользователя — пропуск.")
        return

    password_hash = generate_password_hash(password)
    did = generate_did()
    user_entry = {
        "username": user.get("username", "user"),
        "mail": user["email"],
        "password_hash": password_hash,
        "did": did,
        "ban": None,
        "info": json.dumps({}),
        "contacts": json.dumps([]),
        "language": "ru,en",
        "operator": 1
    }
    storage.add_user(user_entry)
    print(f"[+] Пользователь {user['username']} добавлен.")

def init_llm_backends(storage, config):
    backends = config.get("llm_backends", [])
    storage.clear_llm_registry()
    for backend in backends:
        backend_id = str(uuid.uuid4())
        desc = f"{backend.get('type', 'unknown')} model"
        llm = {
            "id": backend_id,
            "name": backend["name"],
            "endpoint": desc,
            "metadata": json.dumps(backend),
            "created_at": datetime.now(UTC).isoformat()
        }
        storage.add_llm(llm)
        print(f"[+] Зарегистрирован LLM: {backend['name']}")

def init_config_table(storage, config):
    exclude_keys = {"default_user", "llm_backends"}
    flat_config = {k: v for k, v in config.items() if k not in exclude_keys}
    for key, value in flat_config.items():
        storage.set_config(key, json.dumps(value))
    print("[+] Конфигурация сохранена в БД.")

def ensure_directories():
    for folder in ["logs", "scripts"]:
        full_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", folder))
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            print(f"[+] Создан каталог: {full_path}")
        else:
            print(f"[=] Каталог уже существует: {full_path}")

def is_db_initialized(db_path):
    if not os.path.exists(db_path):
        return False
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='identity'")
            return cursor.fetchone() is not None
    except Exception:
        return False

def ensure_db_initialized():
    config = load_config(CONFIG_PATH)

    if not is_db_initialized(DB_PATH):
        print("[*] БД не инициализирована — выполняем инициализацию.")
        try:
            ensure_directories()
            storage = Storage()
            init_identity(storage, config)
            init_user(storage, config)
            init_llm_backends(storage, config)
            init_config_table(storage, config)
            save_config(CONFIG_PATH, config)
        except Exception as e:
            print(f"[!] Ошибка при инициализации: {e}")
            sys.exit(1)
    else:
        print("[=] БД уже инициализирована.")

    return config

if __name__ == "__main__":
    ensure_db_initialized()
