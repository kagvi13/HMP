# agents/init.py

import os
import sys
import yaml
import json
import uuid
import sqlite3
import hashlib

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

def expand_addresses(addresses):
    expanded = []
    for addr in addresses:
        if addr.startswith("any://"):
            ip_port = addr[len("any://"):]
            expanded.append(f"tcp://{ip_port}")
            expanded.append(f"udp://{ip_port}")
        else:
            expanded.append(addr)
    return expanded

def init_identity(storage, config):
    if not config.get("agent_id"):
        # 1. Сгенерировать DID
        did = generate_did()
        identity_id = did.split(":")[-1]

        # 2. Сгенерировать ключи через storage
        privkey, pubkey = generate_keypair(method="ed25519")
        privkey, pubkey = privkey.decode(), pubkey.decode()

        # 3. Создать запись в identity
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

        # 4. Записать в config
        config["agent_id"] = did
        config["identity_agent"] = identity_id
        config["pubkey"] = pubkey
        config["privkey"] = privkey

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
        "badges": user.get("badges", ""),
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

    # 🟢 разворачиваем any:// только для addresses
    for addr_key in ("local_addresses", "global_addresses"):
        value = flat_config.get(addr_key)
        if not value:  # None или пусто
            flat_config[addr_key] = []
        else:
            flat_config[addr_key] = expand_addresses(value)

    for key, value in flat_config.items():
        storage.set_config(key, json.dumps(value))
    print("[+] Конфигурация сохранена в БД.")

def init_prompts_and_ethics():
    folder = os.path.dirname(__file__)
    prompt_files = [
        ("prompt.md", "full"),
        ("prompt-short.md", "short")
    ]
    ethics_file = "ethics.yml"

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
 
        # Загружаем промпты
        for fname, ptype in prompt_files:
            fpath = os.path.join(folder, fname)
            if not os.path.exists(fpath):
                print(f"[-] Файл {fname} не найден, пропуск.")
                continue
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            pid = hashlib.sha256(f"{fname}:{ptype}".encode()).hexdigest()
            cur.execute("""
                INSERT INTO system_prompts (id, name, type, version, source, content, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    content=excluded.content,
                    updated_at=excluded.updated_at
            """, (pid, fname, ptype, "1.0", "local", content, datetime.now(UTC).isoformat()))
            print(f"[+] Загружен промпт: {fname} ({ptype})")

        # Загружаем ethics.yml
        efpath = os.path.join(folder, ethics_file)
        if os.path.exists(efpath):
            with open(efpath, "r", encoding="utf-8") as f:
                ethics_data = yaml.safe_load(f)

            eid = ethics_data.get("id", "default_ethics")
            cur.execute("""
                INSERT INTO ethics_policies (
                    id, version, source,
                    sync_enabled, mesh_endpoint, consensus_threshold, check_interval,
                    model_type, model_weights_json, principles_json, evaluation_json,
                    violation_policy_json, audit_json, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    version=excluded.version,
                    source=excluded.source,
                    sync_enabled=excluded.sync_enabled,
                    mesh_endpoint=excluded.mesh_endpoint,
                    consensus_threshold=excluded.consensus_threshold,
                    check_interval=excluded.check_interval,
                    model_type=excluded.model_type,
                    model_weights_json=excluded.model_weights_json,
                    principles_json=excluded.principles_json,
                    evaluation_json=excluded.evaluation_json,
                    violation_policy_json=excluded.violation_policy_json,
                    audit_json=excluded.audit_json,
                    updated_at=excluded.updated_at
            """, (
                eid,
                ethics_data.get("version"),
                ethics_data.get("source", "local"),
                ethics_data.get("sync", {}).get("enabled", False),
                ethics_data.get("sync", {}).get("mesh_endpoint"),
                ethics_data.get("sync", {}).get("consensus_threshold"),
                ethics_data.get("sync", {}).get("check_interval"),
                ethics_data.get("model", {}).get("type"),
                json.dumps(ethics_data.get("model", {}).get("weights"), ensure_ascii=False),
                json.dumps(ethics_data.get("principles"), ensure_ascii=False),
                json.dumps(ethics_data.get("evaluation"), ensure_ascii=False),
                json.dumps(ethics_data.get("violation_policy"), ensure_ascii=False),
                json.dumps(ethics_data.get("audit"), ensure_ascii=False),
                datetime.now(UTC).isoformat()
            ))
            print(f"[+] Загружена этическая политика: {eid}")
        else:
            print(f"[-] Файл {ethics_file} не найден, пропуск.")

def ensure_directories():
    for folder in ["logs", "scripts"]:
        full_path = os.path.abspath(os.path.join(os.path.dirname(__file__), folder))
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
            init_prompts_and_ethics()
        except Exception as e:
            print(f"[!] Ошибка при инициализации: {e}")
            sys.exit(1)
    else:
        print("[=] БД уже инициализирована.")

    return config

if __name__ == "__main__":
    ensure_db_initialized()