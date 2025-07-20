# cli.py

import argparse
import yaml
import sys
from agent import run_agent, run_mcp_agent  # Ты можешь разделить реализацию
                                            # на функции внутри agent.py

def load_config(path="config.yml"):
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"[Error] Failed to load config: {e}")
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
