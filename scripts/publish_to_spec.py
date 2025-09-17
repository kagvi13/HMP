import os
import json
import hashlib
import time
from pathlib import Path
import requests

PUBLISHED_FILE = "published_spec.json"

# Твой список файлов и слуги
FILES_TO_PUBLISH = {
    "agents/tools/db_structure.sql": {
        "title": "Database Structure (CCore)",
        "slug": "ccore/database",
    },
    "docs/HMP-agent-REPL-cycle.md": {
        "title": "HMP Agent REPL Cycle",
        "slug": "ccore/hmp-agent-repl-cycle",
    },
}

HASHNODE_TOKEN = os.environ["HASHNODE_TOKEN"]
HASHNODE_PUBLICATION_ID = os.environ["HASHNODE_PUBLICATION_ID"]
API_URL = "https://gql.hashnode.com"


def load_published():
    if Path(PUBLISHED_FILE).exists():
        with open(PUBLISHED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_published(data):
    with open(PUBLISHED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def file_hash(text: str):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def graphql_request(query, variables):
    headers = {"Authorization": f"Bearer {HASHNODE_TOKEN}", "Content-Type": "application/json"}
    resp = requests.post(API_URL, json={"query": query, "variables": variables}, headers=headers)
    data = resp.json()
    if "errors" in data:
        raise Exception(f"GraphQL errors: {data['errors']}")
    return data


def create_post(title, slug, markdown_content):
    query = """
    mutation CreateDraft($input: CreateDraftInput!) {
      createDraft(input: $input) { draft { id slug title } }
    }
    """
    variables = {
        "input": {
            "title": title,
            "slug": slug,
            "contentMarkdown": markdown_content,
            "publicationId": HASHNODE_PUBLICATION_ID,
        }
    }
    return graphql_request(query, variables)["data"]["createDraft"]["draft"]


def update_post(post_id, title, markdown_content):
    query = """
    mutation UpdatePost($input: UpdatePostInput!) {
      updatePost(input: $input) { post { id slug title } }
    }
    """
    variables = {
        "input": {"id": post_id, "title": title, "contentMarkdown": markdown_content}
    }
    return graphql_request(query, variables)["data"]["updatePost"]["post"]


def publish_draft(draft_id):
    query = """
    mutation PublishDraft($input: PublishDraftInput!) {
      publishDraft(input: $input) { post { id slug url } }
    }
    """
    variables = {"input": {"draftId": draft_id}}
    return graphql_request(query, variables)["data"]["publishDraft"]["post"]


def read_file_as_markdown(path: str) -> str:
    if path.endswith(".sql"):
        code = Path(path).read_text(encoding="utf-8")
        return f"```sql\n{code}\n```"
    else:
        return Path(path).read_text(encoding="utf-8")


def main(force=False):
    published = load_published()

    for path, meta in FILES_TO_PUBLISH.items():
        path_obj = Path(path)
        if not path_obj.exists():
            print(f"⚠ Файл {path} не найден, пропускаем")
            continue

        md_text = f"Источник: [{path}](https://github.com/kagvi13/HMP/blob/main/{path})\n\n" \
                  + read_file_as_markdown(path)
        h = file_hash(md_text)

        name = meta["slug"]
        title = meta["title"]
        slug = meta["slug"]

        if not force and name in published and published[name].get("hash") == h:
            print(f"✅ Пост '{title}' без изменений — пропускаем.")
            continue

        try:
            if name in published and "id" in published[name]:
                post = update_post(published[name]["id"], title, md_text)
                print(f"♻ Обновлён пост: {post['title']} ({post['slug']})")
            else:
                draft = create_post(title, slug, md_text)
                post = publish_draft(draft["id"])
                print(f"🆕 Пост опубликован: {post['title']} ({post['slug']})")

            published[name] = {"id": post["id"], "slug": post["slug"], "hash": h}
            save_published(published)

            time.sleep(15)

        except Exception as e:
            print(f"❌ Ошибка при публикации {path}: {e}")
            save_published(published)
            break


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Обновить все посты, даже без изменений")
    args = parser.parse_args()
    main(force=args.force)
