# agents/add_message.py

import argparse
from tools.storage import Storage

storage = Storage()

def add_message(content, source="cli", user_did="anon"):
    storage.write_note(
        content,
        source=source,
        user_did=user_did
    )
    print(f"[+] Сообщение от {source} ({user_did}) добавлено: {content}")

# --- CLI interface ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--content", required=True)
    parser.add_argument("--source", default="cli")
    parser.add_argument("--user_did", default="anon")
    args = parser.parse_args()

    add_message(args.content, args.source, args.user_did)
