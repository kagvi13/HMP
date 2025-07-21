# cli.py

import argparse
import yaml
import sys
from agent import main, run_agent, run_mcp_agent  # Ты можешь разделить реализацию
                                                  # на функции внутри agent.py

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

def run():
    config = load_config()
    mode = config.get("agent_mode", "cli")

    if mode == "cli":
        main()
    elif mode == "mcp":
        run_mcp_agent(config)
    elif mode == "full":
        print("[TODO] Full agent mode is not yet implemented.")
        # Здесь в будущем можно будет добавить run_full_agent(config)
    else:
        print(f"[Error] Unknown agent_mode: {mode}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="HMP-Agent CLI Launcher")

    parser.add_argument("--mode", choices=["interactive", "cli", "mcp"], default=None,
                        help="Режим запуска агента")
    parser.add_argument("--config", default="config.yml", help="Путь к конфигурационному файлу")

    args = parser.parse_args()

    config = load_config(args.config)

    mode = args.mode or config.get("agent_mode", "interactive")

    if mode == "interactive":
        print("[HMP-Agent] Запуск в интерактивном режиме (будет добавлен позже).")
        # run_interactive_loop() — можешь позже добавить REPL/LLM-интеграцию

    elif mode == "cli":
        run_agent(config)

    elif mode == "mcp":
        run_mcp_agent(config)

    else:
        print(f"[Error] Неизвестный режим: {mode}")
        sys.exit(1)

if __name__ == "__main__":
    main()
