import os
import json
import hashlib
import time
from pathlib import Path
import requests

# -----------------------------
# Конфигурация
# -----------------------------
HASHNODE_TOKEN = os.environ["HASHNODE_TOKEN"]
HASHNODE_PUBLICATION_ID = os.environ["HASHNODE_SPEC_ID"]
API_URL = "https://gql.hashnode.com"

PUBLISHED_FILE = "published_docs.json"

# Список файлов для публикации: путь -> title/slug
FILES_TO_PUBLISH = {
    "agents/tools/db_structure.sql": {
        "title": "Database Structure (CCore)",
        "slug": "database",
    },
    "docs/HMP-agent-REPL-cycle.md": {
        "title": "HMP Agent REPL Cycle",
        "slug": "hmp-agent-repl-cycle",
    },
}

# -----------------------------
# Функции
# -----------------------------
def file_hash(content: str) -> str:
    return hashlib.md5(content.encode("utf-8")).hexdigest()

def load_published() -> dict:
    if Path(PUBLISHED_FILE).exists():
        with open(PUBLISHED_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_published(data: dict):
    with open(PUBLISHED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def graphql_request(query: str, variables: dict) -> dict:
    headers = {
        "Authorization": f"Bearer {HASHNODE_TOKEN}",
        "Content-Type": "application/json"
    }
    resp = requests.post(API_URL, json={"query": query, "variables": variables}, headers=headers)
    data = resp.json()
    if "errors" in data:
        raise Exception(f"GraphQL errors: {data['errors']}")
    return data

def create_draft(title: str, slug: str, content: str) -> dict:
    query = """
    mutation CreateDraft($input: CreateDraftInput!) {
      createDraft(input: $input) { draft { id slug title } }
    }
    """
    variables = {
        "input": {
            "title": title,
            "contentMarkdown": content,
            "publicationId": HASHNODE_PUBLICATION_ID
        }
    }
    return graphql_request(query, variables)["data"]["createDraft"]["draft"]

def update_post(post_id: str, title: str, content: str) -> dict:
    query = """
    mutation UpdatePost($input: UpdatePostInput!) {
      updatePost(input: $input) { post { id slug title } }
    }
    """
    variables = {"input": {"id": post_id, "title": title, "contentMarkdown": content}}
    return graphql_request(query, variables)["data"]["updatePost"]["post"]

def publish_draft(draft_id: str) -> dict:
    query = """
    mutation PublishDraft($input: PublishDraftInput!) {
      publishDraft(input: $input) { post { id slug url } }
    }
    """
    variables = {"input": {"draftId": draft_id}}
    return graphql_request(query, variables)["data"]["publishDraft"]["post"]

# -----------------------------
# Главная функция
# -----------------------------
def main():
    published = load_published()

    for path, info in FILES_TO_PUBLISH.items():
        p = Path(path)
        if not p.exists():
            print(f"❌ Файл не найден: {path}")
            continue

        # Формируем содержимое поста с ссылкой на исходный файл
        content = f"Источник: [{p.name}](https://github.com/kagvi13/HMP/blob/main/{path})\n\n"
        content += p.read_text(encoding="utf-8")
        h = file_hash(content)
        name = p.stem

        # Проверка изменений
        if name in published and published[name].get("hash") == h:
            print(f"✅ {name} без изменений — пропускаем")
            continue

        try:
            if name in published and "id" in published[name]:
                post = update_post(published[name]["id"], info["title"], content)
                print(f"♻ Обновлён пост: {post['slug']}")
            else:
                draft = create_draft(info["title"], info["slug"], content)
                post = publish_draft(draft["id"])
                print(f"🆕 Опубликован пост: {post['slug']}")

            # Обновляем локальный JSON
            published[name] = {"id": post["id"], "hash": h}
            save_published(published)
            time.sleep(5)

        except Exception as e:
            print(f"❌ Ошибка публикации {name}: {e}")
            break

if __name__ == "__main__":
    main()
