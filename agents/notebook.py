import argparse
from datetime import datetime
from tools.storage import Storage

storage = Storage()

def add_entry():
    print("Введите вашу запись (завершите пустой строкой):")
    lines = []
    try:
        while True:
            line = input()
            if line.strip() == "":
                break
            lines.append(line)
    except KeyboardInterrupt:
        print("\n[⚠️] Ввод прерван.")
        return

    text = "\n".join(lines).strip()
    if text:
        storage.write_note(text, tags=[])
        print("[💾] Запись сохранена в блокнот.")
    else:
        print("[⚠️] Пустая запись не сохранена.")

def list_entries(limit=10):
    notes = storage.read_notes(limit=limit)
    for note in notes:
        note_id, text, tags, source, read, timestamp = note
        title = text.split("\n")[0]
        print(f"[{timestamp}] ({source}) {title}")

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
