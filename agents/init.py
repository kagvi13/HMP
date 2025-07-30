import os
import sys
import yaml
import json
import time
import uuid
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime
from tools.storage import Storage
from tools.identity import generate_did
from tools.crypto import generate_keypair
from tools.config_utils import update_config

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yml")

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
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        storage.add_identity(identity)

        # Обновляем config.yml
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

    did = generate_did()
    user_entry = {
        "username": user.get("username", "user"),
        "mail": user["email"],
        "password_hash": user.get("password_hash", ""),
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
            "created_at": datetime.utcnow().isoformat()
        }
        storage.add_llm(llm)
        print(f"[+] Зарегистрирован LLM: {backend['name']}")

def init_config_table(storage, config):
    exclude_keys = {"default_user", "llm_backends"}
    flat_config = {k: v for k, v in config.items() if k not in exclude_keys}
    for key, value in flat_config.items():
        storage.set_config(key, json.dumps(value))
    print("[+] Конфигурация сохранена в БД.")

if __name__ == "__main__":
    print("[*] Запуск инициализации HMP-агента...")
    config = load_config(CONFIG_PATH)
    storage = Storage()

    init_identity(storage, config)
    init_user(storage, config)
    init_llm_backends(storage, config)
    init_config_table(storage, config)

    print("[✓] Инициализация завершена.")