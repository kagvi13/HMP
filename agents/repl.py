# repl.py

import readline
from storage import Storage
import time

# Заглушка для сравнения мыслей (можно заменить на LLM)
def compare_thoughts(a, b):
    import difflib
    ratio = difflib.SequenceMatcher(None, a, b).ratio()
    if ratio > 0.95:
        return "identical"
    elif ratio > 0.8:
        return "very similar"
    elif ratio > 0.6:
        return "somewhat similar"
    elif ratio > 0.4:
        return "different"
    else:
        return "unrelated"

# Основной REPL-цикл

def run_repl():
    storage = Storage()
    print("🧠 HMP-Agent [REPL режим]")
    print("Введите команду ('help' — список команд)")

    last_thought = None

    while True:
        try:
            cmd = input("🤖 > ").strip()

            if cmd in ("exit", "quit"):
                print("👋 Выход из REPL.")
                break

            elif cmd == "help":
                print("""
Доступные команды:
  think            — агент сгенерирует мысль
  write <текст>    — записать мысль в дневник
  read             — показать последние записи
  concepts         — показать список концептов
  links            — показать связи
  exit / quit      — выйти
""")

            elif cmd == "think":
                thought = input("🧠 Новая мысль: ").strip()
                print(f"💡 Мысль: {thought}")

                if last_thought:
                    similarity = compare_thoughts(last_thought, thought)
                    print(f"🧠 Сравнение с предыдущей мыслью: {similarity}")

                    if similarity in ("identical", "very similar"):
                        print("🔁 Мысли почти совпадают. Завершаю размышление.")
                        continue

                last_thought = thought
                storage.write_entry(thought)
                print("✅ Записано в дневник.")

            elif cmd.startswith("write "):
                text = cmd[len("write "):].strip()
                storage.write_entry(text)
                print("✅ Запись добавлена.")

            elif cmd == "read":
                entries = storage.read_entries()
                for e in entries:
                    print(f"[{e[0]}] {e[1]} | tags: {e[2]} | ts: {e[3]}")

            elif cmd == "concepts":
                for c in storage.get_concepts():
                    print(f"[{c[0]}] {c[1]} — {c[2]}")

            elif cmd == "links":
                for l in storage.get_links():
                    print(f"{l[1]} --[{l[3]}]--> {l[2]}")

            else:
                print("❓ Неизвестная команда. Введите 'help'.")

        except KeyboardInterrupt:
            print("\n👋 Прервано пользователем.")
            break

    storage.close()

if __name__ == "__main__":
    run_repl()
