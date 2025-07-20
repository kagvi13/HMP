# agents/agent.py

import argparse
from storage import Storage

def main():
    parser = argparse.ArgumentParser(description="HMP Agent CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Diary commands
    write_parser = subparsers.add_parser("write_entry", help="Добавить запись в когнитивный дневник")
    write_parser.add_argument("text")
    write_parser.add_argument("--tags", nargs="*", help="Теги (опционально)")

    read_parser = subparsers.add_parser("read_entries", help="Показать последние записи")
    read_parser.add_argument("--limit", type=int, default=5)

    search_time_parser = subparsers.add_parser("search_entries_by_time", help="Поиск записей по временному диапазону")
    search_time_parser.add_argument("--from_ts", required=True)
    search_time_parser.add_argument("--to_ts", required=True)

    # Graph commands
    concept_parser = subparsers.add_parser("add_concept", help="Добавить концепт")
    concept_parser.add_argument("name")
    concept_parser.add_argument("--description", help="Описание (опционально)")

    link_parser = subparsers.add_parser("add_link", help="Добавить связь")
    link_parser.add_argument("--from_node", type=int, required=True)
    link_parser.add_argument("--to_node", type=int, required=True)
    link_parser.add_argument("--relation", required=True)

    expand_parser = subparsers.add_parser("expand_graph", help="Расширить граф от узла с глубиной")
    expand_parser.add_argument("--start_id", type=int, required=True)
    expand_parser.add_argument("--depth", type=int, default=1)

    args = parser.parse_args()
    storage = Storage()

    # Diary logic
    if args.command == "write_entry":
        storage.write_entry(args.text, args.tags)
        print("✅ Запись добавлена.")

    elif args.command == "read_entries":
        for entry in storage.read_entries(limit=args.limit):
            print(f"[{entry[0]}] {entry[1]} | tags: {entry[2]} | ts: {entry[3]}")

    elif args.command == "search_entries_by_time":
        results = storage.search_entries_by_time(args.from_ts, args.to_ts)
        for e in results:
            print(f"[{e[0]}] {e[1]} | tags: {e[2]} | ts: {e[3]}")

    # Graph logic
    elif args.command == "add_concept":
        cid = storage.add_concept(args.name, args.description)
        print(f"✅ Концепт добавлен с ID: {cid}")

    elif args.command == "add_link":
        storage.add_link(args.from_node, args.to_node, args.relation)
        print("✅ Связь добавлена.")

    elif args.command == "expand_graph":
        links = storage.expand_graph(args.start_id, args.depth)
        print(f"📐 Подграф (до глубины {args.depth}):")
        for src, tgt, rel in links:
            print(f"{src} --[{rel}]--> {tgt}")

    else:
        parser.print_help()

    storage.close()

if __name__ == "__main__":
    main()
