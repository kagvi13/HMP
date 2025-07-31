import argparse
from datetime import datetime
from tools.storage import Storage

storage = Storage()

def add_message(role, content, source="cli", user_did=None):
    storage.write_note(
        content,
        role=role,
        source=source,
        user_did=user_did,
        tags=[]
    )
    print(f"[+] Сообщение от {role} ({source}) добавлено: {content}")

# --- CLI interface ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", required=True)
    parser.add_argument("--content", required=True)
    parser.add_argument("--source", default="cli")
    parser.add_argument("--user_did")
    args = parser.parse_args()

    add_message(args.role, args.content, args.source, args.user_did)
