# cli.py

import argparse
import yaml
import sys
from agent import main as cli_main, run_agent, run_mcp_agent
from repl import run_repl

def load_config(path="config.yml"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"[Error] Config file not found: {path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"[Error] Failed to parse YAML config: {e}")
        sys.exit(1)

def launch():
    parser = argparse.ArgumentParser(description="HMP-Agent Launcher")
    parser.add_argument("--mode", choices=["interactive", "cli", "mcp"], default=None,
                        help="Режим запуска агента")
    parser.add_argument("--config", default="config.yml", help="Путь к конфигурационному файлу")
    args = parser.parse_args()

    config = load_config(args.config)
    mode = args.mode or config.get("agent_mode", "cli")

    if mode == "interactive":
        run_repl(config)

    elif mode == "cli":
        cli_main()  # запускается agent.py в CLI-режиме

    elif mode == "mcp":
        run_mcp_agent(config)

    else:
        print(f"[Error] Неизвестный режим: {mode}")
        sys.exit(1)

if __name__ == "__main__":
    launch()
