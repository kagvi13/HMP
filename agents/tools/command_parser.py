# tools/command_parser.py

"""
Извлечение команд из JSON или размеченного текста.
Поддерживает следующие варианты:
- Явно размеченные JSON-блоки (```json ... ```)
- Префиксные команды (например, !shell, !graph)
"""

import json
import re
from typing import List, Optional, Dict, Any


COMMAND_PREFIXES = ["shell", "graph", "diary", "note"]


class ParsedCommand:
    def __init__(self, command_type: str, payload: Any):
        self.command_type = command_type
        self.payload = payload

    def __repr__(self):
        return f"<ParsedCommand {self.command_type}: {repr(self.payload)}>"


def parse_commands(text: str) -> List[ParsedCommand]:
    """Основной интерфейс: принимает текст, возвращает список ParsedCommand."""
    commands = []

    # 1. Поиск JSON-блоков
    for match in re.finditer(r"```json\n(.*?)```", text, re.DOTALL):
        block = match.group(1).strip()
        try:
            data = json.loads(block)
            if isinstance(data, dict) and "type" in data:
                commands.append(ParsedCommand(data["type"], data.get("payload")))
        except json.JSONDecodeError:
            continue

    # 2. Поиск префиксных команд (!shell, !graph и т.д.)
    for line in text.splitlines():
        for prefix in COMMAND_PREFIXES:
            if line.strip().startswith(f"!{prefix}"):
                payload = line.strip()[len(f"!{prefix}"):].strip()
                commands.append(ParsedCommand(prefix, payload))

    return commands


if __name__ == "__main__":
    sample = """
Вот пример команды:
```json
{
  "type": "shell",
  "payload": "ls -la"
}
```
А вот другая: !note Надо не забыть включить свет
"""
    cmds = parse_commands(sample)
    for c in cmds:
        print(c)
