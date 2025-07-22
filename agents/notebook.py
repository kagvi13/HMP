import argparse
from datetime import datetime
from notebook_store import Notebook

notebook = Notebook()

def add_entry():
    print("Введите вашу запись (завершите пустой строкой):")
    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    text = "\n".join(lines).strip()
    if text:
        notebook.add_note(text, source="user")
        print("[💾] Запись сохранена в блокнот.")
    else:
        print("[⚠️] Пустая запись не сохранена.")

def list_entries(limit=10):
    notes = notebook.get_last_notes(limit=limit)
    for note in notes:
        timestamp = note['timestamp']
        source = note['source']
        text = note['text'].split("\n")[0]
        print(f"[{timestamp}] ({source}) {text}")

def main():
    parser = argparse.ArgumentParser(description="Интерфейс пользователя для записи мыслей")
    parser.add_argument("--list", action="store_true", help="Показать последние записи")
    parser.add_argument("--limit", type=int, default=10, help="Сколько записей показать при --list")
    args = parser.parse_args()

    if args.list:
        list_entries(limit=args.limit)
    else:
        add_entry()

if __name__ == "__main__":
    main()
