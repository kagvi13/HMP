# agents/tools/config_utils.py

import json
import os

def update_config(config_path: str, updates: dict):
    """Обновляет JSON-файл конфигурации указанными значениями."""
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = {}

    config.update(updates)

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
