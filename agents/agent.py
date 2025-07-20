# agent.py

import argparse
from storage import DiaryStorage, GraphStorage


def main():
    parser = argparse.ArgumentParser(description="HMP Agent CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Diary commands
    write_parser = subparsers.add_parser("write_entry")
    write_parser.add_argument("text")
    write_parser.add_argument("--tags", nargs="*")

    read_parser = subparsers.add_parser("read_entries")
    read_parser.add_argument("--limit", type=int, default=5)

    # Graph commands
    add_concept_parser = subparsers.add_parser("add_concept")
    add_concept_parser.add_argument("name")

    add_link_parser = subparsers.add_parser("add_link")
    add_link_parser.add_argument("--from_node")
    add_link_parser.add_argument("--to_node")
    add_link_parser.add_argument("--relation")

    args = parser.parse_args()

    diary = DiaryStorage("diary.json")
    graph = GraphStorage("graph.json")

    if args.command == "write_entry":
        eid = diary.write_entry(args.text, args.tags or [])
        print(f"Entry saved with ID: {eid}")

    elif args.command == "read_entries":
        entries = diary.read_entries(limit=args.limit)
        for e in entries:
            print(f"[{e['id']}] {e['text']} (tags: {e['tags']})")

    elif args.command == "add_concept":
        cid = graph.add_concept(args.name)
        print(f"Concept added with ID: {cid}")

    elif args.command == "add_link":
        lid = graph.add_link(args.from_node, args.to_node, args.relation)
        print(f"Link added with ID: {lid}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
